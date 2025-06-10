import { http, HttpResponse } from 'msw'
import type { Organisation } from "@/utils/types";
import {setupServer} from "msw/node";


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
    modifiedDateTime: "2023-01-02T00:00:00Z"
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
    modifiedDateTime: "2023-01-04T00:00:00Z"
  }
] as const;

export const StubData = {
  organisations: organisations,

  reset() {
    this.organisations = organisations;
  }
};


export const server = setupServer(
  http.get('/api/organisations', () => {
    return HttpResponse.json(organisations)
  }),
  http.get('/api/organisations/:id', (req) => {
    const { id } = req.params
    const organisation = StubData.organisations.find(org => org.id === id)
    if (!organisation) {
      return HttpResponse.json({ error: 'Organisation not found' }, { status: 404, headers: {'X-Correlation-ID': 'test-correlation-id'} })
    }

    return HttpResponse.json(organisation, {headers: {'X-Correlation-ID': 'test-correlation-id'}})
  })
);
