import unittest
from uuid import uuid4
from pydantic import ValidationError
from gcm.schema import GeometricNode, Link, RelationshipType

class TestSchema(unittest.TestCase):
    def test_geometric_node_creation(self):
        node = GeometricNode(content="Test content")
        self.assertIsNotNone(node.uid)
        self.assertEqual(node.content, "Test content")
        self.assertEqual(node.weight, 1.0)
        self.assertEqual(node.x, 50.0)
        self.assertEqual(node.y, 50.0)
        self.assertEqual(node.z, 50.0)
        self.assertEqual(len(node.links), 0)

    def test_geometric_node_custom_coords(self):
        node = GeometricNode(content="Test content", x=10.0, y=90.0, z=0.0)
        self.assertEqual(node.x, 10.0)
        self.assertEqual(node.y, 90.0)
        self.assertEqual(node.z, 0.0)

    def test_geometric_node_with_links(self):
        target_uid = uuid4()
        link = Link(target_uid=target_uid, relationship_type=RelationshipType.DEPENDENCY)
        node = GeometricNode(content="Linked node", links=[link])
        self.assertEqual(len(node.links), 1)
        self.assertEqual(node.links[0].target_uid, target_uid)
        self.assertEqual(node.links[0].relationship_type, RelationshipType.DEPENDENCY)

    def test_geometric_node_weight_validation(self):
        with self.assertRaises(ValidationError):
            GeometricNode(content="Too light", weight=0.5)
        with self.assertRaises(ValidationError):
            GeometricNode(content="Too heavy", weight=11.0)

        valid_node = GeometricNode(content="Just right", weight=5.5)
        self.assertEqual(valid_node.weight, 5.5)

if __name__ == '__main__':
    unittest.main()
