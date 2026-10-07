import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import "../i18n";
import type { Day, Event } from "../api/types";
import { ProgrammeList } from "./ProgrammeList";

const day: Day = {
  id: "d1",
  edition: "e1",
  date: "2026-01-05",
  slug: "dia-de-negros",
  label_es: "Día de Negros",
  label_en: "Day of Blacks",
};

const event: Event = {
  id: "ev1",
  day: "d1",
  venue: null,
  starts_at: null,
  ends_at: null,
  title_es: "Gran Desfile",
  title_en: "Grand Parade",
  description_es: "",
  description_en: "",
  sort_order: 0,
  source_url: "https://carnavaldepasto.org/x/",
};

describe("ProgrammeList", () => {
  it("renders the day, the event and its source link", () => {
    render(<ProgrammeList groups={[{ day, events: [event] }]} locale="es" />);

    expect(
      screen.getByRole("heading", { name: "Día de Negros" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Gran Desfile")).toBeInTheDocument();
    expect(screen.getByRole("link")).toHaveAttribute(
      "href",
      "https://carnavaldepasto.org/x/",
    );
  });

  it("renders the English title in the English locale", () => {
    render(<ProgrammeList groups={[{ day, events: [event] }]} locale="en" />);

    expect(
      screen.getByRole("heading", { name: "Day of Blacks" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Grand Parade")).toBeInTheDocument();
  });

  it("shows the empty message with no events", () => {
    render(<ProgrammeList groups={[]} locale="es" />);

    expect(screen.getByText(/no hay eventos publicados/i)).toBeInTheDocument();
  });
});
