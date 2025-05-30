export class ResponseError extends Error {
  constructor(
    message: string,
    public status: number,
    public headers?: Record<string, string>,
    public correlationId?: string,
  ) {
    super(message);
    this.name = "ResponseError";
    this.status = status;
    this.headers = headers;
    this.correlationId = correlationId;
  }

  public static fromResponse(
    response: Response,
    message?: string,
  ): ResponseError {
    return new ResponseError(
      message || `Request failed with status ${response.status}`,
      response.status,
      Object.fromEntries(response.headers.entries()),
      response.headers.get("X-Correlation-ID") || undefined,
    );
  }
}
