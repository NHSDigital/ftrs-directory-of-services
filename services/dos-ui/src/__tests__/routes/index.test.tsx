import { describe } from "node:test";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { render } from "@testing-library/react";
import { act } from "react";
import { expect, it } from "vitest";
import { ClientSessionContext } from "@/core/context";
import { Route as Index } from "@/routes/index";

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

const setUp = async () => {
  const router = createRouter({
    defaultPendingMinMs: 0,
    routeTree: Index,
  });

  const app = render(<RouterProvider router={router} />, {
    wrapper: ContextWrapper,
  });

  await act(async () => router.navigate({ to: "/" }));
  return { router, app };
};

describe("Index Route", () => {
  it("should render the index route with session data", async () => {
    const { app } = await setUp();
    expect(app.container).toBeDefined();

    expect(app.getByText("Home")).toBeDefined();

    expect(app.container).toMatchSnapshot("Index Route with Session Data");
  });
});
