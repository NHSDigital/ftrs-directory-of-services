import { render } from "@testing-library/react";
import Banner from "../Banner";

describe("Banner", () => {
  it("renders the label and children correctly", () => {
    const component = render(<Banner label="Test Label">Test Content</Banner>);

    const labelComponent = component.getByText("TEST LABEL");
    expect(labelComponent).toBeInTheDocument();
    expect(labelComponent).toHaveClass("nhsuk-tag");

    const contentComponent = component.getByText("Test Content");
    expect(contentComponent).toBeInTheDocument();
    expect(contentComponent.tagName).toBe("P");
  });
});
