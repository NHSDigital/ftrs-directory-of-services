type ResponseErrorInput = {
  message: string;
  statusCode: number;
  headers?: Record<string, string>;
  correlationId?: string;
}

export class ResponseError extends Error {
  public statusCode: number;
  public headers?: Record<string, string>;
  public correlationId?: string;

  constructor({
    message,
    statusCode,
    headers,
    correlationId
  }: ResponseErrorInput) {
    super(message);
    this.name = "ResponseError";
    this.statusCode = statusCode;
    this.headers = headers;
    this.correlationId = correlationId;
  }

  public static fromResponse(
    response: Response,
    message?: string,
  ): ResponseError {
    return new ResponseError({
      message: message || `Request failed with status code ${response.status}`,
      statusCode: response.status,
      headers: Object.fromEntries(response.headers.entries()),
      correlationId: response.headers.get("X-Correlation-ID") || undefined,
    });
  }
}
