import zod from 'zod';

export const endpointSchema = zod.object({
  id: zod.string().uuid(),
  identifier_oldDoS_id: zod.number().optional(),
  status: zod.string(),
  connectionType: zod.string(),
  name: zod.string().nullable(),
  format: zod.string().nullable(),
  description: zod.string(),
  payloadType: zod.string().nullable(),
  address: zod.string(),
  managedByOrganisationId: zod.string().uuid(),
  service: zod.string().uuid().optional(),
  order: zod.number(),
  isCompressionEnabled: zod.boolean(),
  createdBy: zod.string(),
  createdDateTime: zod.string().datetime(),
  modifiedBy: zod.string(),
  modifiedDateTime: zod.string().datetime(),
})

export type Endpoint = zod.infer<typeof endpointSchema>;

const organisationSchema = zod.object({
  id: zod.string().uuid(),
  identifier_ODS_ODSCode: zod.string().optional(),
  active: zod.boolean(),
  name: zod.string(),
  type: zod.string(),
  telecom: zod.string().optional(),
  endpoints: zod.array(endpointSchema),
  createdBy: zod.string(),
  createdDateTime: zod.string().datetime(),
  modifiedBy: zod.string(),
  modifiedDateTime: zod.string().datetime(),
})

export type Organisation = zod.infer<typeof organisationSchema>;
