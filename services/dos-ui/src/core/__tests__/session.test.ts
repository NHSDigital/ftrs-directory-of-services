import { useSession } from "@tanstack/react-start/server";
import { beforeEach, describe, expect, it, type Mock, vi } from "vitest";
import { UserSessionSchema } from "../schema";
import { SessionManager, setupSession } from "../session";

vi.mock("@tanstack/react-start/server", () => {
  return {
    useSession: vi.fn().mockReturnValue(
      Promise.resolve({
        data: null,
        update: vi.fn(),
        clear: vi.fn(),
      }),
    ),
  };
});

describe("SessionManager", () => {
  let sessionManager: SessionManager;
  let mockSendCommand: Mock;

  beforeEach(() => {
    process.env.ENVIRONMENT = "local";
    process.env.WORKSPACE = "";
    process.env.SESSION_SECRET =
      "test-session-secret-that-is-long-enough-for-testing";
    mockSendCommand = vi.fn();

    sessionManager = new SessionManager();
    // @ts-expect-error Updating a private property for testing
    sessionManager.client.send = mockSendCommand;

    vi.clearAllMocks();
  });

  it("should generate correct session table name without workspace", () => {
    const tableName = SessionManager.getSessionTableName();
    expect(tableName).toBe("ftrs-dos-local-ui-session-store");
  });

  it("should generate correct session table name with workspace", () => {
    process.env.WORKSPACE = "dev";

    const tableName = SessionManager.getSessionTableName();
    expect(tableName).toBe("ftrs-dos-local-ui-session-store-dev");
  });

  it("should throw error if ENVIRONMENT is not set", () => {
    delete process.env.ENVIRONMENT;

    expect(() => SessionManager.getSessionTableName()).toThrowError(
      "ENVIRONMENT environment variable must be set",
    );
  });

  it("creates a new session", async () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue(
      "fac6596b-d957-4862-a4e1-2728e558410b",
    );

    const session = await sessionManager.createSession();

    expect(session).toEqual({
      sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
      state: "fac6596b-d957-4862-a4e1-2728e558410b",
      expiresAt: expect.any(Number),
      userID: undefined,
      user: undefined,
      tokens: {
        cis2: undefined,
        apim: undefined,
      },
    });

    expect(UserSessionSchema.parse(session)).toEqual(session);

    expect(mockSendCommand).toHaveBeenCalledTimes(1);

    const putCommandInput = mockSendCommand.mock.calls[0][0].input;
    expect(putCommandInput.TableName).toBe("ftrs-dos-local-ui-session-store");
    expect(putCommandInput.Item).toEqual(session);
    expect(putCommandInput.ReturnConsumedCapacity).toBe("INDEXES");
  });

  it("retrieves an existing session", async () => {
    const mockSession = {
      sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
      state: "random-state",
      expiresAt: Date.now() + 3600000,
      userID: undefined,
      user: undefined,
      tokens: {
        cis2: undefined,
        apim: undefined,
      },
    };

    mockSendCommand.mockResolvedValueOnce({ Item: mockSession });

    const session = await sessionManager.getSession(
      "fac6596b-d957-4862-a4e1-2728e558410b",
    );

    expect(session).toEqual(mockSession);

    expect(mockSendCommand).toHaveBeenCalledTimes(1);

    const getCommandInput = mockSendCommand.mock.calls[0][0].input;
    expect(getCommandInput.TableName).toBe("ftrs-dos-local-ui-session-store");
    expect(getCommandInput.Key).toEqual({
      sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
    });
    expect(getCommandInput.ConsistentRead).toBe(true);
    expect(getCommandInput.ReturnConsumedCapacity).toBe("INDEXES");
  });

  it("returns null for non-existing session", async () => {
    mockSendCommand.mockResolvedValueOnce({});

    const session = await sessionManager.getSession("non-existing-session-id");
    expect(session).toBeNull();
  });

  it("returns null for expired session", async () => {
    const mockSession = {
      sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
      state: "random-state",
      expiresAt: Date.now() - 1000,
      userID: undefined,
      user: undefined,
      tokens: {
        cis2: undefined,
        apim: undefined,
      },
    };

    mockSendCommand.mockResolvedValueOnce({ Item: mockSession });

    const session = await sessionManager.getSession(
      "fac6596b-d957-4862-a4e1-2728e558410b",
    );
    expect(session).toBeNull();
  });
  it("updates an existing session", async () => {
    const mockSession = {
      sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
      state: "random-state",
      expiresAt: Date.now() + 3600000,
      userID: "12345",
      user: undefined,
      tokens: {
        cis2: undefined,
        apim: undefined,
      },
    };

    const updatedSession = await sessionManager.updateSession(mockSession);

    expect(updatedSession).toEqual(mockSession);

    expect(mockSendCommand).toHaveBeenCalledTimes(1);

    const putCommandInput = mockSendCommand.mock.calls[0][0].input;
    expect(putCommandInput.TableName).toBe("ftrs-dos-local-ui-session-store");
    expect(putCommandInput.Item).toEqual(mockSession);
    expect(putCommandInput.ReturnConsumedCapacity).toBe("INDEXES");
  });

  it("deletes an existing session", async () => {
    mockSendCommand.mockResolvedValueOnce({});

    await sessionManager.deleteSession("fac6596b-d957-4862-a4e1-2728e558410b");
    expect(mockSendCommand).toHaveBeenCalledTimes(1);
    const deleteCommandInput = mockSendCommand.mock.calls[0][0].input;
    expect(deleteCommandInput.TableName).toBe(
      "ftrs-dos-local-ui-session-store",
    );
    expect(deleteCommandInput.Key).toEqual({
      sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
    });
    expect(deleteCommandInput.ReturnConsumedCapacity).toBe("INDEXES");
  });
});

describe("setupSession", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should create a new session using SessionManager", async () => {
    process.env.SESSION_SECRET = "test-session-secret-that-is-long-enough";

    const createSessionSpy = vi
      .spyOn(SessionManager.prototype, "createSession")
      .mockResolvedValue({
        sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
        state: "random-state",
        expiresAt: Date.now() + 3600000,
        userID: undefined,
        user: undefined,
        tokens: {
          cis2: undefined,
          apim: undefined,
        },
      });

    const session = await setupSession();

    expect(createSessionSpy).toHaveBeenCalledTimes(1);
    expect(session).toEqual({
      sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
      expiresAt: expect.any(Number),
      state: "random-state",
      user: undefined,
      userID: undefined,
    });

    const useSessionMock = useSession as Mock<typeof useSession>;

    expect(useSessionMock).toHaveBeenCalledWith({
      name: "dos-ui-session",
      password: process.env.SESSION_SECRET!,
      maxAge: 1000 * 60 * 60, // 1 hour
    });

    const returnValue = await useSessionMock.mock.results[0].value;
    expect(returnValue.update).toHaveBeenCalledTimes(1);
    expect(returnValue.update).toHaveBeenCalledWith({
      sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
    });
  });

  it("should not create a new session if one already exists", async () => {
    const useSessionMock = useSession as Mock<typeof useSession>;
    useSessionMock.mockReturnValueOnce(
      Promise.resolve({
        id: "dos-ui-session",
        data: {
          sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
        },
        update: vi.fn(),
        clear: vi.fn(),
      }),
    );

    const createSessionSpy = vi.spyOn(
      SessionManager.prototype,
      "createSession",
    );
    const getSessionSpy = vi
      .spyOn(SessionManager.prototype, "getSession")
      .mockResolvedValue({
        sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
        state: "random-state",
        expiresAt: Date.now() + 3600000,
        userID: undefined,
        user: undefined,
        tokens: {
          cis2: undefined,
          apim: undefined,
        },
      });

    const session = await setupSession();

    expect(createSessionSpy).not.toHaveBeenCalled();
    expect(getSessionSpy).toHaveBeenCalledTimes(1);

    expect(session).toEqual({
      sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
      expiresAt: expect.any(Number),
      state: "random-state",
      user: undefined,
      userID: undefined,
    });

    expect(useSessionMock).toHaveBeenCalledWith({
      name: "dos-ui-session",
      password: process.env.SESSION_SECRET!,
      maxAge: 1000 * 60 * 60, // 1 hour
    });

    const returnValue = await useSessionMock.mock.results[0].value;
    expect(returnValue.update).not.toHaveBeenCalled();
    expect(returnValue.clear).not.toHaveBeenCalled();
  });

  it("should create a new session if existing session is not found", async () => {
    const useSessionMock = useSession as Mock<typeof useSession>;
    useSessionMock.mockReturnValueOnce(
      Promise.resolve({
        id: "dos-ui-session",
        data: {
          sessionID: "fac6596b-d957-4862-a4e1-2728e558410b",
        },
        update: vi.fn(),
        clear: vi.fn(),
      }),
    );

    const createSessionSpy = vi
      .spyOn(SessionManager.prototype, "createSession")
      .mockResolvedValue({
        sessionID: "9704d57e-ee93-4e1e-8bd6-130e2c72de79",
        state: "random-state",
        expiresAt: Date.now() + 3600000,
        userID: undefined,
        user: undefined,
        tokens: {
          cis2: undefined,
          apim: undefined,
        },
      });
    const getSessionSpy = vi
      .spyOn(SessionManager.prototype, "getSession")
      .mockResolvedValue(null);

    const session = await setupSession();

    expect(getSessionSpy).toHaveBeenCalledTimes(1);
    expect(createSessionSpy).toHaveBeenCalledTimes(1);

    expect(session).toEqual({
      sessionID: "9704d57e-ee93-4e1e-8bd6-130e2c72de79",
      expiresAt: expect.any(Number),
      state: "random-state",
      user: undefined,
      userID: undefined,
    });

    expect(useSessionMock).toHaveBeenCalledWith({
      name: "dos-ui-session",
      password: process.env.SESSION_SECRET!,
      maxAge: 1000 * 60 * 60, // 1 hour
    });

    const returnValue = await useSessionMock.mock.results[0].value;
    expect(returnValue.update).toHaveBeenCalledTimes(1);
    expect(returnValue.update).toHaveBeenCalledWith({
      sessionID: "9704d57e-ee93-4e1e-8bd6-130e2c72de79",
    });
  });
});
