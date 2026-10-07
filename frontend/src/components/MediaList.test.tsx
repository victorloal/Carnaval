import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import "../i18n";
import type { MediaAsset } from "../api/types";
import { MediaList } from "./MediaList";

const asset: MediaAsset = {
  id: "m1",
  edition: "e1",
  title_es: "Desfile de 1975",
  title_en: "1975 Parade",
  description_es: "",
  description_en: "",
  year_approx: 1975,
  author: "A. Photographer",
  source_ref: "Archive",
  license: "CC BY 4.0",
  citation_text: "A. Photographer, Archive, CC BY 4.0",
  featured: false,
};

describe("MediaList", () => {
  it("shows the citation text beside a published image", () => {
    render(<MediaList items={[asset]} locale="es" />);

    expect(
      screen.getByRole("heading", { name: "Desfile de 1975" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/A\. Photographer, Archive, CC BY 4\.0/),
    ).toBeInTheDocument();
    expect(screen.getByText(/1975 · A\. Photographer/)).toBeInTheDocument();
  });

  it("localises the title and falls back to the source description", () => {
    render(<MediaList items={[{ ...asset, description_en: "" }]} locale="en" />);

    expect(screen.getByRole("heading", { name: "1975 Parade" })).toBeInTheDocument();
  });

  it("shows the empty message with no images", () => {
    render(<MediaList items={[]} locale="es" />);

    expect(screen.getByText(/no hay imágenes publicadas/i)).toBeInTheDocument();
  });
});
