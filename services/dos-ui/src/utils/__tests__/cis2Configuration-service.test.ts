import { beforeEach, describe, expect, it, vi } from "vitest";
import { getLogger } from "../logger.ts";

vi.mock("../logger.ts", () => {
  const originalModule = vi.importActual("../logger.ts");
  const mockLoggerInstance = {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    createChild: vi.fn(),
  }
  return {
    ...originalModule,
    getLogger: vi.fn(() => (mockLoggerInstance)),
  };
});

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
  buildAuthorizationUrl: (_oidcClient: any, parameters: any) => {
    const url = new URL("http://issuer/auth");
    url.searchParams.append("state", parameters.state);
    return url;
  }

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
    const { getAuthorisationUrl } = await import(
      "../cis2Configuration-service.ts"
    );
    const url = await getAuthorisationUrl({ data: { state: "state" } });
    expect(url).toContain("http://issuer/auth?state=state");
  });

  it("throws error on failure", async () => {
    const logger = getLogger();
    mockGetOIDCConfig.mockRejectedValue(new Error("fail"));

    const { getAuthorisationUrl } = await import(
      "../cis2Configuration-service"
    );
    await expect(
      getAuthorisationUrl({ data: { state: "state" } }),
    ).rejects.toThrow("fail");

    expect(logger.error).toHaveBeenCalled();
  });
});
