import type { Route } from "../api/client";

interface RouteCardProps {
  route: Route;
  index: number;
  selected: boolean;
}

/** Route card — distance/duration only in Phase 1; risk/hazards/facilities land in Phase 2+.
 *  Displays verified values only; never fabricated (MASTER_PROJECT_PROMPT.md §75). */
export function RouteCard({ route, index, selected }: RouteCardProps) {
  const km = (route.distance_meters / 1000).toFixed(1);
  const minutes = Math.round(route.duration_seconds / 60);
  return (
    <article className={`route-card${selected ? " route-card-selected" : ""}`} aria-current={selected || undefined}>
      <h3>Route {index + 1}</h3>
      <p>
        {km} km • {minutes} min
      </p>
      <p className="route-id muted">{route.route_id}</p>
    </article>
  );
}