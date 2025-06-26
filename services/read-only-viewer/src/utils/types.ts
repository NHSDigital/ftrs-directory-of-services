import zod from "zod";

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
  managedByOrganisation: zod.string().uuid(),
  service: zod.string().uuid().optional(),
  order: zod.number().positive(),
  isCompressionEnabled: zod.boolean(),
  createdBy: zod.string(),
  createdDateTime: zod.string().datetime(),
  modifiedBy: zod.string(),
  modifiedDateTime: zod.string().datetime(),
});

export type Endpoint = zod.infer<typeof endpointSchema>;

export const organisationSchema = zod.object({
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
});

export type Organisation = zod.infer<typeof organisationSchema>;

export const Telecom = zod.object({
  phone_public: zod.string().optional(),
  phone_private: zod.string().optional(),
  email: zod.string().email().optional(),
  website: zod.string().url().optional(),
})

const openingTimeSchema = zod.discriminatedUnion("category", [
  zod.object({
    id: zod.string().uuid(),
    category: zod.literal("availableTime"),
    dayOfWeek: zod.enum(["mon", "tue", "wed", "thu", "fri", "sat", "sun"]),
    startTime: zod.string(),
    endTime: zod.string(),
    allDay: zod.boolean().default(false),
  }),
  zod.object({
    id: zod.string().uuid(),
    category: zod.literal("availableTimeVariations"),
    description: zod.string(),
    startTime: zod.string().datetime(),
    endTime: zod.string().datetime(),
  }),
  zod.object({
    id: zod.string().uuid(),
    category: zod.literal("availableTimePublicHolidays"),
    startTime: zod.string(),
    endTime: zod.string(),
  }),
  zod.object({
    id: zod.string().uuid(),
    category: zod.literal("notAvailable"),
    description: zod.string(),
    unavailableDate: zod.string(),
  }),
]);

export const healthcareServiceSchema = zod.object({
  id: zod.string().uuid(),
  identifier_oldDoS_uid: zod.string().uuid().optional(),
  active: zod.boolean(),
  category: zod.string().optional(),
  providedBy: zod.string().uuid(),
  location:  zod.string().uuid(),
  name: zod.string(),
  type: zod.string().optional(),
  Telecom: Telecom,
  openingTimes: zod.array(openingTimeSchema).optional(),
});
export type HealthcareService = zod.infer<typeof healthcareServiceSchema>;


