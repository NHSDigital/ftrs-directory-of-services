import { getAuthorisationUrl } from "@/utils/cis2Configuration-service.ts";
import { createFileRoute } from "@tanstack/react-router";
import { useClientSession } from "@/core/context";
import careIdentityLoginImg from "/images/care-identity-buttons/SVG/CIS2_LogInWith_Original.svg"; import { useClientSession } from "@/core/context";

export const Route = createFileRoute("/")({
  component: HomePage,
  head: () => ({
    meta: [{ title: "FtRS DoS UI" }],
  }),
  loader: async () => {
    return {
      authorizeUrl: await getAuthorisationUrl(),
    };
  },
});

function HomePage() {
  const session = useClientSession();
  const { authorizeUrl } = Route.useLoaderData();

  return (
    <>
      <h1 className="nhsuk-heading-l">Home</h1>
      <h2 className="nhsuk-heading-m">Session Details</h2>
      <ul className="nhsuk-list nhsuk-list--bullet">
        <li>Session ID: {session.sessionID}</li>
        <li>Expires At: {new Date(session.expiresAt).toString()}</li>
        <li>State: {session.state}</li>
      </ul>
      <a type="button" className="care-identity-button" href={authorizeUrl}>
        <img
          src={careIdentityLoginImg}
          alt="Care Identity Login"
          className="care-identity-button__image"
        />
      </a>
    </>
  );
}
