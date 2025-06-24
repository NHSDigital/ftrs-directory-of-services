import { StubData } from "@/__mocks__/mockServiceWorker";
import { routeTree } from "@/routeTree.gen";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { act, render, waitFor } from "@testing-library/react";

describe("Organisation Endpoint Details", () => {
  let router: ReturnType<typeof createRouter>;
  let app: ReturnType<typeof render>;

  beforeEach(async () => {
    router = createRouter({
      defaultPendingMinMs: 0,
      routeTree: routeTree,
    });

    app = render(<RouterProvider<typeof router> router={router} />);
  });

  it("should render the Endpoint Details page for an organisation", async () => {
    StubData.organisations.push({
      id: "9521a4ee-d0e6-4cca-9d8c-123bfbf43123",
      name: "Organisation 1",
      identifier_ODS_ODSCode: "ODS1",
      active: true,
      type: "Type A",
      endpoints: [
        {
          id: "db752ac7-d260-44c0-a36d-bd8939b3343e",
          name: "Primary Endpoint",
          status: "active",
          connectionType: "REST",
          managedByOrganisation: "9521a4ee-d0e6-4cca-9d8c-123bfbf43123",
          format: "JSON",
          payloadType:
            "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
          isCompressionEnabled: false,
          address: "https://api.organisation1.example.com",
          order: 1,
          description: "Primary endpoint for Organisation 1",
          createdBy: "user1",
          createdDateTime: "2023-01-01T00:00:00Z",
          modifiedBy: "user2",
          modifiedDateTime: "2023-01-02T00:00:00Z",
        },
      ],
      createdBy: "user1",
      createdDateTime: "2023-01-01T00:00:00Z",
      modifiedBy: "user2",
      modifiedDateTime: "2023-01-02T00:00:00Z",
    });

    await act(() =>
      router.navigate({
        to: "/organisations/$organisationID/endpoints/$endpointID",
        params: {
          organisationID: "9521a4ee-d0e6-4cca-9d8c-123bfbf43123",
          endpointID: "db752ac7-d260-44c0-a36d-bd8939b3343e",
        },
      }),
    );

    await waitFor(() =>
      expect(
        app.getByText("Endpoint: db752ac7-d260-44c0-a36d-bd8939b3343e", {
          selector: "h1",
        }),
      ).toBeInTheDocument(),
    );
    expect(
      app.getByText("This page has not yet been developed."),
    ).toBeInTheDocument();
  });
});
