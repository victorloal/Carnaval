import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { getAllPages } from "../api/client";
import type { Day, Event } from "../api/types";
import { ProgrammeList } from "../components/ProgrammeList";
import { groupEventsByDay, type DayGroup } from "../lib/group";
import { useLocale } from "../lib/useLocale";

export function ProgrammePage() {
  const { t } = useTranslation();
  const locale = useLocale();
  const [groups, setGroups] = useState<DayGroup[]>([]);

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
    <section>
      <h2>{t("programme.heading")}</h2>
      <ProgrammeList groups={groups} locale={locale} />
    </section>
  );
}
