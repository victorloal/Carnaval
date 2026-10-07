import { useTranslation } from "react-i18next";

import type { Locale } from "../lib/config";
import { localized } from "../lib/content";
import type { DayGroup } from "../lib/group";

export function ProgrammeList({
  groups,
  locale,
}: {
  groups: DayGroup[];
  locale: Locale;
}) {
  const { t } = useTranslation();

  if (groups.length === 0) {
    return <p className="empty">{t("programme.empty")}</p>;
  }

  return (
    <div className="programme">
      {groups.map((group) => (
        <section key={group.day.id} className="day">
          <h2>{localized(group.day.label_es, group.day.label_en, locale)}</h2>
          <time dateTime={group.day.date}>{group.day.date}</time>
          <ul>
            {group.events.map((event) => (
              <li key={event.id}>
                <span>{localized(event.title_es, event.title_en, locale)}</span>
                {event.source_url ? (
                  <a
                    href={event.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {t("programme.source")}
                  </a>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
