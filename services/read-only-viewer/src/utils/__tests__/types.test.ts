import { organisationSchema, endpointSchema } from "../types";

describe("organisationSchema", () => {
  it("validates a valid organisation object", () => {
    const validOrganisation = {
      id: "e2f1d47c-a72b-431c-ad99-5e943d450f34",
      identifier_ODS_ODSCode: "ODS1",
      active: true,
      name: "Organisation 1",
      type: "Type A",
      telecom: "1234567890",
      endpoints: [],
      createdBy: "user1",
      createdDateTime: "2023-01-01T00:00:00Z",
      modifiedBy: "user2",
      modifiedDateTime: "2023-01-02T00:00:00Z"
    };

    expect(organisationSchema.safeParse(validOrganisation).success).toBe(true);
  });

  it("rejects an invalid organisation object", () => {
    const invalidOrganisation = {
      id: "invalid-uuid", // Invalid: id should be a valid UUID
      identifier_ODS_ODSCode: "ODS1",
      active: true,
      name: undefined, // Invalid: name should be a string
      type: undefined, // Invalid: type should be a string
      telecom: "1234567890",
      endpoints: [],
      createdBy: "user1",
      createdDateTime: "2023-01-01T00:00:00Z",
      modifiedBy: "user2",
      modifiedDateTime: "2023-01-02T00:00:00Z"
    };

    const result = organisationSchema.safeParse(invalidOrganisation);
    expect(result.success).toBe(false);
    expect(result.error?.issues).toEqual([
      {
        code: "invalid_string",
        message: "Invalid uuid",
        path: ["id"],
        validation: "uuid"
      },
      {
        code: "invalid_type",
        expected: "string",
        message: "Required",
        path: ["name"],
        received: "undefined"
      },
      {
        code: "invalid_type",
        expected: "string",
        message: "Required",
        path: ["type"],
        received: "undefined"
      }
    ])
  });
});

describe("endpointSchema", () => {
  it("validates a valid endpoint object", () => {
    const validEndpoint = {
      id: "f7374aac-a6da-4bfb-96af-da382cc0f145",
      identifier_oldDoS_id: 123,
      status: "active",
      connectionType: "type1",
      name: "Endpoint 1",
      format: "json",
      description: "Test endpoint",
      payloadType: "application/json",
      address: "https://example.com/endpoint",
      managedByOrganisation: "84205e46-52e1-46d0-92a7-51685cd7011c",
      order: 1,
      isCompressionEnabled: true,
      createdBy: "user1",
      createdDateTime: "2023-01-01T00:00:00Z",
      modifiedBy: "user2",
      modifiedDateTime: "2023-01-02T00:00:00Z"
    };

    expect(endpointSchema.safeParse(validEndpoint).success).toBe(true);
  });

  it("rejects an invalid endpoint object", () => {
    const invalidEndpoint = {
      id: "invalid-uuid", // Invalid UUID
      identifier_oldDoS_id: undefined, // Invalid type
      status: 123, // Invalid type
      connectionType: null, // Invalid type
      name: undefined, // Invalid type
      format: null, // Invalid type
      description: "Test endpoint",
      payloadType: undefined, // Invalid type
      address: "https://example.com/endpoint",
      managedByOrganisation: "e2f1d47c-a72b-431c-ad99-5e943d450f34",
      order: -1, // Invalid value (should be non-negative)
      isCompressionEnabled: true,
      createdBy: "user1",
      createdDateTime: "2023-01-01T00:00:00Z",
      modifiedBy: "user2",
      modifiedDateTime: "2023-01-02T00:00:00Z"
    };

    const result = endpointSchema.safeParse(invalidEndpoint);
    expect(result.success).toBe(false);
    expect(result.error?.issues).toEqual([
      {
        validation: 'uuid',
        code: 'invalid_string',
        message: 'Invalid uuid',
        path: [ 'id' ]
      },
      {
        code: 'invalid_type',
        expected: 'string',
        received: 'number',
        path: [ 'status' ],
        message: 'Expected string, received number'
      },
      {
        code: 'invalid_type',
        expected: 'string',
        received: 'null',
        path: [ 'connectionType' ],
        message: 'Expected string, received null'
      },
      {
        code: 'invalid_type',
        expected: 'string',
        received: 'undefined',
        path: [ 'name' ],
        message: 'Required'
      },
      {
        code: 'invalid_type',
        expected: 'string',
        received: 'undefined',
        path: [ 'payloadType' ],
        message: 'Required'
      },
      {
        code: 'too_small',
        minimum: 0,
        type: 'number',
        inclusive: false,
        exact: false,
        message: 'Number must be greater than 0',
        path: [ 'order' ]
      }
    ])
  });
});
