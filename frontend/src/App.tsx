import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";

import { getAllPages } from "./api/client";
import type { Day, Event } from "./api/types";
import { Disclaimer } from "./components/Disclaimer";
import { ProgrammeList } from "./components/ProgrammeList";
import { DEFAULT_LOCALE, isLocale, type Locale } from "./lib/config";
import { groupEventsByDay, type DayGroup } from "./lib/group";

export function App() {
  const params = useParams();
  const { t, i18n } = useTranslation();
  const locale: Locale = isLocale(params.locale) ? params.locale : DEFAULT_LOCALE;
  const [groups, setGroups] = useState<DayGroup[]>([]);

  useEffect(() => {
    void i18n.changeLanguage(locale);
    document.documentElement.lang = locale;
    document.cookie = `locale=${locale}; path=/; max-age=31536000; samesite=lax`;
  }, [locale, i18n]);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      getAllPages<Day>("/days/", controller.signal),
      getAllPages<Event>("/events/", controller.signal),
    ])
      .then(([days, events]) => setGroups(groupEventsByDay(days, events)))
      .catch(() => setGroups([]));
    return () => controller.abort();
  }, []);

  return (
    <main className="site">
      <header>
        <h1>{t("app.title")}</h1>
      </header>
      <ProgrammeList groups={groups} locale={locale} />
      <Disclaimer />
    </main>
  );
}
