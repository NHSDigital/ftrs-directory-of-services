import { StartClient } from "@tanstack/react-start";
import { hydrateRoot } from "react-dom/client";
import { createRouter } from "./router";

const router = createRouter({
  scrollRestoration: true,
});

hydrateRoot(document, <StartClient router={router} />);
