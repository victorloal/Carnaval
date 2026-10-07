import { useParams } from "react-router-dom";

import { DEFAULT_LOCALE, isLocale, type Locale } from "./config";

/** The locale of the current `/:locale` route, defaulting to the source locale. */
export function useLocale(): Locale {
  const params = useParams();
  return isLocale(params.locale) ? params.locale : DEFAULT_LOCALE;
}
