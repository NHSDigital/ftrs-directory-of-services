import { ResponseError } from "@/utils/errors";
import type { HealthcareService, Organisation } from "@/utils/types";
import { useQuery } from "@tanstack/react-query";

export const useOrganisationQuery = (organisationId: string) => {
  return useQuery<Organisation>({
    queryKey: ["organisation", organisationId],
    queryFn: async () => {
      const response = await fetch(`/api/organisation/${organisationId}/`);

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw ResponseError.fromResponse(
          response,
          `Failed to fetch organisation data for ID: ${organisationId}`,
        );
      }
      return await response.json();
    },
  });
};

export const useOrganisationsQuery = () => {
  return useQuery<Organisation[]>({
    queryKey: ["organisations"],
    queryFn: async () => {
      const response = await fetch("/api/organisation/");
      if (!response.ok) {
        throw ResponseError.fromResponse(
          response,
          "Failed to fetch organisations data",
        );
      }

      const data = await response.json();
      return data;
    },
  });
};

export const useHealthcareServiceQuery = (healthcareServiceId: string) => {
  return useQuery<HealthcareService>({
    queryKey: ["healthcareService", healthcareServiceId],
    queryFn: async () => {
      const response = await fetch(
        `/api/healthcareService/${healthcareServiceId}/`,
      );

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw ResponseError.fromResponse(
          response,
          `Failed to fetch healthcare service data for ID: ${healthcareServiceId}`,
        );
      }
      return await response.json();
    },
  });
};
export const useHealthcareServicesQuery = () => {
  return useQuery<HealthcareService[]>({
    queryKey: ["healthcareServices"],
    queryFn: async () => {
      const response = await fetch("/api/healthcareService/");
      if (!response.ok) {
        throw ResponseError.fromResponse(
          response,
          "Failed to fetch healthcare services data",
        );
      }

      const data = await response.json();
      return data;
    },
  });
};
