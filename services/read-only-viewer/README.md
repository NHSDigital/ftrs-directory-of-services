# FtRS Read-Only Viewer

The FtRS Read-Only Viewer is a test utility for the Find the Right Service database. It allows users to view the data from the dynamoDB table in a user-friendly way and test the Crud APIs. The application is designed to be used by developers and testers to ensure that the data in the database is correct and that the APIs are working as expected.

The application is built using React and TypeScript, and it uses the TanStack Router for routing and data fetching.

## Mapping of data from DynamoDB to the Read-Only Viewer

The data from the DynamoDB table is mapped in 1:1 to the Read-Only Viewer in a way that allows users to view the data in a user-friendly way.

Except the Create date and modify date fields are displayed along with Created By and Modified By fields.

The data is displayed in a table format, with each row representing a field/each column representing in the table.

For Healthcare Service, the opening Times and contact information are concatenated and displayed in a single field for more user-friendly view.

## Getting Started

## Prerequisites

- [Node.js](https://nodejs.org/en/download/) version 18 or later
- [NPM](https://www.npmjs.com/get-npm) version 8 or later
- [Make](https://www.gnu.org/software/make/) version 3.82 or later

## To run this application in local development mode

- set up a .env file in the root of the project with the following variables:
  - `ENVIRONMENT=dev`
  - `WORKSPACE=fdos-000` optional variable

- assume the **DOS-FtRS-RW-Developer** AWS role or export the AWS credentials for the role you want to use in your environment.

- run the following command to install the dependencies:

```bash
npm install
# or
make install
```

- run the following command to start the application in development mode:

```bash
npm run dev
# or
make dev
```

- open your browser and navigate to `http://localhost:3000/` to view the application.

## Configuration

The application reads the parameters from AWS Systems Manager Parameter Store, so you will need to ensure that the parameter(ftrs-dos-${environment}-crud-apis/endpoint) is set up in the Parameter Store for the environment you are running the application in.

- Make sure you have the correct permissions to access the Parameter Store and the APIs.

- Create a parameter by clicking Create parameter in AWS System Manager > Parameter Store, give the name "**/ftrs-dos-dev-crud-apis/endpoint/**" and set the value to the API endpoint you want to use from API Gateway.

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

If you would like format/lint suggestions to be automatically applied the run:

```bash
npm run lint -- --write
npm run format -- --write
npm run check -- --write
```

## Routing

This project uses [TanStack Router](https://tanstack.com/router). The initial setup is a file-based router. Which means that the routes are managed as files in `src/routes`.

### Adding A Route

To add a new route, create a new file in the `src/routes` directory. The file name will determine the route path. For example, if you create a file named `about.tsx`, it will be accessible at `/about`.

TanStack will automatically generate the correct route for you based on the file structure. You can also create nested routes by creating a directory with an `index.tsx` file inside it.

Now that you have two routes you can use a `Link` component to navigate between them.

### Adding Links

To use SPA (Single Page Application) navigation, you will need to import the `Link` component from `@tanstack/react-router`.

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
