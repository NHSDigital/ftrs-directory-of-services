import { StubData, server } from "@/__mocks__/mockServiceWorker";
import { routeTree } from "@/routeTree.gen";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { act, render, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";

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
      id: "32200d9e-fa54-43d4-8cb1-514aac0113a1",
      identifier_ODS_ODSCode: "12345",
      active: true,
      createdBy: "ROBOT",
      createdDateTime: "2023-10-01T00:00:00Z",
      modifiedBy: "ROBOT",
      modifiedDateTime: "2023-10-01T00:00:00Z",
      name: "Test Organisation",
      telecom: undefined,
      type: "GP Practice",
      endpoints: [
        {
          id: "d5a852ef-12c7-4014-b398-661716a63027",
          address: "https://example.com/endpoint",
          connectionType: "itk",
          description: "Primary",
          payloadMimeType: "application/fhir",
          identifier_oldDoS_id: 67890,
          isCompressionEnabled: true,
          managedByOrganisation: "32200d9e-fa54-43d4-8cb1-514aac0113a1",
          createdBy: "user1",
          createdDateTime: "2023-01-01T00:00:00Z",
          modifiedBy: "user2",
          modifiedDateTime: "2023-01-02T00:00:00Z",
          name: "Test Endpoint",
          order: 1,
          payloadType:
            "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
          service: undefined,
          status: "active",
        },
      ],
    });

    await act(() =>
      router.navigate({
        to: "/organisations/$organisationID/endpoint/$endpointID",
        params: {
          organisationID: "32200d9e-fa54-43d4-8cb1-514aac0113a1",
          endpointID: "d5a852ef-12c7-4014-b398-661716a63027",
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading...")).not.toBeInTheDocument(),
    );

    const heading = app.getByText(
      "Endpoint: d5a852ef-12c7-4014-b398-661716a63027",
      { selector: "h1" },
    );
    expect(heading).toBeInTheDocument();

    const expectedDetails = [
      { key: "ID", value: "d5a852ef-12c7-4014-b398-661716a63027" },
      { key: "Identifier Old DOS ID", value: "67890" },
      { key: "Status", value: "active" },
      { key: "Connection Type", value: "itk" },
      { key: "Name", value: "Test Endpoint" },
      { key: "Description", value: "Primary" },
      {
        key: "Payload Type",
        value:
          "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
      },
      { key: "Address", value: "https://example.com/endpoint" },
      { key: "Order", value: "1" },
      { key: "Is Compression Enabled", value: "true" },
      { key: "Payload Mime Type", value: "application/fhir" },
      { key: "Created By", value: "user1 (2023-01-01T00:00:00Z)" },
      { key: "Modified By", value: "user2 (2023-01-02T00:00:00Z)" },
    ];

    const detailsList = app.container.querySelector("dl.nhsuk-summary-list")!;
    expect(detailsList).toBeInTheDocument();

    const items = detailsList.querySelectorAll("div.nhsuk-summary-list__row");
    expect(items.length).toBe(expectedDetails.length);

    expectedDetails.forEach((item, index) => {
      const row = items[index];
      const key = row.querySelector("dt.nhsuk-summary-list__key")!;
      const value = row.querySelector("dd.nhsuk-summary-list__value")!;

      expect(key.textContent).toBe(item.key);
      expect(value.textContent).toBe(item.value);
    });
  });

  it("handles null endpoint gracefully", async () => {
    await act(() =>
      router.navigate({
        to: "/organisations/$organisationID/endpoint/$endpointID",
        params: {
          organisationID: "32200d9e-fa54-43d4-8cb1-514aac0113a1",
          endpointID: "non-existent-id",
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading...")).not.toBeInTheDocument(),
    );

    const notFoundTitle = app.getByText("Endpoint");
    expect(notFoundTitle).toBeInTheDocument();

    const notFoundMessage = app.getByText(
      "No endpoint of id: non-existent-id retrieved for this organisation.",
    );

    expect(notFoundMessage).toBeInTheDocument();
  });

  it("handles organisation not found", async () => {
    await act(() =>
      router.navigate({
        to: "/organisations/$organisationID/endpoint/$endpointID",
        params: {
          organisationID: "non-existent-id",
          endpointID: "d5a852ef-12c7-4014-b398-661716a63027",
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading...")).not.toBeInTheDocument(),
    );

    const notFoundTitle = app.getByText("Organisation not found");
    expect(notFoundTitle).toBeInTheDocument();

    const notFoundMessage = app.getByText(
      "The organisation you are looking for does not exist.",
    );
    expect(notFoundMessage).toBeInTheDocument();
    const backLink = app.getByText("Back to Organisations");
    expect(backLink).toBeInTheDocument();
  });

  it("handles server error gracefully", async () => {
    server.use(
      http.get(
        "/api/organisation/32200d9e-fa54-43d4-8cb1-514aac0113a1",
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

    await act(() =>
      router.navigate({
        to: "/organisations/$organisationID/endpoint/$endpointID",
        params: {
          organisationID: "32200d9e-fa54-43d4-8cb1-514aac0113a1",
          endpointID: "d5a852ef-12c7-4014-b398-661716a63027",
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading...")).not.toBeInTheDocument(),
    );

    const errorTitle = app.getByText("Something went wrong");
    expect(errorTitle).toBeInTheDocument();

    const errorMessage = app.getByText(
      "There was an error while processing your request. Please try again later.",
    );
    expect(errorMessage).toBeInTheDocument();

    const correlationId = app.getByText("test-correlation-id");
    expect(correlationId).toBeInTheDocument();

    const statusCode = app.getByText("500");
    expect(statusCode).toBeInTheDocument();

    const apiError = app.getByText(
      "Failed to fetch organisation data for ID: 32200d9e-fa54-43d4-8cb1-514aac0113a1",
    );
    expect(apiError).toBeInTheDocument();
  });
});
