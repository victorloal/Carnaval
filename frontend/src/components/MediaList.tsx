import { useTranslation } from "react-i18next";

import type { MediaAsset } from "../api/types";
import type { Locale } from "../lib/config";
import { localized } from "../lib/content";

/**
 * A published image as a citation card (FR-E-06, LEG-03). The image bytes are
 * served from storage at deployment; until that exists, the card carries what
 * must be shown beside every image: its title, year, author and **citation
 * text**. `rights_status = unknown` never reaches this list — the API returns
 * published rows only.
 */
export function MediaList({
  items,
  locale,
}: {
  items: MediaAsset[];
  locale: Locale;
}) {
  const { t } = useTranslation();

  if (items.length === 0) {
    return <p className="empty">{t("gallery.empty")}</p>;
  }

  return (
    <ul className="gallery">
      {items.map((item) => (
        <li key={item.id}>
          <article>
            <h3>{localized(item.title_es, item.title_en, locale)}</h3>
            <p className="gallery-meta">
              {[item.year_approx, item.author, item.license]
                .filter(Boolean)
                .join(" · ")}
            </p>
            {localized(item.description_es, item.description_en, locale) ? (
              <p>{localized(item.description_es, item.description_en, locale)}</p>
            ) : null}
            <p className="gallery-citation">
              {t("gallery.citation")}: {item.citation_text}
            </p>
          </article>
        </li>
      ))}
    </ul>
  );
}
