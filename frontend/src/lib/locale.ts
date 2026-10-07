import { DEFAULT_LOCALE, isLocale, type Locale } from "./config";

export function localeFromPath(pathname: string): Locale | null {
  const match = /^\/([a-z]{2})(?:\/|$)/.exec(pathname);
  return match && isLocale(match[1]) ? match[1] : null;
}

export function localeFromCookie(cookie: string): Locale | null {
  const value = cookie
    .split("; ")
    .find((part) => part.startsWith("locale="))
    ?.split("=")[1];
  return isLocale(value) ? value : null;
}

/** The locale a path or cookie resolves to, defaulting to `es` (FR-H-04/05). */
export function resolveLocale(pathname: string, cookie: string): Locale {
  return localeFromPath(pathname) ?? localeFromCookie(cookie) ?? DEFAULT_LOCALE;
}

export function redirectTarget(pathname: string, cookie: string): string {
  return `/${resolveLocale(pathname, cookie)}/`;
}
