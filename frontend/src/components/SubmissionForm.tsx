import { useState } from "react";
import { useTranslation } from "react-i18next";

import { submitSubmission } from "../api/client";
import type { SubmissionCreated, SubmissionKind } from "../api/types";

/**
 * The anonymous submission form (FR-F-01/02/13/14). No account, no session.
 *
 * The rights and consent declarations are **unchecked by default and blocking**
 * (FR-F-10); the consent label states that the accepted text is an unreviewed
 * draft (ADR 0016/0018). The `website` field is a honeypot: a bot that fills it
 * gets a silent no-op, the same behaviour the server applies (FR-F-17).
 */
export function SubmissionForm({
  onCreated,
  action = submitSubmission,
}: {
  onCreated: (created: SubmissionCreated) => void;
  action?: (data: FormData) => Promise<SubmissionCreated>;
}) {
  const { t } = useTranslation();
  const [kind, setKind] = useState<SubmissionKind>("image");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    if (data.get("website")) {
      return; // honeypot filled: behave like the server and drop it silently
    }
    if (data.get("rights") !== "on" || data.get("consent") !== "on") {
      setError(t("submit.declarationsRequired"));
      return;
    }
    data.delete("consent"); // a client-side acknowledgement, not a server field

    setBusy(true);
    setError(null);
    try {
      onCreated(await action(data));
    } catch {
      setError(t("submit.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="submission-form" onSubmit={handleSubmit}>
      <fieldset>
        <legend>{t("submit.kind")}</legend>
        <label>
          <input
            type="radio"
            name="kind"
            value="image"
            checked={kind === "image"}
            onChange={() => setKind("image")}
          />
          {t("submit.image")}
        </label>
        <label>
          <input
            type="radio"
            name="kind"
            value="video_link"
            checked={kind === "video_link"}
            onChange={() => setKind("video_link")}
          />
          {t("submit.video")}
        </label>
      </fieldset>

      {kind === "image" ? (
        <label>
          {t("submit.file")}
          <input
            type="file"
            name="file"
            accept="image/jpeg,image/png,image/webp"
            required
          />
        </label>
      ) : (
        <label>
          {t("submit.videoUrl")}
          <input type="url" name="video_url" placeholder="https://…" required />
        </label>
      )}

      <label>
        {t("submit.author")}
        <input type="text" name="author" maxLength={300} />
      </label>
      <label>
        {t("submit.year")}
        <input type="number" name="year" min={1800} max={2200} />
      </label>
      <label>
        {t("submit.place")}
        <input type="text" name="place" maxLength={300} />
      </label>
      <label>
        {t("submit.description")}
        <textarea name="description" rows={3} />
      </label>

      <label className="checkbox">
        <input type="checkbox" name="minor_subject" />
        {t("submit.minor")}
      </label>
      <label className="checkbox">
        <input type="checkbox" name="rights" />
        {t("submit.rights")}
      </label>
      <label className="checkbox">
        <input type="checkbox" name="consent" />
        {t("submit.consent")}
      </label>

      <div className="honeypot">
        <label>
          Website
          <input
            type="text"
            name="website"
            tabIndex={-1}
            autoComplete="off"
          />
        </label>
      </div>

      {error ? (
        <p role="alert" className="form-error">
          {error}
        </p>
      ) : null}

      <button type="submit" disabled={busy}>
        {busy ? t("submit.submitting") : t("submit.submit")}
      </button>
    </form>
  );
}
