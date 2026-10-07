import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import "../i18n";
import type { SearchResponse } from "../api/types";
import { SearchResults } from "./SearchResults";

describe("SearchResults", () => {
  it("renders the matching events and news", () => {
    const result: SearchResponse = {
      query: "desfile",
      events: [{ id: "e1", title_es: "Gran Desfile", title_en: "Grand Parade" }],
      news: [{ id: "n1", headline: "Noticia del desfile" }],
    };

    render(<SearchResults result={result} locale="es" />);

    expect(screen.getByText("Gran Desfile")).toBeInTheDocument();
    expect(screen.getByText("Noticia del desfile")).toBeInTheDocument();
  });

  it("localises event titles", () => {
    const result: SearchResponse = {
      query: "parade",
      events: [{ id: "e1", title_es: "Gran Desfile", title_en: "Grand Parade" }],
      news: [],
    };

    render(<SearchResults result={result} locale="en" />);

    expect(screen.getByText("Grand Parade")).toBeInTheDocument();
  });

  it("shows the empty message when nothing matches", () => {
    render(
      <SearchResults result={{ query: "x", events: [], news: [] }} locale="es" />,
    );

    expect(screen.getByText(/sin resultados/i)).toBeInTheDocument();
  });
});
