import { type ErrorComponentProps, HeadContent } from "@tanstack/react-router";
import {
  Button,
  Container,
  ErrorSummary,
  Footer,
  Header,
  SummaryList,
} from "nhsuk-react-components";
import type { AppError } from "@/core/errors";

const ErrorComponent: React.FC<ErrorComponentProps> = ({ error }) => {
  const sessionID = (error as AppError).sessionID;
  const requestID = (error as AppError).requestID;

  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        <Header transactional>
          <Header.Container>
            <Header.Logo href="/" />
            <Header.ServiceName href="/">
              Directory of Services
            </Header.ServiceName>
          </Header.Container>
        </Header>
        <Container className="ftrs-page-container">
          <h1 className="nhsuk-heading-l">An error occurred</h1>
          <p>Sorry, there was a problem processing your request.</p>
          <ErrorSummary>
            <ErrorSummary.Title>Error Details</ErrorSummary.Title>
            <ErrorSummary.Body>
              <p>
                The following information may be useful when reporting this
                error:
              </p>
              <SummaryList>
                <SummaryList.Row>
                  <SummaryList.Key>Error Message</SummaryList.Key>
                  <SummaryList.Value>{error.message}</SummaryList.Value>
                </SummaryList.Row>
                {sessionID && (
                  <SummaryList.Row>
                    <SummaryList.Key>Session ID</SummaryList.Key>
                    <SummaryList.Value>{sessionID}</SummaryList.Value>
                  </SummaryList.Row>
                )}
                {requestID && (
                  <SummaryList.Row>
                    <SummaryList.Key>Request ID</SummaryList.Key>
                    <SummaryList.Value>{requestID}</SummaryList.Value>
                  </SummaryList.Row>
                )}
              </SummaryList>
            </ErrorSummary.Body>
          </ErrorSummary>
          <Button href="/">Return to Home</Button>
        </Container>
        <Footer>
          <Footer.List>
            <Footer.ListItem href="/">Home</Footer.ListItem>
          </Footer.List>
          <Footer.Copyright>
            &copy; {new Date().getFullYear()} NHS England
          </Footer.Copyright>
        </Footer>
      </body>
    </html>
  );
};

export default ErrorComponent;
