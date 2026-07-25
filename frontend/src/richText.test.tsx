import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { renderRich } from "./richText";

describe("renderRich", () => {
  it("renders **bold** as <strong> and keeps surrounding text", () => {
    const { container } = render(<>{renderRich("Hello **world**")}</>);
    expect(container.querySelector("strong")?.textContent).toBe("world");
    expect(container.textContent).toContain("Hello");
  });

  it("turns newlines into <br> elements", () => {
    const { container } = render(<>{renderRich("line a\nline b")}</>);
    expect(container.querySelectorAll("br").length).toBe(1);
    expect(container.textContent).toContain("line a");
    expect(container.textContent).toContain("line b");
  });
});
