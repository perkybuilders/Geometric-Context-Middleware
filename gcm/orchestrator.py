import math
from typing import List, Tuple
from datetime import datetime, timezone

from .schema import GeometricNode
from .registry import GeometricRegistry


class WeightEngine:
    @staticmethod
    def bend(dots: List[GeometricNode]) -> List[GeometricNode]:
        """
        Sort Dots by weight and temporal_proximity.
        Higher weight comes first, then newer nodes.
        """
        return sorted(
            dots,
            key=lambda d: (-d.weight, -d.timestamp.timestamp()),
        )


class DiscontinuityError(Exception):
    pass

class TimelineOrchestrator:
    def __init__(self, registry: GeometricRegistry, discontinuity_threshold: float = 30.0):
        self.registry = registry
        self.weight_engine = WeightEngine()
        self.discontinuity_threshold = discontinuity_threshold

    def calculate_distance(self, target: Tuple[float, float, float], node: GeometricNode) -> float:
        """
        Calculate Euclidean distance between target coordinates and a node.
        """
        return math.sqrt(
            (node.x - target[0])**2 +
            (node.y - target[1])**2 +
            (node.z - target[2])**2
        )

    def intercept(self, current_coords: Tuple[float, float, float], relevant_uids: List[str] = None) -> List[GeometricNode]:
        """
        Before the LLM sees a prompt, perform a Spatial Query for the 3 nearest dots.
        """
        all_nodes = self.registry.get_all_nodes()
        if relevant_uids is not None:
            relevant_uids_set = set(str(uid) for uid in relevant_uids)
            nodes = [node for node in all_nodes if str(node.uid) in relevant_uids_set]
        else:
            nodes = all_nodes

        if not nodes:
            return []

        # Sort by distance
        nodes.sort(key=lambda n: self.calculate_distance(current_coords, n))

        nearest = nodes[:3]

        # Boost resonance heat for intercepted nodes
        for node in nearest:
            node.weight = min(10.0, node.weight + 1.0)
            self.registry.add_node(node)

        # Check for Void/Geometric Discontinuity
        min_distance = self.calculate_distance(current_coords, nearest[0])
        if min_distance > self.discontinuity_threshold:
            raise DiscontinuityError(
                f"I see where we are {current_coords}, but there are no dots in this region. "
                "Can you provide a bridge to connect the Vision to the Execution?"
            )

        return nearest

    def construct_harness(self, reference_dots: List[GeometricNode]) -> str:
        """
        Inject the "Geometric Line" as a system instruction.
        """
        current_time = datetime.now(timezone.utc).isoformat()

        if not reference_dots:
            dot_representations = "[]"
        else:
            dot_representations = "[" + ", ".join([f"Node({dot.uid}, weight={dot.weight}, content='{dot.content}')" for dot in reference_dots]) + "]"

        instruction = (
            f"You are currently at Point {current_time} on the Timeline. "
            f"Your Reference Dots are {dot_representations}. "
            "Connect your next response to these vertices."
        )
        return instruction
