import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { getCrops, getTrend } from "../api/client";

export default function MarketTrend() {
  const [crops, setCrops] = useState([]);
  const [crop, setCrop] = useState("tomato");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCrops().then(setCrops).catch(() => setCrops(["tomato", "potato", "onion", "wheat", "grapes"]));
  }, []);

  useEffect(() => {
    setLoading(true);
    getTrend(crop)
      .then(setData)
      .finally(() => setLoading(false));
  }, [crop]);

  const chartData = data
    ? [
        ...data.history.slice(-30).map((h) => ({ date: h.date.slice(5), actual: h.price })),
        ...data.forecast.map((f) => ({ date: f.date.slice(5), forecast: f.predicted_price_poly })),
      ]
    : [];

  return (
    <div className="card">
      <h2>📈 Market Price Trends</h2>
      <p className="muted">Regression-based price trend and 7-day forecast (simulated market data).</p>

      <div className="row">
        <select className="crop-select" value={crop} onChange={(e) => setCrop(e.target.value)}>
          {crops.map((c) => (
            <option key={c} value={c}>
              {c[0].toUpperCase() + c.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {loading && <p>Loading trend…</p>}

      {data && !loading && (
        <>
          <div className="stat-row">
            <div className="stat">
              <span className="stat-value">₹{data.current_price}</span>
              <span className="stat-label">Current price / {data.unit}</span>
            </div>
            <div className={`stat trend-${data.trend_direction}`}>
              <span className="stat-value">{data.trend_direction.toUpperCase()}</span>
              <span className="stat-label">7-day trend</span>
            </div>
            <div className="stat">
              <span className="stat-value">
                {data.projected_pct_change_7d > 0 ? "+" : ""}
                {data.projected_pct_change_7d}%
              </span>
              <span className="stat-label">Projected change</span>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e0d5" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="actual" stroke="#2f6b3a" strokeWidth={2} dot={false} name="Actual price" />
              <Line type="monotone" dataKey="forecast" stroke="#d98c2b" strokeWidth={2} strokeDasharray="5 4" dot={false} name="Forecast" />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}
