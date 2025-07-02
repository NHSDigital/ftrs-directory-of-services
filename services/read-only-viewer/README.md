# FtRS Read-Only Viewer

The FtRS Read-Only Viewer is a test utility for the Find the Right Service database. It allows users to view the data in the database and test the APIs that are available.

## Getting Started

### Installing the project

```bash
make install
```

> **Note:** If you are not using `asdf` to manage your runtime versions, you will need to install the dependencies manually. Check the `.tool-version` file in the root of the project for the runtime versions used in this project.
>
> You will then need to run `npm install` manually to install the dependencies.

### Setting Environment Variables

To run the read-only viewer against a cloud deployed instance, you will need to first locally authenticate into the AWS account that the project is deployed to.

```
assume <role_name>

export ENVIRONMENT=dev
export WORKSPACE=fdos-000 # optional
```

> **Note:** There is an issue where the Node.js credential provider does not work correctly with the `assume` command. You may need to manually unset the `AWS_PROFILE` environment variable if you have it set.
>
> ```
> unset AWS_PROFILE
> ```

To run the read-only viewer against a local instance, you will need to set the `ENVIRONMENT` variable to `local` and the `LOCAL_CRUD_API_ENDPOINT` variable to the URL of the local CRUD API instance.

```bash
export ENVIRONMENT=local
export LOCAL_CRUD_API_ENDPOINT=http://localhost:3000
```

## Running the Application

To run the application in development mode, you can use the following command:

```bash
npm run dev
```

## Building For Production

To build this application for production:

```bash
npm run build
# or
make build
```

## Testing

This project uses [Vitest](https://vitest.dev/) for testing. You can run the tests with:

```bash
npm run test
# or
make unit-test
```

## Styling

This project uses SCSS for styling, and imports NHS.UK Frontend as the base of all styles. The stylesheets are located in the `src/styles` directory. You can add your own styles to this directory and import them into your components.

## Linting & Formatting

This project uses [Biome](https://biomejs.dev/) for linting and formatting. The following scripts are available:

```bash
npm run lint
npm run format
npm run check
# or
make format
make lint
```

## Routing

This project uses [TanStack Router](https://tanstack.com/router). The initial setup is a file based router. Which means that the routes are managed as files in `src/routes`.

### Adding A Route

To add a new route to your application just add another a new file in the `./src/routes` directory.

TanStack will automatically generate the content of the route file for you.

Now that you have two routes you can use a `Link` component to navigate between them.

### Adding Links

To use SPA (Single Page Application) navigation you will need to import the `Link` component from `@tanstack/react-router`.

```tsx
import { Link } from "@tanstack/react-router";
```

Then anywhere in your JSX you can use it like so:

```tsx
<Link to="/about">About</Link>
```

This will create a link that will navigate to the `/about` route.

More information on the `Link` component can be found in the [Link documentation](https://tanstack.com/router/v1/docs/framework/react/api/router/linkComponent).

### Using A Layout

In the File Based Routing setup the layout is located in `src/routes/__root.tsx`. Anything you add to the root route will appear in all the routes. The route content will appear in the JSX where you use the `<Outlet />` component.

Here is an example layout that includes a header:

```tsx
import { Outlet, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'

import { Link } from "@tanstack/react-router";

export const Route = createRootRoute({
  component: () => (
    <>
      <header>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/about">About</Link>
        </nav>
      </header>
      <Outlet />
      <TanStackRouterDevtools />
    </>
  ),
})
```

The `<TanStackRouterDevtools />` component is not required so you can remove it if you don't want it in your layout.

More information on layouts can be found in the [Layouts documentation](https://tanstack.com/router/latest/docs/framework/react/guide/routing-concepts#layouts).

## Data Fetching

There are multiple ways to fetch data in your application. You can use TanStack Query to fetch data from a server. But you can also use the `loader` functionality built into TanStack Router to load the data for a route before it's rendered.

For example:

```tsx
const peopleRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/people",
  loader: async () => {
    const response = await fetch("https://swapi.dev/api/people");
    return response.json() as Promise<{
      results: {
        name: string;
      }[];
    }>;
  },
  component: () => {
    const data = peopleRoute.useLoaderData();
    return (
      <ul>
        {data.results.map((person) => (
          <li key={person.name}>{person.name}</li>
        ))}
      </ul>
    );
  },
});
```

Loaders simplify your data fetching logic dramatically. Check out more information in the [Loader documentation](https://tanstack.com/router/latest/docs/framework/react/guide/data-loading#loader-parameters).
