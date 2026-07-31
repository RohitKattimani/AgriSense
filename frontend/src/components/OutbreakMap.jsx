import { useEffect, useState } from "react";
import { getOutbreakMap } from "../api/client";

const COLORS = ["#c0392b", "#2874a6", "#af7ac5", "#117864", "#b9770e", "#7d3c98", "#1e8449"];

export default function OutbreakMap() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getOutbreakMap().then(setData);
  }, []);

  if (!data) return <div className="card"><h2>🗺️ Community Outbreak Map</h2><p>Loading…</p></div>;

  const lats = data.reports.map((r) => r.lat);
  const lons = data.reports.map((r) => r.lon);
  const minLat = Math.min(...lats), maxLat = Math.max(...lats);
  const minLon = Math.min(...lons), maxLon = Math.max(...lons);
  const W = 560, H = 380, PAD = 20;

  const project = (lat, lon) => {
    const x = PAD + ((lon - minLon) / (maxLon - minLon || 1)) * (W - 2 * PAD);
    const y = H - PAD - ((lat - minLat) / (maxLat - minLat || 1)) * (H - 2 * PAD);
    return [x, y];
  };

  const diseaseColor = {};
  let ci = 0;
  data.reports.forEach((r) => {
    if (!(r.disease in diseaseColor)) diseaseColor[r.disease] = COLORS[ci++ % COLORS.length];
  });

  return (
    <div className="card">
      <h2>🗺️ Community Outbreak Map</h2>
      <p className="muted">
        Simulated scan reports from {data.total_reports} farmers in the region. DBSCAN clustering
        flags where a disease looks like it's spreading versus isolated cases.
      </p>

      {data.outbreak_alerts.length > 0 && (
        <div className="outbreak-alerts">
          {data.outbreak_alerts.map((a) => (
            <div key={a.cluster_id} className="alert-chip">
              ⚠️ Possible {a.disease.replace(/___|_/g, " ")} outbreak - {a.report_count} nearby reports
            </div>
          ))}
        </div>
      )}

      <svg viewBox={`0 0 ${W} ${H}`} className="outbreak-svg">
        <rect x="0" y="0" width={W} height={H} fill="#f4f1e8" rx="12" />
        {data.reports.map((r) => {
          const [x, y] = project(r.lat, r.lon);
          return (
            <circle
              key={r.id}
              cx={x}
              cy={y}
              r={r.is_outbreak_cluster ? 5 : 3}
              fill={diseaseColor[r.disease]}
              opacity={r.is_outbreak_cluster ? 0.9 : 0.4}
            >
              <title>{`${r.disease.replace(/___|_/g, " ")} - ${r.farmer}`}</title>
            </circle>
          );
        })}
      </svg>

      <div className="legend">
        {Object.entries(diseaseColor).map(([d, c]) => (
          <span key={d} className="legend-item">
            <span className="legend-dot" style={{ background: c }} />
            {d.replace(/___|_/g, " ")}
          </span>
        ))}
      </div>
    </div>
  );
}
