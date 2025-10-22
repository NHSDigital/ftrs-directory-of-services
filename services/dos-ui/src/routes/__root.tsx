import {
  createRootRoute,
  HeadContent,
  Outlet,
  Scripts,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { Container, Footer, Header } from "nhsuk-react-components";
import type { PropsWithChildren } from "react";
import Banner from "@/components/Banner";
import appStylesUrl from "../styles/App.scss?url";

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { title: "FtRS DoS UI" },
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
        <RootDocument>
          <Outlet />
        </RootDocument>
        <TanStackRouterDevtools />
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
});

const RootDocument: React.FC<PropsWithChildren> = ({ children }) => {
  return (
    <>
      <Header transactional={true}>
        <Header.Container>
          <Header.Logo href="/" />
          <Header.ServiceName href="/">
            Directory of Services
          </Header.ServiceName>
        </Header.Container>
      </Header>
      <Banner label="DoS UI">This is a basic placeholder landing page.</Banner>
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
