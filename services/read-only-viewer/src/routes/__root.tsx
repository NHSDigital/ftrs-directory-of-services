import { HeadContent, Outlet, createRootRoute } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { Container, Footer, Header } from "nhsuk-react-components";
import type { PropsWithChildren } from "react";
import appStylesUrl from "../styles/App.scss?url";

export const Route = createRootRoute({
  head: () => ({
    links: [
      {
        rel: "stylesheet",
        href: appStylesUrl,
        type: "text/css",
      },
    ],
  }),
  component: () => (
    <>
      <HeadContent />
      <RootDocument>
        <Outlet />
      </RootDocument>
      <TanStackRouterDevtools />
    </>
  ),
  notFoundComponent: () => (
    <RootDocument>
      <Container className="ftrs-page-container">
        <h1 className="nhsuk-heading-l">Page not found</h1>
        <p>This page does not exist.</p>
        <p>
          <a href="/">Return to the homepage</a>
        </p>
      </Container>
    </RootDocument>
  ),
});

const RootDocument: React.FC<PropsWithChildren> = ({ children }) => (
  <>
    <Header transactional>
      <Header.Container>
        <Header.Logo href="/" />
        <Header.ServiceName href="/">FtRS Read-Only Viewer</Header.ServiceName>
      </Header.Container>
    </Header>
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
