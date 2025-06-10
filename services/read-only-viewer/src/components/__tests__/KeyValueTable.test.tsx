import { render } from "@testing-library/react";
import KeyValueTable from "../KeyValueTable";

describe("KeyValueTable", () => {

  const mockItems = [
    { key: "Key 1", value: "Value 1" },
    { key: "Key 2", value: "Value 2" },
    { key: "Key 3", value: null },
    { key: "Key 4", value: undefined },
    { key: "Key 5", value: "Value 5" },
  ];

  it("renders key-value pairs correctly", () => {
    const { container } = render(<KeyValueTable items={mockItems} />);

    const summaryListRows = container.querySelectorAll("div.nhsuk-summary-list__row");
    expect(summaryListRows.length).toBe(mockItems.length);

    mockItems.forEach((item, idx) => {
      const summaryListRow = summaryListRows[idx];

      const keyElement = summaryListRow.querySelector("dt.nhsuk-summary-list__key");
      expect(keyElement).toBeInTheDocument();
      expect(keyElement?.textContent).toBe(item.key);

      const valueElement = summaryListRow.querySelector("dd.nhsuk-summary-list__value");
      expect(valueElement).toBeInTheDocument();
      if (item.value !== null && item.value !== undefined) {
        expect(valueElement?.textContent).toBe(item.value);
      } else {
        expect(valueElement?.textContent).toBe("None Provided");
      }
    });
  });
});
