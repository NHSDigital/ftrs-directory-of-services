import { render } from "@testing-library/react";
import RequestErrorDetails from "../RequestErrorDetails";
import { ResponseError } from "@/utils/errors";

describe("RequestErrorDetails", () => {
  it("renders error details with correct information", () => {

    const error = new ResponseError({
      message: "Request failed with status code 500",
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
        "X-Request-ID": "abcde"
      },
      correlationId: "12345",
    })

    const { getByText } = render(
      <RequestErrorDetails error={error} />
    );

    const errorSummaryTitle = getByText("Something went wrong");
    expect(errorSummaryTitle).toBeInTheDocument();
    expect(errorSummaryTitle.tagName).toBe("H2");

    const errorDetails = getByText("There was an error while processing your request. Please try again later.");
    expect(errorDetails).toBeInTheDocument();
    expect(errorDetails.tagName).toBe("P");

    const correlationId = getByText("12345");
    expect(correlationId).toBeInTheDocument();
    expect(correlationId.tagName).toBe("P");
    expect(correlationId.textContent).toContain("Correlation ID: 12345");

    const statusCode = getByText("500");
    expect(statusCode).toBeInTheDocument();
    expect(statusCode.tagName).toBe("P");
    expect(statusCode.textContent).toContain("Status Code: 500");

    const message = getByText("Request failed with status code 500");
    expect(message).toBeInTheDocument();
    expect(message.tagName).toBe("PRE");
    expect(message).toHaveClass("ftrs-code-block");

    const headersLabel = getByText("Headers:");
    expect(headersLabel).toBeInTheDocument();
    expect(headersLabel.tagName).toBe("P");

    const headersContent = headersLabel.nextSibling;
    expect(headersContent).toBeInTheDocument();
    expect(headersContent?.textContent).toContain(
      JSON.stringify(error.headers, null, 2)
    );
  });

  it("renders with any error type", () => {
    const error = new Error("An unexpected error occurred");

    const { getByText } = render(
      <RequestErrorDetails error={error as ResponseError} />
    );

    const errorSummaryTitle = getByText("Something went wrong");
    expect(errorSummaryTitle).toBeInTheDocument();
    expect(errorSummaryTitle.tagName).toBe("H2");

    const errorDetails = getByText("There was an error while processing your request. Please try again later.");
    expect(errorDetails).toBeInTheDocument();
    expect(errorDetails.tagName).toBe("P");

    const message = getByText("An unexpected error occurred");
    expect(message).toBeInTheDocument();
    expect(message.tagName).toBe("PRE");
    expect(message).toHaveClass("ftrs-code-block");
  })
});
