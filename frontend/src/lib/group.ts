import type { Day, Event } from "../api/types";

export interface DayGroup {
  day: Day;
  events: Event[];
}

/** Days in chronological order, each with its events in source order (FR-A-08). */
export function groupEventsByDay(days: Day[], events: Event[]): DayGroup[] {
  const daysById = new Map(days.map((day) => [day.id, day]));
  const groups = new Map<string, DayGroup>();

  for (const event of events) {
    const day = daysById.get(event.day);
    if (!day) {
      continue;
    }
    const existing = groups.get(day.id);
    if (existing) {
      existing.events.push(event);
    } else {
      groups.set(day.id, { day, events: [event] });
    }
  }

  for (const group of groups.values()) {
    group.events.sort((a, b) => a.sort_order - b.sort_order);
  }

  return [...groups.values()].sort((a, b) =>
    a.day.date.localeCompare(b.day.date),
  );
}
