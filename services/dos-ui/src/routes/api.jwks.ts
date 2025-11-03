import { createFileRoute } from "@tanstack/react-router";
import { getCIS2PublicKey } from "@/utils/api-jwksUtil.ts";

export const Route = createFileRoute("/api/jwks")({
  server: {
    handlers: {
      GET: async () => {
        try {
          const cis2PublicKey = await getCIS2PublicKey();
          return new Response(JSON.stringify({ key: cis2PublicKey }));
        } catch (error) {
          return new Response(
            JSON.stringify({ message: "Error retrieving JWKS" }),
            { status: 500 },
          );
        }
      },
    },
  },
});
