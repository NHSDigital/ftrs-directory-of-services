import { routeTree } from "@/routeTree.gen.ts";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { render, waitFor } from "@testing-library/react";
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
          locationID: "location-2",
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading locations")).not.toBeInTheDocument(),
    );
  });
});
