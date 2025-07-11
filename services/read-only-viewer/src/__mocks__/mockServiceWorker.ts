import type { HealthcareService, Location, Organisation } from "@/utils/types";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

const organisations: Organisation[] = [
  {
    id: "e2f1d47c-a72b-431c-ad99-5e943d450f34",
    name: "Organisation 1",
    identifier_ODS_ODSCode: "ODS1",
    active: true,
    type: "Type A",
    endpoints: [],
    createdBy: "user1",
    createdDateTime: "2023-01-01T00:00:00Z",
    modifiedBy: "user2",
    modifiedDateTime: "2023-01-02T00:00:00Z",
  },
  {
    id: "763fdc39-1e9f-4e3d-bb69-9d1e398d0fdc",
    name: "Organisation 2",
    identifier_ODS_ODSCode: "ODS2",
    active: true,
    type: "Type B",
    endpoints: [],
    createdBy: "user3",
    createdDateTime: "2023-01-03T00:00:00Z",
    modifiedBy: "user4",
    modifiedDateTime: "2023-01-04T00:00:00Z",
  },
] as const;

const healthcareServices: HealthcareService[] = [
  {
    id: "healthcare-service-1",
    name: "Healthcare Service 1",
    type: "Type A",
    providedBy: "e2f1d47c-a72b-431c-ad99-5e943d450f34",
    active: true,
    createdBy: "user1",
    createdDateTime: "2023-01-01T00:00:00Z",
    modifiedBy: "user2",
    modifiedDateTime: "2023-01-02T00:00:00Z",
    location: "",
    telecom: {},
  },
  {
    id: "healthcare-service-2",
    name: "Healthcare Service 2",
    type: "Type B",
    providedBy: "763fdc39-1e9f-4e3d-bb69-9d1e398d0fdc",
    active: true,
    createdBy: "user3",
    createdDateTime: "2023-01-03T00:00:00Z",
    modifiedBy: "user4",
    modifiedDateTime: "2023-01-04T00:00:00Z",
    category: "",
    telecom: {
      email: "test@example.com",
      phone_public: "01234567890",
      website: "https://example.com",
    },
    openingTime: [
      {
        id: "opening-time-1",
        category: "availableTime",
        dayOfWeek: "mon",
        startTime: "09:00",
        endTime: "17:00",
        allDay: false,
      },
    ],
    location: "location-1",
  },
] as const;

const locations: Location[] = [
  {
    id: "l2f1d47c-a72b-431c-ad99-5e943d450f65",
    active: true,
    address: {
      street: "123 Main St",
      town: "Test Town",
      postcode: "AB12 3CD",
    },
    createdBy: "test_user",
    createdDateTime: "2023-10-01T00:00:00Z",
    managedByOrganisation: "e2f1d47c-a72b-431c-ad99-5e943d450f34",
    modifiedBy: "test_user",
    modifiedDateTime: "2023-10-01T00:00:00Z",
    name: "Test Location 1",
    positionGCS: { latitude: "51.5074", longitude: "-0.1278" },
    positionReferenceNumber_UPRN: 1234567890,
    positionReferenceNumber_UBRN: 9876543210,
    primaryAddress: true,
    partOf: "",
  },
  {
    id: "g6f1d47c-a72b-431c-ad99-5e943d450f777",
    active: true,
    address: {
      street: "123 Main St",
      town: "Test Town",
      postcode: "AB12 3CD",
    },
    createdBy: "test_user",
    createdDateTime: "2023-10-01T00:00:00Z",
    managedByOrganisation: "763fdc39-1e9f-4e3d-bb69-9d1e398d0fdc",
    modifiedBy: "test_user",
    modifiedDateTime: "2023-10-01T00:00:00Z",
    name: "Test Location 2",
    positionGCS: { latitude: "51.5074", longitude: "-0.1278" },
    positionReferenceNumber_UPRN: 1234567890,
    positionReferenceNumber_UBRN: 9876543210,
    primaryAddress: true,
    partOf: "",
  },
] as const;

export const StubData = {
  organisations: organisations,
  healthcareServices: healthcareServices,
  locations: locations,

  reset() {
    this.organisations = organisations;
    this.healthcareServices = healthcareServices;
    this.locations = locations;
  },
};

export const server = setupServer(
  http.get("/api/organisation", () => {
    return HttpResponse.json(organisations);
  }),
  http.get("/api/organisation/:id", (req) => {
    const { id } = req.params;
    const organisation = StubData.organisations.find((org) => org.id === id);
    if (!organisation) {
      return HttpResponse.json(
        { error: "Organisation not found" },
        { status: 404, headers: { "X-Correlation-ID": "test-correlation-id" } },
      );
    }

    return HttpResponse.json(organisation, {
      headers: { "X-Correlation-ID": "test-correlation-id" },
    });
  }),
  http.get("/api/healthcareService/", () => {
    return HttpResponse.json(healthcareServices);
  }),
  http.get("/api/healthcareService/:id", (req) => {
    const { id } = req.params;
    const healthcareService = healthcareServices.find(
      (service) => service.id === id,
    );
    if (!healthcareService) {
      return HttpResponse.json(
        { error: "Healthcare Service not found" },
        { status: 404, headers: { "X-Correlation-ID": "test-correlation-id" } },
      );
    }

    return HttpResponse.json(healthcareService, {
      headers: { "X-Correlation-ID": "test-correlation-id" },
    });
  }),
  http.get("/api/location/", () => {
    return HttpResponse.json(locations);
  }),
);
