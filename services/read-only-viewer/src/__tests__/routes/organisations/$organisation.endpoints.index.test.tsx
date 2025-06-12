import { routeTree } from "@/routeTree.gen";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { act, render, waitFor } from "@testing-library/react";

describe("Organisation Endpoints", () => {
  let router: ReturnType<typeof createRouter>;
  let app: ReturnType<typeof render>;

  beforeEach(async () => {
    router = createRouter({
      defaultPendingMinMs: 0,
      routeTree: routeTree,
    });

    app = render(<RouterProvider<typeof router> router={router} />);
  });

  it("should render the Endpoints page for an organisation", async () => {
    await act(() =>
      router.navigate({
        to: "/organisations/$organisationID/endpoints",
        params: { organisationID: "e2f1d47c-a72b-431c-ad99-5e943d450f34" },
      }),
    );

    await waitFor(() =>
      expect(
        app.getByText("Endpoints for Organisation 1", { selector: "h1" }),
      ).toBeInTheDocument(),
    );
    expect(
      app.getByText("This page has not yet been developed."),
    ).toBeInTheDocument();
  });
});
