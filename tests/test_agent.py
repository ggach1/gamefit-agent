import unittest

from agent_server.agent import GameJobAgent
from agent_server.tools import REGISTRY


class GameJobAgentTest(unittest.TestCase):
    def setUp(self):
        self.agent = GameJobAgent()

    def test_four_tools_are_registered(self):
        self.assertEqual(4, len(REGISTRY))
        self.assertIn("calculate_fit", REGISTRY)

    def test_tool_selection_requires_both_inputs_for_comparison(self):
        self.assertEqual(["extract_requirements"], self.agent.select_tools("C++", ""))
        self.assertEqual(4, len(self.agent.select_tools("C++", "C++")))

    def test_analysis_calculates_match_and_gap(self):
        result = self.agent.analyze("C++ TCP Redis Git", "C++ TCP Git Python")
        self.assertEqual(75, result["fit"]["score"])
        self.assertEqual(["Redis"], result["fit"]["missing_skills"])
        self.assertEqual(4, len(result["trace"]))

    def test_empty_input_is_rejected(self):
        with self.assertRaises(ValueError):
            self.agent.analyze("", "C++")


if __name__ == "__main__":
    unittest.main()

