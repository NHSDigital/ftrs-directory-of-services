import { z } from "zod/v4";

export const UserInfoSchema = z.object({
  uid: z.string(),
  selectedRoleID: z.string(),
  name: z.string(),
  givenName: z.string(),
  familyName: z.string(),
  displayName: z.string(),
  rbacRoles: z.array(
    z.object({
      personOrgID: z.string(),
      personRoleID: z.string(),
      orgCode: z.string(),
      roleName: z.string(),
    }),
  ),
  orgMemberships: z.array(
    z.object({
      personOrgID: z.string(),
      orgName: z.string(),
      orgCode: z.string(),
    }),
  ),
  userOrgs: z.array(
    z.object({
      orgCode: z.string(),
      orgName: z.string(),
    }),
  ),
});

export type UserInfo = z.infer<typeof UserInfoSchema>;

export const CIS2TokenSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string().optional(),
  id_token: z.string(),
  token_type: z.string(),
  expires_in: z.number(),
});

export type CIS2Token = z.infer<typeof CIS2TokenSchema>;

export const APIMTokenSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string().optional(),
  token_type: z.string(),
  expires_in: z.number(),
});

export type APIMToken = z.infer<typeof APIMTokenSchema>;

export const UserSessionSchema = z.object({
  sessionID: z.uuid(),
  state: z.string(),
  expires: z.number(),
  userID: z.string().optional(),
  user: UserInfoSchema.optional(),
  tokens: z.object({
    cis2: CIS2TokenSchema.optional(),
    apim: APIMTokenSchema.optional(),
  }),
});

export type UserSession = z.infer<typeof UserSessionSchema>;

export const ClientSessionSchema = z.object({
  sessionID: z.uuid(),
  expires: z.number(),
  userID: z.string().optional(),
  user: UserInfoSchema.optional(),
});

export type ClientSession = z.infer<typeof ClientSessionSchema>;
