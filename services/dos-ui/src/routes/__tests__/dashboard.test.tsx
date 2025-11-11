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
});

