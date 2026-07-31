"""
Community outbreak map.

Simulates crop-disease scan reports from many farmers across a region
(lat/lon jittered around a center point) and runs DBSCAN clustering on
the reports of the *same* disease to flag geographic clusters, i.e.
"this disease seems to be spreading in this area" versus isolated cases.

In production, `reports` would come from a database of real farmer scans
(each diagnosis call in diagnose.py would also log lat/lon + label here).
"""
from __future__ import annotations
import random
from datetime import date, timedelta
from typing import Dict, List

import numpy as np
from sklearn.cluster import DBSCAN

from app.services.vision_model import KNOWN_CLASSES

REGION_CENTER = (12.9716, 77.5946)  # Bengaluru, as a default demo region


def _simulate_reports(n: int = 60, center=REGION_CENTER, seed: int = 42) -> List[Dict]:
    rng = random.Random(seed)
    diseases = [c for c in KNOWN_CLASSES if "healthy" not in c]
    # Bias the simulation so 2-3 diseases form real geographic clusters,
    # and the rest are scattered noise - makes the demo map meaningful.
    hotspot_diseases = rng.sample(diseases, 2)
    hotspots = [(center[0] + rng.uniform(-0.05, 0.05), center[1] + rng.uniform(-0.05, 0.05)) for _ in hotspot_diseases]

    reports = []
    for i in range(n):
        if rng.random() < 0.55:
            idx = rng.randrange(len(hotspot_diseases))
            disease = hotspot_diseases[idx]
            base_lat, base_lon = hotspots[idx]
            lat = base_lat + rng.gauss(0, 0.008)
            lon = base_lon + rng.gauss(0, 0.008)
        else:
            disease = rng.choice(diseases)
            lat = center[0] + rng.uniform(-0.15, 0.15)
            lon = center[1] + rng.uniform(-0.15, 0.15)

        reports.append({
            "id": i + 1,
            "farmer": f"Farmer #{rng.randint(1000, 9999)}",
            "disease": disease,
            "crop": disease.split("___")[0].strip("_"),
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "date": (date.today() - timedelta(days=rng.randint(0, 14))).isoformat(),
        })
    return reports


def get_outbreak_map(eps_km: float = 2.0, min_samples: int = 4) -> Dict:
    reports = _simulate_reports()

    # Cluster separately within each disease type so we only flag spread
    # of the *same* disease, not just "farmers happen to be near each other".
    clustered_reports = []
    cluster_summaries = []
    cluster_id_counter = 0

    by_disease: Dict[str, List[Dict]] = {}
    for r in reports:
        by_disease.setdefault(r["disease"], []).append(r)

    eps_deg = eps_km / 111.0  # rough km -> degrees conversion

    for disease, group in by_disease.items():
        coords = np.array([[g["lat"], g["lon"]] for g in group])
        if len(group) < min_samples:
            labels = [-1] * len(group)
        else:
            labels = DBSCAN(eps=eps_deg, min_samples=min_samples).fit_predict(coords)

        local_clusters: Dict[int, List[Dict]] = {}
        for g, lbl in zip(group, labels):
            g = dict(g)
            g["is_outbreak_cluster"] = bool(lbl != -1)
            g["local_cluster_label"] = int(lbl)
            clustered_reports.append(g)
            if lbl != -1:
                local_clusters.setdefault(lbl, []).append(g)

        for lbl, members in local_clusters.items():
            cluster_id_counter += 1
            lats = [m["lat"] for m in members]
            lons = [m["lon"] for m in members]
            cluster_summaries.append({
                "cluster_id": cluster_id_counter,
                "disease": disease,
                "crop": members[0]["crop"],
                "report_count": len(members),
                "center_lat": round(sum(lats) / len(lats), 5),
                "center_lon": round(sum(lons) / len(lons), 5),
                "alert": len(members) >= min_samples,
            })

    cluster_summaries.sort(key=lambda c: -c["report_count"])

    return {
        "region_center": {"lat": REGION_CENTER[0], "lon": REGION_CENTER[1]},
        "total_reports": len(reports),
        "reports": clustered_reports,
        "clusters": cluster_summaries,
        "outbreak_alerts": [c for c in cluster_summaries if c["alert"]],
    }
