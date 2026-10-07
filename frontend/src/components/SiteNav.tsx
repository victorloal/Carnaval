import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { SUPPORTED_LOCALES, type Locale } from "../lib/config";
import { localePath, switchLocalePath } from "../lib/paths";

/**
 * The site navigation and the locale switcher. Every link preserves the reader's
 * page while changing the locale (FR-H-03/05).
 */
export function SiteNav({
  locale,
  pathname,
}: {
  locale: Locale;
  pathname: string;
}) {
  const { t } = useTranslation();

  return (
    <nav className="site-nav" aria-label={t("nav.heading")}>
      <ul>
        <li>
          <Link to={localePath(locale)}>{t("nav.programme")}</Link>
        </li>
        <li>
          <Link to={localePath(locale, "news")}>{t("nav.news")}</Link>
        </li>
        <li>
          <Link to={localePath(locale, "search")}>{t("nav.search")}</Link>
        </li>
      </ul>
      <ul className="locale-switcher">
        {SUPPORTED_LOCALES.map((candidate) => (
          <li key={candidate}>
            <Link
              to={switchLocalePath(pathname, candidate)}
              lang={candidate}
              aria-current={candidate === locale ? "true" : undefined}
            >
              {t(`nav.locale.${candidate}`)}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
