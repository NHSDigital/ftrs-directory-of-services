import { ResponseError } from "../errors";

describe("ResponseError", () => {
  it("initialises and sets properties correctly", () => {
    const error = new ResponseError({
      message: "Request failed with status code 500",
      statusCode: 500,
      headers: {
        "content-type": "application/json",
        "x-correlation-id": "test-correlation-id",
      },
      correlationId: "test-correlation-id",
    });

    expect(error).toBeInstanceOf(ResponseError);
    expect(error.name).toBe("ResponseError");
    expect(error.message).toBe("Request failed with status code 500");
    expect(error.statusCode).toBe(500);
    expect(error.headers).toEqual({
      "content-type": "application/json",
      "x-correlation-id": "test-correlation-id",
    });
    expect(error.correlationId).toBe("test-correlation-id");
  });

  it("fromResponse sets properties correctly", () => {
    const mockResponse = new Response(JSON.stringify({ error: "Not Found" }), {
      status: 404,
      headers: {
        "content-type": "application/json",
        "x-correlation-id": "test-correlation-id",
      },
    });

    const error = ResponseError.fromResponse(
      mockResponse,
      "Resource not found",
    );
    expect(error).toBeInstanceOf(ResponseError);
    expect(error.message).toBe("Resource not found");
    expect(error.statusCode).toBe(404);
    expect(error.headers).toEqual({
      "content-type": "application/json",
      "x-correlation-id": "test-correlation-id",
    });
    expect(error.correlationId).toBe("test-correlation-id");
  });

  it("fromResponse uses default message if none provided", () => {
    const mockResponse = new Response(null, { status: 500 });
    const error = ResponseError.fromResponse(mockResponse);
    expect(error.message).toBe("Request failed with status code 500");
  });

  it("fromResponse handles missing correlation ID", () => {
    const mockResponse = new Response(null, { status: 400 });
    const error = ResponseError.fromResponse(mockResponse);
    expect(error.correlationId).toBeUndefined();
  });
});
