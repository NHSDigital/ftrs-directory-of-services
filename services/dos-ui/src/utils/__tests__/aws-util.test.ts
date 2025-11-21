import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock the modules before importing
vi.mock("@aws-lambda-powertools/parameters/secrets");
vi.mock("@aws-lambda-powertools/parameters/ssm");
vi.mock("../logger", () => {
  const originalModule = vi.importActual("../logger");
  return {
    ...originalModule,
    getLogger: vi.fn(() => ({
      debug: vi.fn(),
      info: vi.fn(),
      warn: vi.fn(),
      error: vi.fn(),
      createChild: vi.fn(),
    })),
  };
});

import { getSecret } from "@aws-lambda-powertools/parameters/secrets";
import { getParameter } from "@aws-lambda-powertools/parameters/ssm";
import type { SDKOptionsTypeFromPowertools } from "@/types/SDKOptionsTypeFromPowertools";
// Import after mocking
import { getawsParameter, getawsSecret } from "../aws-util";

describe("getawsSecret", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns the secret value as string", async () => {
    vi.mocked(getSecret).mockResolvedValue("mocked-secret-value");
    const secret = await getawsSecret("test-secret");
    expect(secret).toBe("mocked-secret-value");
  });

  it("decodes Uint8Array secret to string", async () => {
    const uint8Array = new Uint8Array(new TextEncoder().encode("binary-secret-data"));
    vi.mocked(getSecret).mockResolvedValue(uint8Array as any);
    const secret = await getawsSecret("test-secret");
    expect(secret).toBe("binary-secret-data");
  });

  it("returns undefined when secret is not found", async () => {
    vi.mocked(getSecret).mockResolvedValue(undefined);
    const secret = await getawsSecret("test-secret");
    expect(secret).toBeUndefined();
  });

  it("throws error on failure", async () => {
    vi.mocked(getSecret).mockRejectedValue(new Error("Secret not found"));
    await expect(getawsSecret("test-secret")).rejects.toThrow(
      "Secret not found",
    );
  });
});

describe("getawsParameter", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns parameter with default options (WithDecryption: true, transform: json)", async () => {
    vi.mocked(getParameter).mockResolvedValue('{"key":"value"}');

    const param = await getawsParameter("test-param");

    expect(getParameter).toHaveBeenCalledWith("test-param", {
      sdkOptions: {
        WithDecryption: true,
        transform: "json",
      },
    });
    expect(param).toBe('{"key":"value"}');
  });

  it("allows overriding WithDecryption option", async () => {
    vi.mocked(getParameter).mockResolvedValue("plain-value");

    const options: Partial<SDKOptionsTypeFromPowertools> = { WithDecryption: false };
    await getawsParameter("test-param", options);

    expect(getParameter).toHaveBeenCalledWith("test-param", {
      sdkOptions: {
        WithDecryption: false,
        transform: "json",
      },
    });
  });

  it("allows overriding transform option", async () => {
    vi.mocked(getParameter).mockResolvedValue("binary-data");

    const options: Partial<SDKOptionsTypeFromPowertools> = { transform: "binary" };
    await getawsParameter("test-param", options);

    expect(getParameter).toHaveBeenCalledWith("test-param", {
      sdkOptions: {
        WithDecryption: true,
        transform: "binary",
      },
    });
  });

  it("allows overriding both options", async () => {
    vi.mocked(getParameter).mockResolvedValue("custom-value");

    const options: Partial<SDKOptionsTypeFromPowertools> = {
      WithDecryption: false,
      transform: "binary",
    };
    await getawsParameter("test-param", options);

    expect(getParameter).toHaveBeenCalledWith("test-param", {
      sdkOptions: {
        WithDecryption: false,
        transform: "binary",
      },
    });
  });

  it("throws error on failure", async () => {
    vi.mocked(getParameter).mockRejectedValue(new Error("Parameter not found"));
    await expect(getawsParameter("test-param")).rejects.toThrow(
      "Parameter not found",
    );
  });
});
