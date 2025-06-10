import '@testing-library/jest-dom';
import { afterAll, afterEach, beforeAll } from 'vitest'
import { server, StubData } from './__mocks__/mockServiceWorker';
import {queryClient} from "@/routes/__root";

beforeAll(() => server.listen({onUnhandledRequest: "error"}));
afterAll(() => server.close());
afterEach(() => {
  server.resetHandlers();
  queryClient.clear();
  StubData.reset();
});

