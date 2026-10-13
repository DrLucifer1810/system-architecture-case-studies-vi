#!/usr/bin/env python3
"""
Sanitized Reference Implementation: Semantic Edit Ratio & Dreyfus/Bloom Prompt Compiler
"""
import difflib
import json
from typing import Dict, Any, Tuple


class EvaluationCompiler:
    """
    Computes Myers line-level Edit Ratio and synthesizes Bloom/Dreyfus evaluation prompts.
    """

    @staticmethod
    def calculate_edit_ratio(ai_output: str, final_user_output: str) -> float:
        """
        Calculates the Edit Ratio:
        0.0 = User accepted AI output verbatim (0 modifications).
        1.0 = User completely rewrote or deleted the AI output.
        """
        if not ai_output.strip():
            return 1.0

        ai_lines = ai_output.splitlines(keepends=True)
        user_lines = final_user_output.splitlines(keepends=True)

        matcher = difflib.SequenceMatcher(None, ai_lines, user_lines)
        total_lines = 0
        changed_lines = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                total_lines += (i2 - i1)
            elif tag in ('replace', 'delete', 'insert'):
                diff_count = max(i2 - i1, j2 - j1)
                total_lines += diff_count
                changed_lines += diff_count

        if total_lines == 0:
            return 0.0

        return round(changed_lines / total_lines, 4)

    @classmethod
    def build_enterprise_prompt(
        cls,
        category: str,
        ai_output: str,
        final_user_output: str,
        edit_ratio: float
    ) -> str:
        ai_token_estimate = max(1, len(ai_output) // 4)
        final_token_estimate = max(1, len(final_user_output) // 4)

        return f"""You are an Enterprise AI Evaluator. Analyze the user's AI-assisted session.
Category: {category}
AI Original Output (Est. {ai_token_estimate} tokens):
---
{ai_output}
---
User's Final Saved Output (Est. {final_token_estimate} tokens):
---
{final_user_output}
---
Edit Ratio (0.0 = untouched, 1.0 = full rewrite): {edit_ratio:.2f}

Evaluate the user's interaction based on Enterprise 6-D metrics (score 0-100):
1. competence: (Bloom's Taxonomy) Did they Apply/Analyze to solve a problem vs blind copy?
2. discipline: Code standards, error handling, edge cases, and documentation.
3. creativity: (Dreyfus Model) Expert adaptation beyond naive generation.
4. critical_thinking: Detecting and correcting AI hallucinations.
5. collaboration: Readability, clean architecture, and maintainability.
6. ai_efficiency: Token ROI. High score if AI saved time without excessive rewrites.

Respond ONLY with a JSON object:
{{
    "competence": 85,
    "discipline": 90,
    "creativity": 75,
    "critical_thinking": 88,
    "collaboration": 85,
    "ai_efficiency": 92,
    "tips": "Well structured, consider adding docstrings to public types."
}}"""


def run_tests():
    # Scenario 1: Exact match (Edit Ratio = 0.0)
    ai_code = "fn compute() -> u64 {\n    42\n}\n"
    user_same = "fn compute() -> u64 {\n    42\n}\n"
    ratio1 = EvaluationCompiler.calculate_edit_ratio(ai_code, user_same)
    assert ratio1 == 0.0, f"Expected 0.0, got {ratio1}"

    # Scenario 2: Refactoring with hallucination fix (Partial edit)
    user_edited = "fn compute() -> Result<u64, Error> {\n    Ok(42)\n}\n"
    ratio2 = EvaluationCompiler.calculate_edit_ratio(ai_code, user_edited)
    assert 0.0 < ratio2 < 1.0, f"Expected 0 < ratio < 1, got {ratio2}"

    # Scenario 3: Complete discard (Edit Ratio = 1.0)
    user_rewritten = "fn completely_different() {}\n"
    ratio3 = EvaluationCompiler.calculate_edit_ratio(ai_code, user_rewritten)
    assert ratio3 == 1.0, f"Expected 1.0, got {ratio3}"

    # Verify prompt builder output
    prompt = EvaluationCompiler.build_enterprise_prompt("Coding", ai_code, user_edited, ratio2)
    assert "Category: Coding" in prompt
    assert "Edit Ratio" in prompt
    assert "competence" in prompt
    print("All Python EvaluationCompiler unit tests passed successfully!")


if __name__ == "__main__":
    run_tests()
