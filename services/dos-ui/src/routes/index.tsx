import { createFileRoute } from '@tanstack/react-router'
import careIdentityLoginImg from '/images/care-identity-buttons/SVG/CIS2_LogInWith_Original.svg';

export const Route = createFileRoute('/')({
  component: HomePage,
  head: () => ({
    meta: [{ title: "FtRS DoS UI" }],
  }),
});

function HomePage() {
  return (
    <>
      <h1 className="nhsuk-heading-l">Home</h1>
      <button
        type="button"
        className="care-identity-button"
        onClick={() =>
          // TODO: Implement Care Identity login logic here
          console.log('Care Identity button clicked')
        }
      >
        <img
          src={careIdentityLoginImg}
          alt="Care Identity Login"
          className="care-identity-button__image"
        />
      </button>
    </>
  );
}
