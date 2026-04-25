import json
import os
import fcntl
from typing import Dict, List
from uuid import UUID

from .schema import GeometricNode


class GeometricRegistry:
    def __init__(self, filepath: str = None):
        if filepath is None:
            filepath = os.getenv("GCM_DATA_PATH", "geometric_registry.json")
        self.filepath = filepath
        self._ensure_file()
        self.decay_weights()

    def decay_weights(self):
        """
        Decays the weight of every dot by 5% (min 1.0).
        Called on initialization and whenever 'list' is run.
        """
        data = self._read_data()
        changed = False
        for uid_str, node_data in data.items():
            if 'weight' in node_data:
                current_weight = float(node_data['weight'])
                new_weight = max(1.0, current_weight * 0.95)
                if current_weight != new_weight:
                    node_data['weight'] = new_weight
                    changed = True

        if changed:
            self._write_data(data)

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
        # Store as dict to easily serialize with datetime string
        node_dict = node.model_dump(mode="json")
        data[str(node.uid)] = node_dict
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
        from .schema import Link
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
