import type { Organisation } from '@/utils/types'
import { createFileRoute, Link } from '@tanstack/react-router'
import { Breadcrumb, Table } from 'nhsuk-react-components'
import { createColumnHelper, useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table'
import RequestErrorDetails from '@/components/RequestErrorDetails'
import type { ResponseError } from '@/utils/errors'
import { useOrganisationsQuery } from '@/hooks/queryHooks'

export const Route = createFileRoute('/organisations/')({
  component: RouteComponent,
})


const columnHelper = createColumnHelper<Organisation>();

const OrganisationsDataTable: React.FC<{ data: Organisation[] }> = ({ data }) => {
  const table = useReactTable({
    data: data,
    columns: [
      columnHelper.accessor('name', {
        cell: info => <Link to="/organisations/$organisationID" params={{ organisationID: info.row.id }} className="nhsuk-link nhsuk-link--no-visited-state">{info.getValue()}</Link>,
        header: () => "Name",
        footer: props => props.column.id,
      }),
      columnHelper.accessor('identifier_ODS_ODSCode', {
        cell: info => info.getValue(),
        header: () => "ODS Code",
        footer: props => props.column.id,
      })
    ],
    getCoreRowModel: getCoreRowModel(),
    getRowId: row => row.id,
  })

  return (
    <Table>
      <Table.Head>
        {table.getHeaderGroups().map(headerGroup => (
          <Table.Row key={headerGroup.id}>
            {headerGroup.headers.map(header => (
              <Table.Cell key={header.id} colSpan={header.colSpan}>
                {header.isPlaceholder ? null : (
                  flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )
                )}
              </Table.Cell>
            ))}
          </Table.Row>
        ))}
      </Table.Head>
      <Table.Body>
        {table.getRowModel().rows.map(row => (
          <Table.Row key={row.id}>
            {row.getVisibleCells().map(cell => (
              <Table.Cell key={cell.id}>
                {flexRender(
                  cell.column.columnDef.cell,
                  cell.getContext()
                )}
              </Table.Cell>
            ))}
          </Table.Row>
        ))}
      </Table.Body>
    </Table >
  )
}

function RouteComponent() {
  const { data, isLoading, isError, error } = useOrganisationsQuery();

  return (
    <>
      <Breadcrumb className="nhsuk-u-margin-bottom-3">
        <Breadcrumb.Back asElement={Link} to="/">Back</Breadcrumb.Back>
        <Breadcrumb.Item asElement={Link} to="/" className="nhsuk-link--no-visited-state">
          Home
        </Breadcrumb.Item>
        <Breadcrumb.Item asElement={Link} to="/organisations" className="nhsuk-link--no-visited-state">
          Organisations
        </Breadcrumb.Item>
      </Breadcrumb>
      <h1 className="nhsuk-heading-l">Organisations</h1>
      {isLoading && <p>Loading organisations...</p>}
      {isError && (
        <RequestErrorDetails error={error as ResponseError} />
      )}
      {data && data.length > 0 && (
        <OrganisationsDataTable data={data} />
      )}
    </>
  )
}
