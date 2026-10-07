import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useSearchParams } from "react-router-dom";

import { getSubmissionStatus } from "../api/client";
import type { SubmissionStatus as Status } from "../api/types";
import { SubmissionStatus } from "../components/SubmissionStatus";

interface StatusState {
  token: string;
  status: Status | null;
}

export function StatusPage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const [state, setState] = useState<StatusState | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }
    const controller = new AbortController();
    getSubmissionStatus(token, controller.signal)
      .then((status) => setState({ token, status }))
      .catch(() => setState({ token, status: null }));
    return () => controller.abort();
  }, [token]);

  const resolved = state?.token === token ? state.status : undefined;

  return (
    <section>
      <h2>{t("status.heading")}</h2>
      {!token ? (
        <p className="empty">{t("status.prompt")}</p>
      ) : resolved === undefined ? (
        <p>{t("status.loading")}</p>
      ) : resolved === null ? (
        <p className="empty">{t("status.notFound")}</p>
      ) : (
        <SubmissionStatus
          status={resolved.status}
          rejectionReason={resolved.rejection_reason}
        />
      )}
    </section>
  );
}
