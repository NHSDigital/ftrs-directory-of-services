import { Link } from "@tanstack/react-router";
import { Breadcrumb } from "nhsuk-react-components";

type PageBreadcrumbsProps = {
  backTo: string | null;
  items: Array<{
    label: string;
    to: string;
    params?: Record<string, string>;
  }>;
};

const PageBreadcrumbs: React.FC<PageBreadcrumbsProps> = ({ backTo, items }) => {
  return (
    <Breadcrumb className="nhsuk-u-margin-bottom-3">
      {backTo && (
        <Breadcrumb.Back asElement={Link} to={backTo}>
          Back
        </Breadcrumb.Back>
      )}
      {items.map((item) => (
        <Breadcrumb.Item
          key={item.label}
          asElement={Link}
          to={item.to}
          // @ts-expect-error - TanStack Router expects params to be an object
          params={item.params}
          className="nhsuk-link--no-visited-state"
        >
          {item.label}
        </Breadcrumb.Item>
      ))}
    </Breadcrumb>
  );
};

export default PageBreadcrumbs;
