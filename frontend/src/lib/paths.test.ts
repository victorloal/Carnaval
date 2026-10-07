import { describe, expect, it } from "vitest";

import { localePath, switchLocalePath } from "./paths";

describe("localePath", () => {
  it("builds the root path for a locale", () => {
    expect(localePath("es")).toBe("/es/");
    expect(localePath("en")).toBe("/en/");
  });

  it("builds a page path", () => {
    expect(localePath("es", "news")).toBe("/es/news");
    expect(localePath("en", "search")).toBe("/en/search");
  });
});

describe("switchLocalePath", () => {
  it("keeps the page while changing the locale", () => {
    expect(switchLocalePath("/es/news", "en")).toBe("/en/news");
    expect(switchLocalePath("/en/search", "es")).toBe("/es/search");
  });

  it("handles the locale root with and without a trailing slash", () => {
    expect(switchLocalePath("/es", "en")).toBe("/en");
    expect(switchLocalePath("/en/", "es")).toBe("/es/");
  });
});
