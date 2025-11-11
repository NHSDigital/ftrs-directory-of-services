import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock the modules before importing
vi.mock("@aws-lambda-powertools/parameters/secrets");
vi.mock("@aws-lambda-powertools/parameters/ssm");
vi.mock("../logger");

import { getSecret } from "@aws-lambda-powertools/parameters/secrets";
import { getParameter } from "@aws-lambda-powertools/parameters/ssm";
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

    await getawsParameter("test-param", { WithDecryption: false });

    expect(getParameter).toHaveBeenCalledWith("test-param", {
      sdkOptions: {
        WithDecryption: false,
        transform: "json",
      },
    });
  });

  it("allows overriding transform option", async () => {
    vi.mocked(getParameter).mockResolvedValue("binary-data");

    await getawsParameter("test-param", { transform: "binary" });

    expect(getParameter).toHaveBeenCalledWith("test-param", {
      sdkOptions: {
        WithDecryption: true,
        transform: "binary",
      },
    });
  });

  it("allows overriding both options", async () => {
    vi.mocked(getParameter).mockResolvedValue("custom-value");

    await getawsParameter("test-param", {
      WithDecryption: false,
      transform: "binary",
    });

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
