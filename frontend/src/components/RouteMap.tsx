import { MapContainer, TileLayer, Polyline } from "react-leaflet";
import type { Route } from "../api/client";

interface RouteMapProps {
  routes: Route[];
  selectedRouteId: string | null;
}

/** Map shows all candidate routes; selection is emphasized, others subdued.
 *  Never relies on color alone (08_UI_SPEC.md §10). */
export function RouteMap({ routes, selectedRouteId }: RouteMapProps) {
  const positions = (route: Route): [number, number][] => {
    if (!route.geometry || route.geometry.type !== "LineString") return [];
    return route.geometry.coordinates.map(([lon, lat]) => [lat, lon] as [number, number]);
  };

  return (
    <MapContainer center={[12.97, 74.88]} zoom={12} className="map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {routes.map((route) => {
        const isSelected = route.route_id === selectedRouteId;
        const pts = positions(route);
        if (pts.length === 0) {
          return (
            <p key={route.route_id} className="error">
              Route geometry unavailable for {route.route_id}.
            </p>
          );
        }
        return (
          <Polyline
            key={route.route_id}
            positions={pts}
            pathOptions={{
              color: isSelected ? "#b91c1c" : "#1d4ed8",
              weight: isSelected ? 8 : 5,
              opacity: isSelected ? 1 : 0.45,
            }}
          />
        );
      })}
    </MapContainer>
  );
}