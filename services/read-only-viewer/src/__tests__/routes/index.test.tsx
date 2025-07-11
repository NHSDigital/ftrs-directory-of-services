import { routeTree } from "@/routeTree.gen";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { act, render } from "@testing-library/react";

describe("Index Route", () => {
  let router: ReturnType<typeof createRouter>;
  let app: ReturnType<typeof render>;

  beforeEach(async () => {
    router = createRouter({
      defaultPendingMinMs: 0,
      routeTree: routeTree,
    });
    app = render(<RouterProvider<typeof router> router={router} />);

    await act(() => router.navigate({ to: "/" }));
  });

  it("should render the HomePage component", () => {
    const { getByText } = app;

    expect(getByText("Read Only Viewer")).toBeInTheDocument();
    expect(getByText("Available Entity Types")).toBeInTheDocument();

    const organisationsCardLink = getByText("Organisations");
    expect(organisationsCardLink).toBeInTheDocument();
    expect(organisationsCardLink.closest("a")).toHaveAttribute(
      "href",
      "/organisations",
    );

    const healthcareServicesCardLink = getByText("Healthcare Services");
    expect(healthcareServicesCardLink).toBeInTheDocument();
    expect(healthcareServicesCardLink.closest("a")).toHaveAttribute(
      "href",
      "/healthcare-services",
    );

    const locationsCardLink = getByText("Locations");
    expect(locationsCardLink).toBeInTheDocument();
    expect(locationsCardLink.closest("a")).toHaveAttribute(
      "href",
      "/locations",
    );
  });
});
