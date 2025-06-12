import { server } from "@/__mocks__/mockServiceWorker";
import { ResponseError } from "@/utils/errors";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import type { PropsWithChildren } from "react";
import { useOrganisationQuery, useOrganisationsQuery } from "../queryHooks";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
    },
  },
});

const QueryClientWrapper: React.FC<PropsWithChildren> = ({ children }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

beforeEach(() => {
  queryClient.clear();
});

describe("useOrganisationQuery", () => {
  it("should return organisation data", async () => {
    const queryHook = renderHook(
      () => useOrganisationQuery("e2f1d47c-a72b-431c-ad99-5e943d450f34"),
      { wrapper: QueryClientWrapper },
    );

    expect(queryHook.result.current.status).toBe("pending");
    expect(queryHook.result.current.data).toBeUndefined();
    expect(queryHook.result.current.error).toBeNull();

    await waitFor(() => queryHook.result.current.isLoading === true);
    expect(queryHook.result.current.isLoading).toBe(true);
    expect(queryHook.result.current.data).toBeUndefined();
    expect(queryHook.result.current.error).toBeNull();

    await waitFor(() => queryHook.result.current.isSuccess === true);
    expect(queryHook.result.current.isSuccess).toBe(true);
    expect(queryHook.result.current.data).toEqual({
      id: "e2f1d47c-a72b-431c-ad99-5e943d450f34",
      name: "Organisation 1",
      identifier_ODS_ODSCode: "ODS1",
      active: true,
      type: "Type A",
      endpoints: [],
      createdBy: "user1",
      createdDateTime: "2023-01-01T00:00:00Z",
      modifiedBy: "user2",
      modifiedDateTime: "2023-01-02T00:00:00Z",
    });

    // Check data is stored in query cache
    const cachedData = queryClient.getQueryData([
      "organisation",
      "e2f1d47c-a72b-431c-ad99-5e943d450f34",
    ]);
    expect(cachedData).toEqual({
      id: "e2f1d47c-a72b-431c-ad99-5e943d450f34",
      name: "Organisation 1",
      identifier_ODS_ODSCode: "ODS1",
      active: true,
      type: "Type A",
      endpoints: [],
      createdBy: "user1",
      createdDateTime: "2023-01-01T00:00:00Z",
      modifiedBy: "user2",
      modifiedDateTime: "2023-01-02T00:00:00Z",
    });
  });

  it("should handle error when organisation not found", async () => {
    const queryHook = renderHook(
      () => useOrganisationQuery("non-existent-id"),
      { wrapper: QueryClientWrapper },
    );

    expect(queryHook.result.current.status).toBe("pending");
    expect(queryHook.result.current.data).toBeUndefined();
    expect(queryHook.result.current.error).toBeNull();

    await waitFor(() => queryHook.result.current.isLoading === true);
    expect(queryHook.result.current.isLoading).toBe(true);
    expect(queryHook.result.current.data).toBeUndefined();
    expect(queryHook.result.current.error).toBeNull();

    await waitFor(() => queryHook.result.current.isError === true);
    expect(queryHook.result.current.isError).toBe(true);
    expect(queryHook.result.current.data).toBeUndefined();

    const error = queryHook.result.current.error as ResponseError;
    expect(error).toBeInstanceOf(ResponseError);

    expect(error.message).toBe(
      "Failed to fetch organisation data for ID: non-existent-id",
    );
    expect(error.statusCode).toBe(404);
    expect(error.headers).toEqual({
      "content-length": "34",
      "content-type": "application/json",
      "x-correlation-id": "test-correlation-id",
    });
    expect(error.correlationId).toBe("test-correlation-id");
  });
});

describe("useOrganisationsQuery", () => {
  it("should return list of organisations", async () => {
    const expectedResponse = [
      {
        id: "e2f1d47c-a72b-431c-ad99-5e943d450f34",
        name: "Organisation 1",
        identifier_ODS_ODSCode: "ODS1",
        active: true,
        type: "Type A",
        endpoints: [],
        createdBy: "user1",
        createdDateTime: "2023-01-01T00:00:00Z",
        modifiedBy: "user2",
        modifiedDateTime: "2023-01-02T00:00:00Z",
      },
      {
        id: "763fdc39-1e9f-4e3d-bb69-9d1e398d0fdc",
        name: "Organisation 2",
        identifier_ODS_ODSCode: "ODS2",
        active: true,
        type: "Type B",
        endpoints: [],
        createdBy: "user3",
        createdDateTime: "2023-01-03T00:00:00Z",
        modifiedBy: "user4",
        modifiedDateTime: "2023-01-04T00:00:00Z",
      },
    ];

    const queryHook = renderHook(() => useOrganisationsQuery(), {
      wrapper: QueryClientWrapper,
    });

    expect(queryHook.result.current.status).toBe("pending");
    expect(queryHook.result.current.data).toBeUndefined();
    expect(queryHook.result.current.error).toBeNull();

    await waitFor(() => queryHook.result.current.isLoading === true);
    expect(queryHook.result.current.isLoading).toBe(true);
    expect(queryHook.result.current.data).toBeUndefined();
    expect(queryHook.result.current.error).toBeNull();

    await waitFor(() => queryHook.result.current.isSuccess === true);
    expect(queryHook.result.current.isSuccess).toBe(true);
    expect(queryHook.result.current.data).toEqual(expectedResponse);

    // Check data is stored in query cache
    const cachedData = queryClient.getQueryData(["organisations"]);
    expect(cachedData).toEqual(expectedResponse);
  });

  it("should handle error when fetching organisations fails", async () => {
    // Override the server response to simulate an error
    server.use(
      http.get(
        "/api/organisations",
        () => {
          return HttpResponse.json(
            { error: "Failed to fetch organisations" },
            {
              status: 500,
              headers: { "X-Correlation-ID": "test-correlation-id" },
            },
          );
        },
        {
          once: true,
        },
      ),
    );

    const queryHook = renderHook(() => useOrganisationsQuery(), {
      wrapper: QueryClientWrapper,
    });
    expect(queryHook.result.current.status).toBe("pending");
    expect(queryHook.result.current.data).toBeUndefined();
    expect(queryHook.result.current.error).toBeNull();

    await waitFor(() => queryHook.result.current.isLoading === true);
    expect(queryHook.result.current.isLoading).toBe(true);
    expect(queryHook.result.current.data).toBeUndefined();
    expect(queryHook.result.current.error).toBeNull();

    await waitFor(() => queryHook.result.current.isError === true);
    expect(queryHook.result.current.isError).toBe(true);
    expect(queryHook.result.current.data).toBeUndefined();

    const error = queryHook.result.current.error as ResponseError;
    expect(error).toBeInstanceOf(ResponseError);
    expect(error.message).toBe("Failed to fetch organisations data");
    expect(error.statusCode).toBe(500);
    expect(error.headers).toEqual({
      "content-length": "41",
      "content-type": "application/json",
      "x-correlation-id": "test-correlation-id",
    });
    expect(error.correlationId).toBe("test-correlation-id");
  });
});
