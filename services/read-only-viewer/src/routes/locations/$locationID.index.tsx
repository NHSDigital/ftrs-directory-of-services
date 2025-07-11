import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/locations/$locationID/")({
  component: LocationDetailsRoute,
  head: () => ({
    meta: [{ title: "Location Details - FtRS Read Only Viewer" }],
  }),
});

function LocationDetailsRoute() {}
