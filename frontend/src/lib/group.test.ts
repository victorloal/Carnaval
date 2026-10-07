import { describe, expect, it } from "vitest";

import type { Day, Event } from "../api/types";
import { groupEventsByDay } from "./group";

function day(id: string, date: string): Day {
  return {
    id,
    edition: "edition",
    date,
    slug_es: id,
    slug_en: "",
    label_es: id,
    label_en: id,
  };
}

function event(id: string, dayId: string, sortOrder: number): Event {
  return {
    id,
    day: dayId,
    venue: null,
    starts_at: null,
    ends_at: null,
    title_es: id,
    title_en: id,
    description_es: "",
    description_en: "",
    sort_order: sortOrder,
    source_url: "",
  };
}

describe("groupEventsByDay", () => {
  it("groups by day and orders days chronologically", () => {
    const groups = groupEventsByDay(
      [day("d2", "2026-01-06"), day("d1", "2026-01-05")],
      [event("b", "d2", 0), event("a", "d1", 1), event("a0", "d1", 0)],
    );

    expect(groups.map((group) => group.day.id)).toEqual(["d1", "d2"]);
    expect(groups[0].events.map((item) => item.id)).toEqual(["a0", "a"]);
  });

  it("ignores events whose day is absent", () => {
    expect(groupEventsByDay([], [event("x", "missing", 0)])).toEqual([]);
  });
});
