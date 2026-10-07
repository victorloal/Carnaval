import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Outlet, useLocation } from "react-router-dom";

import { Disclaimer } from "./components/Disclaimer";
import { SiteNav } from "./components/SiteNav";
import { useLocale } from "./lib/useLocale";

/** The site shell: title, navigation, the active page and the disclaimer. */
export function App() {
  const { t, i18n } = useTranslation();
  const locale = useLocale();
  const { pathname } = useLocation();

  useEffect(() => {
    void i18n.changeLanguage(locale);
    document.documentElement.lang = locale;
    document.cookie = `locale=${locale}; path=/; max-age=31536000; samesite=lax`;
  }, [locale, i18n]);

  return (
    <main className="site">
      <header>
        <h1>{t("app.title")}</h1>
        <SiteNav locale={locale} pathname={pathname} />
      </header>
      <Outlet />
      <Disclaimer />
    </main>
  );
}
