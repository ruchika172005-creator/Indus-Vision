from typing import Dict, Any, List, Tuple

# Inherent structural risk weighting for known industrial defect types
CATEGORY_RISK_WEIGHTS: Dict[str, float] = {
    # NEU-DET steel defect categories
    "crazing": 0.85,          # Surface micro-cracks propagate under cyclic load
    "inclusion": 0.90,        # Foreign non-metallic particles cause stress concentration
    "patches": 0.70,          # Surface oxidation or scale overlap
    "pitted surface": 0.75,   # Cavities from acid washing or corrosion
    "rolled-in scale": 0.80,  # Mill scale pressed into surface during hot rolling
    "scratches": 0.50,        # Mechanical surface abrasion

    # GC10-DET metallic surface defects
    "welding line": 0.85,
    "crescent gap": 0.90,
    "punching hole": 0.95,
    "waist folding": 0.80,
    "water spot": 0.35,
    "oil spot": 0.30,
    "silk spot": 0.40,

    # MVTec AD generic defects
    "crack": 0.95,
    "hole": 0.95,
    "contamination": 0.60,
    "deformed": 0.85,
    "cut": 0.85,
}

class SeverityEngine:
    """
    Transparent, explainable industrial defect severity and quality decision engine.
    Computes individual defect severity levels (LOW, MEDIUM, HIGH, CRITICAL)
    and overall quality disposition (PASS, FAIL, MANUAL_REVIEW).
    """

    def __init__(
        self,
        critical_area_ratio: float = 0.15,
        high_area_ratio: float = 0.08,
        medium_area_ratio: float = 0.03
    ):
        self.critical_area_ratio = critical_area_ratio
        self.high_area_ratio = high_area_ratio
        self.medium_area_ratio = medium_area_ratio

    def evaluate_defect(
        self,
        defect_name: str,
        bbox: List[float],
        image_width: int,
        image_height: int,
        confidence: float
    ) -> Dict[str, Any]:
        """
        Calculates severity for a single detected bounding box.
        """
        x1, y1, x2, y2 = bbox
        defect_w = max(0.0, x2 - x1)
        defect_h = max(0.0, y2 - y1)
        defect_area = defect_w * defect_h
        image_area = max(1.0, float(image_width * image_height))
        area_ratio = min(1.0, defect_area / image_area)

        # Normalized defect name lookup
        clean_name = defect_name.strip().lower()
        cat_weight = CATEGORY_RISK_WEIGHTS.get(clean_name, 0.60)

        # Transparent formula:
        # 45% based on area ratio normalized against critical threshold
        # 35% based on metallurgical / structural category risk
        # 20% based on detection confidence
        normalized_area = min(1.0, area_ratio / max(0.01, self.critical_area_ratio))
        score = (0.45 * normalized_area + 0.35 * cat_weight + 0.20 * confidence) * 100.0

        if score >= 80.0 or area_ratio >= self.critical_area_ratio:
            severity = "CRITICAL"
            reason = f"High structural risk ({clean_name}) or critical surface area fraction ({area_ratio:.1%})."
        elif score >= 60.0 or area_ratio >= self.high_area_ratio:
            severity = "HIGH"
            reason = f"Substantial defect footprint ({area_ratio:.1%}) with elevated category risk."
        elif score >= 35.0 or area_ratio >= self.medium_area_ratio:
            severity = "MEDIUM"
            reason = f"Moderate surface deviation ({area_ratio:.1%}) requiring monitoring."
        else:
            severity = "LOW"
            reason = f"Minor superficial defect ({area_ratio:.1%}) with low mechanical consequence."

        return {
            "defect_name": defect_name,
            "confidence": round(float(confidence), 3),
            "bbox": [round(float(c), 1) for c in bbox],
            "area_pixels": round(defect_area, 1),
            "area_ratio": round(area_ratio, 4),
            "severity_level": severity,
            "severity_score": round(score, 1),
            "evaluation_reason": reason
        }

    def evaluate_inspection(
        self,
        defects: List[Dict[str, Any]],
        image_width: int,
        image_height: int
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Determines overall inspection decision: PASS, FAIL, or MANUAL_REVIEW,
        along with maximum severity level.
        """
        if not defects:
            return "PASS", "LOW", {
                "decision": "PASS",
                "summary": "No surface defects identified. Product meets quality standards.",
                "action": "Proceed to next manufacturing stage."
            }

        severities = [d.get("severity_level", "LOW") for d in defects]
        critical_count = severities.count("CRITICAL")
        high_count = severities.count("HIGH")
        medium_count = severities.count("MEDIUM")
        low_count = severities.count("LOW")
        total = len(defects)

        # Max severity ranking
        if "CRITICAL" in severities:
            max_sev = "CRITICAL"
        elif "HIGH" in severities:
            max_sev = "HIGH"
        elif "MEDIUM" in severities:
            max_sev = "MEDIUM"
        else:
            max_sev = "LOW"

        # Transparent Decision Logic
        if critical_count > 0 or high_count >= 2 or total >= 5:
            decision = "FAIL"
            summary = (
                f"Inspection rejected with {total} defect(s) "
                f"({critical_count} critical, {high_count} high). Exceeds tolerance."
            )
            action = "Quarantine part immediately. Flag lot for metallurgical audit."
        elif high_count == 1 or medium_count >= 2:
            decision = "MANUAL_REVIEW"
            summary = (
                f"Quality advisory: {total} defect(s) detected. "
                "Severity requires supervisor inspection before signoff."
            )
            action = "Reroute to secondary manual inspection station."
        elif medium_count == 1 and low_count <= 1:
            decision = "MANUAL_REVIEW"
            summary = "Isolated medium defect detected. Verify tolerance specification."
            action = "Verify dimensional tolerance against CAD/part drawing."
        else:
            # Low severity isolated defects
            decision = "PASS"
            summary = f"Passed with advisory: {low_count} low-severity superficial anomaly logged."
            action = "Approved for finishing / coating stage."

        explanation_metadata = {
            "decision": decision,
            "max_severity": max_sev,
            "defect_counts": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
                "total": total
            },
            "summary": summary,
            "recommended_disposition": action
        }

        return decision, max_sev, explanation_metadata

severity_engine = SeverityEngine()
