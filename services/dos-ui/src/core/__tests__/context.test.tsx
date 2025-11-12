import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClientSessionContext, useClientSession } from "../context";

describe("ClientSessionContext", () => {
  it("should create a context with default values", () => {
    const { result } = renderHook(() => useClientSession(), {
      wrapper: ({ children }) => (
        <ClientSessionContext.Provider
          value={{ sessionID: "", expiresAt: 0, state: "" }}
        >
          {" "}
          {children}{" "}
        </ClientSessionContext.Provider>
      ),
    });

    expect(result.current).toEqual({
      sessionID: "",
      expiresAt: 0,
      state: "",
    });
  });
});
