// import { before, beforeEach, describe } from "node:test";
// import { createRouter, RouterProvider } from "@tanstack/react-router";
// import { render } from "@testing-library/react";
// import { act } from "react";
// import { expect, it } from "vitest";

import { createRouter, RouterProvider } from "@tanstack/react-router";
import { act, render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ClientSessionContext } from "@/core/context";
import { setupSessionFn } from "@/core/session";
import { Route as Index } from "@/routes/index";
import { getAuthorisationUrlFn } from "@/utils/cis2Configuration-service";

vi.mock("@/core/session", () => {
  return {
    setupSessionFn: vi.fn().mockResolvedValue({
      sessionID: "test-session-id",
      expiresAt: 1762257930743,
      state: "test-state",
    }),
  };
});

vi.mock("@/utils/cis2Configuration-service", () => {
  return {
    getAuthorisationUrlFn: vi
      .fn()
      .mockResolvedValue("http://example.com/authorize?state=test-state"),
  };
});

const ContextWrapper = ({ children }: { children: React.ReactNode }) => {
  const mockSession = {
    sessionID: "test-session-id",
    expiresAt: 1762257930743,
    state: "test-state",
  };
  return (
    <ClientSessionContext.Provider value={mockSession}>
      {children}
    </ClientSessionContext.Provider>
  );
};

describe("Index Route", () => {
  const setUp = async () => {
    const router = createRouter({
      defaultPendingMinMs: 0,
      routeTree: Index,
    });

    process.env.ENVIRONMENT = "local";
    const app = render(<RouterProvider router={router} />, {
      wrapper: ContextWrapper,
    });

    await act(async () => router.navigate({ to: "/" }));
    return { router, app };
  };

  it("should load the user session and render the home page", async () => {
    const { app } = await setUp();
    expect(app.getByText("Home")).toBeDefined();

    expect(app.getByText("Session Details")).toBeDefined();
    expect(app.getByText("Session ID: test-session-id")).toBeDefined();
    expect(app.getByText("Expires At: 2025-11-04T12:05:30.743Z"));
    expect(app.getByText("State: test-state")).toBeDefined();

    expect(setupSessionFn).toHaveBeenCalled();
    expect(getAuthorisationUrlFn).toHaveBeenCalledWith({
      data: { state: "test-state" },
    });
  });

  it("should have the correct authorization URL in the login button", async () => {
    const { app } = await setUp();

    const loginButton = app.getByRole("link") as HTMLAnchorElement;
    expect(loginButton).toBeDefined();
    expect(loginButton.href).toBe(
      "http://example.com/authorize?state=test-state",
    );
  });
});
