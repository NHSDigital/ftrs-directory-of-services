import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: App,
});

function App() {
  return (
    <>
      <h1 className="nhsuk-heading-l">Hello World!</h1>
      <p>This is the basic boilerplate FtRS Read Only Viewer application.</p>
    </>
  );
}
