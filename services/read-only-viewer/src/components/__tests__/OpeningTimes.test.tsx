import type { OpeningTime } from "@/utils/types";
import { render } from "@testing-library/react";
import OpeningTimes from "../OpeningTimes";

describe("OpeningTimes Component", () => {
  it("renders 'No Opening Times Provided' when openingTime is empty", () => {
    const { getByText } = render(<OpeningTimes openingTime={[]} />);
    expect(getByText("No Opening Times Provided")).toBeInTheDocument();
  });

  it("renders categorized opening times correctly", () => {
    const openingTime: OpeningTime[] = [
      {
        id: "testID",
        category: "availableTime",
        dayOfWeek: "mon",
        startTime: "09:00",
        endTime: "17:00",
        allDay: false,
      },
      {
        id: "testID",
        category: "notAvailable",
        description: "Holiday",
        unavailableDate: "2023-12-25",
      },
    ];
    const { getByText } = render(<OpeningTimes openingTime={openingTime} />);
    expect(getByText("AvailableTime")).toBeInTheDocument();
    expect(getByText("mon 09:00 - 17:00")).toBeInTheDocument();
    expect(getByText("NotAvailable")).toBeInTheDocument();
    expect(getByText("Holiday 2023-12-25")).toBeInTheDocument();
  });

  it("renders multiple entries for the same category", () => {
    const openingTime: OpeningTime[] = [
      {
        id: "testID1",
        category: "availableTime",
        dayOfWeek: "mon",
        startTime: "09:00",
        endTime: "17:00",
        allDay: false,
      },
      {
        id: "testID2",
        category: "availableTime",
        dayOfWeek: "tue",
        startTime: "10:00",
        endTime: "16:00",
        allDay: true,
      },
    ];
    const { getByText } = render(<OpeningTimes openingTime={openingTime} />);
    expect(getByText("AvailableTime")).toBeInTheDocument();
    expect(
      getByText("mon 09:00 - 17:00, tue 10:00 - 16:00"),
    ).toBeInTheDocument();
  });

  it("renders correctly when openingTime contains only one category", () => {
    const openingTime: OpeningTime[] = [
      {
        id: "testID2",
        category: "availableTime",
        dayOfWeek: "tue",
        startTime: "10:00",
        endTime: "16:00",
        allDay: true,
      },
    ];
    const { getByText } = render(<OpeningTimes openingTime={openingTime} />);
    expect(getByText("AvailableTime")).toBeInTheDocument();
    expect(getByText("tue 10:00 - 16:00")).toBeInTheDocument();
  });
});
