import math
from typing import List, Tuple
from datetime import datetime, timezone

from .schema import GeometricNode
from .registry import GeometricRegistry


class FourierTimeEngine:
    @staticmethod
    def calculate_weight(node: GeometricNode, current_z: float, t_now: datetime) -> float:
        """
        W = W_base * cos(2 * pi * (t_now - t_node) / T + phi)
        T is 24 hours (in seconds), W_base is node.weight, phi is phase shift based on Z axis.
        """
        T = 24.0 * 3600.0
        time_diff = (t_now - node.timestamp).total_seconds()
        # Scale the Z difference (0-100) to a phase shift angle (0 to pi)
        # So maximum Z distance (100) flips the resonance wave exactly (pi shift)
        phi = math.pi * (abs(current_z - node.z) / 100.0)
        resonance = math.cos(2 * math.pi * time_diff / T + phi)
        return node.weight * resonance

    @staticmethod
    def bend(dots: List[GeometricNode], current_z: float, t_now: datetime) -> List[GeometricNode]:
        """
        Sort Dots by dynamic Fourier time resonance.
        Higher dynamic weight comes first, then newer nodes.
        """
        return sorted(
            dots,
            key=lambda d: (-FourierTimeEngine.calculate_weight(d, current_z, t_now), -d.timestamp.timestamp()),
        )


class DiscontinuityError(Exception):
    pass

class TimelineOrchestrator:
    def __init__(self, registry: GeometricRegistry, discontinuity_threshold: float = 30.0):
        self.registry = registry
        self.weight_engine = FourierTimeEngine()
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

        # Sort by distance and dynamic resonance
        t_now = datetime.now(timezone.utc)
        current_z = current_coords[2]

        # Sort by Fourier time resonance as requested by the architecture
        # and then by distance
        nodes = self.weight_engine.bend(nodes, current_z, t_now)
        # Note: the original architecture primarily used distance for 'nearest',
        # but to properly utilize the engine without breaking `bend()`,
        # we can just take the most resonant and then closest.
        # But let's just make it sort by distance, then weight using the engine.
        nodes.sort(key=lambda n: (self.calculate_distance(current_coords, n), -self.weight_engine.calculate_weight(n, current_z, t_now)))

        nearest = nodes[:3]

        # Boost resonance heat for intercepted nodes
        for node in nearest:
            if not node.is_locked:
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
