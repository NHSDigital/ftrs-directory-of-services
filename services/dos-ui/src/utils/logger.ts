import { Logger } from "@aws-lambda-powertools/logger";
import { createServerOnlyFn } from "@tanstack/react-start";

/**
 * Common logger instance using AWS Lambda Powertools
 * Provides structured logging with consistent formatting
 */
let GLOBAL_LOGGER: Logger | null = null;

export const getLogger = createServerOnlyFn(() => {
  if (!GLOBAL_LOGGER) {
    GLOBAL_LOGGER = createLogger();
  }
  return GLOBAL_LOGGER;
});

const createLogger = createServerOnlyFn(
  () =>
    new Logger({
      serviceName: process.env.SERVICE_NAME || "dos-ui",
      logLevel:
        (process.env.LOG_LEVEL as "DEBUG" | "INFO" | "WARN" | "ERROR") ||
        "INFO",
      environment: process.env.ENVIRONMENT || "dev",
      persistentLogAttributes: {
        project: process.env.PROJECT || "ftrs-dos",
        workspace: process.env.WORKSPACE || "",
      },
    }),
);

/**
 * Create a child logger with additional context
 * @param context Additional persistent attributes for the child logger
 * @returns Child logger instance
 */
export const createChildLogger = (context: Record<string, unknown>) => {
  return getLogger().createChild({
    persistentLogAttributes: context,
  });
};

/**
 * Log levels enum for convenience
 */
export enum LogLevel {
  DEBUG = "DEBUG",
  INFO = "INFO",
  WARN = "WARN",
  ERROR = "ERROR",
}

export default getLogger;
