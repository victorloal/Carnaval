import { useTranslation } from "react-i18next";

import type { SearchResponse } from "../api/types";
import type { Locale } from "../lib/config";
import { localized } from "../lib/content";

/** Published events and news that match a search query (FR-I-01/02). */
export function SearchResults({
  result,
  locale,
}: {
  result: SearchResponse;
  locale: Locale;
}) {
  const { t } = useTranslation();
  const isEmpty = result.events.length === 0 && result.news.length === 0;

  if (isEmpty) {
    return <p className="empty">{t("search.empty")}</p>;
  }

  return (
    <div className="search-results">
      {result.events.length > 0 ? (
        <section>
          <h2>{t("search.events")}</h2>
          <ul>
            {result.events.map((event) => (
              <li key={event.id}>
                {localized(event.title_es, event.title_en, locale)}
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      {result.news.length > 0 ? (
        <section>
          <h2>{t("search.news")}</h2>
          <ul>
            {result.news.map((item) => (
              <li key={item.id}>{item.headline}</li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
