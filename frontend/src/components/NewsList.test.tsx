import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import "../i18n";
import type { NewsItem } from "../api/types";
import { NewsList } from "./NewsList";

const item: NewsItem = {
  id: "n1",
  headline: "Inicio de las fiestas",
  url: "https://example.org/news/1",
  outlet: "Diario X",
  published_on: "2026-01-03",
  summary_es: "Resumen propio en español.",
  summary_en: "Original summary in English.",
};

describe("NewsList", () => {
  it("renders the citation: headline, outlet, date, summary and the source link", () => {
    render(<NewsList items={[item]} locale="es" />);

    expect(
      screen.getByRole("heading", { name: "Inicio de las fiestas" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/Diario X/)).toBeInTheDocument();
    expect(screen.getByText("2026-01-03")).toBeInTheDocument();
    expect(screen.getByText("Resumen propio en español.")).toBeInTheDocument();
    expect(screen.getByRole("link")).toHaveAttribute(
      "href",
      "https://example.org/news/1",
    );
  });

  it("falls back to the source locale when the English summary is empty", () => {
    render(<NewsList items={[{ ...item, summary_en: "" }]} locale="en" />);

    expect(screen.getByText("Resumen propio en español.")).toBeInTheDocument();
  });

  it("shows the empty message with no news", () => {
    render(<NewsList items={[]} locale="es" />);

    expect(screen.getByText(/no hay noticias publicadas/i)).toBeInTheDocument();
  });
});
