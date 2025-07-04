import type { OpeningTime } from "@/utils/types";
import type React from "react";

const formatters: Record<string, (times: OpeningTime[]) => string> = {
  availableTime: (times) =>
    times
      .filter(
        (time): time is Extract<OpeningTime, { category: "availableTime" }> =>
          time.category === "availableTime",
      )
      .map((time) => `${time.dayOfWeek} ${time.startTime} - ${time.endTime}`)
      .join(", "),
  availableTimeVariations: (times) =>
    times
      .filter(
        (
          time,
        ): time is Extract<
          OpeningTime,
          { category: "availableTimeVariations" }
        > => time.category === "availableTimeVariations",
      )
      .map((time) => `${time.description} ${time.startTime} - ${time.endTime}`)
      .join(", "),
  availableTimePublicHolidays: (times) =>
    times
      .filter(
        (
          time,
        ): time is Extract<
          OpeningTime,
          { category: "availableTimePublicHolidays" }
        > => time.category === "availableTimePublicHolidays",
      )
      .map((time) => `${time.startTime} - ${time.endTime}`)
      .join(", "),
  notAvailable: (times) =>
    times
      .filter(
        (time): time is Extract<OpeningTime, { category: "notAvailable" }> =>
          time.category === "notAvailable",
      )
      .map((time) => `${time.description} ${time.unavailableDate}`)
      .join(", "),
};

const formatOpeningTimes = (category: string, times: OpeningTime[]): string => {
  return (formatters[category] || formatters.default)(times);
};

const OpeningTimes: React.FC<{ openingTime: OpeningTime[] }> = ({
  openingTime,
}) => {
  if (!openingTime?.length) {
    return <p>No Opening Times Provided</p>;
  }

  const categorizedTimes = openingTime.reduce<Record<string, OpeningTime[]>>(
    (acc, time) => {
      const category = time.category;
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(time);
      return acc;
    },
    {},
  );

  return (
    <div aria-label="Opening Times">
      {Object.entries(categorizedTimes).map(([category, times]) => (
        <div key={category} className="nhsuk-u-margin-bottom-4">
          <h4 className="nhsuk-heading-s nhsuk-u-margin-bottom-2">
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </h4>
          <p className="nhsuk-u-font-size-16">
            {formatOpeningTimes(category, times)}
          </p>
        </div>
      ))}
    </div>
  );
};

export default OpeningTimes;
