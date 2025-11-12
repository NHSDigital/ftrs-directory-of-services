import { createContext, useContext } from "react";
import type { ClientSession } from "./schema";

export const ClientSessionContext = createContext<ClientSession>({
  sessionID: "",
  expiresAt: 0,
  state: "",
});

export const useClientSession = () => useContext(ClientSessionContext);
