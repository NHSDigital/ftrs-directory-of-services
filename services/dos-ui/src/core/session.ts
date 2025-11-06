import { getSecret } from "@aws-lambda-powertools/parameters/secrets";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  DeleteCommand,
  DynamoDBDocumentClient,
  GetCommand,
  PutCommand,
} from "@aws-sdk/lib-dynamodb";
import { createServerFn, createServerOnlyFn } from "@tanstack/react-start";
import { useSession } from "@tanstack/react-start/server";
import {
  ClientSessionSchema,
  type UserSession,
  UserSessionSchema,
} from "@/core/schema";
import {
  SESSION_COOKIE_MAX_AGE,
  SESSION_COOKIE_NAME,
  SESSION_TIMEOUT_MS,
} from "./constants";

export class SessionManager {
  private tableName: string;
  private baseClient: DynamoDBClient;
  private client: DynamoDBDocumentClient;

  constructor() {
    this.tableName = SessionManager.getSessionTableName();
    this.baseClient = new DynamoDBClient({
      endpoint: process.env.DYNAMODB_ENDPOINT,
    });
    this.client = DynamoDBDocumentClient.from(this.baseClient, {
      marshallOptions: { removeUndefinedValues: true },
    });
  }

  public async createSession(): Promise<UserSession> {
    const sessionID = crypto.randomUUID();
    const session = UserSessionSchema.parse({
      sessionID,
      state: crypto.randomUUID(),
      expiresAt: Date.now() + SESSION_TIMEOUT_MS,
      userID: undefined,
      user: undefined,
      tokens: {
        cis2: undefined,
        apim: undefined,
      },
    });

    const putCommand = new PutCommand({
      TableName: this.tableName,
      Item: session,
      ReturnConsumedCapacity: "INDEXES",
    });

    await this.client.send(putCommand);
    return session;
  }

  async getSession(sessionID: string): Promise<UserSession | null> {
    const getCommand = new GetCommand({
      TableName: this.tableName,
      Key: { sessionID },
      ConsistentRead: true,
      ReturnConsumedCapacity: "INDEXES",
    });

    const response = await this.client.send(getCommand);
    if (!response.Item) {
      return null;
    }

    const session = UserSessionSchema.parse(response.Item);
    if (session.expiresAt <= Date.now()) {
      return null;
    }

    return session;
  }

  async updateSession(session: UserSession): Promise<UserSession> {
    const putCommand = new PutCommand({
      TableName: this.tableName,
      Item: session,
      ReturnConsumedCapacity: "INDEXES",
    });

    await this.client.send(putCommand);
    return session;
  }

  async deleteSession(sessionID: string): Promise<void> {
    const deleteCommand = new DeleteCommand({
      TableName: this.tableName,
      Key: { sessionID },
      ReturnConsumedCapacity: "INDEXES",
    });
    await this.client.send(deleteCommand);
  }

  static getSessionTableName(): string {
    const env = process.env.ENVIRONMENT;
    const workspace = process.env.WORKSPACE;

    if (!env) {
      throw new Error("ENVIRONMENT environment variable must be set");
    }

    const tableName = `ftrs-dos-${env}-ui-session-store`;
    return workspace ? `${tableName}-${workspace}` : tableName;
  }

  static async getSessionSecret(): Promise<string> {
    const env = process.env.ENVIRONMENT;
    const workspace = process.env.WORKSPACE;

    if (!env) {
      throw new Error("ENVIRONMENT environment variable must be set");
    }

    if (env === "local" && process.env.LOCAL_SESSION_SECRET) {
      return process.env.LOCAL_SESSION_SECRET;
    }

    const envPrefix = workspace ? `${env}-${workspace}` : env;
    const secretName = `/ftrs-dos/${envPrefix}/ui-session-secret`;

    const secretValue = await getSecret(secretName);
    if (!secretValue) {
      throw new Error(
        `Session secret not found in Secrets Manager: ${secretName}`,
      );
    }

    return secretValue.toString();
  }
}

export const buildSession = async () => {
  const manager = new SessionManager();
  const session = await useSession({
    name: SESSION_COOKIE_NAME,
    password: await SessionManager.getSessionSecret(),
    maxAge: SESSION_COOKIE_MAX_AGE,
  });

  if (!session.data || !session.data.sessionID) {
    const newSession = await manager.createSession();
    await session.update({ sessionID: newSession.sessionID });
    return ClientSessionSchema.parse(newSession);
  }

  const sessionID = session.data.sessionID;
  const existingSession = await manager.getSession(sessionID);

  if (!existingSession) {
    const newSession = await manager.createSession();
    await session.update({ sessionID: newSession.sessionID });
    return ClientSessionSchema.parse(newSession);
  }

  return ClientSessionSchema.parse(existingSession);
};

export const setupSessionFn = createServerFn({ method: "GET" }).handler(buildSession);
