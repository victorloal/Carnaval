import type { Locale } from "./config";

/** The source locale wins unless the secondary locale has content (FR-H-06). */
export function localized(es: string, en: string, locale: Locale): string {
  return locale === "en" && en ? en : es;
}
