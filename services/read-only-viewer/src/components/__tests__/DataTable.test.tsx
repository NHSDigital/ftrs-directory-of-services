import { render, renderHook } from "@testing-library/react";
import DataTable from "../DataTable";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";

describe("DataTable", () => {
  const mockData = [
    { id: 1, name: "Item 1", value: "Value 1" },
    { id: 2, name: "Item 2", value: "Value 2" },
  ];

  it("renders table headers and rows correctly", () => {
    const tableHook = renderHook(() => useReactTable({
      data: mockData,
      columns: [
        {
          accessorKey: "id",
          header: "ID"
        },
        {
          accessorKey: "name",
          header: "Name"
        },
        {
          accessorKey: "value",
          header: "Value"
        }
      ],
      getCoreRowModel: getCoreRowModel()
    }));

    const headerGroups = tableHook.result.current.getHeaderGroups();
    expect(headerGroups.length).toBe(1);
    expect(headerGroups[0].headers.length).toEqual(3);

    const rowModel = tableHook.result.current.getRowModel();
    expect(rowModel.rows.length).toBe(2);

    const { container } = render(
      <DataTable table={tableHook.result.current} />
    );

    const headers = container.querySelectorAll("th");
    expect(headers.length).toBe(3);

    expect(headers[0].textContent).toBe("ID");
    expect(headers[1].textContent).toBe("Name");
    expect(headers[2].textContent).toBe("Value");

    const rows = container.querySelectorAll("tr");
    expect(rows.length).toBe(3); // 1 header row + 2 data rows

    expect(rows).toMatchInlineSnapshot(`
      NodeList [
        <tr
          class="nhsuk-table__row"
        >
          <th
            class="nhsuk-table__header"
            colspan="1"
            scope="col"
          >
            ID
          </th>
          <th
            class="nhsuk-table__header"
            colspan="1"
            scope="col"
          >
            Name
          </th>
          <th
            class="nhsuk-table__header"
            colspan="1"
            scope="col"
          >
            Value
          </th>
        </tr>,
        <tr
          class="nhsuk-table__row"
        >
          <td
            class="nhsuk-table__cell"
          >
            1
          </td>
          <td
            class="nhsuk-table__cell"
          >
            Item 1
          </td>
          <td
            class="nhsuk-table__cell"
          >
            Value 1
          </td>
        </tr>,
        <tr
          class="nhsuk-table__row"
        >
          <td
            class="nhsuk-table__cell"
          >
            2
          </td>
          <td
            class="nhsuk-table__cell"
          >
            Item 2
          </td>
          <td
            class="nhsuk-table__cell"
          >
            Value 2
          </td>
        </tr>,
      ]
    `)
  })
})
