import { useTranslation } from "react-i18next";

/** The moderation state of a submission, looked up by token (FR-F-18). */
export function SubmissionStatus({
  status,
  rejectionReason,
}: {
  status: string;
  rejectionReason: string;
}) {
  const { t } = useTranslation();
  const key = `status.states.${status}`;
  const translated = t(key);

  return (
    <div className="submission-status">
      <p className="status-value">{translated === key ? status : translated}</p>
      {rejectionReason ? (
        <p className="status-reason">
          {t("status.reason")}: {rejectionReason}
        </p>
      ) : null}
    </div>
  );
}
