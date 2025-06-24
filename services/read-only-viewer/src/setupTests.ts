import "@testing-library/jest-dom";
import { queryClient } from "@/routes/__root";
import { afterAll, afterEach, beforeAll } from "vitest";
import { StubData, server } from "./__mocks__/mockServiceWorker";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterAll(() => server.close());
afterEach(() => {
  server.resetHandlers();
  queryClient.clear();
  StubData.reset();
});
