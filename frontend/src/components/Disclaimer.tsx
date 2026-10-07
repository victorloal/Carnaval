import { useTranslation } from "react-i18next";

export function Disclaimer() {
  const { t } = useTranslation();
  return (
    <p role="note" className="disclaimer">
      {t("app.disclaimer")}
    </p>
  );
}
