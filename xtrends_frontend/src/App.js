import React, { useEffect, useState } from "react";
import "./App.css";

const API_BASE = ("http://127.0.0.1:8000").replace(/\/$/, "") + "/api";

function formatTime(iso) {
  try {
    if (!iso) return "";
    return new Date(iso).toLocaleString();
  } catch {
    return iso || "";
  }
}

function extractTrendsFromPayload(payload) {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload.slice(0, 5);
  if (Array.isArray(payload.trends)) return payload.trends.slice(0, 5);
  const keys = ["trend1","trend2","trend3","trend4","trend5"];
  const arr = [];
  for (const k of keys) {
    if (k in payload && payload[k]) arr.push(payload[k]);
  }
  if (arr.length) return arr.slice(0,5);
  if (Array.isArray(payload.results)) return payload.results.slice(0,5);
  if (Array.isArray(payload.data)) return payload.data.slice(0,5);
  return [];
}

export default function App() {
  const [trends, setTrends] = useState([]);
  const [meta, setMeta] = useState({ unique_id: "", ip_address: "", scraped_at: "" });
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState("");

  async function fetchLatest() {
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/latest-trends/`);
      if (res.status === 404) {
        setTrends([]);
        setMeta({ unique_id: "", ip_address: "", scraped_at: "" });
        setLoading(false);
        return;
      }
      if (!res.ok) throw new Error("Failed to fetch latest");
      const data = await res.json();
      const list = extractTrendsFromPayload(data);
      setTrends(list);
      const uid = data.unique_id || data.id || data.run_id || "";
      const ip = data.ip_address || data.ip || data.ipAddress || "";
      const ts = data.scraped_at || data.run_timestamp || data.scrapedAt || "";
      setMeta({ unique_id: uid, ip_address: ip, scraped_at: ts });
    } catch (err) {
      setError(err.message || "Error fetching latest");
    } finally {
      setLoading(false);
    }
  }

  async function triggerScrape() {
    setError("");
    setScraping(true);
    try {
      const res = await fetch(`${API_BASE}/scrape-save-trend/`, { method: "POST" });
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(text || "Scrape failed");
      }
      const data = await res.json();
      const list = extractTrendsFromPayload(data);
      setTrends(list);
      const uid = data.unique_id || data.id || data.run_id || "";
      const ip = data.ip_address || data.ip || data.ipAddress || "";
      const ts = data.scraped_at || data.run_timestamp || data.scrapedAt || "";
      setMeta({ unique_id: uid, ip_address: ip, scraped_at: ts });
    } catch (err) {
      setError(err.message || "Error triggering scrape");
    } finally {
      setScraping(false);
    }
  }

  useEffect(() => {
    fetchLatest();
  }, []);

  return (
    <div className="app-shell">
      <div className="card">
        <div className="header">
          <div className="brand">
            <div className="logo">XT</div>
            <div className="title">
              <h1>XTrends</h1>
              <p className="subtitle">Top 5 — What’s happening on X</p>
            </div>
          </div>
          <div className="actions">
            <button className="btn btn-outline" onClick={fetchLatest} disabled={loading || scraping}>
              {loading ? "Loading…" : "Fetch Latest"}
            </button>
            <button className="btn btn-primary" onClick={triggerScrape} disabled={scraping || loading}>
              {scraping ? <div className="spinner" /> : "Scrape Now"}
            </button>
          </div>
        </div>

        {error && <div style={{ color: "#ff9fa8", margin: "8px 0" }}>{error}</div>}

        <div className="content">
          <div className="meta">
            <div className="meta-item">
              <div className="meta-label">Run ID</div>
              <div className="meta-value">{meta.unique_id || "—"}</div>
            </div>
            <div className="meta-item">
              <div className="meta-label">IP</div>
              <div className="meta-value">{meta.ip_address || "DIRECT"}</div>
            </div>
            <div className="meta-item">
              <div className="meta-label">Scraped</div>
              <div className="meta-value">{formatTime(meta.scraped_at) || "—"}</div>
            </div>
          </div>

          <div className="section-title">Top 5 — What’s happening</div>
          <div className="trends">
            {trends.length === 0 && <div className="empty">No trends yet. Click “Scrape Now”.</div>}
            {trends.map((t, i) => (
              <div className="trend" key={i}>
                <div className="trend-index">{i + 1}</div>
                <div>
                  <div className="trend-text">{t}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="footer">Tip: Scrape may take several seconds while Selenium runs. Backend stores each run.</div>
        </div>
      </div>
    </div>
  );
}
