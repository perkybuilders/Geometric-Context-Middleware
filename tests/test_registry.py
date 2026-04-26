import unittest
import os
import json
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from gcm.schema import GeometricNode, Link, RelationshipType
from gcm.registry import GeometricRegistry

class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_registry.json"
        self.registry = GeometricRegistry(filepath=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_and_get_node(self):
        node = GeometricNode(content="Registry test")
        self.registry.add_node(node)

        retrieved_node = self.registry.get_node(node.uid)
        self.assertEqual(retrieved_node.uid, node.uid)
        self.assertEqual(retrieved_node.content, node.content)

    def test_get_all_nodes(self):
        node1 = GeometricNode(content="Node 1")
        node2 = GeometricNode(content="Node 2")
        self.registry.add_node(node1)
        self.registry.add_node(node2)

        all_nodes = self.registry.get_all_nodes()
        self.assertEqual(len(all_nodes), 2)
        uids = [n.uid for n in all_nodes]
        self.assertIn(node1.uid, uids)
        self.assertIn(node2.uid, uids)

    def test_check_voids(self):
        # Node with no links (a void)
        void_node = GeometricNode(content="Void node")

        # Node with a link (not a void)
        linked_node = GeometricNode(
            content="Linked node",
            links=[Link(target_uid=void_node.uid, relationship_type=RelationshipType.DEPENDENCY)]
        )

        self.registry.add_node(void_node)
        self.registry.add_node(linked_node)

        voids = self.registry.check_voids()
        self.assertEqual(len(voids), 1)
        self.assertEqual(voids[0].uid, void_node.uid)

    def test_link_nodes(self):
        node1 = GeometricNode(content="Source Node")
        node2 = GeometricNode(content="Target Node")

        self.registry.add_node(node1)
        self.registry.add_node(node2)

        self.registry.link_nodes(node1.uid, node2.uid, RelationshipType.DEPENDENCY)

        updated_node1 = self.registry.get_node(node1.uid)

        self.assertEqual(len(updated_node1.links), 1)
        self.assertEqual(updated_node1.links[0].target_uid, node2.uid)
        self.assertEqual(updated_node1.links[0].relationship_type, RelationshipType.DEPENDENCY)

    def test_locked_node_modification_prevented(self):
        old_time = datetime.now(timezone.utc) - timedelta(days=2)
        node = GeometricNode(content="Historical Bubble", timestamp=old_time)

        # Add initially
        # Bypass add_node logic for initial creation of old node, or use _write_data
        data = {str(node.uid): node.model_dump(mode="json")}
        self.registry._write_data(data)

        self.assertTrue(node.is_locked)

        # Attempt to modify
        node.content = "Modified Content"
        with self.assertRaises(ValueError):
            self.registry.add_node(node)

    def test_auto_surveyor_routing(self):
        node_existing = GeometricNode(content="Existing Enterprise System", y=50.0, z=50.0)
        self.registry.add_node(node_existing)

        node_new = GeometricNode(content="New AnyRide Module", y=55.0, z=55.0) # distance is sqrt(25 + 25) = ~7.07 < 10.0
        self.registry.add_node(node_new)

        retrieved_new = self.registry.get_node(node_new.uid)
        self.assertEqual(len(retrieved_new.links), 1)
        self.assertEqual(retrieved_new.links[0].target_uid, node_existing.uid)
        self.assertEqual(retrieved_new.links[0].relationship_type, RelationshipType.EXPANSION)

    def test_locked_node_link_prevented(self):
        old_time = datetime.now(timezone.utc) - timedelta(days=2)
        node1 = GeometricNode(content="Old Source Node", timestamp=old_time)
        node2 = GeometricNode(content="Target Node")

        # Bypass add_node check for initial add
        data = {str(node1.uid): node1.model_dump(mode="json"), str(node2.uid): node2.model_dump(mode="json")}
        self.registry._write_data(data)

        with self.assertRaises(ValueError):
            self.registry.link_nodes(node1.uid, node2.uid, RelationshipType.DEPENDENCY)

if __name__ == '__main__':
    unittest.main()
