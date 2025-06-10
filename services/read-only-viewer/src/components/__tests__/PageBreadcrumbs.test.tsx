import { createRootRoute, createRouter } from "@tanstack/react-router";
import { RouterProvider } from "@tanstack/react-router";
import { render } from "@testing-library/react";
import { act } from "react";
import PageBreadcrumbs from "../PageBreadcrumbs";

describe("PageBreadcrumbs", () => {
  const rootRoute = createRootRoute();

  it("renders breadcrumbs with correct links", async () => {
    const backToHref = "/section";
    const items = [
      { label: "Home", to: "/" },
      { label: "Pages", to: "/pages" },
      { label: "Page by ID", to: "/pages/$pageID", params: { pageID: "123" } },
    ];

    const router = createRouter({
      routeTree: rootRoute,
      defaultComponent: () => (
        <PageBreadcrumbs backTo={backToHref} items={items} />
      ),
    });

    const { container } = await act(() => {
      return render(<RouterProvider router={router} />);
    });

    const backLink = container.querySelector("a.nhsuk-breadcrumb__backlink");
    expect(backLink).toBeInTheDocument();
    expect(backLink?.getAttribute("href")).toBe(backToHref);

    const breadcrumbItems = container.querySelectorAll(
      "li.nhsuk-breadcrumb__item",
    );
    expect(breadcrumbItems.length).toBe(items.length);

    const homeLink = breadcrumbItems[0].querySelector(
      "a.nhsuk-breadcrumb__link",
    );
    expect(homeLink).toBeInTheDocument();
    expect(homeLink?.getAttribute("href")).toBe(items[0].to);
    expect(homeLink?.textContent).toBe(items[0].label);

    const pagesLink = breadcrumbItems[1].querySelector(
      "a.nhsuk-breadcrumb__link",
    );
    expect(pagesLink).toBeInTheDocument();
    expect(pagesLink?.getAttribute("href")).toBe(items[1].to);
    expect(pagesLink?.textContent).toBe(items[1].label);

    const pageByIdLink = breadcrumbItems[2].querySelector(
      "a.nhsuk-breadcrumb__link",
    );
    expect(pageByIdLink).toBeInTheDocument();
    expect(pageByIdLink?.getAttribute("href")).toBe("/pages/123");
    expect(pageByIdLink?.textContent).toBe(items[2].label);
  });
});
