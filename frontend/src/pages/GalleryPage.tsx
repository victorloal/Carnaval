import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { getAllPages } from "../api/client";
import type { MediaAsset } from "../api/types";
import { MediaList } from "../components/MediaList";
import { useLocale } from "../lib/useLocale";

export function GalleryPage() {
  const { t } = useTranslation();
  const locale = useLocale();
  const [items, setItems] = useState<MediaAsset[]>([]);

  useEffect(() => {
    const controller = new AbortController();
    getAllPages<MediaAsset>("/media/", controller.signal)
      .then(setItems)
      .catch(() => setItems([]));
    return () => controller.abort();
  }, []);

  return (
    <section>
      <h2>{t("gallery.heading")}</h2>
      <MediaList items={items} locale={locale} />
    </section>
  );
}
