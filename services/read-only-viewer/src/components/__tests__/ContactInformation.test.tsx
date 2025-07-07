import { render, screen } from "@testing-library/react";
import { describe, it } from "vitest";
import ContactInformation from "../ContactInformation";

describe("ContactInformation", () => {
  it("displays email when provided", () => {
    render(<ContactInformation telecom={{ email: "test@example.com" }} />);
    expect(screen.getByText("Email: test@example.com")).toBeInTheDocument();
  });

  it("displays public phone when provided", () => {
    render(<ContactInformation telecom={{ phone_public: "123-456-7890" }} />);
    expect(screen.getByText("Public Phone: 123-456-7890")).toBeInTheDocument();
  });

  it("displays private phone when provided", () => {
    render(<ContactInformation telecom={{ phone_private: "098-765-4321" }} />);
    expect(screen.getByText("Private Phone: 098-765-4321")).toBeInTheDocument();
  });

  it("displays website when provided", () => {
    render(<ContactInformation telecom={{ website: "https://example.com" }} />);
    expect(
      screen.getByText("Website: https://example.com"),
    ).toBeInTheDocument();
  });

  it("displays 'None Provided' when no contact information is given", () => {
    render(<ContactInformation telecom={{}} />);
    expect(screen.getByText("None Provided")).toBeInTheDocument();
  });

  it("renders all contact information fields when all are provided", () => {
    render(
      <ContactInformation
        telecom={{
          email: "test@example.com",
          phone_public: "123-456-7890",
          phone_private: "098-765-4321",
          website: "https://example.com",
        }}
      />,
    );
    expect(screen.getByText("Email: test@example.com")).toBeInTheDocument();
    expect(screen.getByText("Public Phone: 123-456-7890")).toBeInTheDocument();
    expect(screen.getByText("Private Phone: 098-765-4321")).toBeInTheDocument();
    expect(
      screen.getByText("Website: https://example.com"),
    ).toBeInTheDocument();
  });
});
