import json
import re
from typing import Dict, Any

REQUIRED_KEYS = [
    "defect_name",
    "description",
    "location",
    "severity",
    "possible_causes",
    "recommended_actions",
    "inspection_decision"
]

class ResponseValidator:
    @staticmethod
    def parse_and_validate(raw_text: str) -> Dict[str, Any]:
        """
        Extracts JSON from VLM output text, stripping any accidental markdown fences,
        and ensures all mandatory schema fields exist.
        """
        cleaned = raw_text.strip()
        # Remove markdown code block if present
        if "```" in cleaned:
            # Extract content between ```json ... ``` or ``` ... ```
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            if match:
                cleaned = match.group(1).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            # Attempt to extract first outer curly braces
            brace_match = re.search(r"(\{[\s\S]*\})", cleaned)
            if brace_match:
                parsed = json.loads(brace_match.group(1))
            else:
                raise ValueError(f"Could not parse valid JSON from VLM output: {raw_text[:200]}...")

        # Schema validation
        for key in REQUIRED_KEYS:
            if key not in parsed:
                raise KeyError(f"Missing required key in VLM response: '{key}'")

        # Type sanitization
        if not isinstance(parsed["possible_causes"], list):
            parsed["possible_causes"] = [str(parsed["possible_causes"])]
        if not isinstance(parsed["recommended_actions"], list):
            parsed["recommended_actions"] = [str(parsed["recommended_actions"])]

        # Ensure strings
        parsed["defect_name"] = str(parsed["defect_name"])
        parsed["description"] = str(parsed["description"])
        parsed["location"] = str(parsed["location"])
        parsed["severity"] = str(parsed["severity"]).upper()
        parsed["inspection_decision"] = str(parsed["inspection_decision"]).upper()

        if "quality_summary" not in parsed or not parsed["quality_summary"]:
            parsed["quality_summary"] = (
                f"Inspection concluded with decision: {parsed['inspection_decision']} "
                f"for defect: {parsed['defect_name']}."
            )

        return parsed
