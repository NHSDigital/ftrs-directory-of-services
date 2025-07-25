import ContactInformation from "@/components/ContactInformation";
import KeyValueTable from "@/components/KeyValueTable.tsx";
import OpeningTimes from "@/components/OpeningTimes";
import PageBreadcrumbs from "@/components/PageBreadcrumbs.tsx";
import RequestErrorDetails from "@/components/RequestErrorDetails.tsx";
import { useHealthcareServiceQuery } from "@/hooks/queryHooks.ts";
import type { ResponseError } from "@/utils/errors.ts";
import type { HealthcareService } from "@/utils/types.ts";
import { Link, createFileRoute } from "@tanstack/react-router";
import { ActionLink, Card } from "nhsuk-react-components";

export const Route = createFileRoute(
  "/healthcare-services/$healthcareServiceID/",
)({
  component: HealthCareServiceDetailsRoute,
  head: () => ({
    meta: [{ title: "Healthcare Service Details - FtRS Read Only Viewer" }],
  }),
});

const HealthCareServiceOverview: React.FC<{
  healthcareService: HealthcareService;
}> = ({ healthcareService }) => {
  return (
    <Card className="nhsuk-u-padding-5">
      <h2 className="nhsuk-heading-m">HealthCare Service Details</h2>
      <KeyValueTable
        items={[
          { key: "ID", value: healthcareService.id },
          { key: "Name", value: healthcareService.name },
          { key: "Type", value: healthcareService.type },
          { key: "Active", value: healthcareService.active ? "Yes" : "No" },
          {
            key: "Contact Information",
            value: <ContactInformation telecom={healthcareService.telecom} />,
          },
          {
            key: "Provided By",
            value: healthcareService.providedBy ? (
              <Link
                to="/organisations/$organisationID"
                params={{ organisationID: healthcareService.providedBy }}
                className="nhsuk-link nhsuk-link--no-visited-state"
              >
                {healthcareService.providedBy} (View Provider Organisation)
              </Link>
            ) : (
              "Not Specified"
            ),
          },
          {
            key: "Location",
            value: healthcareService.location ? (
              <Link
                to="/locations/$locationID"
                params={{ locationID: healthcareService.location }}
                className="nhsuk-link nhsuk-link--no-visited-state"
              >
                {healthcareService.location} (View Location)
              </Link>
            ) : (
              "Not Specified"
            ),
          },
          {
            key: "Category",
            value: healthcareService.category || "Not Specified",
          },
          {
            key: "Opening Times",
            value: healthcareService.openingTime?.length ? (
              <OpeningTimes openingTime={healthcareService.openingTime} />
            ) : (
              "Not Specified"
            ),
          },
          {
            key: "Created By",
            value: (
              <>
                {healthcareService.createdBy}{" "}
                <span className="nhsuk-u-font-size-16">
                  ({healthcareService.createdDateTime})
                </span>
              </>
            ),
          },
          {
            key: "Modified By",
            value: (
              <>
                {healthcareService.modifiedBy}{" "}
                <span className="nhsuk-u-font-size-16">
                  ({healthcareService.modifiedDateTime})
                </span>
              </>
            ),
          },
        ]}
      />
    </Card>
  );
};

function HealthCareServiceDetailsRoute() {
  const { healthcareServiceID } = Route.useParams();
  const {
    data: healthcareService,
    isLoading,
    isSuccess,
    error,
  } = useHealthcareServiceQuery(healthcareServiceID);

  return (
    <>
      <PageBreadcrumbs
        backTo="/healthcare-services"
        items={[
          { to: "/", label: "Home" },
          { to: "/healthcare-services", label: "HealthCare Services" },
          {
            to: "/healthcare-services/$healthcareServiceID/",
            label: healthcareService?.name || "HealthCare Service Details",
          },
        ]}
      />
      <span className="nhsuk-caption-l">HealthCare Service Details </span>
      {isLoading && <p>Loading...</p>}
      {error && <RequestErrorDetails error={error as ResponseError} />}
      {healthcareService && (
        <>
          <h1 className="nhsuk-heading-l">{healthcareService.name}</h1>
          <HealthCareServiceOverview healthcareService={healthcareService} />
        </>
      )}
      {isSuccess && !healthcareService && (
        <>
          <h2 className="nhsuk-heading-l">HealthCare Service not found</h2>
          <p>The healthcare service you are looking for does not exist.</p>
          <ActionLink
            asElement={Link}
            to="/healthcare-services"
            className="nhsuk-link--no-visited-state"
          >
            Back to HealthCare Services
          </ActionLink>
        </>
      )}
    </>
  );
}
