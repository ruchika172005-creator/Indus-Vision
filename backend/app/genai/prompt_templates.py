import json
from typing import List, Dict, Any

SYSTEM_INSTRUCTION = """
You are a Senior Metallurgical Quality Assurance Specialist and Computer Vision Auditor in an automated industrial manufacturing plant.
Your role is to interpret optical quality inspection results, inspect the physical image of the manufactured part, and provide rigorous, actionable quality explanations.

CRITICAL OPERATIONAL RULES:
1. Ground your observations strictly in the visual evidence and the computer vision detection output provided.
2. DO NOT hallucinate or alter detection coordinates, bounding boxes, or confidence scores.
3. Distinguish clearly between OBSERVED PHYSICAL FACTS (what is visible on the surface) and HYPOTHESES/POSSIBLE CAUSES (manufacturing root causes that cannot be proven by single-angle imagery alone).
4. Provide structured, ISO 9001-compliant quality inspection summaries and practical corrective actions for shop-floor technicians.
5. Return ONLY a valid JSON object matching the exact schema specified. Do not include markdown code block markers or conversational preamble.
"""

def build_defect_analysis_prompt(
    product_category: str,
    defects: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> str:
    """
    Constructs the prompt instructing the VLM to analyze the image alongside detection coordinates.
    """
    if not defects:
        return f"""
Analyze this industrial product image for quality verification.
Product Category: {product_category}
Detection System Output: 0 defects detected. The surface appears clean and uniform.

Provide your evaluation as a valid JSON object with this exact structure:
{{
  "defect_name": "None (Defect-Free)",
  "description": "Surface exhibits uniform finish without detectable structural or cosmetic anomalies.",
  "location": "Full product surface",
  "severity": "LOW",
  "possible_causes": [
    "Nominal manufacturing process parameters maintained",
    "Proper lubrication and tooling alignment"
  ],
  "recommended_actions": [
    "Release part to packaging / assembly line",
    "Continue standard in-line monitoring"
  ],
  "inspection_decision": "PASS",
  "quality_summary": "Component meets visual surface quality compliance criteria."
}}
"""

    primary_defect = defects[0]
    defect_list_str = json.dumps(defects, indent=2)

    return f"""
Analyze this industrial product image. The automated YOLOv8 computer vision system detected {len(defects)} defect(s):

Product Category: {product_category}
Primary Detected Defect: {primary_defect.get('defect_name')} (Confidence: {primary_defect.get('confidence')})
All Detections:
{defect_list_str}

Inspection Rule Disposition: {metadata.get('decision', 'MANUAL_REVIEW')}
Calculated Severity: {metadata.get('max_severity', 'MEDIUM')}

Review the visual features in the image corresponding to these coordinates.
Produce a strict JSON response with this exact schema:
{{
  "defect_name": "{primary_defect.get('defect_name')}",
  "description": "Precise visual description of the observed surface deviation, color variance, texture, or geometric distortion.",
  "location": "Quadrant or physical location on the component (e.g. Center-right region, Longitudinal edge)",
  "severity": "{metadata.get('max_severity', 'MEDIUM')}",
  "possible_causes": [
    "Most likely mechanical or thermal process cause (hypothesis 1)",
    "Secondary tooling, material handling, or environmental factor (hypothesis 2)"
  ],
  "recommended_actions": [
    "Immediate containment or corrective action for machine operator",
    "Preventative maintenance or calibration recommendation"
  ],
  "inspection_decision": "{metadata.get('decision', 'MANUAL_REVIEW')}",
  "quality_summary": "Comprehensive 1-2 sentence engineering disposition summary."
}}
"""
