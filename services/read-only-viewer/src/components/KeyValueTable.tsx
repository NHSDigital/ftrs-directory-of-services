import { SummaryList } from "nhsuk-react-components";
import type { ReactNode } from "react";

type KeyValueTableProps = {
  items: Array<{
    key: string;
    value: ReactNode;
  }>;
};

const KeyValueTable: React.FC<KeyValueTableProps> = ({ items }) => {
  return (
    <SummaryList>
      {items.map((item) => (
        <SummaryList.Row key={item.key}>
          <SummaryList.Key>{item.key}</SummaryList.Key>
          <SummaryList.Value>
            {item.value !== null && item.value !== undefined
              ? item.value
              : "None Provided"}
          </SummaryList.Value>
        </SummaryList.Row>
      ))}
    </SummaryList>
  );
};

export default KeyValueTable;
