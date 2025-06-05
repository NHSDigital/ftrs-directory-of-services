import { ResponseError } from "@/utils/errors";
import type { Organisation } from "@/utils/types";
import { useQuery } from "@tanstack/react-query";

export const useOrganisationQuery = (organisationID: string) => {
  return useQuery<Organisation>({
    queryKey: ["organisation", organisationID],
    queryFn: async () => {
      const response = await fetch(`/api/organisations/${organisationID}/`);
      if (!response.ok) {
        throw new ResponseError(
          `Failed to fetch organisation: ${response.status} ${response.statusText}`,
          response.status,
          Object.fromEntries(response.headers.entries()),
          await response.text(),
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
        throw new ResponseError(
          `Failed to fetch organisations: ${response.status} ${response.statusText}`,
          response.status,
          Object.fromEntries(response.headers.entries()),
          await response.json(),
        );
      }

      const data = await response.json();
      return data;
    },
  });
};
