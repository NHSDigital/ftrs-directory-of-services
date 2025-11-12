import { describe, expect, it, vi } from "vitest";
import { getawsSecret } from "../aws-util.ts";
import {
  getAuthConfig,
  getCIS2PrivateKey,
  validateConfig,
} from "../cis2Configuration";

vi.mock("../aws-util.ts", () => ({
  getawsParameter: vi.fn(async () =>
    JSON.stringify({
      issuerUrl: "http://issuer",
      clientId: "client-id",
      redirectUri: "http://localhost/callback",
      scope: "openid",
    }),
  ),
  getawsSecret: vi.fn(),
}));

vi.mock("jose", async () => ({
  ...(await vi.importActual("jose")),
  importPKCS8: vi.fn(async () => "mocked-crypto-key"),
}));

describe("validateConfig", () => {
  it("throws error if issuerUrl or clientId missing", () => {
    expect(() =>
      validateConfig({
        clientId: "",
        issuerUrl: "",
        redirectUri: "",
        scope: "",
      }),
    ).toThrowError(
      "Invalid CIS2ClientConfig: issuerUrl and clientId are required",
    );
  });
  it("does not throw if config is valid", () => {
    expect(() =>
      validateConfig({
        issuerUrl: "url",
        clientId: "id",
        redirectUri: "",
        scope: "",
      }),
    ).not.toThrow();
  });
});

describe("getAuthConfig", () => {
  it("returns parsed config and calls validateConfig", async () => {
    const config = await getAuthConfig();
    expect(config.issuerUrl).toBe("http://issuer");
    expect(config.clientId).toBe("client-id");
  });
});

describe("getCIS2PrivateKey", () => {
  it("throws error if private key not found", async () => {
    vi.mocked(getawsSecret).mockResolvedValueOnce(undefined);
    await expect(getCIS2PrivateKey()).rejects.toThrow(
      "CIS2 Private Key not found",
    );
  });

  it("returns imported CryptoKey", async () => {
    vi.mocked(getawsSecret).mockResolvedValueOnce("mocked-pem-key");
    const key = await getCIS2PrivateKey();
    expect(key).toBe("mocked-crypto-key");
    const { importPKCS8 } = await import("jose");
    expect(importPKCS8).toHaveBeenCalledWith("mocked-pem-key", "RS512");
  });
});
