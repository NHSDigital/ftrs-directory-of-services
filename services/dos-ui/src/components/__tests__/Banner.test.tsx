import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Banner from "../Banner";

describe("Banner", () => {
  it("renders correctly", () => {
    const result = render(
      <Banner label="Test Label">This is a test banner message.</Banner>,
    );

    expect(result.getByText("TEST LABEL")).toBeDefined();
    expect(result.container).toMatchSnapshot("Banner Component");
  });
});
