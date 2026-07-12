import { t } from "@/shared/i18n/ui-text";

export type AiGeneratedContentKind = "draft" | "suggestion";

interface AiGeneratedContentNoticeProps {
  id: string;
  kind: AiGeneratedContentKind;
  className?: string;
}

const STATUS_KEYS = {
  draft: "legal.ai.status.draft",
  suggestion: "legal.ai.status.suggestion",
} as const;

export const AiGeneratedContentNotice = ({
  id,
  kind,
  className = "",
}: AiGeneratedContentNoticeProps) => {
  const titleId = `${id}-title`;
  const descriptionId = `${id}-description`;

  return (
    <aside
      aria-describedby={descriptionId}
      aria-labelledby={titleId}
      className={`rounded-[var(--radius-card)] border border-[var(--app-border)] bg-[var(--app-surface)] p-8 ${className}`.trim()}
      id={id}
    >
      <h2 className="mono-label text-[var(--app-subtle)]" id={titleId}>
        {t(STATUS_KEYS[kind])}
      </h2>
      <p className="mt-4 text-base text-[var(--app-subtle)]" id={descriptionId}>
        {t("legal.ai.disclaimer.contextual")}
      </p>
    </aside>
  );
};
