import { vi } from "vitest";
import { getCIS2PublicKey } from "@/utils/api-jwksUtil";
import { getawsSecret } from "@/utils/aws-util";

vi.mock("@/utils/aws-util", () => ({
  getawsSecret: vi.fn(),
}));

describe("getCIS2PublicKey", () => {
  it("returns the CIS2 public key when the secret is found", async () => {
    const mockKey = "mock-public-key";
    vi.mocked(getawsSecret).mockResolvedValueOnce(mockKey);

    const result = await getCIS2PublicKey();

    expect(result).toBe(mockKey);
    expect(getawsSecret).toHaveBeenCalledWith(
      `/${process.env.PROJECT}/${process.env.ENVIRONMENT}/cis2-public-key`
    );
  });

  it("throws an error when the CIS2 public key is not found", async () => {
    vi.mocked(getawsSecret).mockResolvedValueOnce(null);

    await expect(getCIS2PublicKey()).rejects.toThrow("CIS2 public Key not found");
    expect(getawsSecret).toHaveBeenCalledWith(
      `/${process.env.PROJECT}/${process.env.ENVIRONMENT}/cis2-public-key`
    );
  });

});
