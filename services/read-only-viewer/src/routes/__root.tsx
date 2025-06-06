import Banner from "@/components/Banner";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRoute,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { Container, Footer, Header } from "nhsuk-react-components";
import type { PropsWithChildren } from "react";
import appStylesUrl from "../styles/App.scss?url";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
    },
  },
});

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { title: "FtRS Read-Only Viewer" },
      {
        name: "viewport",
        content: "width=device-width, initial-scale=1.0",
      },
    ],
    links: [
      {
        rel: "stylesheet",
        href: appStylesUrl,
        type: "text/css",
      },
    ],
  }),
  component: () => (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <RootDocument>
            <Outlet />
          </RootDocument>
          <TanStackRouterDevtools />
          <ReactQueryDevtools />
        </QueryClientProvider>
        <Scripts />
      </body>
    </html>
  ),
  notFoundComponent: () => (
    <>
      <h1 className="nhsuk-heading-l">Page not found</h1>
      <p>This page does not exist.</p>
      <p>
        <a href="/">Return to the homepage</a>
      </p>
    </>
  ),
  errorComponent: ({ error }) => (
    <>
      <h1 className="nhsuk-heading-l">An error occurred</h1>
      <p>{error.message}</p>
      <p>
        <a href="/">Return to the homepage</a>
      </p>
    </>
  ),
});

const RootDocument: React.FC<PropsWithChildren> = ({ children }) => {
  return (
    <>
      <Header transactional>
        <Header.Container>
          <Header.Logo href="/" />
          <Header.ServiceName href="/">
            FtRS Read-Only Viewer
          </Header.ServiceName>
        </Header.Container>
      </Header>
      <Banner label="Test Utility">
        This is an internal test tool for Find the Right Service (FtRS) teams.
      </Banner>
      <Container className="ftrs-page-container">{children}</Container>
      <Footer>
        <Footer.List>
          <Footer.ListItem href="/">Home</Footer.ListItem>
        </Footer.List>
        <Footer.Copyright>
          &copy; {new Date().getFullYear()} NHS England
        </Footer.Copyright>
      </Footer>
    </>
  );
};
