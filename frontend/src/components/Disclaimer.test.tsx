import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import "../i18n";
import { Disclaimer } from "./Disclaimer";

describe("Disclaimer", () => {
  it("states the site is unofficial and unaffiliated", () => {
    render(<Disclaimer />);

    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/no oficial/i);
    expect(note).toHaveTextContent(/Corpocarnaval/);
  });
});
