import { HeadContent, Outlet, createRootRoute } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { Container, Footer, Header } from "nhsuk-react-components";
import appStylesUrl from "../App.scss?url";

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
			<Header transactional>
				<Header.Container>
					<Header.Logo href="/" />
					<Header.ServiceName href="/">
						FtRS Read-Only Viewer
					</Header.ServiceName>
				</Header.Container>
			</Header>
			<Container className="ftrs-page-container">
				<Outlet />
			</Container>
			<Footer>
				<Footer.List>
					<Footer.ListItem href="/">Home</Footer.ListItem>
				</Footer.List>
				<Footer.Copyright>
					&copy; {new Date().getFullYear()} NHS England
				</Footer.Copyright>
			</Footer>
			<TanStackRouterDevtools />
		</>
	),
});
