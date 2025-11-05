import { Logger } from "@aws-lambda-powertools/logger";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@aws-lambda-powertools/logger", () => {
  const mockLoggerInstance = {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    createChild: vi.fn(),
  };

  const MockLogger = vi.fn(() => mockLoggerInstance);

  return {
    Logger: MockLogger,
  };
});

describe("logger utility", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.clearAllMocks();
    // Reset modules to get fresh logger instance
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe("logger initialization", () => {
    it("should create logger with default values", async () => {
      delete process.env.SERVICE_NAME;
      delete process.env.LOG_LEVEL;
      delete process.env.ENVIRONMENT;
      delete process.env.PROJECT;
      delete process.env.WORKSPACE;

      await import("../logger");

      expect(Logger).toHaveBeenCalledWith({
        serviceName: "dos-ui",
        logLevel: "INFO",
        environment: "dev",
        persistentLogAttributes: {
          project: "ftrs-dos",
          workspace: "",
        },
      });
    });

    it("should create logger with environment variables", async () => {
      process.env.SERVICE_NAME = "test-service";
      process.env.LOG_LEVEL = "DEBUG";
      process.env.ENVIRONMENT = "prod";
      process.env.PROJECT = "test-project";
      process.env.WORKSPACE = "test-workspace";

      await import("../logger");

      expect(Logger).toHaveBeenCalledWith({
        serviceName: "test-service",
        logLevel: "DEBUG",
        environment: "prod",
        persistentLogAttributes: {
          project: "test-project",
          workspace: "test-workspace",
        },
      });
    });

    it("should handle WARN log level from environment", async () => {
      process.env.LOG_LEVEL = "WARN";

      await import("../logger");

      expect(Logger).toHaveBeenCalledWith(
        expect.objectContaining({
          logLevel: "WARN",
        }),
      );
    });

    it("should handle ERROR log level from environment", async () => {
      process.env.LOG_LEVEL = "ERROR";

      await import("../logger");

      expect(Logger).toHaveBeenCalledWith(
        expect.objectContaining({
          logLevel: "ERROR",
        }),
      );
    });
  });

  describe("createChildLogger", () => {
    it("should create a child logger with additional context", async () => {
      const { logger, createChildLogger } = await import("../logger");
      const context = { userId: "123", requestId: "abc" };

      createChildLogger(context);

      expect(logger.createChild).toHaveBeenCalledWith({
        persistentLogAttributes: context,
      });
    });

    it("should create child logger with empty context", async () => {
      const { logger, createChildLogger } = await import("../logger");

      createChildLogger({});

      expect(logger.createChild).toHaveBeenCalledWith({
        persistentLogAttributes: {},
      });
    });

    it("should create child logger with nested context", async () => {
      const { logger, createChildLogger } = await import("../logger");
      const context = {
        user: { id: "123", name: "John" },
        request: { id: "abc", method: "GET" },
      };

      createChildLogger(context);

      expect(logger.createChild).toHaveBeenCalledWith({
        persistentLogAttributes: context,
      });
    });
  });

  describe("LogLevel enum", () => {
    it("should export LogLevel enum with correct values", async () => {
      const { LogLevel } = await import("../logger");

      expect(LogLevel.DEBUG).toBe("DEBUG");
      expect(LogLevel.INFO).toBe("INFO");
      expect(LogLevel.WARN).toBe("WARN");
      expect(LogLevel.ERROR).toBe("ERROR");
    });
  });

  describe("logger methods", () => {
    it("should have debug method", async () => {
      const { logger } = await import("../logger");

      expect(logger.debug).toBeDefined();
      expect(typeof logger.debug).toBe("function");
    });

    it("should have info method", async () => {
      const { logger } = await import("../logger");

      expect(logger.info).toBeDefined();
      expect(typeof logger.info).toBe("function");
    });

    it("should have warn method", async () => {
      const { logger } = await import("../logger");

      expect(logger.warn).toBeDefined();
      expect(typeof logger.warn).toBe("function");
    });

    it("should have error method", async () => {
      const { logger } = await import("../logger");

      expect(logger.error).toBeDefined();
      expect(typeof logger.error).toBe("function");
    });

    it("should have createChild method", async () => {
      const { logger } = await import("../logger");

      expect(logger.createChild).toBeDefined();
      expect(typeof logger.createChild).toBe("function");
    });
  });

  describe("default export", () => {
    it("should export logger as default", async () => {
      const module = await import("../logger");

      expect(module.default).toBe(module.logger);
    });
  });
});
