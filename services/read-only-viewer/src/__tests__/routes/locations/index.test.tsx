import { server } from "@/__mocks__/mockServiceWorker";
import { routeTree } from "@/routeTree.gen";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { act, render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

describe("Location Index Route", () => {
  let router: ReturnType<typeof createRouter>;
  let app: ReturnType<typeof render>;

  beforeEach(async () => {
    router = createRouter({
      defaultPendingMinMs: 0,
      routeTree: routeTree,
    });

    app = render(<RouterProvider<typeof router> router={router} />);
  });

  it("should render locations page with data", async () => {
    await router.navigate({ to: "/locations" });

    // Check loading state
    expect(screen.getByText("Loading locations...")).toBeInTheDocument();

    // Wait for data to load
    await waitFor(() => {
      expect(
        screen.queryByText("Loading locations..."),
      ).not.toBeInTheDocument();
    });

    // Check table headers
    expect(screen.getByText("Street")).toBeInTheDocument();
    expect(screen.getByText("Town")).toBeInTheDocument();
    expect(screen.getByText("Postcode")).toBeInTheDocument();

    // Check data rows
    expect(screen.getByText("123 Main St")).toBeInTheDocument();
    expect(screen.getByText("Test Town")).toBeInTheDocument();
    expect(screen.getByText("AB12 3CD")).toBeInTheDocument();

    expect(screen.getByText("321 Secondary St, Borough")).toBeInTheDocument();
    expect(screen.getByText("Second Town")).toBeInTheDocument();
    expect(screen.getByText("YZ12 3VX")).toBeInTheDocument();
  });

  it("should handle error state", async () => {
    server.use(
      http.get(
        "/api/location",
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
    await act(() => router.navigate({ to: "/locations" }));

    await waitFor(() => {
      expect(
        screen.queryByText("Loading locations..."),
      ).not.toBeInTheDocument();
    });

    // Check an error message
    expect(app.getByText("Something went wrong")).toBeInTheDocument();
    expect(
      app.getByText(
        "There was an error while processing your request. Please try again later.",
      ),
    ).toBeInTheDocument();

    expect(app.getByText("test-correlation-id")).toBeInTheDocument();
    expect(app.getByText("500")).toBeInTheDocument();
  });

  it("should handle empty data state", async () => {
    server.use(
      http.get("/api/location", () => {
        return HttpResponse.json([]);
      }),
    );

    await router.navigate({ to: "/locations" });

    await waitFor(() => {
      expect(
        screen.queryByText("Loading locations..."),
      ).not.toBeInTheDocument();
    });

    // Verify that the table is not rendered when there's no data
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });
});
