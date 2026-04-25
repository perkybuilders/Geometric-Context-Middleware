import unittest
import os
import time
from datetime import datetime, timedelta, timezone
from gcm.schema import GeometricNode
from gcm.registry import GeometricRegistry
from gcm.orchestrator import TimelineOrchestrator, WeightEngine, DiscontinuityError

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_orchestrator.json"
        self.registry = GeometricRegistry(filepath=self.test_file)
        self.orchestrator = TimelineOrchestrator(self.registry)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_weight_engine_bend(self):
        now = datetime.now(timezone.utc)

        node_heavy = GeometricNode(content="Heavy", weight=9.0, timestamp=now)
        node_light_new = GeometricNode(content="Light New", weight=2.0, timestamp=now)
        node_light_old = GeometricNode(content="Light Old", weight=2.0, timestamp=now - timedelta(days=1))

        nodes = [node_light_old, node_heavy, node_light_new]

        sorted_nodes = WeightEngine.bend(nodes)

        self.assertEqual(sorted_nodes[0].content, "Heavy")
        self.assertEqual(sorted_nodes[1].content, "Light New")
        self.assertEqual(sorted_nodes[2].content, "Light Old")

    def test_orchestrator_intercept_spatial(self):
        # Target coords will be (50, 50, 50)
        target = (50.0, 50.0, 50.0)

        # Very close
        node1 = GeometricNode(content="Node 1", x=50.0, y=51.0, z=50.0)
        # A bit further
        node2 = GeometricNode(content="Node 2", x=60.0, y=50.0, z=50.0)
        # Even further
        node3 = GeometricNode(content="Node 3", x=70.0, y=50.0, z=50.0)
        # Far away
        node4 = GeometricNode(content="Node 4", x=100.0, y=100.0, z=100.0)

        self.registry.add_node(node1)
        self.registry.add_node(node2)
        self.registry.add_node(node3)
        self.registry.add_node(node4)

        # Intercept should return the 3 nearest
        intercepted = self.orchestrator.intercept(target)
        self.assertEqual(len(intercepted), 3)
        self.assertEqual(intercepted[0].content, "Node 1")
        self.assertEqual(intercepted[1].content, "Node 2")
        self.assertEqual(intercepted[2].content, "Node 3")

    def test_discontinuity_error(self):
        target = (0.0, 0.0, 0.0)

        # Only node is very far away
        node1 = GeometricNode(content="Node 1", x=100.0, y=100.0, z=100.0)
        self.registry.add_node(node1)

        with self.assertRaises(DiscontinuityError):
            self.orchestrator.intercept(target)

    def test_orchestrator_construct_harness(self):
        node = GeometricNode(content="Reference Content")
        harness = self.orchestrator.construct_harness([node])

        self.assertIn("You are currently at Point", harness)
        self.assertIn("Your Reference Dots are [", harness)
        self.assertIn(str(node.uid), harness)
        self.assertIn("Reference Content", harness)

if __name__ == '__main__':
    unittest.main()
