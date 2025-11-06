import {
  createRootRoute,
  HeadContent,
  Outlet,
  type RouteComponent,
  Scripts,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { Container, Footer, Header, InsetText, SummaryList } from "nhsuk-react-components";
import { useEffect, useState, type PropsWithChildren } from "react";
import Banner from "@/components/Banner";
import { ClientSessionContext } from "@/core/context";
import { setupSessionFn } from "@/core/session";
import appStylesUrl from "../styles/App.scss?url";
import { AppError } from "@/core/errors";
import NotFoundComponent from "@/components/NotFoundComponent";
import ErrorComponent from "@/components/ErrorComponent";

const RootComponent: RouteComponent = () => {
  const { session } = Route.useLoaderData();
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        <ClientSessionContext.Provider value={session}>
          <RootDocument>
            <Outlet />
          </RootDocument>
        </ClientSessionContext.Provider>
        <TanStackRouterDevtools />
        <Scripts />
      </body>
    </html>
  );
};

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
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
  loader: async () => {
    const session = await setupSessionFn();
    return { session };
  },
});
