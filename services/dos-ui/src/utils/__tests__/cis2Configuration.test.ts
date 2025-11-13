import { describe, expect, it, vi } from "vitest";
import {getawsParameter, getawsSecret} from "../aws-util.ts";
import {
  getAuthConfig,
  getCIS2PrivateKey, getOIDCConfig,
  validateConfig,
} from "../cis2Configuration";
import {importPKCS8} from "jose";
import * as client from "openid-client";

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

vi.mock("openid-client", () => ({
  discovery: vi.fn(),
  PrivateKeyJwt: vi.fn(),
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

describe("getOIDCConfig", () => {
  it("returns OIDC configuration on successful discovery", async () => {
    const mockPrivateKeyJwtResult = "mocked-private-key-jwt" as any;
    vi.mocked(client.PrivateKeyJwt).mockReturnValueOnce(mockPrivateKeyJwtResult);

    vi.mocked(getawsParameter).mockResolvedValueOnce(
      JSON.stringify({
        issuerUrl: "http://issuer",
        clientId: "client-id",
        redirectUri: "http://localhost/callback",
        scope: "openid",
      }),
    );
    vi.mocked(getawsSecret).mockResolvedValueOnce("mocked-pem-key");
    vi.mocked(importPKCS8).mockResolvedValueOnce("mocked-crypto-key" as any);
    vi.mocked(client.discovery).mockResolvedValueOnce({
      serverMetadata: () => ({
        authorization_endpoint: "http://auth",
        token_endpoint: "http://token",
        issuer: "http://issuer",
        userinfo_endpoint: "http://userinfo",
        supportsPKCE: vi.fn(),
      } as any),
    } as any);

    const config = await getOIDCConfig();

    expect(config).toBeDefined();
    expect(client.PrivateKeyJwt).toHaveBeenCalledWith("mocked-crypto-key");
    expect(client.discovery).toHaveBeenCalledWith(
      new URL(".well-known/openid-configuration", "http://issuer"),
      "client-id",
      {},
      mockPrivateKeyJwtResult,
    );
  });

  it("throws an error if discovery fails", async () => {
    vi.mocked(getawsParameter).mockResolvedValueOnce(
      JSON.stringify({
        issuerUrl: "http://issuer",
        clientId: "client-id",
        redirectUri: "http://localhost/callback",
        scope: "openid",
      }),
    );
    vi.mocked(getawsSecret).mockResolvedValueOnce("mocked-pem-key");
    vi.mocked(importPKCS8).mockResolvedValueOnce("mocked-crypto-key" as any);
    vi.mocked(client.discovery).mockRejectedValueOnce(new Error("Discovery failed"));

    await expect(getOIDCConfig()).rejects.toThrow("Discovery failed");
  });

  it("throws an error if issuerUrl is invalid", async () => {
    vi.mocked(getawsParameter).mockResolvedValueOnce(
      JSON.stringify({
        issuerUrl: "invalid-url",
        clientId: "client-id",
        redirectUri: "http://localhost/callback",
        scope: "openid",
      }),
    );

    await expect(getOIDCConfig()).rejects.toThrow();
  });

});
