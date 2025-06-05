import { Container, Tag } from "nhsuk-react-components";
import type { PropsWithChildren } from "react";

type BannerProps = PropsWithChildren<{
  label: string;
}>;

const Banner: React.FC<BannerProps> = ({ label, children }) => {
  return (
    <Container>
      <p className="nhsuk-u-margin-top-3 nhsuk-u-margin-bottom-3 nhsuk-u-font-size-19">
        <Tag className="nhsuk-u-margin-right-3">{label.toUpperCase()}</Tag>
        {children}
      </p>
      <hr className="nhsuk-section-break nhsuk-section-break--s nhsuk-section-break--visible" />
    </Container>
  );
};

export default Banner;
