import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import type { SubmissionCreated } from "../api/types";
import { SubmissionForm } from "../components/SubmissionForm";
import { localePath } from "../lib/paths";
import { useLocale } from "../lib/useLocale";

export function SubmitPage() {
  const { t } = useTranslation();
  const locale = useLocale();
  const [created, setCreated] = useState<SubmissionCreated | null>(null);

  return (
    <section>
      <h2>{t("submit.heading")}</h2>
      <p>{t("submit.intro")}</p>
      {created ? (
        <div className="submit-result">
          <p>{t("submit.created")}</p>
          <p>
            <code>{created.token}</code>
          </p>
          <Link to={`${localePath(locale, "status")}?token=${created.token}`}>
            {t("submit.checkStatus")}
          </Link>
        </div>
      ) : (
        <SubmissionForm onCreated={setCreated} />
      )}
    </section>
  );
}
