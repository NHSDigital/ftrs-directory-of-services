import type { ResponseError } from "@/utils/errors";
import { Details, ErrorSummary } from "nhsuk-react-components";

type RequestErrorDetailsProps = {
  error: ResponseError;
};

const RequestErrorDetails: React.FC<RequestErrorDetailsProps> = ({ error }) => {
  return (
    <ErrorSummary>
      <ErrorSummary.Title>Something went wrong</ErrorSummary.Title>
      <ErrorSummary.Body>
        <p>
          There was an error while processing your request. Please try again
          later.
        </p>
        <Details>
          <Details.Summary>Error Details</Details.Summary>
          <Details.Text>
            {error?.correlationId && (
              <p className="nhsuk-u-margin-bottom-1">
                <span className="nhsuk-u-font-weight-bold">
                  Correlation ID:
                </span>{" "}
                {error?.correlationId}
              </p>
            )}
            {error?.status && (
              <p className="nhsuk-u-margin-bottom-1">
                <span className="nhsuk-u-font-weight-bold">Status Code:</span>{" "}
                {error?.status}
              </p>
            )}
            <p className="nhsuk-u-font-weight-bold nhsuk-u-margin-bottom-1">
              Message:{" "}
            </p>
            <pre className="ftrs-code-block">{error?.message}</pre>
            {error?.headers && (
              <>
                <p className="nhsuk-u-font-weight-bold nhsuk-u-margin-bottom-1">
                  Headers:{" "}
                </p>
                <pre className="ftrs-code-block">
                  {JSON.stringify(error?.headers, null, 2)}
                </pre>
              </>
            )}
          </Details.Text>
        </Details>
      </ErrorSummary.Body>
    </ErrorSummary>
  );
};

export default RequestErrorDetails;
