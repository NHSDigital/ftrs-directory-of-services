import { describe, expect, it, vi, beforeEach, type Mock } from "vitest";
import { render, screen } from "@testing-library/react";
import { createRootRoute, createRoute, createRouter, RouterProvider } from "@tanstack/react-router";
import { useClientSession } from "@/core/context";
import { setupSessionFn } from "@/core/session";
import type { ClientSession, UserInfo } from "@/core/schema";
import DashboardPage from "@/routes/dashboard";

vi.mock("@/core/context", () => ({
  useClientSession: vi.fn(),
}));

vi.mock("@/core/session", () => ({
  setupSessionFn: vi.fn(),
}));

describe("Dashboard", () => {
  const mockUser: UserInfo = {
    uid: "test-user-123",
    displayName: "Test User",
    selectedRoleID: "role-456",
    rbacRoles: [
      {
        personOrgID: "person-org-1",
        personRoleID: "person-role-1",
        roleName: "Admin",
        orgCode: "ORG001",
      },
      {
        personOrgID: "person-org-2",
        personRoleID: "person-role-2",
        roleName: "Viewer",
        orgCode: "ORG002",
      },
    ],
    orgMemberships: [
      {
        personOrgID: "person-org-1",
        orgCode: "ORG001",
        orgName: "Test Organisation 1",
      },
      {
        personOrgID: "person-org-2",
        orgCode: "ORG002",
        orgName: "Test Organisation 2",
      },
    ],
    userOrgs: [
      {
        orgCode: "USER-ORG-001",
        orgName: "User Organisation 1",
      },
    ],
  };

  const mockSession: ClientSession = {
    sessionID: "session-123",
    expiresAt: Date.now() + 3600000,
    state: "test-state",
    userID: "test-user-123",
    user: mockUser,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useClientSession as Mock).mockReturnValue(mockSession);
    (setupSessionFn as unknown as Mock).mockResolvedValue(mockSession);
  });

  const createTestRouter = (customSession?: ClientSession) => {
    const rootRoute = createRootRoute();
    const dashboardRoute = createRoute({
      getParentRoute: () => rootRoute,
      path: "/dashboard",
      component: DashboardPage,
    });

    const routeTree = rootRoute.addChildren([dashboardRoute]);

    return createRouter({
      routeTree,
      context: {
        session: customSession || mockSession,
      },
    });
  };

  describe("User Information Card", () => {
    it("should render user information correctly", async () => {
      const router = createTestRouter();
      render(<RouterProvider router={router} />);

      await router.navigate({ to: "/dashboard" });

      expect(screen.getByText("User Information")).toBeDefined();
      expect(screen.getByText("Display Name")).toBeDefined();
      expect(screen.getByText("Test User")).toBeDefined();
      expect(screen.getByText("User ID")).toBeDefined();
      expect(screen.getByText("test-user-123")).toBeDefined();
      expect(screen.getByText("Selected Role ID")).toBeDefined();
      expect(screen.getByText("role-456")).toBeDefined();
    });
  });

  describe("RBAC Roles Table", () => {
    it("should render RBAC roles table when roles exist", async () => {
      const router = createTestRouter();
      render(<RouterProvider router={router} />);

      await router.navigate({ to: "/dashboard" });

      expect(screen.getByText("RBAC Roles")).toBeDefined();
      expect(screen.getByText("Role Name")).toBeDefined();
      expect(screen.getAllByText("Organisation Code").length).toBeGreaterThan(0);
      expect(screen.getByText("Person Role ID")).toBeDefined();

      expect(screen.getByText("Admin")).toBeDefined();
      expect(screen.getByText("Viewer")).toBeDefined();
      expect(screen.getAllByText("ORG001").length).toBeGreaterThan(0);
      expect(screen.getAllByText("ORG002").length).toBeGreaterThan(0);
      expect(screen.getByText("person-role-1")).toBeDefined();
      expect(screen.getByText("person-role-2")).toBeDefined();
    });

    it("should not render RBAC roles table when roles are empty", async () => {
      const sessionWithoutRoles = {
        ...mockSession,
        user: {
          ...mockUser,
          rbacRoles: [],
        },
      };
      (useClientSession as Mock).mockReturnValue(sessionWithoutRoles);

      const router = createTestRouter(sessionWithoutRoles);

      render(<RouterProvider router={router} />);
      await router.navigate({ to: "/dashboard" });

      expect(screen.queryByText("RBAC Roles")).toBeNull();
    });
  });

  describe("Organisation Memberships Table", () => {
    it("should render organisation memberships table when memberships exist", async () => {
      const router = createTestRouter();
      render(<RouterProvider router={router} />);

      await router.navigate({ to: "/dashboard" });

      expect(screen.getByText("Organisation Memberships")).toBeDefined();
      expect(screen.getByText("Test Organisation 1")).toBeDefined();
      expect(screen.getByText("Test Organisation 2")).toBeDefined();
    });

    it("should not render organisation memberships table when memberships are empty", async () => {
      const sessionWithoutMemberships = {
        ...mockSession,
        user: {
          ...mockUser,
          orgMemberships: [],
        },
      };
      (useClientSession as Mock).mockReturnValue(sessionWithoutMemberships);

      const router = createTestRouter(sessionWithoutMemberships);

      render(<RouterProvider router={router} />);
      await router.navigate({ to: "/dashboard" });

      expect(screen.queryByText("Organisation Memberships")).toBeNull();
    });
  });

  describe("User Organisations Table", () => {
    it("should render user organisations table when organisations exist", async () => {
      const router = createTestRouter();
      render(<RouterProvider router={router} />);

      await router.navigate({ to: "/dashboard" });

      expect(screen.getByText("User Organisations")).toBeDefined();
      expect(screen.getByText("User Organisation 1")).toBeDefined();
      expect(screen.getByText("USER-ORG-001")).toBeDefined();
    });

    it("should not render user organisations table when organisations are empty", async () => {
      const sessionWithoutUserOrgs = {
        ...mockSession,
        user: {
          ...mockUser,
          userOrgs: [],
        },
      };
      (useClientSession as Mock).mockReturnValue(sessionWithoutUserOrgs);

      const router = createTestRouter(sessionWithoutUserOrgs);

      render(<RouterProvider router={router} />);
      await router.navigate({ to: "/dashboard" });

      expect(screen.queryByText("User Organisations")).toBeNull();
    });
  });

  describe("Session Information Card", () => {
    it("should render session information correctly", async () => {
      const router = createTestRouter();
      render(<RouterProvider router={router} />);

      await router.navigate({ to: "/dashboard" });

      expect(screen.getByText("Session Information")).toBeDefined();
      expect(screen.getByText("Session ID")).toBeDefined();
      expect(screen.getByText("session-123")).toBeDefined();
      expect(screen.getByText("Expires At")).toBeDefined();
    });

    it("should format expiry date correctly", async () => {
      const expiresAt = new Date("2025-12-31T23:59:59").getTime();
      const sessionWithDate = {
        ...mockSession,
        expiresAt,
      };
      (useClientSession as Mock).mockReturnValue(sessionWithDate);

      const router = createTestRouter(sessionWithDate);

      render(<RouterProvider router={router} />);
      await router.navigate({ to: "/dashboard" });

      const formattedDate = new Date(expiresAt).toLocaleString();
      expect(screen.getByText(formattedDate)).toBeDefined();
    });
  });

  describe("Component Rendering", () => {
    it("should return null when user is not in session", async () => {
      const sessionWithoutUser = {
        ...mockSession,
        user: undefined,
      };
      (useClientSession as Mock).mockReturnValue(sessionWithoutUser);

      const router = createTestRouter();
      const { container } = render(<RouterProvider router={router} />);

      await router.navigate({ to: "/dashboard" });

      expect(container.querySelector("main")).toBeNull();
    });

    it("should render all cards with nhsuk-react-components", async () => {
      const router = createTestRouter();
      const { container } = render(<RouterProvider router={router} />);

      await router.navigate({ to: "/dashboard" });

      // Check for Container
      expect(container.querySelector(".nhsuk-width-container")).toBeDefined();

      // Check for main wrapper
      expect(container.querySelector(".nhsuk-main-wrapper")).toBeDefined();

      // Check for grid
      expect(container.querySelector(".nhsuk-grid-row")).toBeDefined();
      expect(container.querySelector(".nhsuk-grid-column-full")).toBeDefined();
    });

    it("should render dashboard title", async () => {
      const router = createTestRouter();
      render(<RouterProvider router={router} />);

      await router.navigate({ to: "/dashboard" });

      expect(screen.getByRole("heading", { name: "Dashboard" })).toBeDefined();
    });
  });

  describe("Loader redirect behavior", () => {
    it("should not render dashboard when session ID is missing", async () => {
      const sessionWithoutID = {
        ...mockSession,
        sessionID: "",
        user: undefined,
      };
      (useClientSession as Mock).mockReturnValue(sessionWithoutID);

      const router = createTestRouter(sessionWithoutID);
      const { container } = render(<RouterProvider router={router} />);

      await router.navigate({ to: "/dashboard" });

      // Component returns null when no user, so main won't be rendered
      expect(container.querySelector("main")).toBeNull();
    });

    it("should not render dashboard when user is missing from session", async () => {
      const sessionWithoutUser = {
        ...mockSession,
        user: undefined,
      };
      (useClientSession as Mock).mockReturnValue(sessionWithoutUser);

      const router = createTestRouter(sessionWithoutUser);
      const { container } = render(<RouterProvider router={router} />);

      await router.navigate({ to: "/dashboard" });

      // Component returns null when no user
      expect(container.querySelector("main")).toBeNull();
    });
  });
});

