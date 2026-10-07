import { describe, expect, it } from "vitest";

import en from "./locales/en.json";
import es from "./locales/es.json";

type Json = { [key: string]: unknown };

function flatten(value: Json, prefix = ""): string[] {
  return Object.entries(value).flatMap(([key, child]) =>
    typeof child === "object" && child !== null
      ? flatten(child as Json, `${prefix}${key}.`)
      : [`${prefix}${key}`],
  );
}

function leaves(value: Json): string[] {
  return Object.values(value).flatMap((child) =>
    typeof child === "object" && child !== null
      ? leaves(child as Json)
      : [String(child)],
  );
}

describe("translations", () => {
  it("has the same keys in both locales", () => {
    expect(flatten(en).sort()).toEqual(flatten(es).sort());
  });

  it("has no empty values", () => {
    for (const value of [...leaves(es), ...leaves(en)]) {
      expect(value.trim().length).toBeGreaterThan(0);
    }
  });
});
