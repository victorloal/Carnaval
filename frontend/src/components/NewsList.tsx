import { useTranslation } from "react-i18next";

import type { NewsItem } from "../api/types";
import type { Locale } from "../lib/config";
import { localized } from "../lib/content";

/**
 * Published news as a citation: headline, outlet, date, a short own-words
 * summary and the link to the source (FR-E-01/02, LEG-04). The article body is
 * never stored or shown.
 */
export function NewsList({
  items,
  locale,
}: {
  items: NewsItem[];
  locale: Locale;
}) {
  const { t } = useTranslation();

  if (items.length === 0) {
    return <p className="empty">{t("news.empty")}</p>;
  }

  return (
    <ul className="news">
      {items.map((item) => (
        <li key={item.id}>
          <article>
            <h2>{item.headline}</h2>
            <p className="news-meta">
              {item.outlet}
              {item.published_on ? (
                <>
                  {" · "}
                  <time dateTime={item.published_on}>{item.published_on}</time>
                </>
              ) : null}
            </p>
            <p>{localized(item.summary_es, item.summary_en, locale)}</p>
            {item.url ? (
              <a href={item.url} target="_blank" rel="noopener noreferrer">
                {t("news.read")}
              </a>
            ) : null}
          </article>
        </li>
      ))}
    </ul>
  );
}
