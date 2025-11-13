import {createFileRoute} from '@tanstack/react-router'
import * as client from 'openid-client';
import {getLogger} from "@/utils/logger";
import {getOIDCConfig} from "@/utils/cis2Configuration.ts";
import {CIS2TokenSchema, UserInfoSchema} from "@/core/schema.ts";
import {SessionManager} from "@/core/session.ts";
import {useSession} from "@tanstack/react-start/server";
import {SESSION_COOKIE_MAX_AGE, SESSION_COOKIE_NAME} from "@/core/constants.ts";



export const Route = createFileRoute('/api/auth/callback')({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const url = new URL(request.url);
        const code = url.searchParams.get('code');
        const state = url.searchParams.get('state');
        const logger = getLogger();

        if (!code || !state) {
          logger.error("Missing code or state parameter from callback URL");
          throw new Error("Missing code or state parameter from callback URL");
        }
        const cookieSession = await useSession({
          name: SESSION_COOKIE_NAME,
          password: await SessionManager.getSessionSecret(),
          maxAge: SESSION_COOKIE_MAX_AGE,
        });
        if (!cookieSession.data || !cookieSession.data.sessionID) {
          logger.error("[SERVER] No session ID found in cookie");
          throw new Error("No session ID found in cookie");
        }
        const sessionID = cookieSession.data.sessionID;
        const sessionState = cookieSession.data.state;

        const manager = new SessionManager();
        const userSession = await manager.getSession(sessionID);

        if (!userSession || userSession.expiresAt < Date.now() || (userSession.state !== state && userSession.state !== sessionState)) {
          logger.error("[SERVER] Session not found in DynamoDB or it has expired or state mismatch", {
            sessionID,
            requestedState: state
          });
          throw new Error("Session not found in DynamoDB or it has expired or state mismatch");
        }
        try {
          const oidcConfig = await getOIDCConfig();
          const tokens = await client.authorizationCodeGrant(
            oidcConfig,
            url,
            {
              expectedState: state,
            }
          );

          // Parse and validate tokens
          const cis2Tokens = CIS2TokenSchema.parse(tokens);
          logger.info("[SERVER] Successfully exchanged authorization code for tokens");
          // Fetch user info
          const claims = tokens.claims();
          const userinfo = await client.fetchUserInfo(oidcConfig, tokens.access_token, claims?.sub ?? '');

          logger.info("[SERVER] Userinfo received", {
            sub: userinfo.sub,
            name: userinfo.name,
            email: userinfo.email
          });
          const user = await parseUserinfo(userinfo);
          userSession.userID = userinfo.sub as string;
          userSession.user = user;
          userSession.tokens.cis2 = cis2Tokens;
          await manager.updateSession(userSession);
          logger.debug("Session updated successfully with user details");

          const headers = new Headers();
          headers.set('Location', '/dashboard');

          return new Response(null, {
            status: 302,
            headers: headers,
          });
        } catch (error) {
          const details = errorDetails(error);
          logger.error("Token exchange failed", details);
          throw error;
        }
      },
    },
  },
})

async function parseUserinfo(userinfo: any) {
  // Extract NHS ID claims as arrays
  const nhsidRoles = Array.isArray(userinfo.nhsid_nrbac_roles) ? userinfo.nhsid_nrbac_roles : [];
  const nhsidOrgMemberships = Array.isArray(userinfo.nhsid_org_memberships) ? userinfo.nhsid_org_memberships : [];
  const nhsidUserOrgs = Array.isArray(userinfo.nhsid_user_orgs) ? userinfo.nhsid_user_orgs : [];

  const firstRole = nhsidRoles[0] as any;

  // Parse user info into the expected schema
  const user = UserInfoSchema.parse({
    uid: userinfo.sub,
    selectedRoleID: firstRole?.person_roleid || '',
    displayName: userinfo.name || `${userinfo.given_name || ''} ${userinfo.family_name || ''}`.trim(),
    rbacRoles: nhsidRoles.map((role: any) => ({
      personOrgID: role.person_orgid || '',
      personRoleID: role.person_roleid || '',
      orgCode: role.org_code || '',
      roleName: role.role_name || '',
    })),
    orgMemberships: nhsidOrgMemberships.map((org: any) => ({
      personOrgID: org.person_orgid || '',
      orgName: org.org_name || '',
      orgCode: org.org_code || '',
    })),
    userOrgs: nhsidUserOrgs.map((org: any) => ({
      orgCode: org.org_code || '',
      orgName: org.org_name || '',
    })),
  });

  return user

}

function errorDetails(error: any) {
  // Capture comprehensive error details
  const details: any = {
    message: error instanceof Error ? error.message : 'Unknown error',
    stack: error instanceof Error ? error.stack : undefined,
    errorType: error?.constructor?.name,
  };

  // Check if this is an OAuth error response with body
  if (error && typeof error === 'object') {
    const err = error as any;

    // Log all available error properties
    details.errorProperties = Object.keys(err);

    // Common OAuth/OIDC error properties
    if (err.error) details.error = err.error;
    if (err.error_description) details.error_description = err.error_description;
    if (err.error_uri) details.error_uri = err.error_uri;

    // HTTP response details if available
    if (err.response) {
      details.response = {
        status: err.response.status,
        statusText: err.response.statusText,
        headers: err.response.headers,
        body: err.response.body,
      };
    }

    // Body/data from the error
    if (err.body) details.body = err.body;
    if (err.data) details.data = err.data;

    // Status code if present
    if (err.status) details.status = err.status;
    if (err.statusCode) details.statusCode = err.statusCode;

    // URL that was called
    if (err.url) details.url = err.url;
    if (err.config?.url) details.requestUrl = err.config.url;
  }
  return details;
}
