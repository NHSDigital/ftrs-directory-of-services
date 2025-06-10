import { server } from "@/__mocks__/mockServiceWorker";
import { routeTree } from "@/routeTree.gen";
import { createRouter } from "@tanstack/react-router";
import { RouterProvider } from "@tanstack/react-router";
import { act, render, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

describe("Organisations Index Route", () => {
  let router: ReturnType<typeof createRouter>;
  let app: ReturnType<typeof render>;

  beforeEach(async () => {
    router = createRouter({
      defaultPendingMinMs: 0,
      routeTree: routeTree,
    });

    app = render(<RouterProvider<typeof router> router={router} />);
  });

  it("should render the Organisations page", async () => {
    await act(() => router.navigate({ to: "/organisations" }));
    const loadingText = app.queryByText("Loading organisations...");
    expect(loadingText).toBeInTheDocument();

    await waitFor(() =>
      expect(
        app.queryByText("Loading organisations..."),
      ).not.toBeInTheDocument(),
    );

    const heading = app.getByText("Organisations", { selector: "h1" });
    expect(heading).toBeInTheDocument();

    const table = app.container.querySelector("table.nhsuk-table")!;
    expect(table).toBeInTheDocument();

    const headings = table.querySelectorAll("th");
    expect(headings.length).toBe(2);
    expect(headings[0].textContent).toBe("Name");
    expect(headings[1].textContent).toBe("ODS Code");

    const rows = table.querySelectorAll("tbody tr");
    expect(rows.length).toBe(2);

    const firstRowCells = rows[0].querySelectorAll("td");
    expect(firstRowCells.length).toBe(2);

    expect(firstRowCells[0].textContent).toBe("Organisation 1");
    expect(firstRowCells[0].querySelector("a")).toHaveAttribute(
      "href",
      "/organisations/e2f1d47c-a72b-431c-ad99-5e943d450f34",
    );
    expect(firstRowCells[1].textContent).toBe("ODS1");

    const secondRowCells = rows[1].querySelectorAll("td");
    expect(secondRowCells.length).toBe(2);
    expect(secondRowCells[0].textContent).toBe("Organisation 2");
    expect(secondRowCells[0].querySelector("a")).toHaveAttribute(
      "href",
      "/organisations/763fdc39-1e9f-4e3d-bb69-9d1e398d0fdc",
    );
    expect(secondRowCells[1].textContent).toBe("ODS2");
  });

  it("should handle errors gracefully", async () => {
    server.use(
      http.get(
        "/api/organisations",
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
    await act(() => router.navigate({ to: "/organisations" }));

    await waitFor(() => {
      expect(
        app.queryByText("Loading organisations..."),
      ).not.toBeInTheDocument();
    });

    expect(app.getByText("Something went wrong")).toBeInTheDocument();
    expect(
      app.getByText(
        "There was an error while processing your request. Please try again later.",
      ),
    ).toBeInTheDocument();

    expect(app.getByText("test-correlation-id")).toBeInTheDocument();
    expect(app.getByText("500")).toBeInTheDocument();
    expect(
      app.getByText("Failed to fetch organisations data"),
    ).toBeInTheDocument();
  });
});
