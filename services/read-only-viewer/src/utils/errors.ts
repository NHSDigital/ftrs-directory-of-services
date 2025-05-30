export class ResponseError extends Error {
  constructor(message: string, public status: number, public headers?: Record<string, string>, public body?: unknown) {
    super(message);
    this.name = 'ResponseError';
    this.status = status;
    this.headers = headers;
    this.body = body;
  }
}
