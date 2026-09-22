import { useCallback, useState } from "react";
import { createRouteRequest, ApiError, type Route } from "./api/client";
import { SearchForm } from "./components/SearchForm";
import { RouteMap } from "./components/RouteMap";
import { RouteCard } from "./components/RouteCard";
import type { AnalysisStatus } from "./types";

export default function App() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [status, setStatus] = useState<AnalysisStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);

  const onSearch = useCallback(async (source: { latitude: number; longitude: number }, destination: { latitude: number; longitude: number }) => {
    setStatus("loading");
    setError(null);
    setSelectedRouteId(null);
    try {
      const res = await createRouteRequest(source, destination);
      setRoutes(res.routes);
      setStatus(res.routes.length > 0 ? "routes_loaded" : "failed");
      if (res.routes.length === 0) {
        setError("No routes were found for the selected locations.");
      }
    } catch (err) {
      setRoutes([]);
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unable to generate routes right now.");
      }
      setStatus("failed");
    }
  }, []);

  return (
    <main className="app">
      <header className="app-header">
        <h1>SafeRoute AI</h1>
        <p>Intelligent road-safety navigation — compare routes by risk, hazards, and nearby facilities.</p>
      </header>

      <SearchForm onSearch={onSearch} disabled={status === "loading"} />

      {error && <p className="error" role="alert">{error}</p>}

      <div className="app-body">
        <section className="map-panel" aria-label="Route map">
          <RouteMap routes={routes} selectedRouteId={selectedRouteId} />
        </section>

        <section className="routes-panel" aria-label="Candidate routes">
          {status === "loading" && <p className="muted">Finding routes…</p>}
          {routes.length > 0 && (
            <ul className="route-list">
              {routes.map((route, i) => (
                <li key={route.route_id}>
                  <button type="button" className="route-card-button" onClick={() => setSelectedRouteId(route.route_id)}>
                    <RouteCard route={route} index={i} selected={route.route_id === selectedRouteId} />
                  </button>
                </li>
              ))}
            </ul>
          )}
          {routes.length === 0 && status !== "loading" && !error && (
            <p className="muted">Enter a source and destination to generate routes.</p>
          )}
        </section>
      </div>

      <footer className="app-footer">
        <p>
          SafeRoute AI provides route information based on available data. Results may be incomplete or
          outdated. Users remain responsible for exercising appropriate judgment.
        </p>
      </footer>
    </main>
  );
}