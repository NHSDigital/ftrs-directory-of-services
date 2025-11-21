export const SESSION_COOKIE_NAME = "dos-ui-session";
export const SESSION_COOKIE_MAX_AGE =
  Number(process.env.SESSION_COOKIE_MAX_AGE) || 60 * 60 * 1000; // 1 hour
export const SESSION_TIMEOUT_MS =
  Number(process.env.SESSION_TIMEOUT_MS) || 60 * 60 * 1000; // 1 hour
