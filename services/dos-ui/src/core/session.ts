import type { Logger } from "@aws-lambda-powertools/logger";
import { getSecret } from "@aws-lambda-powertools/parameters/secrets";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  DeleteCommand,
  DynamoDBDocumentClient,
  GetCommand,
  PutCommand,
} from "@aws-sdk/lib-dynamodb";
import { createServerFn } from "@tanstack/react-start";
import { useSession } from "@tanstack/react-start/server";
import { randomState } from "openid-client";
import {
  ClientSessionSchema,
  type UserSession,
  UserSessionSchema,
} from "@/core/schema";
import { getLogger } from "@/utils/logger";
import {
  SESSION_COOKIE_MAX_AGE,
  SESSION_COOKIE_NAME,
  SESSION_TIMEOUT_MS,
} from "./constants";

export class SessionManager {
  private logger: Logger;
  private tableName: string;
  private baseClient: DynamoDBClient;
  private client: DynamoDBDocumentClient;

  constructor() {
    this.logger = getLogger();
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
      state: randomState(),
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
    this.logger.info("Session created", {
      sessionID,
      expiresAt: session.expiresAt,
    });

    return session;
  }

  async getSession(sessionID: string): Promise<UserSession | null> {
    this.logger.debug("Fetching session from DynamoDB", {
      sessionID,
      tableName: this.tableName,
    });
    const getCommand = new GetCommand({
      TableName: this.tableName,
      Key: { sessionID },
      ConsistentRead: true,
      ReturnConsumedCapacity: "INDEXES",
    });

    const response = await this.client.send(getCommand);
    if (!response.Item) {
      this.logger.info("Session not found", {
        sessionID,
        tableName: this.tableName,
      });
      return null;
    }

    const session = UserSessionSchema.parse(response.Item);
    if (session.expiresAt <= Date.now()) {
      this.logger.info("Session has expired", {
        sessionID,
        expiresAt: session.expiresAt,
        tableName: this.tableName,
      });
      return null;
    }

    this.logger.info("Session fetched successfully", {
      sessionID,
      expiresAt: session.expiresAt,
      tableName: this.tableName,
    });
    return session;
  }

  async updateSession(session: UserSession): Promise<UserSession> {
    this.logger.debug("Updating session in DynamoDB", {
      sessionID: session.sessionID,
    });
    const putCommand = new PutCommand({
      TableName: this.tableName,
      Item: session,
      ReturnConsumedCapacity: "INDEXES",
    });

    await this.client.send(putCommand);
    this.logger.info("Session updated", {
      sessionID: session.sessionID,
      expiresAt: session.expiresAt,
    });
    return session;
  }

  async deleteSession(sessionID: string): Promise<void> {
    this.logger.debug("Deleting session from DynamoDB", { sessionID });
    const deleteCommand = new DeleteCommand({
      TableName: this.tableName,
      Key: { sessionID },
      ReturnConsumedCapacity: "INDEXES",
    });
    await this.client.send(deleteCommand);
    this.logger.info("Session deleted", { sessionID });
  }

  static getSessionTableName(): string {
    const logger = getLogger();
    const env = process.env.ENVIRONMENT;
    const workspace = process.env.WORKSPACE;

    if (!env) {
      logger.critical("ENVIRONMENT environment variable is not set");
      throw new Error("ENVIRONMENT environment variable must be set");
    }

    const tableName = `ftrs-dos-${env}-ui-session-store`;
    logger.debug("Determined session table name", { tableName, workspace });
    return workspace ? `${tableName}-${workspace}` : tableName;
  }

  static async getSessionSecret(): Promise<string> {
    const logger = getLogger();
    const env = process.env.ENVIRONMENT;
    const workspace = process.env.WORKSPACE;

    if (!env) {
      logger.critical("ENVIRONMENT environment variable is not set");
      throw new Error("ENVIRONMENT environment variable must be set");
    }

    if (env === "local" && process.env.LOCAL_SESSION_SECRET) {
      logger.warn("Using local session secret from environment variable");
      return process.env.LOCAL_SESSION_SECRET;
    }

    const envPrefix = workspace ? `${env}-${workspace}` : env;
    const secretName = `/ftrs-dos/${envPrefix}/ui-session-secret`;
    const secretValue = await getSecret(secretName, { maxAge: 60 });

    if (!secretValue) {
      logger.critical("Session secret not found in Secrets Manager", {
        secretName,
      });
      throw new Error(
        `Session secret not found in Secrets Manager: ${secretName}`,
      );
    }

    logger.debug("Session secret retrieved from Secrets Manager", {
      secretName,
    });
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

export const setupSessionFn = createServerFn({ method: "GET" }).handler(
  buildSession,
);
