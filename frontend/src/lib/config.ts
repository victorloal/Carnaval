export const SUPPORTED_LOCALES = ["es", "en"] as const;

export type Locale = (typeof SUPPORTED_LOCALES)[number];

export const DEFAULT_LOCALE: Locale = "es";

export function isLocale(value: string | null | undefined): value is Locale {
  return value === "es" || value === "en";
}
