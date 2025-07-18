import { StubData, server } from "@/__mocks__/mockServiceWorker";
import { routeTree } from "@/routeTree.gen.ts";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { render, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { act } from "react";
import { describe, expect, it } from "vitest";

describe("LocationDetailsRoute", () => {
  let router: ReturnType<typeof createRouter>;
  let app: ReturnType<typeof render>;

  beforeEach(async () => {
    router = createRouter({
      defaultPendingMinMs: 0,
      routeTree: routeTree,
    });

    app = render(<RouterProvider<typeof router> router={router} />);
  });

  it("should display loading state initially", async () => {
    await act(() =>
      router.navigate({
        to: "/locations/$locationID",
        params: {
          locationID: StubData.locations[0].id,
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading locations")).not.toBeInTheDocument(),
    );
  });

  it("should display location details when data is loaded", async () => {
    await act(() =>
      router.navigate({
        to: "/locations/$locationID",
        params: {
          locationID: StubData.locations[0].id,
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading locations")).not.toBeInTheDocument(),
    );
    const heading = app.getByText("Location Details", {
      selector: "h2",
    });
    expect(heading).toBeInTheDocument();

    const expectedLocationDetails = [
      { key: "ID", value: "l2f1d47c-a72b-431c-ad99-5e943d450f65" },
      { key: "Name", value: "Test Location 1" },
      { key: "Active", value: "Yes" },
      {
        key: "Address",
        value: "Street: 123 Main StTown: Test TownPostcode: AB12 3CD",
      },
      {
        key: "Managing Organisation",
        value:
          "e2f1d47c-a72b-431c-ad99-5e943d450f34 (View Managing Organisation)",
      },
      { key: "PositionGCS", value: "latitude: 51.5074longitude: -0.1278" },
      { key: "Position Reference Number UPRN", value: "1234567890" },
      { key: "Position Reference Number UBRN", value: "9876543210" },
      { key: "Primary Address", value: "Yes" },
      { key: "Part Of", value: "" },
      { key: "Created By", value: "test_user (2023-10-01T00:00:00Z)" },
      { key: "Modified By", value: "test_user (2023-10-01T00:00:00Z)" },
    ];

    const detailsList = app.container.querySelector("dl.nhsuk-summary-list")!;
    expect(detailsList).toBeInTheDocument();

    const items = detailsList.querySelectorAll("div.nhsuk-summary-list__row");
    expect(items.length).toBe(expectedLocationDetails.length);

    expectedLocationDetails.forEach((item, index) => {
      const row = items[index];
      const key = row.querySelector("dt.nhsuk-summary-list__key")!;
      const value = row.querySelector("dd.nhsuk-summary-list__value")!;

      expect(key.textContent).toBe(item.key);
      expect(value.textContent).toBe(item.value);
    });
  });

  it("Handle location not found", async () => {
    server.use(
      http.get(
        "/api/location/:id",
        () => {
          return HttpResponse.json(
            { error: "Location not found" },
            {
              status: 404,
              headers: { "X-Correlation-ID": "test-correlation-id" },
            },
          );
        },
        {
          once: true,
        },
      ),
    );

    await act(() =>
      router.navigate({
        to: "/locations/$locationID",
        params: {
          locationID: "non-existent-location",
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading...")).not.toBeInTheDocument(),
    );

    const errorMessage = app.getByText(
      "The location you are looking for does not exist.",
    );
    expect(errorMessage).toBeInTheDocument();
  });

  it("handles server error gracefully", async () => {
    server.use(
      http.get(
        "/api/location/l2f1d47c-a72b-431c-ad99-5e943d450f65",
        () => {
          return HttpResponse.json(
            { error: "Internal Server Error" },
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

    await act(() =>
      router.navigate({
        to: "/locations/$locationID",
        params: {
          locationID: "l2f1d47c-a72b-431c-ad99-5e943d450f65",
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading...")).not.toBeInTheDocument(),
    );

    const errorTitle = app.getByText("Something went wrong");
    expect(errorTitle).toBeInTheDocument();

    const errorMessage = app.getByText(
      "There was an error while processing your request. Please try again later.",
    );
    expect(errorMessage).toBeInTheDocument();

    const correlationId = app.getByText("test-correlation-id");
    expect(correlationId).toBeInTheDocument();

    const statusCode = app.getByText("500");
    expect(statusCode).toBeInTheDocument();

    const apiError = app.getByText(
      "Failed to fetch location data for ID: l2f1d47c-a72b-431c-ad99-5e943d450f65",
    );
    expect(apiError).toBeInTheDocument();
  });
});
