import { type Table as TableType, flexRender } from "@tanstack/react-table";
import { Table } from "nhsuk-react-components";
import type { JSX } from "react";

type DataTableProps<T> = {
  table: TableType<T>;
};

const DataTable = <T,>({ table }: DataTableProps<T>): JSX.Element => {
  return (
    <Table>
      <Table.Head>
        {table.getHeaderGroups().map((headerGroup) => (
          <Table.Row key={headerGroup.id}>
            {headerGroup.headers.map((header) => (
              <Table.Cell key={header.id} colSpan={header.colSpan}>
                {flexRender(
                  header.column.columnDef.header,
                  header.getContext(),
                )}
              </Table.Cell>
            ))}
          </Table.Row>
        ))}
      </Table.Head>
      <Table.Body>
        {table.getRowModel().rows.map((row) => (
          <Table.Row key={row.id}>
            {row.getVisibleCells().map((cell) => (
              <Table.Cell key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </Table.Cell>
            ))}
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  );
};

export default DataTable;
