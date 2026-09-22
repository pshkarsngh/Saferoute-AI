/** SafeRoute AI — frontend API client (typed, mirrors 07_API_CONTRACT.md schemas). */
export interface Location {
  latitude: number;
  longitude: number;
  name?: string | null;
}

export interface Route {
  route_id: string;
  request_id: string;
  sequence: number;
  distance_meters: number;
  duration_seconds: number;
  geometry: { type: "LineString"; coordinates: [number, number][] } | null;
  status: string;
}

export interface RouteRequestResponse {
  request_id: string;
  status: string;
  routes: Route[];
}

export interface ApiLocation {
  latitude: number;
  longitude: number;
}

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api/v1";

export class ApiError extends Error {
  code: string;
  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (res.ok) {
    return (await res.json()) as T;
  }
  let body: { error?: { code?: string; message?: string } } = {};
  try {
    body = (await res.json()) as typeof body;
  } catch {
    body = {};
  }
  throw new ApiError(body.error?.code ?? "INTERNAL_ERROR", body.error?.message ?? "Request failed");
}

/** POST /api/v1/route-requests — generate up to 4 candidate routes. */
export async function createRouteRequest(
  source: ApiLocation,
  destination: ApiLocation,
): Promise<RouteRequestResponse> {
  return handle<RouteRequestResponse>(
    await fetch(`${API_BASE}/route-requests`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source, destination }),
    }),
  );
}