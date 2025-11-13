import { describe, expect, it } from "vitest";
import { AppError } from "../errors";

describe("AppError", () => {
  it("should create an AppError from a standard Error", () => {
    const standardError = new Error("Test error message");
    const sessionID = "test-session-id";
    const requestID = "test-request-id";

    const appError = AppError.from(standardError, sessionID, requestID);

    expect(appError).toBeInstanceOf(AppError);
    expect(appError.message).toBe("Test error message");
    expect(appError.sessionID).toBe(sessionID);
    expect(appError.requestID).toBe(requestID);
  });

  it("should create an AppError with optional parameters", () => {
    const message = "Another test error";
    const appError = new AppError(message);

    expect(appError).toBeInstanceOf(AppError);
    expect(appError.message).toBe(message);
    expect(appError.sessionID).toBeUndefined();
    expect(appError.requestID).toBeUndefined();
  });
});
