import { useOrganisationQuery } from '@/hooks/queryHooks';
import { createFileRoute, Link } from '@tanstack/react-router'
import { Breadcrumb } from 'nhsuk-react-components'

export const Route = createFileRoute('/organisations/$organisationID/endpoints/$endpointID')({
  component: RouteComponent,
})

function RouteComponent() {
  const { organisationID, endpointID } = Route.useParams();
  const { data: organisation } = useOrganisationQuery(organisationID);

  return (
    <>
      <Breadcrumb className="nhsuk-u-margin-bottom-5">
        <Breadcrumb.Back
          asElement={Link}
          to="/organisations/$organisationID/endpoints"
          // @ts-expect-error - TanStack Router expects params to be an object
          params={{ organisationID }}
        />
        <Breadcrumb.Item
          asElement={Link}
          to="/"
          className="nhsuk-link--no-visited-state"
        >
          Home
        </Breadcrumb.Item>

        <Breadcrumb.Item
          asElement={Link}
          to="/organisations/$organisationID"
          // @ts-expect-error - TanStack Router expects params to be an object
          params={{ organisationID }}
          className="nhsuk-link--no-visited-state"
        >
          {organisation?.name || 'Organisation'}
        </Breadcrumb.Item>
        <Breadcrumb.Item
          asElement={Link}
          to="/organisations/$organisationID"
          // @ts-expect-error - TanStack Router expects params to be an object
          params={{ organisationID }}
          className="nhsuk-link--no-visited-state"
        >
          Endpoints
        </Breadcrumb.Item>
        <Breadcrumb.Item
          asElement={Link}
          to="/organisations/$organisationID/endpoints/$endpointID"
          // @ts-expect-error - TanStack Router expects params to be an object
          params={{ organisationID, endpointID }}
          className="nhsuk-link--no-visited-state"
        >
          {endpointID}
        </Breadcrumb.Item>

      </Breadcrumb>
    </>
  )
}
