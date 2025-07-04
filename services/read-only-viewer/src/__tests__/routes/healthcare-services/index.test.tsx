import { server } from "@/__mocks__/mockServiceWorker";
import { routeTree } from "@/routeTree.gen";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { act, render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

describe("Healthcare Service Index Route", () => {
  let router: ReturnType<typeof createRouter>;
  let app: ReturnType<typeof render>;

  beforeEach(async () => {
    router = createRouter({
      defaultPendingMinMs: 0,
      routeTree: routeTree,
    });

    app = render(<RouterProvider<typeof router> router={router} />);
  });

  it("should render healthcare services page with data", async () => {
    await router.navigate({ to: "/healthcare-services" });

    // Check loading state
    expect(
      screen.getByText("Loading healthcare services..."),
    ).toBeInTheDocument();

    // Wait for data to load
    await waitFor(() => {
      expect(
        screen.queryByText("Loading healthcare services..."),
      ).not.toBeInTheDocument();
    });

    // Check table headers
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Type")).toBeInTheDocument();

    // Check data rows
    expect(screen.getByText("Healthcare Service 1")).toBeInTheDocument();
    expect(screen.getByText("Healthcare Service 2")).toBeInTheDocument();
    expect(screen.getByText("Type A")).toBeInTheDocument();
    expect(screen.getByText("Type B")).toBeInTheDocument();
  });

  it("should handle error state", async () => {
    server.use(
      http.get(
        "/api/healthcareService",
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
    await act(() => router.navigate({ to: "/healthcare-services" }));

    await waitFor(() => {
      expect(
        screen.queryByText("Loading health care service..."),
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
      http.get("/api/healthcareService", () => {
        return HttpResponse.json([]);
      }),
    );

    await router.navigate({ to: "/healthcare-services" });

    await waitFor(() => {
      expect(
        screen.queryByText("Loading health care service..."),
      ).not.toBeInTheDocument();
    });

    // Verify that the table is not rendered when there's no data
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });
});
