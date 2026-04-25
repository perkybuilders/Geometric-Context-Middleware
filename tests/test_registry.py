import unittest
import os
import json
from uuid import uuid4
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

if __name__ == '__main__':
    unittest.main()
