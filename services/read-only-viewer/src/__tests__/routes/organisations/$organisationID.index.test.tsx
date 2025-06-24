import { StubData, server } from "@/__mocks__/mockServiceWorker";
import { routeTree } from "@/routeTree.gen";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { render, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { act } from "react";

describe("Organisation Details", () => {
  let router: ReturnType<typeof createRouter>;
  let app: ReturnType<typeof render>;

  beforeEach(async () => {
    router = createRouter({
      defaultPendingMinMs: 0,
      routeTree: routeTree,
    });

    app = render(<RouterProvider<typeof router> router={router} />);
  });

  it("renders organisation details correctly", async () => {
    StubData.organisations.push({
      id: "32200d9e-fa54-43d4-8cb1-514aac0113a1",
      name: "Organisation 1",
      identifier_ODS_ODSCode: "ODS1",
      active: true,
      type: "Type A",
      endpoints: [
        {
          id: "endpoint1",
          name: "Primary Endpoint",
          status: "active",
          connectionType: "REST",
          managedByOrganisation: "32200d9e-fa54-43d4-8cb1-514aac0113a1",
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
        to: "/organisations/$organisationID",
        params: {
          organisationID: "32200d9e-fa54-43d4-8cb1-514aac0113a1",
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading...")).not.toBeInTheDocument(),
    );

    const heading = app.getByText("Organisation 1", { selector: "h1" });
    expect(heading).toBeInTheDocument();

    const expectedDetails = [
      { key: "ID", value: "32200d9e-fa54-43d4-8cb1-514aac0113a1" },
      { key: "Name", value: "Organisation 1" },
      { key: "ODS Code", value: "ODS1" },
      { key: "Type", value: "Type A" },
      { key: "Active", value: "Yes" },
      { key: "Telecom", value: "None Provided" },
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

    const endpointDetailsSummary = app.getByText(
      "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
    );
    expect(endpointDetailsSummary).toBeInTheDocument();

    const endpointDetails = endpointDetailsSummary.closest("details")!;
    expect(endpointDetails).toBeInTheDocument();

    const tableHeadings = endpointDetails.querySelectorAll("th");
    expect(tableHeadings.length).toBe(5);
    expect(tableHeadings[0].textContent).toBe("Order");
    expect(tableHeadings[1].textContent).toBe("Status");
    expect(tableHeadings[2].textContent).toBe("Type");
    expect(tableHeadings[3].textContent).toBe("Address");
    expect(tableHeadings[4].textContent).toBe("Action");

    const tableRows = endpointDetails.querySelectorAll("tbody tr");
    expect(tableRows.length).toBe(1);

    const firstRowCells = tableRows[0].querySelectorAll("td");
    expect(firstRowCells.length).toBe(5);

    expect(firstRowCells[0].textContent).toBe("1");
    expect(firstRowCells[1].textContent).toBe("active");
    expect(firstRowCells[2].textContent).toBe("REST");
    expect(firstRowCells[3].textContent).toBe(
      "https://api.organisation1.example.com",
    );

    const actionLink = firstRowCells[4].querySelector("a");
    expect(actionLink).toBeInTheDocument();
    expect(actionLink?.textContent).toBe("View");
    expect(actionLink).toHaveAttribute(
      "href",
      "/organisations/32200d9e-fa54-43d4-8cb1-514aac0113a1/endpoints/endpoint1",
    );
  });

  it("handles no endpoints gracefully", async () => {
    StubData.organisations.push({
      id: "d8a60e97-d77d-4331-85b3-5e378f83f9cd",
      name: "Organisation 2",
      identifier_ODS_ODSCode: "ODS2",
      active: true,
      type: "Type B",
      endpoints: [],
      createdBy: "user3",
      createdDateTime: "2023-01-03T00:00:00Z",
      modifiedBy: "user4",
      modifiedDateTime: "2023-01-04T00:00:00Z",
    });

    await act(() =>
      router.navigate({
        to: "/organisations/$organisationID",
        params: {
          organisationID: "d8a60e97-d77d-4331-85b3-5e378f83f9cd",
        },
      }),
    );

    await waitFor(() =>
      expect(app.queryByText("Loading...")).not.toBeInTheDocument(),
    );

    const heading = app.getByText("Organisation 2", { selector: "h1" });
    expect(heading).toBeInTheDocument();

    const noEndpointsMessage = app.getByText(
      "No endpoints available for this organisation.",
    );
    expect(noEndpointsMessage).toBeInTheDocument();
  });

  it("handles organisation not found", async () => {
    await act(() =>
      router.navigate({
        to: "/organisations/$organisationID",
        params: {
          organisationID: "non-existent-id",
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
        to: "/organisations/$organisationID",
        params: {
          organisationID: "32200d9e-fa54-43d4-8cb1-514aac0113a1",
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
