import DataTable from "@/components/DataTable.tsx";
import PageBreadcrumbs from "@/components/PageBreadcrumbs";
import RequestErrorDetails from "@/components/RequestErrorDetails.tsx";
import { useHealthcareServicesQuery } from "@/hooks/queryHooks.ts";
import type { ResponseError } from "@/utils/errors.ts";
import type { HealthcareService } from "@/utils/types.ts";
import { Link, createFileRoute } from "@tanstack/react-router";
import {
  createColumnHelper,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useMemo } from "react";

const HealthCareServicePage: React.FC = () => {
  const { data, isLoading, isError, error } = useHealthcareServicesQuery();
  return (
    <>
      <PageBreadcrumbs
        backTo="/"
        items={[
          { to: "/", label: "Home" },
          { to: "/healthcare-services", label: "Healthcare Services" },
        ]}
      />
      <h1 className="nhsuk-heading-l">Healthcare Services</h1>
      {isLoading && <p>Loading healthcare services...</p>}
      {isError && <RequestErrorDetails error={error as ResponseError} />}
      {data && data.length > 0 && <HealthcareServiceDataTable data={data} />}
    </>
  );
};

const useHealthcareServicesTable = (
  healthcareServices: HealthcareService[],
) => {
  const columnHelper = useMemo(
    () => createColumnHelper<HealthcareService>(),
    [],
  );
  return useReactTable({
    data: healthcareServices,
    columns: [
      columnHelper.accessor("name", {
        cell: (info) => (
          <Link
            to="/healthcare-services/$healthcareServiceID"
            params={{ healthcareServiceID: info.row.id }}
            className="nhsuk-link nhsuk-link--no-visited-state"
          >
            {info.getValue()}
          </Link>
        ),
        header: () => "Name",
        footer: (props) => props.column.id,
      }),
      columnHelper.accessor("type", {
        cell: (info) => info.getValue(),
        header: () => "Type",
        footer: (props) => props.column.id,
      }),
    ],
    getCoreRowModel: getCoreRowModel(),
    getRowId: (row) => row.id,
  });
};
const HealthcareServiceDataTable: React.FC<{ data: HealthcareService[] }> = ({
  data,
}) => {
  const table = useHealthcareServicesTable(data);
  return <DataTable table={table} />;
};

export const Route = createFileRoute("/healthcare-services/")({
  component: HealthCareServicePage,
  head: () => ({
    meta: [{ title: "Healthcare Service - FtRS Read Only Viewer" }],
  }),
});
