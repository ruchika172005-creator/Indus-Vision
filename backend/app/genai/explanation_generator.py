from typing import List, Dict, Any, Optional
from app.genai.gemini_provider import GeminiVisionProvider
from app.genai.vision_analyzer import vision_analyzer
from app.core.logging import logger

# Metallurgical domain knowledge base for steel and metallic defect taxonomy
DEFECT_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "crazing": {
        "description": "Network of fine, interconnected micro-fissures resembling spiderweb cracking across the rolled steel surface.",
        "possible_causes": [
            "Severe thermal fatigue caused by improper work roll cooling water spray patterns",
            "Excessive tensile strain during high-speed cold reduction passes",
            "Residual chemical segregation (copper or tin enrichment at grain boundaries)"
        ],
        "recommended_actions": [
            "Inspect and descale roll cooling nozzles on Stand 3 and 4",
            "Perform dye-penetrant or eddy-current testing to measure crack depth",
            "Slow rolling pass speed by 12% and verify roll temperature differential"
        ]
    },
    "inclusion": {
        "description": "Embedded non-metallic foreign particles (oxides, sulfides, or refractory fragments) entrapped in the steel matrix.",
        "possible_causes": [
            "Ladle shroud or tundish refractory erosion during continuous casting",
            "Incomplete deoxidation slag flotation in secondary steelmaking",
            "Tundish nozzle clogging and sudden slag entrapment"
        ],
        "recommended_actions": [
            "Perform ultrasonic thickness testing for subsurface inclusion depth",
            "Verify tundish argon bubbling flow rate and refractory wear log",
            "Reject component if inclusion intersects critical load-bearing cross-section"
        ]
    },
    "patches": {
        "description": "Irregular dark, scaly surface patches caused by localized oxidation and unremoved high-temperature scale.",
        "possible_causes": [
            "Descaling header water pressure drop below standard 180 bar specification",
            "Uneven reheating furnace atmosphere with localized excess oxygen ingress",
            "Reoxidation between roughing and finishing rolling stands"
        ],
        "recommended_actions": [
            "Calibrate high-pressure hydraulic descaling pump pressure transducers",
            "Adjust air-to-fuel ratio in reheat furnace Zone 2 to minimize oxidizing atmosphere",
            "Mechanical flap wheel grinding if patch thickness is within cosmetic tolerance"
        ]
    },
    "pitted surface": {
        "description": "Localized microscopic crater-like depressions and surface porosity distributed across the metal face.",
        "possible_causes": [
            "Over-pickling in hydrochloric/sulfuric acid bath resulting in intergranular acid attack",
            "Pitted roll surface transfer from damaged or worn work rolls",
            "Atmospheric moisture condensation in post-annealing storage bays"
        ],
        "recommended_actions": [
            "Check hydrochloric acid bath concentration and inhibitor dosing schedule",
            "Replace finishing roll pair during the upcoming scheduled maintenance shift",
            "Ensure climate-controlled dehumidification in coil staging warehouse"
        ]
    },
    "rolled-in scale": {
        "description": "Iron oxide mill scale embedded flush or depressed into the steel substrate under high rolling pressure.",
        "possible_causes": [
            "Delayed primary descaling before entry into the roughing mill",
            "Cracked or clogged descaler spray nozzles failing to dislodge primary scale",
            "Excessive slab soak time in reheat furnace creating heavy tertiary scale"
        ],
        "recommended_actions": [
            "Perform blast cleaning or chemical acid washing test on sample coupon",
            "Check descaler manifold pressure and clean spray header orifices",
            "Review reheating furnace furnace residence time for current heat"
        ]
    },
    "scratches": {
        "description": "Continuous or interrupted linear surface abrasion grooves aligned parallel to the processing direction.",
        "possible_causes": [
            "Mechanical rubbing against worn guide plates, table rollers, or transfer skids",
            "Metal slivers or foreign debris lodged in pinch roller assembly",
            "Improper coil payoff tension causing slippage during uncoiling"
        ],
        "recommended_actions": [
            "Inspect conveyor rollers and side guides for burrs, debris, or seized bearings",
            "Polish contact surfaces with 400-grit dressing stone",
            "Verify line strip tension settings on bridle rolls"
        ]
    },
    "welding line": {
        "description": "Transverse or longitudinal seam irregularity, lack of fusion, or heat-affected zone discoloration.",
        "possible_causes": [
            "Inconsistent laser/arc welding power feed or unstable travel velocity",
            "Shielding gas turbulence causing localized surface oxidation",
            "Improper joint gap alignment prior to tack welding"
        ],
        "recommended_actions": [
            "Perform radiographic or phased array ultrasonic testing along weld seam",
            "Recalibrate automated torch height control and shielding gas flow rate",
            "Quarantine weld joint segment for cross-section metallurgical microscopy"
        ]
    },
    "punching hole": {
        "description": "Perforation or edge rupture deviation resulting from mechanical shearing or tooling puncture.",
        "possible_causes": [
            "Misaligned die punch tooling or worn cutting clearance",
            "Sheet metal thickness variance exceeding tooling tolerance specification"
        ],
        "recommended_actions": [
            "Stop stamping line to inspect punch die sharpness and clearance",
            "Measure material yield strength and thickness against supplier mill certificate"
        ]
    },
    "crescent gap": {
        "description": "Curved edge notch or tear occurring along the strip margin from mechanical shearing tear.",
        "possible_causes": [
            "Side trimmer blade dullness or improper knife horizontal clearance",
            "High edge wave tension leading to strip edge tearing under rolling load"
        ],
        "recommended_actions": [
            "Sharpen or rotate side trimmer rotary knives",
            "Trim outer 25mm margin before coiling if width specification permits"
        ]
    }
}

class ExplanationGenerator:
    """
    Orchestrates Multimodal Vision-Language explanation with
    intelligent fallback to metallurgical engineering knowledge base.
    """

    def __init__(self, gemini_provider: Optional[GeminiVisionProvider] = None):
        self.gemini_provider = gemini_provider or GeminiVisionProvider()

    def update_api_key(self, api_key: str):
        self.gemini_provider.set_api_key(api_key)

    async def generate(
        self,
        image_path: str,
        defects: List[Dict[str, Any]],
        product_category: str,
        detection_metadata: Dict[str, Any],
        image_width: int = 640,
        image_height: int = 640
    ) -> Dict[str, Any]:
        """
        Generates explanation using Google Gemini if available,
        otherwise generates rule-based industrial expert explanation.
        """
        # Try Gemini VLM first if configured
        if self.gemini_provider.is_configured():
            try:
                logger.info("Executing Multimodal Gemini Vision-Language Defect Explanation...")
                return await self.gemini_provider.generate_explanation(
                    image_path=image_path,
                    defects=defects,
                    product_category=product_category,
                    detection_metadata=detection_metadata
                )
            except Exception as e:
                logger.warning(f"Gemini VLM call failed ({e}). Activating Rule-Based Metallurgical Engine.")

        # Rule-based fallback
        return self._generate_rule_based(
            defects=defects,
            product_category=product_category,
            detection_metadata=detection_metadata,
            img_w=image_width,
            img_h=image_height
        )

    def _generate_rule_based(
        self,
        defects: List[Dict[str, Any]],
        product_category: str,
        detection_metadata: Dict[str, Any],
        img_w: int,
        img_h: int
    ) -> Dict[str, Any]:
        """
        Generates transparent, expert-level metallurgical explanation
        without relying on external cloud APIs.
        """
        decision = detection_metadata.get("decision", "PASS")
        max_sev = detection_metadata.get("max_severity", "LOW")

        if not defects:
            return {
                "defect_name": "Defect-Free Surface",
                "description": f"The inspected {product_category.lower()} surface presents a uniform, homogenous appearance with no detectable cracks, inclusions, pitting, or deformation.",
                "location": "Whole surface area",
                "severity": "LOW",
                "possible_causes": [
                    "Rolling mill reduction schedules and lubrication maintained within optimal bounds",
                    "Continuous casting cooling and deoxidation parameters fully compliant"
                ],
                "recommended_actions": [
                    "Authorize component for immediate transfer to next production stage",
                    "Retain inspection record in quality database for traceability audit"
                ],
                "inspection_decision": "PASS",
                "quality_summary": f"Product passed automated visual QA criteria with zero defects detected.",
                "provider_used": "Rule-Based Industrial Expert Engine"
            }

        primary_defect = defects[0]
        raw_name = primary_defect.get("defect_name", "Surface Anomaly")
        clean_key = raw_name.strip().lower()

        # Spatial location
        bbox = primary_defect.get("bbox", [0, 0, img_w, img_h])
        quadrant = vision_analyzer.determine_quadrant(bbox, img_w, img_h)

        kb_entry = DEFECT_KNOWLEDGE_BASE.get(clean_key, {
            "description": f"Detected surface anomaly identified as {raw_name} with optical contrast deviation.",
            "possible_causes": [
                "Transient mechanical contact or tooling misalignment",
                "Localized metallurgical or surface temperature inconsistency"
            ],
            "recommended_actions": [
                "Inspect mechanical contact points along the processing line",
                "Perform optical profilometry verification if part requires high surface finish"
            ]
        })

        return {
            "defect_name": raw_name,
            "description": kb_entry["description"],
            "location": quadrant,
            "severity": max_sev,
            "possible_causes": kb_entry["possible_causes"],
            "recommended_actions": kb_entry["recommended_actions"],
            "inspection_decision": decision,
            "quality_summary": (
                f"Automated quality inspection detected {len(defects)} instance(s) of '{raw_name}' in the {quadrant.lower()}. "
                f"Evaluated severity is {max_sev}; assigned disposition is {decision}."
            ),
            "provider_used": "Rule-Based Industrial Expert Engine"
        }

explanation_generator = ExplanationGenerator()
