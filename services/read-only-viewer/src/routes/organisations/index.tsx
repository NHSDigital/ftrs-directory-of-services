import DataTable from "@/components/DataTable";
import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import RequestErrorDetails from "@/components/RequestErrorDetails";
import { useOrganisationsQuery } from "@/hooks/queryHooks";
import type { ResponseError } from "@/utils/errors";
import type { Organisation } from "@/utils/types";
import { Link, createFileRoute } from "@tanstack/react-router";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useMemo } from "react";

const OrganisationsPage: React.FC = () => {
  const { data, isLoading, isError, error } = useOrganisationsQuery();

  return (
    <>
      <PageBreadcrumbs
        backTo="/"
        items={[
          { to: "/", label: "Home" },
          { to: "/organisations", label: "Organisations" },
        ]}
      />
      <h1 className="nhsuk-heading-l">Organisations</h1>
      {isLoading && <p>Loading organisations...</p>}
      {isError && <RequestErrorDetails error={error as ResponseError} />}
      {data && data.length > 0 && <OrganisationsDataTable data={data} />}
    </>
  );
};

const useOrganisationsTable = (data: Organisation[]) => {
  const columnHelper = useMemo(() => createColumnHelper<Organisation>(), []);
  return useReactTable({
    data: data,
    columns: [
      columnHelper.accessor("name", {
        cell: (info) => (
          <Link
            to="/organisations/$organisationID"
            params={{ organisationID: info.row.id }}
            className="nhsuk-link nhsuk-link--no-visited-state"
          >
            {info.getValue()}
          </Link>
        ),
        header: () => "Name",
        footer: (props) => props.column.id,
      }),
      columnHelper.accessor("identifier_ODS_ODSCode", {
        cell: (info) => info.getValue(),
        header: () => "ODS Code",
        footer: (props) => props.column.id,
      }),
    ],
    getCoreRowModel: getCoreRowModel(),
    getRowId: (row) => row.id,
  });
};

const OrganisationsDataTable: React.FC<{ data: Organisation[] }> = ({
  data,
}) => {
  const table = useOrganisationsTable(data);
  return <DataTable table={table} />;
};

export const Route = createFileRoute("/organisations/")({
  component: OrganisationsPage,
  head: () => ({
    meta: [{ title: "Organisations - FtRS Read Only Viewer" }],
  }),
});
