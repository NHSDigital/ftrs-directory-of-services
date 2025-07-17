import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import { Link, createFileRoute } from "@tanstack/react-router";
import { Card } from "nhsuk-react-components";

export const Route = createFileRoute("/")({
  component: HomePage,
  head: () => ({
    meta: [{ title: "FtRS Read Only Viewer" }],
  }),
});

type HomePageCardGroupProps = {
  items: Array<{
    title: string;
    description: string;
    link: string;
    disabled?: boolean;
  }>;
};

const HomePageCardGroup: React.FC<HomePageCardGroupProps> = ({ items }) => {
  return (
    <Card.Group>
      {items.map((item) => (
        <Card.GroupItem key={item.title} width="one-half">
          <Card clickable={!item.disabled}>
            <Card.Content>
              <Card.Heading headingLevel="h3">
                <Card.Link
                  asElement={Link}
                  to={item.link}
                  disabled={item.disabled}
                >
                  {item.title}
                </Card.Link>
              </Card.Heading>
              <Card.Description>{item.description}</Card.Description>
            </Card.Content>
          </Card>
        </Card.GroupItem>
      ))}
    </Card.Group>
  );
};

function HomePage() {
  return (
    <>
      <PageBreadcrumbs backTo={null} items={[{ to: "/", label: "Home" }]} />
      <h1 className="nhsuk-heading-l">Read Only Viewer</h1>
      <h2 className="nhsuk-heading-m">Available Entity Types</h2>
      <HomePageCardGroup
        items={[
          {
            title: "Organisations",
            description: "View and search organisations.",
            link: "/organisations",
          },
          {
            title: "Healthcare Services",
            description: "View and search healthcare services",
            link: "/healthcare-services",
          },
          {
            title: "Locations",
            description: "View and search locations",
            link: "/locations",
          },
        ]}
      />
    </>
  );
}
