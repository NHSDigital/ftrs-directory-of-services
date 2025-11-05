import { beforeEach, describe, expect, it, vi } from "vitest";

const mockGetAuthConfig = vi.fn(async () => ({
  redirectUri: "http://localhost/callback",
  scope: "openid",
  issuerUrl: "http://issuer",
  clientId: "client-id",
}));

const mockGetOIDCConfig = vi.fn(async () => ({
  authorization_endpoint: "http://issuer/auth",
}));

vi.mock("../cis2Configuration.ts", () => ({
  getAuthConfig: mockGetAuthConfig,
  getOIDCConfig: mockGetOIDCConfig,
}));

vi.mock("openid-client", () => ({
  randomState: () => "state",
  randomNonce: () => "nonce",
  randomPKCECodeVerifier: () => "verifier",
  calculatePKCECodeChallenge: async () => "challenge",
  buildAuthorizationUrl: (config: any, params: any) => ({
    href: `${config.authorization_endpoint}?state=${params.state}`,
  }),
}));

describe("getAuthorisationUrl", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetAuthConfig.mockResolvedValue({
      redirectUri: "http://localhost/callback",
      scope: "openid",
      issuerUrl: "http://issuer",
      clientId: "client-id",
    });
    mockGetOIDCConfig.mockResolvedValue({
      authorization_endpoint: "http://issuer/auth",
    });
  });

  it("returns the correct authorization URL", async () => {
    const { getAuthorisationUrl } = await import("../cis2Configuration-service.ts");
    const url = await getAuthorisationUrl();
    expect(url).toContain("http://issuer/auth?state=state");
  });

  it("throws error on failure", async () => {
    const { logger } = await import("../logger");
    const loggerErrorSpy = vi
      .spyOn(logger, "error")
      .mockImplementation(() => {});
    mockGetOIDCConfig.mockRejectedValue(new Error("fail"));

    const { getAuthorisationUrl } = await import("../cis2Configuration-service.ts");
    await expect(getAuthorisationUrl()).rejects.toThrow("fail");
    expect(loggerErrorSpy).toHaveBeenCalled();
    loggerErrorSpy.mockRestore();
  });
});
