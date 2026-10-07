import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import "../i18n";
import { SiteNav } from "./SiteNav";

function renderNav(pathname: string, locale: "es" | "en" = "es") {
  return render(
    <MemoryRouter>
      <SiteNav locale={locale} pathname={pathname} />
    </MemoryRouter>,
  );
}

describe("SiteNav", () => {
  it("links to the site's pages in the current locale", () => {
    renderNav("/es/");

    expect(screen.getByRole("link", { name: "Programa" })).toHaveAttribute(
      "href",
      "/es/",
    );
    expect(screen.getByRole("link", { name: "Noticias" })).toHaveAttribute(
      "href",
      "/es/news",
    );
    expect(screen.getByRole("link", { name: "Galería" })).toHaveAttribute(
      "href",
      "/es/gallery",
    );
    expect(screen.getByRole("link", { name: "Buscar" })).toHaveAttribute(
      "href",
      "/es/search",
    );
  });

  it("switches locale without dropping the page", () => {
    renderNav("/es/news", "es");

    expect(screen.getByRole("link", { name: "English" })).toHaveAttribute(
      "href",
      "/en/news",
    );
  });
});
