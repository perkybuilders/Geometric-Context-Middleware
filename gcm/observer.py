from typing import List, Tuple

from .schema import GeometricNode


class Observer:
    def evaluate(self, llm_output: str, required_dots: List[GeometricNode]) -> Tuple[bool, List[GeometricNode]]:
        """
        Evaluates the LLM output.
        Checks: "Did the LLM reference the required Dots?"
        Returns a tuple: (Passed Evaluation, List of Missing Dots)
        """
        missing_dots = []
        for dot in required_dots:
            # Simple substring matching for now.
            # In a more advanced implementation, this could use semantic similarity.
            if str(dot.uid) not in llm_output and dot.content not in llm_output:
                missing_dots.append(dot)

        passed = len(missing_dots) == 0
        return passed, missing_dots

    def trigger_regrounding_maneuver(self, missing_dots: List[GeometricNode]) -> str:
        """
        Trigger a "Re-Grounding Maneuver" and prompt the user for the "Missing Bridge Dot."
        """
        if not missing_dots:
            return ""

        missing_uids = [str(dot.uid) for dot in missing_dots]
        warning = f"[!] RE-GROUNDING MANEUVER TRIGGERED. The LLM failed to reference the following required Dots: {', '.join(missing_uids)}. "
        warning += "Please provide a 'Missing Bridge Dot' to connect the response to the graph."
        return warning
