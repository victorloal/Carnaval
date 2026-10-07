import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useSearchParams } from "react-router-dom";

import { search } from "../api/client";
import type { SearchResponse } from "../api/types";
import { SearchResults } from "../components/SearchResults";
import { useLocale } from "../lib/useLocale";

interface SearchState {
  query: string;
  result: SearchResponse | null;
}

export function SearchPage() {
  const { t } = useTranslation();
  const locale = useLocale();
  const [params, setParams] = useSearchParams();
  const query = params.get("q") ?? "";
  const [text, setText] = useState(query);
  const [state, setState] = useState<SearchState | null>(null);

  useEffect(() => {
    if (!query.trim()) {
      return;
    }
    const controller = new AbortController();
    search(query, controller.signal)
      .then((result) => setState({ query, result }))
      .catch(() => setState({ query, result: null }));
    return () => controller.abort();
  }, [query]);

  return (
    <section>
      <h2>{t("search.heading")}</h2>
      <form
        role="search"
        onSubmit={(event) => {
          event.preventDefault();
          const value = text.trim();
          setParams(value ? { q: value } : {});
        }}
      >
        <label htmlFor="search-input">{t("search.label")}</label>
        <input
          id="search-input"
          name="q"
          type="search"
          value={text}
          placeholder={t("search.placeholder")}
          onChange={(event) => setText(event.target.value)}
        />
        <button type="submit">{t("search.submit")}</button>
      </form>
      {state?.query === query && state.result ? (
        <SearchResults result={state.result} locale={locale} />
      ) : null}
    </section>
  );
}
