import { createRouter, RouterProvider } from "@tanstack/react-router";
import { act, render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppError } from "@/core/errors";
import { setupSessionFn } from "@/core/session";
import { Route as RootRoute } from "@/routes/__root";

vi.mock("@/core/session", () => {
  return {
    setupSessionFn: vi
      .fn()
      .mockRejectedValue(new Error("Session setup failed")),
  };
});

describe("ErrorComponent", () => {
  const setUp = async () => {
    const router = createRouter({
      defaultPendingMinMs: 0,
      routeTree: RootRoute,
    });

    const app = render(<RouterProvider router={router} />);

    await act(async () => router.navigate({ to: "/" }));
    return { router, app };
  };

  it("should render the error component", async () => {
    const { app } = await setUp();

    expect(app.getByText("Session setup failed")).toBeDefined();
    expect(app.getByText("An error occurred")).toBeDefined();
    expect(
      app.getByText("Sorry, there was a problem processing your request."),
    ).toBeDefined();

    expect(app.container).toMatchSnapshot("ErrorComponent");
  });

  it("should display session and request IDs when provided", async () => {
    // @ts-expect-error Mock implementation
    setupSessionFn.mockRejectedValue(
      new AppError(
        "Test error for session and request IDs",
        "session-123",
        "request-456",
      ),
    );

    const { app } = await setUp();

    expect(
      app.getByText("Test error for session and request IDs"),
    ).toBeDefined();
    expect(app.getByText("session-123")).toBeDefined();
    expect(app.getByText("request-456")).toBeDefined();

    expect(app.container).toMatchSnapshot(
      "ErrorComponent with Session and Request IDs",
    );
  });
});
