import { server } from "@/__mocks__/mockServiceWorker";
import { getParameter } from "@aws-lambda-powertools/parameters/ssm";
import { fromNodeProviderChain } from "@aws-sdk/credential-providers";
import { http, HttpResponse } from "msw";
import type { Mock } from "vitest";
import {
  getBaseEndpoint,
  getSignedHeaders,
  makeSignedFetch,
} from "../authentication";
import { ResponseError } from "../errors";

vi.mock("@aws-lambda-powertools/parameters/ssm", () => ({
  getParameter: vi.fn().mockReturnValue("https://example.com"),
}));
vi.mock("@aws-sdk/credential-providers", () => ({
  fromNodeProviderChain: vi.fn().mockReturnValue({}),
}));
vi.mock("@aws-sdk/signature-v4", () => ({
  SignatureV4: vi.fn().mockImplementation(() => ({
    sign: vi.fn().mockImplementation((request) => ({
      headers: {
        ...request.headers,
        "X-Signed": "true",
      },
      method: request.method,
      hostname: request.hostname,
    })),
  })),
}));

describe("getBaseEndpoint", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env.ENVIRONMENT = undefined;
    process.env.WORKSPACE = undefined;
  });

  it("loads the base endpoint from parameter store", async () => {
    process.env.ENVIRONMENT = "test";
    process.env.WORKSPACE = "test-workspace";

    const endpoint = await getBaseEndpoint();
    expect(endpoint).toBe("https://example.com");

    expect(getParameter).toHaveBeenCalledWith(
      "/ftrs-dos-test-crud-apis-test-workspace/endpoint",
    );
    expect(getParameter).toHaveBeenCalledTimes(1);
  });

  it("loads the base endpoint without workspace", async () => {
    process.env.ENVIRONMENT = "test";
    process.env.WORKSPACE = undefined;

    const endpoint = await getBaseEndpoint();
    expect(endpoint).toBe("https://example.com");

    expect(getParameter).toHaveBeenCalledWith(
      "/ftrs-dos-test-crud-apis/endpoint",
    );
    expect(getParameter).toHaveBeenCalledTimes(1);
  });

  it("throws an error if base URL is not found", async () => {
    (getParameter as Mock).mockReturnValueOnce(null);

    process.env.ENVIRONMENT = "test";
    process.env.WORKSPACE = "test-workspace";

    await expect(getBaseEndpoint()).rejects.toThrow(
      "Base URL not found for environment: test, workspace: test-workspace",
    );

    expect(getParameter).toHaveBeenCalledWith(
      "/ftrs-dos-test-crud-apis-test-workspace/endpoint",
    );
  });
});

describe("getSignedHeaders", () => {
  it("returns signed headers for a request", async () => {
    const options = {
      method: "GET",
      url: "https://example.com/resource",
      headers: { "Custom-Header": "value" },
    };

    const signedHeaders = await getSignedHeaders(options);
    expect(signedHeaders).toEqual({
      "Custom-Header": "value",
      Host: "example.com",
      "X-Signed": "true",
    });
  });

  it("throws an error if signing fails", async () => {
    (fromNodeProviderChain as Mock).mockImplementationOnce(() => {
      throw new Error("Signing failed");
    });

    const options = {
      method: "GET",
      url: "https://example.com/resource",
    };

    await expect(getSignedHeaders(options)).rejects.toThrow("Signing failed");
  });
});

describe("makeSignedFetch", () => {
  it("makes a signed fetch request with correct options", async () => {
    server.use(
      http.get(
        "https://example.com/api/organisations/",
        () => {
          return HttpResponse.json([
            { id: "1", name: "Org 1" },
            { id: "2", name: "Org 2" },
          ]);
        },
        {
          once: true,
        },
      ),
    );

    const options = {
      pathname: "/api/organisations/",
      method: "GET",
      headers: { "Custom-Header": "value" },
      expectedStatus: [200],
    };

    const response = await makeSignedFetch(options);
    expect(response.status).toBe(200);

    const data = await response.json();
    expect(data).toEqual([
      { id: "1", name: "Org 1" },
      { id: "2", name: "Org 2" },
    ]);
  });

  it("throws an error if the response status is not expected", async () => {
    server.use(
      http.get(
        "https://example.com/api/resource",
        () => {
          return HttpResponse.json({ error: "Not Found" }, { status: 404 });
        },
        {
          once: true,
        },
      ),
    );

    const options = {
      pathname: "/api/resource",
      method: "GET",
      expectedStatus: [200],
    };

    const expectedResponseError = new ResponseError({
      message: "Request failed with status code 404",
      statusCode: 404,
      headers: {
        "content-length": "21",
        "content-type": "application/json",
      },
      correlationId: undefined,
    });

    await expect(makeSignedFetch(options)).rejects.toThrow(
      expectedResponseError,
    );
  });
});
