import type { Locale } from "./config";

/** The locale-prefixed URL for a page within the site (FR-H-03). */
export function localePath(
  locale: Locale,
  page: "" | "news" | "gallery" | "search" = "",
): string {
  const base = `/${locale}/`;
  return page ? `${base}${page}` : base;
}

/**
 * The same page in another locale: `/es/news` → `/en/news` (FR-H-05). The
 * prefix is the only part that changes, so a link never drops the reader onto
 * a different page.
 */
export function switchLocalePath(pathname: string, locale: Locale): string {
  const rest = pathname.replace(/^\/[a-z]{2}(?=\/|$)/, "");
  return `/${locale}${rest}`;
}
