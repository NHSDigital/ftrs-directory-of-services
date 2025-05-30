import type { ResponseError } from "@/utils/errors";
import { Details, ErrorSummary } from "nhsuk-react-components";

type RequestErrorDetailsProps = {
  error: ResponseError;
}

const RequestErrorDetails: React.FC<RequestErrorDetailsProps> = ({ error }) => {
  return (
    <ErrorSummary>
      <ErrorSummary.Title>
        Something went wrong
      </ErrorSummary.Title>
      <ErrorSummary.Body>
        <p>There was an error while processing your request. Please try again later.</p>
        <Details open>
          <Details.Summary>Error Details</Details.Summary>
          <Details.Text>
            <p className="nhsuk-u-margin-bottom-1">
              <span className="nhsuk-u-font-weight-bold">Status Code:</span> {error?.status}
            </p>
            <p className="nhsuk-u-font-weight-bold nhsuk-u-margin-bottom-1">Message: </p>
            <pre
              className="nhsuk-u-padding-3 nhsuk-u-margin-top-0" style={{ backgroundColor: "#dedede", border: "2px solid #aaa", overflow: "scroll" }}>{JSON.stringify(error?.message, null, 2)}</pre>
            <p className="nhsuk-u-font-weight-bold nhsuk-u-margin-bottom-1">Headers: </p>
            <pre className="nhsuk-u-padding-3 nhsuk-u-margin-top-0" style={{ backgroundColor: "#dedede", border: "2px solid #aaa", overflow: "scroll" }}>{JSON.stringify(error?.headers, null, 2)}</pre>
            <p className="nhsuk-u-font-weight-bold nhsuk-u-margin-bottom-1">Response Body: </p>
            <pre className="nhsuk-u-padding-3 nhsuk-u-margin-top-0" style={{ backgroundColor: "#dedede", border: "2px solid #aaa", overflow: "scroll" }}>{error?.body}</pre>
          </Details.Text>
        </Details>
      </ErrorSummary.Body>
    </ErrorSummary>
  );
}

export default RequestErrorDetails;
