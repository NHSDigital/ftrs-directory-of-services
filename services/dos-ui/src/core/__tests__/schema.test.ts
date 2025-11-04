import { describe, expect, it } from "vitest";
import {
  type ClientSession,
  ClientSessionSchema,
  type UserInfo,
  UserInfoSchema,
  type UserSession,
  UserSessionSchema,
} from "../schema";

describe("UserInfoSchema", () => {
  const validData: UserInfo = {
    uid: "12345",
    selectedRoleID: "role-1",
    name: "John Doe",
    givenName: "John",
    familyName: "Doe",
    displayName: "Johnny",
    rbacRoles: [
      {
        personOrgID: "org-1",
        personRoleID: "role-1",
        orgCode: "ORG001",
        roleName: "Admin",
      },
    ],
    orgMemberships: [
      {
        personOrgID: "org-1",
        orgName: "Organization One",
        orgCode: "ORG001",
      },
    ],
    userOrgs: [
      {
        orgCode: "ORG001",
        orgName: "Organization One",
      },
    ],
  };

  it("should validate user info structure", () => {
    const parsedData = UserInfoSchema.parse(validData);
    expect(parsedData).toEqual(validData);
  });

  it("should throw an error for invalid user info structure", () => {
    const invalidData = {
      ...validData,
      uid: 12345, // Invalid type
    };

    expect(() =>
      UserInfoSchema.parse(invalidData),
    ).toThrowErrorMatchingInlineSnapshot(`
      [ZodError: [
        {
          "expected": "string",
          "code": "invalid_type",
          "path": [
            "uid"
          ],
          "message": "Invalid input: expected string, received number"
        }
      ]]
    `);
  });

  it("should throw an error for missing required fields", () => {
    const invalidData = {
      ...validData,
    };
    // @ts-expect-error Testing missing field
    delete invalidData.name;

    expect(() =>
      UserInfoSchema.parse(invalidData),
    ).toThrowErrorMatchingInlineSnapshot(`
      [ZodError: [
        {
          "expected": "string",
          "code": "invalid_type",
          "path": [
            "name"
          ],
          "message": "Invalid input: expected string, received undefined"
        }
      ]]
    `);
  });
});

describe("UserSessionSchema", () => {
  const validSessionData: UserSession = {
    sessionID: "1645a835-e830-41df-b8ee-5f2e0d541635",
    state: "random-state",
    expiresAt: 1716239022,
    tokens: {
      cis2: undefined,
      apim: undefined,
    },
  };

  it("should validate user session structure", () => {
    expect(UserSessionSchema.parse(validSessionData)).toEqual(validSessionData);
  });

  it("should accept user information", () => {
    const sessionDataWithUser: UserSession = {
      ...validSessionData,
      userID: "12345",
      user: {
        uid: "12345",
        selectedRoleID: "role-1",
        name: "John Doe",
        givenName: "John",
        familyName: "Doe",
        displayName: "Johnny",
        rbacRoles: [],
        orgMemberships: [],
        userOrgs: [],
      },
      tokens: {
        cis2: {
          access_token: "some-access-token",
          id_token: "some-id-token",
          token_type: "Bearer",
          expires_in: 3600,
        },
        apim: {
          access_token: "some-apim-access-token",
          token_type: "Bearer",
          expires_in: 3600,
        },
      },
    };

    expect(UserSessionSchema.parse(sessionDataWithUser)).toEqual(
      sessionDataWithUser,
    );
  });

  it("should throw an error for invalid sessionID format", () => {
    const invalidSessionData = {
      ...validSessionData,
      sessionID: "invalid-uuid",
    };

    expect(() => UserSessionSchema.parse(invalidSessionData)).toThrowError(
      "Invalid UUID",
    );
  });

  it("should throw an error for missing required fields", () => {
    const invalidSessionData = {
      ...validSessionData,
    };
    // @ts-expect-error Testing missing field
    delete invalidSessionData.state;

    expect(() =>
      UserSessionSchema.parse(invalidSessionData),
    ).toThrowErrorMatchingInlineSnapshot(`
      [ZodError: [
        {
          "expected": "string",
          "code": "invalid_type",
          "path": [
            "state"
          ],
          "message": "Invalid input: expected string, received undefined"
        }
      ]]
    `);
  });
});

describe("ClientSessionSchema", () => {
  // Additional tests for ClientSessionSchema can be added here
  const validClientSessionData: ClientSession = {
    sessionID: "1645a835-e830-41df-b8ee-5f2e0d541635",
    expiresAt: 1716239022,
    state: "random-state",
  };

  it("should validate client session structure", () => {
    expect(ClientSessionSchema.parse(validClientSessionData)).toEqual(
      validClientSessionData,
    );
  });

  it("should accept user information", () => {
    const clientSessionDataWithUser: ClientSession = {
      ...validClientSessionData,
      userID: "12345",
      user: {
        uid: "12345",
        selectedRoleID: "role-1",
        name: "John Doe",
        givenName: "John",
        familyName: "Doe",
        displayName: "Johnny",
        rbacRoles: [],
        orgMemberships: [],
        userOrgs: [],
      },
    };

    expect(ClientSessionSchema.parse(clientSessionDataWithUser)).toEqual(
      clientSessionDataWithUser,
    );
  });
});
