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

    const heading = app.getByText("Locations", { selector: "h1" });
    expect(heading).toBeInTheDocument();

    const table = app.container.querySelector("table.nhsuk-table")!;
    expect(table).toBeInTheDocument();

    const headings = table.querySelectorAll("th");
    expect(headings.length).toBe(3);
    expect(headings[0].textContent).toBe("Street");
    expect(headings[1].textContent).toBe("Town");
    expect(headings[2].textContent).toBe("Postcode");

    const rows = table.querySelectorAll("tbody tr");
    expect(rows.length).toBe(2);

    const firstRowCells = rows[0].querySelectorAll("td");
    expect(firstRowCells.length).toBe(3);

    expect(firstRowCells[0].textContent).toBe("123 Main St");
    expect(firstRowCells[0].querySelector("a")).toHaveAttribute(
      "href",
      "/locations/l2f1d47c-a72b-431c-ad99-5e943d450f65",
    );
    expect(firstRowCells[1].textContent).toBe("Test Town");
    expect(firstRowCells[2].textContent).toBe("AB12 3CD");

    const secondRowCells = rows[1].querySelectorAll("td");
    expect(secondRowCells.length).toBe(3);
    expect(secondRowCells[0].textContent).toBe("321 Secondary St, Borough");
    expect(secondRowCells[0].querySelector("a")).toHaveAttribute(
      "href",
      "/locations/g6f1d47c-a72b-431c-ad99-5e943d450f777",
    );
    expect(secondRowCells[1].textContent).toBe("Second Town");
    expect(secondRowCells[2].textContent).toBe("YZ12 3VX");
  });

  it("should handle errors gracefully", async () => {
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
