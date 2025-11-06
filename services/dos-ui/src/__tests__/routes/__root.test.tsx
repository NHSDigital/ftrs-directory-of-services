import { describe } from "node:test";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { render } from "@testing-library/react";
import { act } from "react";
import { expect, it, vi } from "vitest";
import { setupSessionFn } from "@/core/session";
import { Route as RootRoute } from "@/routes/__root";

vi.mock("@/core/session", async (importActual) => {
  const actual = await importActual<typeof import("@/core/session")>();
  return {
    ...actual,
    setupSessionFn: vi.fn().mockResolvedValue({
      sessionID: "test-session-id",
      state: "test-state",
      expires: Date.now() + 3600000,
      tokens: {
        cis2: undefined,
        apim: undefined,
      },
    }),
  };
});

const setUp = async () => {
  const router = createRouter({
    defaultPendingMinMs: 0,
    routeTree: RootRoute,
  });

  const app = render(<RouterProvider router={router} />);

  await act(async () => router.navigate({ to: "/" }));
  return { router, app };
};

describe("Root Route", () => {
  it("should render the root route", async () => {
    const { app } = await setUp();
    expect(app.container).toBeDefined();
    expect(setupSessionFn).toHaveBeenCalled();

    expect(app.container).toMatchSnapshot("Root Route");
  });
});
