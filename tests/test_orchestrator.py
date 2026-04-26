import unittest
import os
import time
from datetime import datetime, timedelta, timezone
from gcm.schema import GeometricNode
from gcm.registry import GeometricRegistry
from gcm.orchestrator import TimelineOrchestrator, FourierTimeEngine, DiscontinuityError

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_orchestrator.json"
        self.registry = GeometricRegistry(filepath=self.test_file)
        self.orchestrator = TimelineOrchestrator(self.registry)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_fourier_time_engine_bend(self):
        t_now = datetime.now(timezone.utc)
        current_z = 50.0

        # Close in Z, recent timestamp -> high dynamic weight
        node_high_res = GeometricNode(content="High Resonance", weight=5.0, timestamp=t_now, z=50.0)
        # Far in Z -> low dynamic weight (negative cosine value if pi distance)
        # Note: distance in Z is 50.0, which is 50 radians (~7.96 * 2pi + ~0.96pi). It's close to -1 resonance.
        node_low_res = GeometricNode(content="Low Resonance", weight=5.0, timestamp=t_now, z=0.0)

        nodes = [node_low_res, node_high_res]

        sorted_nodes = FourierTimeEngine.bend(nodes, current_z, t_now)

        self.assertEqual(sorted_nodes[0].content, "High Resonance")
        self.assertEqual(sorted_nodes[1].content, "Low Resonance")

    def test_orchestrator_intercept_locked_node(self):
        # Target coords will be (50, 50, 50)
        target = (50.0, 50.0, 50.0)

        t_old = datetime.now(timezone.utc) - timedelta(days=2)
        # Locked node
        node_locked = GeometricNode(content="Locked Node", weight=2.0, timestamp=t_old, x=50.0, y=50.0, z=50.0)

        self.registry.add_node(node_locked)

        # Intercept should return the nearest but NOT modify weight of locked node
        intercepted = self.orchestrator.intercept(target)
        self.assertEqual(len(intercepted), 1)

        # Verify node weight did NOT increase
        retrieved_node = self.registry.get_node(node_locked.uid)
        self.assertEqual(retrieved_node.weight, 2.0)

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
