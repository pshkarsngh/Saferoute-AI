import { describe, it, expect } from "vitest";
import { RouteCard } from "./RouteCard";
import type { Route } from "../api/client";
import { render, screen } from "@testing-library/react";

function makeRoute(overrides: Partial<Route> = {}): Route {
  return {
    route_id: "route_1",
    request_id: "req_1",
    sequence: 0,
    distance_meters: 8200,
    duration_seconds: 1140,
    geometry: null,
    status: "available",
    ...overrides,
  };
}

describe("RouteCard", () => {
  it("shows distance and duration from verified values", () => {
    render(<RouteCard route={makeRoute()} index={0} selected={false} />);
    expect(screen.getByText("8.2 km • 19 min")).toBeTruthy();
    expect(screen.getByText("Route 1")).toBeTruthy();
  });

  it("marks the selected route", () => {
    render(<RouteCard route={makeRoute()} index={1} selected />);
    expect(screen.getByRole("article").getAttribute("aria-current")).toBe("true");
  });
});