import { beforeEach, describe, expect, it, vi, type Mock } from "vitest";
import { getCIS2PublicKey } from "@/utils/api-jwksUtil";
import { Route } from "../api.jwks";

// Mock dependencies
vi.mock("@/utils/api-jwksUtil", () => ({
  getCIS2PublicKey: vi.fn(),
}));

describe("api.jwks route", () => {
  // Helper to get handler without type errors
  const getHandler = () => {
    // @ts-expect-error - Accessing internal handler structure for testing
    return Route.options?.server?.handlers?.GET;
  };

  const mockPublicKey = `-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z4rJYvHHrVrPgp6zc7r
xVF9YqgkGQXp5V4h0OE5b1aTQnz7sOXJK5bIshFMgHi0P1IvQ0pXJ4aKZ9rITJLv
-----END PUBLIC KEY-----`;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("GET handler", () => {
    it("should successfully return JWKS when public key is retrieved", async () => {
      (getCIS2PublicKey as Mock).mockResolvedValue(mockPublicKey);

      const handler = getHandler();
      expect(handler).toBeDefined();

      const response = await handler!();

      expect(response.status).toBe(200);
      expect(response.headers.get("Content-Type")).toBe("application/json");
      expect(await response.text()).toBe(mockPublicKey);
      expect(getCIS2PublicKey).toHaveBeenCalledTimes(1);
    });

    it("should return 500 error when getCIS2PublicKey throws an error", async () => {
      const mockError = new Error("Failed to retrieve public key from AWS");
      (getCIS2PublicKey as Mock).mockRejectedValue(mockError);

      const handler = getHandler();
      const response = await handler!();

      expect(response.status).toBe(500);
      const responseBody = await response.json();
      expect(responseBody).toEqual({ message: "Error retrieving JWKS" });
      expect(getCIS2PublicKey).toHaveBeenCalledTimes(1);
    });

    it("should return 500 error when getCIS2PublicKey returns null", async () => {
      (getCIS2PublicKey as Mock).mockRejectedValue(
        new Error("CIS2 public Key not found")
      );

      const handler = getHandler();
      const response = await handler!();

      expect(response.status).toBe(500);
      const responseBody = await response.json();
      expect(responseBody).toEqual({ message: "Error retrieving JWKS" });
    });

    it("should handle network timeout errors", async () => {
      const timeoutError = new Error("Network timeout");
      (getCIS2PublicKey as Mock).mockRejectedValue(timeoutError);

      const handler = getHandler();
      const response = await handler!();

      expect(response.status).toBe(500);
      const responseBody = await response.json();
      expect(responseBody.message).toBe("Error retrieving JWKS");
    });

    it("should handle AWS Secrets Manager errors", async () => {
      const awsError = new Error("AccessDeniedException: User is not authorized");
      (getCIS2PublicKey as Mock).mockRejectedValue(awsError);

      const handler = getHandler();
      const response = await handler!();

      expect(response.status).toBe(500);
      const responseBody = await response.json();
      expect(responseBody.message).toBe("Error retrieving JWKS");
    });

    it("should return valid JSON response structure on error", async () => {
      (getCIS2PublicKey as Mock).mockRejectedValue(new Error("Test error"));

      const handler = getHandler();
      const response = await handler!();

      expect(response.status).toBe(500);

      const responseBody = await response.json();
      expect(responseBody).toHaveProperty("message");
      expect(typeof responseBody.message).toBe("string");
      expect(responseBody.message).toBe("Error retrieving JWKS");
    });

    it("should handle empty string from getCIS2PublicKey", async () => {
      (getCIS2PublicKey as Mock).mockResolvedValue("");

      const handler = getHandler();
      const response = await handler!();

      expect(response.status).toBe(200);
      expect(await response.text()).toBe("");
      expect(getCIS2PublicKey).toHaveBeenCalledTimes(1);
    });

    it("should set correct Content-Type header for successful response", async () => {
      (getCIS2PublicKey as Mock).mockResolvedValue(mockPublicKey);

      const handler = getHandler();
      const response = await handler!();

      expect(response.headers.get("Content-Type")).toBe("application/json");
    });

    it("should handle malformed public key data", async () => {
      const malformedKey = "not-a-valid-public-key";
      (getCIS2PublicKey as Mock).mockResolvedValue(malformedKey);

      const handler = getHandler();
      const response = await handler!();

      expect(response.status).toBe(200);
      expect(await response.text()).toBe(malformedKey);
    });

    it("should handle large public key responses", async () => {
      const largePublicKey = mockPublicKey.repeat(10);
      (getCIS2PublicKey as Mock).mockResolvedValue(largePublicKey);

      const handler = getHandler();
      const response = await handler!();

      expect(response.status).toBe(200);
      const responseText = await response.text();
      expect(responseText.length).toBe(largePublicKey.length);
    });

    it("should not expose internal error details in response", async () => {
      const internalError = new Error(
        "Internal AWS error: Secret arn:aws:secretsmanager:..."
      );
      (getCIS2PublicKey as Mock).mockRejectedValue(internalError);

      const handler = getHandler();
      const response = await handler!();

      const responseBody = await response.json();
      expect(responseBody.message).toBe("Error retrieving JWKS");
      expect(responseBody.message).not.toContain("arn:aws");
      expect(responseBody.message).not.toContain("Internal");
    });
  });
});

