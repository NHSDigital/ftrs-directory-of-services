import { createFileRoute, Link } from "@tanstack/react-router";
import { useHealthcareServiceQuery } from "@/hooks/queryHooks.ts";
import PageBreadcrumbs from "@/components/PageBreadcrumbs.tsx";
import RequestErrorDetails from "@/components/RequestErrorDetails.tsx";
import type { ResponseError } from "@/utils/errors.ts";
import { ActionLink, Card } from "nhsuk-react-components";
import type { HealthcareService } from "@/utils/types.ts";
import KeyValueTable from "@/components/KeyValueTable.tsx";

export const Route = createFileRoute("/healthcare-services/$healthcareServiceID/")({
  component: HealthCareServiceDetailsRoute,
  head: () => ({
    meta: [{ title: "HealthCare Service Details - FtRS Read Only Viewer" }],
  }),
});

const HealthCareServiceOverview: React.FC<{ healthcareService: HealthcareService }> = ({
  healthcareService,
}) => {
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
            value: (
              <>
                {healthcareService.telecom?.email && <div>Email: {healthcareService.telecom.email}</div>}
                {healthcareService.telecom?.phone_public && (
                  <div>Public Phone: {healthcareService.telecom.phone_public}</div>
                )}
                {healthcareService.telecom?.phone_private && (
                  <div>Private Phone: {healthcareService.telecom.phone_private}</div>
                )}
                {healthcareService.telecom?.website && (
                  <div>Website: {healthcareService.telecom.website}</div>
                )}
                {(!healthcareService.telecom ||
                  (!healthcareService.telecom.email &&
                    !healthcareService.telecom.phone_public &&
                    !healthcareService.telecom.phone_private &&
                    !healthcareService.telecom.website)) && "None Provided"}
              </>
            ),
          },
          {
            key: "Provided By",
            value: healthcareService.providedBy ? (
              <Link
                to="/organisations/$organisationID"
                params={{ organisationID: healthcareService.providedBy }}
                className="nhsuk-link nhsuk-link--no-visited-state"
              >
                {healthcareService.providedBy} (Organisation Link)
              </Link>
            ) : (
              "Not Specified"
            ),
          },
          {
            key: "Location",
            value: healthcareService.location || "Not Specified",
          },
          {
            key: "Category",
            value: healthcareService.category || "Not Specified",
          },
          {
            key: "Opening Times",
            value: healthcareService.openingTime?.length ? (
              <>
                {Object.entries(
                  healthcareService.openingTime.reduce((acc, time) => {
                    const category = time.category;
                    if (!acc[category]) {
                      acc[category] = [];
                    }
                    acc[category].push(time);
                    return acc;
                  }, {} as Record<string, typeof healthcareService.openingTime>)
                ).map(([category, times]) => (
                  <div key={category} className="nhsuk-u-margin-bottom-4">
                    <h4 className="nhsuk-heading-s nhsuk-u-margin-bottom-2">
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </h4>
                    <p className="nhsuk-u-font-size-16">
                      {category === "availableTime"
                        ? times
                            .map((time) => `${time.dayOfWeek} ${time.startTime} - ${time.endTime}`)
                            .join(",")
                        : category === "notAvailable"
                        ? times.map((time) => time.description).join(", ")
                        : times.map((time) => `${time.startTime} - ${time.endTime}`).join("/")}
                    </p>
                  </div>
                ))}
              </>
            ) : (
              "No Opening Times Provided"
            ),
          },
          {
            key: "Created By",
            value: (
              <>
                {healthcareService.createdBy}{" "}
                <span className="nhsuk-u-font-size-16">({healthcareService.createdDateTime})</span>
              </>
            ),
          },
          {
            key: "Modified By",
            value: (
              <>
                {healthcareService.modifiedBy}{" "}
                <span className="nhsuk-u-font-size-16">({healthcareService.modifiedDateTime})</span>
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
  const { data: healthcareService, isLoading, isSuccess, error } = useHealthcareServiceQuery(
    healthcareServiceID
  );

  return (
    <>
      <PageBreadcrumbs
        backTo="/healthcare-services"
        items={[
          { to: "/", label: "Home" },
          { to: "/healthcare-services", label: "HealthCare Services" },
          {
            to: `/healthcare-services/$healthcareServiceID/`,
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
