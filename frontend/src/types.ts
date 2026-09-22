/** SafeRoute AI — app state types (snake_case mirrors backend; 07_API_CONTRACT.md). */
export type AnalysisStatus =
  | "idle"
  | "loading"
  | "routes_loaded"
  | "analysis_pending"
  | "analyzing"
  | "completed"
  | "partial"
  | "failed";

export interface RouteProfile {
  route_id: string;
  risk_score: number | null;
  hazard_count: number | null;
  hazard_summary: Record<string, number>;
  images_analyzed: number;
  segments_analyzed: number;
  facilities: Record<string, { count: number; nearest_distance_km: number | null }>;
  status: string;
}