import { ResponseError } from "@/utils/errors";
import type { Organisation } from "@/utils/types";
import { useQuery } from "@tanstack/react-query";

export const useOrganisationQuery = (organisationId: string) => {
  return useQuery<Organisation>({
    queryKey: ["organisation", organisationId],
    queryFn: async () => {
      const response = await fetch(`/api/organisations/${organisationId}/`);
      if (!response.ok) {
        throw ResponseError.fromResponse(
          response,
          `Failed to fetch organisation data for ID: ${organisationId}`
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
      const response = await fetch("/api/organisations/");
      if (!response.ok) {
        throw ResponseError.fromResponse(
          response,
          "Failed to fetch organisations data"
        );
      }

      const data = await response.json();
      return data;
    },
  });
};
