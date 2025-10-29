import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import careIdentityLoginImg from "/images/care-identity-buttons/SVG/CIS2_LogInWith_Original.svg";

export const Route = createFileRoute("/")({
  component: HomePage,
  head: () => ({
    meta: [{ title: "FtRS DoS UI" }],
  }),
  loader: async () => {
    return {
      authorizeUrl: "https://example.com/authorize"
    }
  }
});

const useUserSessionData = () => useLoaderData({ from: "__root__" }).session;

function HomePage() {
  const session = useUserSessionData();
  const { authorizeUrl } = Route.useLoaderData();

  return (
    <>
      <h1 className="nhsuk-heading-l">Home</h1>
      <h2 className="nhsuk-heading-m">Session Details</h2>
      <pre>{JSON.stringify(session, null, 2)}</pre>
      <a
        type="button"
        className="care-identity-button"
        href={authorizeUrl}
      >
        <img
          src={careIdentityLoginImg}
          alt="Care Identity Login"
          className="care-identity-button__image"
        />
      </a>
    </>
  );
}
