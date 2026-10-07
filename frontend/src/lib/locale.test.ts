import { describe, expect, it } from "vitest";

import {
  localeFromCookie,
  localeFromPath,
  redirectTarget,
  resolveLocale,
} from "./locale";

describe("locale resolution", () => {
  it("reads the locale from a prefixed path", () => {
    expect(localeFromPath("/en/")).toBe("en");
    expect(localeFromPath("/es/events")).toBe("es");
    expect(localeFromPath("/fr/")).toBeNull();
    expect(localeFromPath("/")).toBeNull();
  });

  it("reads the locale from the cookie", () => {
    expect(localeFromCookie("a=1; locale=en")).toBe("en");
    expect(localeFromCookie("locale=fr")).toBeNull();
    expect(localeFromCookie("")).toBeNull();
  });

  it("prefers the path, then the cookie, then Spanish", () => {
    expect(resolveLocale("/en/", "locale=es")).toBe("en");
    expect(resolveLocale("/", "locale=en")).toBe("en");
    expect(resolveLocale("/", "")).toBe("es");
  });

  it("redirects the unprefixed root to the resolved locale", () => {
    expect(redirectTarget("/", "locale=en")).toBe("/en/");
    expect(redirectTarget("/", "")).toBe("/es/");
  });
});
