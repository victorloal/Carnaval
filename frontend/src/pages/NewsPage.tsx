import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { getAllPages } from "../api/client";
import type { NewsItem } from "../api/types";
import { NewsList } from "../components/NewsList";
import { useLocale } from "../lib/useLocale";

export function NewsPage() {
  const { t } = useTranslation();
  const locale = useLocale();
  const [items, setItems] = useState<NewsItem[]>([]);

  useEffect(() => {
    const controller = new AbortController();
    getAllPages<NewsItem>("/news/", controller.signal)
      .then(setItems)
      .catch(() => setItems([]));
    return () => controller.abort();
  }, []);

  return (
    <section>
      <h2>{t("news.heading")}</h2>
      <NewsList items={items} locale={locale} />
    </section>
  );
}
