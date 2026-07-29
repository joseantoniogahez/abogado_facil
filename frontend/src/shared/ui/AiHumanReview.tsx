import { useId, useState } from "react";

import { t } from "@/shared/i18n/ui-text";
import {
  ACCENT_ACTION_CLASS_NAME,
  DANGER_ACTION_CLASS_NAME,
  SECONDARY_ACTION_CLASS_NAME,
} from "@/shared/ui/actionStyles";
import { type AiGeneratedContentKind, AiGeneratedContentNotice } from "@/shared/ui/AiGeneratedContentNotice";

export type AiReviewDecision = "accepted" | "partially_accepted" | "rejected";

interface AiHumanReviewProps {
  kind: AiGeneratedContentKind;
  value: string;
  pending?: boolean;
  initiallyAccepted?: boolean;
  onSave: (decision: AiReviewDecision, value: string) => void;
  onCopy?: (value: string) => void;
  onDirtyChange?: (dirty: boolean) => void;
}

export const AiHumanReview = ({
  kind,
  value,
  pending = false,
  initiallyAccepted = false,
  onSave,
  onCopy,
  onDirtyChange,
}: AiHumanReviewProps) => {
  const generatedId = useId().replaceAll(":", "");
  const noticeId = `ai-review-${generatedId}`;
  const [edited, setEdited] = useState(value);
  const [accepted, setAccepted] = useState(initiallyAccepted);

  const change = (next: string) => {
    setEdited(next);
    setAccepted(false);
    onDirtyChange?.(next !== value);
  };
  const accept = (decision: "accepted" | "partially_accepted") => {
    onSave(decision, edited);
  };

  return (
    <section aria-describedby={noticeId} className="grid gap-4">
      <AiGeneratedContentNotice id={noticeId} kind={kind} />
      <label>
        {t("ai.review.content")}
        <textarea
          aria-describedby={noticeId}
          className="mt-1 min-h-48 w-full rounded-xl border p-3 font-mono text-sm"
          onChange={event => change(event.target.value)}
          value={edited}
        />
      </label>
      <p className="text-sm text-(--app-subtle)">{t("ai.review.noAutomaticSend")}</p>
      <div aria-describedby={noticeId} className="flex flex-wrap gap-2">
        <button
          className={ACCENT_ACTION_CLASS_NAME}
          disabled={pending || !edited.trim()}
          onClick={() => accept(edited === value ? "accepted" : "partially_accepted")}
          type="button"
        >
          {t("ai.review.accept")}
        </button>
        <button
          className={DANGER_ACTION_CLASS_NAME}
          disabled={pending}
          onClick={() => {
            setAccepted(false);
            onDirtyChange?.(false);
            onSave("rejected", edited);
          }}
          type="button"
        >
          {t("ai.review.reject")}
        </button>
        {onCopy
          ? (
              <button
                className={SECONDARY_ACTION_CLASS_NAME}
                disabled={!accepted || pending}
                onClick={() => onCopy(edited)}
                type="button"
              >
                {t("ai.review.copy")}
              </button>
            )
          : null}
      </div>
    </section>
  );
};
