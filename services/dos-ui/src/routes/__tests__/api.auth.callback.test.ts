import { beforeEach, describe, expect, it, vi, type Mock } from "vitest";
import * as client from "openid-client";
import { useSession } from "@tanstack/react-start/server";
import { SessionManager } from "@/core/session";
import { getOIDCConfig } from "@/utils/cis2Configuration";
import { getLogger } from "@/utils/logger";
import { Route } from "../api.auth.callback";
import type { UserSession } from "@/core/schema";

// Mock dependencies
vi.mock("openid-client", () => ({
  authorizationCodeGrant: vi.fn(),
  fetchUserInfo: vi.fn(),
}));

vi.mock("@tanstack/react-start/server", () => ({
  useSession: vi.fn(),
}));

vi.mock("@/core/session", () => ({
  SessionManager: vi.fn().mockImplementation(() => ({
    getSession: vi.fn(),
    updateSession: vi.fn(),
    getSessionSecret: vi.fn(),
  })),
}));

vi.mock("@/utils/cis2Configuration", () => ({
  getOIDCConfig: vi.fn(),
}));

vi.mock("@/utils/logger", () => ({
  getLogger: vi.fn().mockReturnValue({
    info: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  }),
}));

describe("api.auth.callback route", () => {
  // Helper to get handler without type errors
  const getHandler = () => {
    // @ts-expect-error - Accessing internal handler structure for testing
    return Route.options?.server?.handlers?.GET;
  };

  let mockSessionManager: {
    getSession: Mock;
    updateSession: Mock;
    getSessionSecret: Mock;
  };
  let mockCookieSession: {
    data: { sessionID: string; state: string } | null;
    update: Mock;
    clear: Mock;
  };
  let mockLogger: {
    info: Mock;
    error: Mock;
    debug: Mock;
  };

  const mockOIDCConfig = {
    issuer: "https://example.com",
    client_id: "test-client-id",
  };

  const mockTokens = {
    access_token: "mock-access-token",
    refresh_token: "mock-refresh-token",
    id_token: "mock-id-token",
    token_type: "Bearer",
    expires_in: 3600,
    claims: vi.fn().mockReturnValue({ sub: "user-123" }),
  };

  const mockUserInfo = {
    sub: "user-123",
    name: "Test User",
    email: "test@example.com",
    given_name: "Test",
    family_name: "User",
    nhsid_nrbac_roles: [
      {
        person_orgid: "org-1",
        person_roleid: "role-1",
        org_code: "ORG001",
        role_name: "Admin",
      },
    ],
    nhsid_org_memberships: [
      {
        person_orgid: "org-1",
        org_name: "Test Organization",
        org_code: "ORG001",
      },
    ],
    nhsid_user_orgs: [
      {
        org_code: "ORG001",
        org_name: "Test Organization",
      },
    ],
  };

  const mockUserSession: UserSession = {
    sessionID: "session-123",
    state: "test-state",
    expiresAt: Date.now() + 3600000,
    userID: undefined,
    user: undefined,
    tokens: {},
  };

  beforeEach(() => {
    vi.clearAllMocks();

    mockLogger = {
      info: vi.fn(),
      error: vi.fn(),
      debug: vi.fn(),
    };
    (getLogger as Mock).mockReturnValue(mockLogger);

    mockCookieSession = {
      data: {
        sessionID: "session-123",
        state: "test-state",
      },
      update: vi.fn(),
      clear: vi.fn(),
    };
    (useSession as Mock).mockResolvedValue(mockCookieSession);

    mockSessionManager = {
      getSession: vi.fn().mockResolvedValue(mockUserSession),
      updateSession: vi.fn().mockResolvedValue(undefined),
      getSessionSecret: vi.fn().mockResolvedValue("test-secret-key-32-chars-long"),
    };
    // @ts-expect-error - Mocking class constructor requires type conversion for testing
    (SessionManager as Mock).mockImplementation(() => mockSessionManager);
    SessionManager.getSessionSecret = mockSessionManager.getSessionSecret;

    (getOIDCConfig as Mock).mockResolvedValue(mockOIDCConfig);
    (client.authorizationCodeGrant as Mock).mockResolvedValue(mockTokens);
    (client.fetchUserInfo as Mock).mockResolvedValue(mockUserInfo);
  });

  describe("GET handler", () => {
    it("should successfully process callback with valid code and state", async () => {
      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();
      expect(handler).toBeDefined();

      const response = await handler!({ request } as any);

      expect(response.status).toBe(302);
      expect(response.headers.get("Location")).toBe("/dashboard");
      expect(client.authorizationCodeGrant).toHaveBeenCalledWith(
        mockOIDCConfig,
        expect.any(URL),
        { expectedState: "test-state" }
      );
      expect(client.fetchUserInfo).toHaveBeenCalledWith(
        mockOIDCConfig,
        "mock-access-token",
        "user-123"
      );
      expect(mockSessionManager.updateSession).toHaveBeenCalledWith(
        expect.objectContaining({
          sessionID: "session-123",
          userID: "user-123",
          user: expect.objectContaining({
            uid: "user-123",
            displayName: "Test User",
          }),
        })
      );
      expect(mockLogger.info).toHaveBeenCalledWith(
        "[SERVER] Successfully exchanged authorization code for tokens"
      );
    });

    it("should return 400 when code parameter is missing", async () => {
      const request = new Request(
        "http://localhost:3000/api/auth/callback?state=test-state"
      );

      const handler = getHandler();
      await expect(handler!({ request } as any)).rejects.toThrow(
        "Missing code or state parameter from callback URL"
      );
      expect(mockLogger.error).toHaveBeenCalledWith(
        "Missing code or state parameter from callback URL"
      );
    });

    it("should return 400 when state parameter is missing", async () => {
      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code"
      );

      const handler = getHandler();
      await expect(handler!({ request } as any)).rejects.toThrow(
        "Missing code or state parameter from callback URL"
      );
      expect(mockLogger.error).toHaveBeenCalledWith(
        "Missing code or state parameter from callback URL"
      );
    });

    it("should throw error when session ID is not found in cookie", async () => {
      mockCookieSession.data = null;

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();

      await expect(handler!({ request } as any)).rejects.toThrow(
        "No session ID found in cookie"
      );
      expect(mockLogger.error).toHaveBeenCalledWith(
        "[SERVER] No session ID found in cookie"
      );
    });

    it("should throw error when session is not found in DynamoDB", async () => {
      mockSessionManager.getSession.mockResolvedValue(null);

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();

      await expect(handler!({ request } as any)).rejects.toThrow(
        "Session not found in DynamoDB or it has expired or state mismatch"
      );
      expect(mockLogger.error).toHaveBeenCalledWith(
        "[SERVER] Session not found in DynamoDB or it has expired or state mismatch",
        expect.any(Object)
      );
    });

    it("should throw error when session has expired", async () => {
      mockSessionManager.getSession.mockResolvedValue({
        ...mockUserSession,
        expiresAt: Date.now() - 1000,
      });

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();

      await expect(handler!({ request } as any)).rejects.toThrow(
        "Session not found in DynamoDB or it has expired or state mismatch"
      );
    });

    it("should throw error when state does not match", async () => {
      mockSessionManager.getSession.mockResolvedValue({
        ...mockUserSession,
        state: "different-state",
      });
      mockCookieSession.data!.state = "another-different-state";

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();

      await expect(handler!({ request } as any)).rejects.toThrow(
        "Session not found in DynamoDB or it has expired or state mismatch"
      );
    });

    it("should handle token exchange failure and log error details", async () => {
      const mockError = new Error("Token exchange failed");
      (client.authorizationCodeGrant as Mock).mockRejectedValue(mockError);

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();

      await expect(handler!({ request } as any)).rejects.toThrow(
        "Token exchange failed"
      );
      expect(mockLogger.error).toHaveBeenCalledWith(
        "Token exchange failed",
        expect.objectContaining({
          message: "Token exchange failed",
          errorType: "Error",
        })
      );
    });

    it("should handle OAuth error with error_description", async () => {
      const mockOAuthError = {
        error: "invalid_grant",
        error_description: "Authorization code has expired",
        error_uri: "https://example.com/docs/errors",
      };
      (client.authorizationCodeGrant as Mock).mockRejectedValue(mockOAuthError);

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();

      await expect(handler!({ request } as any)).rejects.toThrow();
      expect(mockLogger.error).toHaveBeenCalledWith(
        "Token exchange failed",
        expect.objectContaining({
          error: "invalid_grant",
          error_description: "Authorization code has expired",
          error_uri: "https://example.com/docs/errors",
        })
      );
    });

    it("should parse userinfo correctly when user has multiple roles", async () => {
      const multiRoleUserInfo = {
        ...mockUserInfo,
        nhsid_nrbac_roles: [
          {
            person_orgid: "org-1",
            person_roleid: "role-1",
            org_code: "ORG001",
            role_name: "Admin",
          },
          {
            person_orgid: "org-2",
            person_roleid: "role-2",
            org_code: "ORG002",
            role_name: "Viewer",
          },
        ],
      };
      (client.fetchUserInfo as Mock).mockResolvedValue(multiRoleUserInfo);

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();
      await handler!({ request } as any);

      expect(mockSessionManager.updateSession).toHaveBeenCalledWith(
        expect.objectContaining({
          user: expect.objectContaining({
            rbacRoles: expect.arrayContaining([
              expect.objectContaining({
                personRoleID: "role-1",
                roleName: "Admin",
              }),
              expect.objectContaining({
                personRoleID: "role-2",
                roleName: "Viewer",
              }),
            ]),
          }),
        })
      );
    });

    it("should handle userinfo without optional fields", async () => {
      const minimalUserInfo = {
        sub: "user-456",
        nhsid_nrbac_roles: [],
        nhsid_org_memberships: [],
        nhsid_user_orgs: [],
      };
      (client.fetchUserInfo as Mock).mockResolvedValue(minimalUserInfo);

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();
      await handler!({ request } as any);

      expect(mockSessionManager.updateSession).toHaveBeenCalledWith(
        expect.objectContaining({
          userID: "user-456",
          user: expect.objectContaining({
            uid: "user-456",
            selectedRoleID: "",
            displayName: "",
            rbacRoles: [],
            orgMemberships: [],
            userOrgs: [],
          }),
        })
      );
    });

    it("should construct display name from given_name and family_name when name is missing", async () => {
      const userInfoWithoutName = {
        ...mockUserInfo,
        name: undefined,
        given_name: "John",
        family_name: "Doe",
      };
      (client.fetchUserInfo as Mock).mockResolvedValue(userInfoWithoutName);

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();
      await handler!({ request } as any);

      expect(mockSessionManager.updateSession).toHaveBeenCalledWith(
        expect.objectContaining({
          user: expect.objectContaining({
            displayName: "John Doe",
          }),
        })
      );
    });

    it("should handle state match from cookie session state", async () => {
      mockSessionManager.getSession.mockResolvedValue({
        ...mockUserSession,
        state: "cookie-state",
      });
      mockCookieSession.data!.state = "cookie-state";

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=cookie-state"
      );

      const handler = getHandler();
      const response = await handler!({ request } as any);

      expect(response.status).toBe(302);
      expect(mockSessionManager.updateSession).toHaveBeenCalled();
    });

    it("should log userinfo details after fetching", async () => {
      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();
      await handler!({ request } as any);

      expect(mockLogger.info).toHaveBeenCalledWith(
        "[SERVER] Userinfo received",
        {
          sub: "user-123",
          name: "Test User",
          email: "test@example.com",
        }
      );
      expect(mockLogger.debug).toHaveBeenCalledWith(
        "Session updated successfully with user details"
      );
    });

    it("should handle error with HTTP response details", async () => {
      const mockHttpError = {
        message: "HTTP Error",
        response: {
          status: 401,
          statusText: "Unauthorized",
          headers: { "content-type": "application/json" },
          body: { error: "invalid_token" },
        },
      };
      (client.authorizationCodeGrant as Mock).mockRejectedValue(mockHttpError);

      const request = new Request(
        "http://localhost:3000/api/auth/callback?code=test-code&state=test-state"
      );

      const handler = getHandler();

      await expect(handler!({ request } as any)).rejects.toThrow();
      expect(mockLogger.error).toHaveBeenCalledWith(
        "Token exchange failed",
        expect.objectContaining({
          response: expect.objectContaining({
            status: 401,
            statusText: "Unauthorized",
          }),
        })
      );
    });
  });
});

