import DataTable from "@/components/DataTable.tsx";
import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import RequestErrorDetails from "@/components/RequestErrorDetails.tsx";
import { useLocationsQuery } from "@/hooks/queryHooks.ts";
import type { ResponseError } from "@/utils/errors.ts";
import type { Location } from "@/utils/types.ts";
import { Link, createFileRoute } from "@tanstack/react-router";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useMemo } from "react";

const LocationsPage: React.FC = () => {
  const { data, isLoading, isError, error } = useLocationsQuery();
  return (
    <>
      <PageBreadcrumbs
        backTo="/"
        items={[
          { to: "/", label: "Home" },
          { to: "/locations", label: "Locations" },
        ]}
      />
      <h1 className="nhsuk-heading-l">Locations</h1>
      {isLoading && <p>Loading locations...</p>}
      {isError && <RequestErrorDetails error={error as ResponseError} />}
      {data && data.length > 0 && <LocationsDataTable data={data} />}
    </>
  );
};

const useLocationsTable = (data: Location[]) => {
  const columnHelper = useMemo(() => createColumnHelper<Location>(), []);
  return useReactTable({
    data: data,
    columns: [
      columnHelper.accessor("address.street", {
        cell: (info) => (
          <Link
            to="/locations/$locationID"
            params={{ locationID: info.row.id }}
            className="nhsuk-link nhsuk-link--no-visited-state"
          >
            {info.getValue().replace(/\$/g, ", ")}
          </Link>
        ),
        header: () => "Street",
        footer: (props) => props.column.id,
      }),
      columnHelper.accessor("address.town", {
        cell: (info) => info.getValue(),
        header: () => "Town",
        footer: (props) => props.column.id,
      }),
      columnHelper.accessor("address.postcode", {
        cell: (info) => info.getValue(),
        header: () => "Postcode",
        footer: (props) => props.column.id,
      }),
    ],
    getCoreRowModel: getCoreRowModel(),
    getRowId: (row) => row.id,
  });
};

const LocationsDataTable: React.FC<{ data: Location[] }> = ({ data }) => {
  const table = useLocationsTable(data);
  return <DataTable table={table} />;
};

export const Route = createFileRoute("/locations/")({
  component: LocationsPage,
  head: () => ({
    meta: [{ title: "Location - FtRS Read Only Viewer" }],
  }),
});
