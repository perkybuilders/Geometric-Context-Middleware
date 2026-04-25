import unittest
from gcm.schema import GeometricNode
from gcm.observer import Observer

class TestObserver(unittest.TestCase):
    def setUp(self):
        self.observer = Observer()

    def test_evaluate_passed(self):
        node1 = GeometricNode(content="Important Concept")
        node2 = GeometricNode(content="Another Detail")

        # Output contains contents of both nodes
        llm_output = "I have considered the Important Concept and also Another Detail."

        passed, missing = self.observer.evaluate(llm_output, [node1, node2])
        self.assertTrue(passed)
        self.assertEqual(len(missing), 0)

    def test_evaluate_passed_with_uid(self):
        node = GeometricNode(content="Complex Content")

        # Output contains UID instead of content
        llm_output = f"Referencing node {node.uid}."

        passed, missing = self.observer.evaluate(llm_output, [node])
        self.assertTrue(passed)
        self.assertEqual(len(missing), 0)

    def test_evaluate_failed(self):
        node1 = GeometricNode(content="Important Concept")
        node2 = GeometricNode(content="Missing Link")

        # Output is missing node2
        llm_output = "I only know about Important Concept."

        passed, missing = self.observer.evaluate(llm_output, [node1, node2])
        self.assertFalse(passed)
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].uid, node2.uid)

    def test_trigger_regrounding_maneuver(self):
        node = GeometricNode(content="Bridge Needed")
        warning = self.observer.trigger_regrounding_maneuver([node])

        self.assertIn("[!] RE-GROUNDING MANEUVER TRIGGERED", warning)
        self.assertIn(str(node.uid), warning)

        empty_warning = self.observer.trigger_regrounding_maneuver([])
        self.assertEqual(empty_warning, "")

if __name__ == '__main__':
    unittest.main()
