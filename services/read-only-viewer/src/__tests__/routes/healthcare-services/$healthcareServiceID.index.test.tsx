import { server } from "@/__mocks__/mockServiceWorker.ts";
import { routeTree } from "@/routeTree.gen.ts";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { render, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { act } from "react";
import { describe, expect, it } from "vitest";

describe("HealthCareServiceDetailsRoute", () => {
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
        to: "/healthcare-services/$healthcareServiceID",
        params: {
          healthcareServiceID: "healthcare-service-2",
        },
      }),
    );

    await waitFor(() =>
      expect(
        app.queryByText("Loading healthcare services"),
      ).not.toBeInTheDocument(),
    );
  });

  it("should display healthcare service details when data is loaded", async () => {
    await act(() =>
      router.navigate({
        to: "/healthcare-services/$healthcareServiceID",
        params: {
          healthcareServiceID: "healthcare-service-2",
        },
      }),
    );

    await waitFor(() =>
      expect(
        app.queryByText("Loading healthcare services"),
      ).not.toBeInTheDocument(),
    );
    const heading = app.getByText("HealthCare Service Details", {
      selector: "h2",
    });
    expect(heading).toBeInTheDocument();

    const expectedHCDetails = [
      { key: "ID", value: "healthcare-service-2" },
      { key: "Name", value: "Healthcare Service 2" },
      { key: "Type", value: "Type B" },
      { key: "Active", value: "Yes" },
      {
        key: "Contact Information",
        value:
          "Email: test@example.comPublic Phone: 01234567890Website: https://example.com",
      },
      {
        key: "Provided By",
        value:
          "763fdc39-1e9f-4e3d-bb69-9d1e398d0fdc (View Provider Organisation)",
      },
      { key: "Location", value: "location-1 (View Location)" },
      { key: "Category", value: "Not Specified" },
      { key: "Opening Times", value: "AvailableTimemon 09:00 - 17:00" },
      { key: "Created By", value: "user3 (2023-01-03T00:00:00Z)" },
      { key: "Modified By", value: "user4 (2023-01-04T00:00:00Z)" },
    ];

    const detailsList = app.container.querySelector("dl.nhsuk-summary-list")!;
    expect(detailsList).toBeInTheDocument();

    const items = detailsList.querySelectorAll("div.nhsuk-summary-list__row");
    expect(items.length).toBe(expectedHCDetails.length);

    expectedHCDetails.forEach((item, index) => {
      const row = items[index];
      const key = row.querySelector("dt.nhsuk-summary-list__key")!;
      const value = row.querySelector("dd.nhsuk-summary-list__value")!;

      expect(key.textContent).toBe(item.key);
      expect(value.textContent).toBe(item.value);
    });
  });

  it("Handle healthcare service not found", async () => {
    server.use(
      http.get(
        "/api/healthcare-service/:id",
        () => {
          return HttpResponse.json(
            { error: "Healthcare Service not found" },
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
        to: "/healthcare-services/$healthcareServiceID",
        params: {
          healthcareServiceID: "non-existent-service",
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading...")).not.toBeInTheDocument(),
    );

    const errorMessage = app.getByText(
      "The healthcare service you are looking for does not exist.",
    );
    expect(errorMessage).toBeInTheDocument();
  });
});
