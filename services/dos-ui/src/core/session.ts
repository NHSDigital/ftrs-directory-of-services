import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  DeleteCommand,
  DynamoDBDocumentClient,
  GetCommand,
  PutCommand,
} from "@aws-sdk/lib-dynamodb";
import { createServerOnlyFn } from "@tanstack/react-start";
import { useSession } from "@tanstack/react-start/server";
import {
  ClientSessionSchema,
  type UserSession,
  UserSessionSchema,
} from "@/core/schema";

export class SessionManager {
  private readonly SESSION_TIMEOUT = 1000 * 60 * 60; // 1 hour
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
      expiresAt: Date.now() + this.SESSION_TIMEOUT,
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
}

export const setupSession = createServerOnlyFn(async () => {
  const manager = new SessionManager();
  const session = await useSession({
    name: "dos-ui-session",
    password: process.env.SESSION_SECRET!,
    maxAge: 1000 * 60 * 60, // 1 hour
  });

  if (!session.data || !session.data.sessionID) {
    const newSession = await manager.createSession();
    await session.update({ sessionID: newSession.sessionID });
    return ClientSessionSchema.parse(newSession);
  }

  const sessionID = session.data.sessionID as string;
  const existingSession = await manager.getSession(sessionID);

  if (!existingSession) {
    const newSession = await manager.createSession();
    await session.update({ sessionID: newSession.sessionID });
    return ClientSessionSchema.parse(newSession);
  }

  return ClientSessionSchema.parse(existingSession);
});
