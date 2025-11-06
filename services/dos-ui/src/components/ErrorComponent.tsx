import { AppError } from "@/core/errors";
import { Button, Container, ErrorSummary, Footer, Header, InsetText, SummaryList } from "nhsuk-react-components";
import { HeadContent, Scripts, type ErrorComponentProps } from "@tanstack/react-router";
import Banner from "./Banner";

const ErrorComponent: React.FC<ErrorComponentProps> = ({ error }) => {
  return (
    <html>
      <head>
        <HeadContent />
      </head>
      <body>
        <Header transactional>
          <Header.Container>
            <Header.Logo href="/" />
            <Header.ServiceName href="/">Directory of Services</Header.ServiceName>
          </Header.Container>
        </Header>
        <Container className="ftrs-page-container">
          <h1 className="nhsuk-heading-l">An error occurred</h1>
          <p>Sorry, there was a problem processing your request.</p>
          <ErrorSummary>
            <ErrorSummary.Title>Error Details</ErrorSummary.Title>
            <ErrorSummary.Body>
              <p>The following information may be useful when reporting this error:</p>
              <SummaryList>
                <SummaryList.Row>
                  <SummaryList.Key>Error Message</SummaryList.Key>
                  <SummaryList.Value>{error.message}</SummaryList.Value>
                </SummaryList.Row>
                <SummaryList.Row>
                  <SummaryList.Key>Session ID</SummaryList.Key>
                  <SummaryList.Value>{(error as AppError).sessionID ?? "Unknown"}</SummaryList.Value>
                </SummaryList.Row>
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
