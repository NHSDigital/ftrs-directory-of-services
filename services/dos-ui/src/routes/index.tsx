import { createFileRoute } from '@tanstack/react-router'

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
    </>
  );
}
