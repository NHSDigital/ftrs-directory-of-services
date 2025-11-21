export class AppError extends Error {
  public sessionID?: string;
  public requestID?: string;
  public name = "AppError";

  constructor(message: string, sessionID?: string, requestID?: string) {
    super(message);
    this.sessionID = sessionID;
    this.requestID = requestID;
  }

  public static from(
    error: Error,
    sessionID?: string,
    requestID?: string,
  ): AppError {
    return new AppError(error.message, sessionID, requestID);
  }
}
