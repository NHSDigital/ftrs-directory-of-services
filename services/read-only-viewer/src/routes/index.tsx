import { Link, createFileRoute } from "@tanstack/react-router";
import { createServerFn } from "@tanstack/react-start";
import {
  Breadcrumb,
  Button,
  Card,
  Form,
  TextInput,
} from "nhsuk-react-components";
import { useState } from "react";

export const Route = createFileRoute("/")({
  component: HomePage,
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
      <Breadcrumb className="nhsuk-u-margin-bottom-3">
        <Breadcrumb.Item>
          <Link to="/" className="nhsuk-link nhsuk-link--no-visited-state">
            Home
          </Link>
        </Breadcrumb.Item>
      </Breadcrumb>
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
            description: "View and search services (coming soon).",
            link: "/healthcare-services",
            disabled: true,
          },
          {
            title: "Locations",
            description: "View and search locations (coming soon).",
            link: "/locations",
            disabled: true,
          },
        ]}
      />
    </>
  );
}
