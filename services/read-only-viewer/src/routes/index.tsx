import { createFileRoute } from "@tanstack/react-router";
import { createServerFn } from "@tanstack/react-start";
import { Button, Form, TextInput } from "nhsuk-react-components";
import { useState } from "react";

export const Route = createFileRoute("/")({
  component: HomePage,
  loader: async (_ctx) => {
    // This is where you can load data for the route
    // For example, you can fetch data from an API or a database
    // and return it as props to the component
    return {
      title: "Hello World!",
      description:
        "This is the basic boilerplate FtRS Read Only Viewer application.",
    };
  },
});

const exampleServerFn = createServerFn()
  .validator((input: { name: string }) => input)
  .handler(async (ctx) => {
    const { name } = ctx.data;
    return `Hello, ${name}!`;
  });

function HomePage() {
  const { title, description } = Route.useLoaderData();
  const [name, setName] = useState("");
  const [error, setError] = useState<string | undefined>();
  const [response, setResponse] = useState<string | undefined>();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!name) {
      setError("Name is required");
      return;
    }

    setError(undefined);
    setResponse(undefined);
    const response = await exampleServerFn({ data: { name } });
    setResponse(response);
  };

  return (
    <>
      <h1 className="nhsuk-heading-l">{title}</h1>
      <p>{description}</p>
      <h2 className="nhsuk-heading-m">Test Server Function Support</h2>
      <Form onSubmit={handleSubmit} method="POST">
        <TextInput
          id="name"
          value={name}
          onChange={(e) => setName(e.currentTarget.value)}
          error={error}
          label="What is your name?"
          width="20"
        />
        <Button type="submit">Submit</Button>
      </Form>
      <h3 className="nhsuk-heading-s">Server Response</h3>
      <p>{response}</p>
    </>
  );
}
