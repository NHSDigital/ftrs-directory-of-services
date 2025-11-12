import { beforeEach, describe, expect, it, vi, type Mock } from "vitest";
import { SessionManager, setupSessionFn } from "@/core/session";
import { useClientSession } from "@/core/context";
import { Route } from "../dashboard";
import type { UserSession } from "@/core/schema";

vi.mock("@/core/session", () => ({
  SessionManager: vi.fn().mockImplementation(() => ({
    getSession: vi.fn(),
  })),
  setupSessionFn: vi.fn(),
}));

vi.mock("@/core/context", () => ({
  useClientSession: vi.fn(),
}));

vi.mock("@tanstack/react-router", async () => {
  const actual = await vi.importActual("@tanstack/react-router");
  return {
    ...actual,
    useLoaderData: vi.fn(),
  };
});

describe("dashboard route", () => {
  const mockUser = {
    uid: "user-123",
    displayName: "John Doe",
    selectedRoleID: "role-1",
    rbacRoles: [
      {
        personOrgID: "org-1",
        personRoleID: "role-123",
        orgCode: "ORG001",
        roleName: "Admin",
      },
    ],
    orgMemberships: [
      {
        personOrgID: "org-1",
        orgName: "Test Hospital",
        orgCode: "ORG001",
      },
    ],
    userOrgs: [
      {
        orgCode: "ORG001",
        orgName: "Test Hospital",
      },
    ],
  };

  const mockSession = {
    sessionID: "session-123",
    expiresAt: 1700000000000,
  };

  const mockUserSession: UserSession = {
    sessionID: "session-123",
    state: "test-state",
    expiresAt: Date.now() + 3600000,
    userID: "user-123",
    user: mockUser,
    tokens: {},
  };

  let mockSessionManager: {
    getSession: Mock;
  };

  beforeEach(() => {
    vi.clearAllMocks();

    mockSessionManager = {
      getSession: vi.fn().mockResolvedValue(mockUserSession),
    };
    // @ts-expect-error - Mocking class constructor requires type conversion for testing
    (SessionManager as Mock).mockImplementation(() => mockSessionManager);

    (useClientSession as Mock).mockReturnValue(mockSession);
  });

  describe("loader", () => {
    it("returns user data when session is valid", async () => {
      const context = {
        session: {
          sessionID: "session-123",
        },
      };

      const result = await Route.options.loader!({ context } as any);

      expect(result).toEqual({ user: mockUser });
      expect(mockSessionManager.getSession).toHaveBeenCalledWith("session-123");
    });

    it("calls setupSessionFn when session is missing from context", async () => {
      const mockSetupSession = { sessionID: "new-session-123" };
      // @ts-expect-error - Mocking function for testing
      (setupSessionFn as Mock).mockResolvedValue(mockSetupSession);
      mockSessionManager.getSession.mockResolvedValue(mockUserSession);

      const context = { session: null };

      await Route.options.loader!({ context } as any);

      expect(setupSessionFn).toHaveBeenCalled();
      expect(context.session).toEqual(mockSetupSession);
    });

    it("redirects to home when session ID is missing", async () => {
      const context = {
        session: {
          sessionID: null,
        },
      };

      await expect(Route.options.loader!({ context } as any)).rejects.toThrow();
    });

    it("redirects to home when session ID is undefined", async () => {
      const context = {
        session: {},
      };

      await expect(Route.options.loader!({ context } as any)).rejects.toThrow();
    });

    it("redirects to home when user session is not found", async () => {
      mockSessionManager.getSession.mockResolvedValue(null);

      const context = {
        session: {
          sessionID: "session-123",
        },
      };

      await expect(Route.options.loader!({ context } as any)).rejects.toThrow();
      expect(mockSessionManager.getSession).toHaveBeenCalledWith("session-123");
    });

    it("redirects to home when user session exists but user is missing", async () => {
      mockSessionManager.getSession.mockResolvedValue({
        ...mockUserSession,
        user: null,
      });

      const context = {
        session: {
          sessionID: "session-123",
        },
      };

      await expect(Route.options.loader!({ context } as any)).rejects.toThrow();
    });

    it("redirects to home when user session exists but user is undefined", async () => {
      mockSessionManager.getSession.mockResolvedValue({
        ...mockUserSession,
        user: undefined,
      });

      const context = {
        session: {
          sessionID: "session-123",
        },
      };

      await expect(Route.options.loader!({ context } as any)).rejects.toThrow();
    });

    it("creates new SessionManager instance for each loader call", async () => {
      const context = {
        session: {
          sessionID: "session-123",
        },
      };

      await Route.options.loader!({ context } as any);
      await Route.options.loader!({ context } as any);

      expect(SessionManager).toHaveBeenCalledTimes(2);
    });
  });

  describe("head", () => {
    it("returns correct meta title", async () => {
      const head = await Route.options.head!({} as any);

      expect(head?.meta).toEqual([{ title: "Dashboard - FtRS DoS UI" }]);
    });
  });

  describe("DashboardPage component", () => {
    beforeEach(async () => {
      const { cleanup } = await import("@testing-library/react");
      const { useLoaderData } = await import("@tanstack/react-router");

      cleanup();
      vi.clearAllMocks();
      (useClientSession as Mock).mockReturnValue(mockSession);
      (useLoaderData as Mock).mockReturnValue({ user: mockUser });
    });

    it("renders dashboard heading", async () => {
      const { render } = await import("@testing-library/react");
      const DashboardPage = Route.options.component as any;

      const { getAllByText } = render(<DashboardPage />);

      expect(getAllByText("Dashboard")[0]).toBeDefined();
    });

    it("renders user information with display name", async () => {
      const { render } = await import("@testing-library/react");
      const DashboardPage = Route.options.component as any;

      const { getAllByText } = render(<DashboardPage />);

      expect(getAllByText("John Doe")[0]).toBeDefined();
    });

    it("renders user information with user ID", async () => {
      const { render } = await import("@testing-library/react");
      const DashboardPage = Route.options.component as any;

      const { getAllByText } = render(<DashboardPage />);

      expect(getAllByText("user-123")[0]).toBeDefined();
    });

    it("renders user information with selected role ID", async () => {
      const { render } = await import("@testing-library/react");
      const DashboardPage = Route.options.component as any;

      const { getAllByText } = render(<DashboardPage />);

      expect(getAllByText("role-1")[0]).toBeDefined();
    });

    it("renders RBAC roles section when roles exist", async () => {
      const { render } = await import("@testing-library/react");
      const DashboardPage = Route.options.component as any;

      const { getAllByText } = render(<DashboardPage />);

      expect(getAllByText("RBAC Roles")[0]).toBeDefined();
      expect(getAllByText("Admin")[0]).toBeDefined();
      expect(getAllByText(/ORG001/)[0]).toBeDefined();
      expect(getAllByText("role-123")[0]).toBeDefined();
    });

    it("does not render RBAC roles section when roles are empty", async () => {
      const { render } = await import("@testing-library/react");
      const { useLoaderData } = await import("@tanstack/react-router");
      const DashboardPage = Route.options.component as any;

      (useLoaderData as Mock).mockReturnValue({
        user: { ...mockUser, rbacRoles: [] }
      });

      const { queryByText } = render(<DashboardPage />);

      expect(queryByText("RBAC Roles")).toBeNull();
    });

    it("renders organisation memberships section when memberships exist", async () => {
      const { render } = await import("@testing-library/react");
      const DashboardPage = Route.options.component as any;

      const { getAllByText } = render(<DashboardPage />);

      expect(getAllByText("Organisation Memberships")[0]).toBeDefined();
      expect(getAllByText(/Test Hospital/)[0]).toBeDefined();
    });

    it("does not render organisation memberships section when memberships are empty", async () => {
      const { render } = await import("@testing-library/react");
      const { useLoaderData } = await import("@tanstack/react-router");
      const DashboardPage = Route.options.component as any;

      (useLoaderData as Mock).mockReturnValue({
        user: { ...mockUser, orgMemberships: [] }
      });

      const { queryByText } = render(<DashboardPage />);

      expect(queryByText("Organisation Memberships")).toBeNull();
    });

    it("renders user organisations section when organisations exist", async () => {
      const { render } = await import("@testing-library/react");
      const DashboardPage = Route.options.component as any;

      const { getAllByText } = render(<DashboardPage />);

      expect(getAllByText("User Organisations")[0]).toBeDefined();
    });

    it("does not render user organisations section when organisations are empty", async () => {
      const { render } = await import("@testing-library/react");
      const { useLoaderData } = await import("@tanstack/react-router");
      const DashboardPage = Route.options.component as any;

      (useLoaderData as Mock).mockReturnValue({
        user: { ...mockUser, userOrgs: [] }
      });

      const { queryByText } = render(<DashboardPage />);

      expect(queryByText("User Organisations")).toBeNull();
    });

    it("renders session information with session ID", async () => {
      const { render } = await import("@testing-library/react");
      const DashboardPage = Route.options.component as any;

      const { getAllByText } = render(<DashboardPage />);

      expect(getAllByText("session-123")[0]).toBeDefined();
    });

    it("renders session information with formatted expiry date", async () => {
      const { render } = await import("@testing-library/react");
      const DashboardPage = Route.options.component as any;

      const { getAllByText } = render(<DashboardPage />);

      const expectedDate = new Date(1700000000000).toLocaleString();
      expect(getAllByText(expectedDate)[0]).toBeDefined();
    });

    it("renders multiple RBAC roles correctly", async () => {
      const { render, cleanup } = await import("@testing-library/react");
      const { useLoaderData } = await import("@tanstack/react-router");
      const DashboardPage = Route.options.component as any;

      cleanup();
      const userWithMultipleRoles = {
        ...mockUser,
        rbacRoles: [
          {
            personOrgID: "org-1",
            personRoleID: "role-123",
            orgCode: "ORG001",
            roleName: "Admin",
          },
          {
            personOrgID: "org-2",
            personRoleID: "role-456",
            orgCode: "ORG002",
            roleName: "Manager",
          },
        ],
      };

      (useLoaderData as Mock).mockReturnValue({ user: userWithMultipleRoles });

      const { getByText } = render(<DashboardPage />);

      expect(getByText("Admin")).toBeDefined();
      expect(getByText("Manager")).toBeDefined();
      expect(getByText("role-456")).toBeDefined();
      expect(getByText("ORG002")).toBeDefined();
    });

    it("renders multiple organisation memberships correctly", async () => {
      const { render, cleanup } = await import("@testing-library/react");
      const { useLoaderData } = await import("@tanstack/react-router");
      const DashboardPage = Route.options.component as any;

      cleanup();
      const userWithMultipleOrgs = {
        ...mockUser,
        rbacRoles: [],
        userOrgs: [],
        orgMemberships: [
          {
            personOrgID: "org-1",
            orgName: "Test Hospital",
            orgCode: "ORG001",
          },
          {
            personOrgID: "org-2",
            orgName: "Test Clinic",
            orgCode: "ORG002",
          },
        ],
      };

      (useLoaderData as Mock).mockReturnValue({ user: userWithMultipleOrgs });

      const { getByText } = render(<DashboardPage />);

      expect(getByText("Test Hospital")).toBeDefined();
      expect(getByText("Test Clinic")).toBeDefined();
    });

    it("renders multiple user organisations correctly", async () => {
      const { render, cleanup } = await import("@testing-library/react");
      const { useLoaderData } = await import("@tanstack/react-router");
      const DashboardPage = Route.options.component as any;

      cleanup();
      const userWithMultipleUserOrgs = {
        ...mockUser,
        rbacRoles: [],
        orgMemberships: [],
        userOrgs: [
          {
            orgCode: "ORG001",
            orgName: "Test Hospital",
          },
          {
            orgCode: "ORG003",
            orgName: "Health Center",
          },
        ],
      };

      (useLoaderData as Mock).mockReturnValue({ user: userWithMultipleUserOrgs });

      const { getByText } = render(<DashboardPage />);

      expect(getByText("Test Hospital")).toBeDefined();
      expect(getByText("Health Center")).toBeDefined();
      expect(getByText("ORG003")).toBeDefined();
    });
  });

});

