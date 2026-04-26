import json
import os
import fcntl
import math
from typing import Dict, List
from uuid import UUID

from .schema import GeometricNode, Link, RelationshipType


class GeometricRegistry:
    def __init__(self, filepath: str = None):
        if filepath is None:
            filepath = os.getenv("GCM_DATA_PATH", "geometric_registry.json")
        self.filepath = filepath
        self._ensure_file()
        self.decay_weights()

    def decay_weights(self):
        """
        No-op. Linear decay is replaced by the dynamic Fourier Time Engine.
        """
        pass

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)

    def _read_data(self) -> Dict[str, dict]:
        with open(self.filepath, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        return data

    def _write_data(self, data: Dict[str, dict]):
        with open(self.filepath, 'w') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=2)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def add_node(self, node: GeometricNode):
        data = self._read_data()
        uid_str = str(node.uid)

        if uid_str in data:
            # Gade Murde Protocol: protect historical bubbles
            existing_node = GeometricNode(**data[uid_str])
            if existing_node.is_locked:
                raise ValueError(f"Node {node.uid} is locked and cannot be modified.")
        else:
            # Auto-Surveyor Routing for new nodes
            is_isolated = node.x == -80 or "theory" in node.content.lower() or "learning" in node.content.lower()
            is_peak_isolated = node.z == 100 or "music" in node.content.lower()

            if not is_isolated and not is_peak_isolated:
                content_lower = node.content.lower()
                if "enterprise" in content_lower or "anyride" in content_lower or "grubxpress" in content_lower:
                    # Calculate distance to other Enterprise nodes in Y and Z
                    for other_uid, other_data in data.items():
                        other_node = GeometricNode(**other_data)
                        other_content_lower = other_node.content.lower()
                        if "enterprise" in other_content_lower or "anyride" in other_content_lower or "grubxpress" in other_content_lower:
                            distance = math.sqrt((node.y - other_node.y)**2 + (node.z - other_node.z)**2)
                            if distance < 10.0:
                                node.links.append(Link(target_uid=other_node.uid, relationship_type=RelationshipType.EXPANSION))

        # Store as dict to easily serialize with datetime string
        node_dict = node.model_dump(mode="json")
        data[uid_str] = node_dict
        self._write_data(data)

    def link_nodes(self, source_uid: UUID, target_uid: UUID, rel_type):
        data = self._read_data()

        source_data = data.get(str(source_uid))
        if not source_data:
            raise KeyError(f"Source node with uid {source_uid} not found.")

        target_data = data.get(str(target_uid))
        if not target_data:
            raise KeyError(f"Target node with uid {target_uid} not found.")

        # Re-instantiate the source node to easily validate/append the link
        source_node = GeometricNode(**source_data)
        if source_node.is_locked:
            raise ValueError(f"Source node {source_uid} is locked and cannot be modified.")

        source_node.links.append(Link(target_uid=target_uid, relationship_type=rel_type))

        # Save back to dict
        data[str(source_uid)] = source_node.model_dump(mode="json")
        self._write_data(data)

    def get_node(self, uid: UUID) -> GeometricNode:
        data = self._read_data()
        node_data = data.get(str(uid))
        if not node_data:
            raise KeyError(f"Node with uid {uid} not found.")
        return GeometricNode(**node_data)

    def get_all_nodes(self) -> List[GeometricNode]:
        data = self._read_data()
        return [GeometricNode(**node_data) for node_data in data.values()]

    def check_voids(self) -> List[GeometricNode]:
        """
        Identify "Negative Space" where a ContextNode has no outgoing Edges.
        Returns a list of nodes that have empty links.
        """
        all_nodes = self.get_all_nodes()
        voids = []
        for node in all_nodes:
            if not node.links:
                voids.append(node)
        return voids
