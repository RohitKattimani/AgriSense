"""
Rough yield-loss projection.

Combines per-plant disease severity (derived from model confidence + how
destructive the identified condition typically is) with the estimated
percentage of the field affected, to give the farmer a ballpark
"you might lose about X% of this field's yield" figure. This is
intentionally simple/transparent rather than a black box, since farmers
need to trust and sanity-check the number.
"""
from __future__ import annotations
from typing import List, Dict

# Rough "how damaging is this if untreated" weight per condition keyword,
# used only to turn a classification into a severity estimate.
SEVERITY_WEIGHTS = {
    "late_blight": 0.9, "black_rot": 0.75, "esca": 0.85, "bacterial_spot": 0.6,
    "early_blight": 0.55, "leaf_mold": 0.4, "septoria": 0.5, "common_rust": 0.35,
    "northern_leaf_blight": 0.6, "apple_scab": 0.45, "healthy": 0.0,
}


def _severity_weight(label: str) -> float:
    label_l = label.lower()
    for key, w in SEVERITY_WEIGHTS.items():
        if key in label_l:
            return w
    return 0.5  # unknown disease -> assume moderate severity


def estimate_field_yield_loss(scan_results: List[Dict], affected_area_pct: float) -> Dict:
    """
    scan_results: list of per-photo classification dicts (from vision_model.classify_image)
    affected_area_pct: farmer's estimate (or default) of what % of the field
                        shows similar symptoms to the diseased photos, 0-100
    """
    if not scan_results:
        raise ValueError("scan_results cannot be empty")

    diseased = [r for r in scan_results if not r["is_healthy"]]
    healthy_pct = round(100 * (len(scan_results) - len(diseased)) / len(scan_results), 1)

    if not diseased:
        return {
            "field_health_score_pct": 100.0,
            "estimated_yield_loss_pct": 0.0,
            "severity_index": 0.0,
            "affected_area_pct": 0.0,
            "summary": "No disease symptoms detected across scanned plants. No yield loss projected.",
        }

    # Average severity across diseased samples, weighted by model confidence
    weighted_sum = sum(_severity_weight(r["top_label"]) * r["top_confidence"] for r in diseased)
    severity_index = round(weighted_sum / len(diseased), 3)  # 0..1

    area_fraction = max(0.0, min(100.0, affected_area_pct)) / 100.0
    # Simple, explainable model: yield loss ~= severity * affected area,
    # dampened slightly since not all affected tissue = total crop loss.
    estimated_loss_pct = round(severity_index * area_fraction * 100 * 0.85, 1)

    field_health_score = round(100 - (len(diseased) / len(scan_results)) * 100, 1)

    return {
        "field_health_score_pct": field_health_score,
        "healthy_sample_pct": healthy_pct,
        "estimated_yield_loss_pct": estimated_loss_pct,
        "severity_index": severity_index,
        "affected_area_pct": affected_area_pct,
        "summary": (
            f"{len(diseased)}/{len(scan_results)} scanned plants show symptoms "
            f"(avg severity {severity_index:.0%}). At an estimated {affected_area_pct:.0f}% "
            f"of the field affected, potential yield loss is roughly {estimated_loss_pct}% "
            f"if untreated."
        ),
    }
