import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { t } from "@/shared/i18n/ui-text";
import { ACCENT_ACTION_CLASS_NAME, SECONDARY_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";
import { AiHumanReview, type AiReviewDecision } from "@/shared/ui/AiHumanReview";

import { matterChecklistQueryKey } from "../matter-checklist/api";
import { matterNotesQueryKey } from "../matter-notes/api";
import { matterTasksQueryKey } from "../matter-tasks/api";
import {
  type AiExecutionInput,
  convertMatterAi,
  executeMatterAi,
  matterAiQueryKey,
  matterAiQueryOptions,
  previewMatterAi,
  reviewMatterAi,
} from "./api";
import type { AiFeature, AiResult } from "./contracts";

const MODEL_OPTIONS = {
  openai: [
    { value: "gpt-4.1-mini", label: "GPT-4.1 mini" },
    { value: "gpt-4.1", label: "GPT-4.1" },
  ],
  gemini: [
    { value: "gemini-3.5-flash-lite", label: "Gemini 3.5 Flash-Lite" },
    { value: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
    { value: "gemini-2.5-flash-lite", label: "Gemini 2.5 Flash-Lite" },
  ],
} as const;

type AiProvider = keyof typeof MODEL_OPTIONS;

const AI_ACTION_TYPES = [
  "note",
  "task",
  "question",
  "checklist",
  "missing_document",
  "message",
] as const;

type AiActionType = (typeof AI_ACTION_TYPES)[number];

const listText = (value: unknown) =>
  Array.isArray(value) ? value.filter(item => typeof item === "string").join("\n") : "";

interface TimelineEvent {
  date: string | null;
  description: string;
  source: string | null;
}

const timelineEvents = (value: unknown): TimelineEvent[] =>
  Array.isArray(value)
    ? value.flatMap((item) => {
        if (!item || typeof item !== "object") return [];
        const event = item as Record<string, unknown>;
        if (typeof event.description !== "string") return [];
        return [{
          date: typeof event.date === "string" ? event.date : null,
          description: event.description,
          source: typeof event.source === "string" ? event.source : null,
        }];
      })
    : [];

const timelineText = (value: unknown) =>
  timelineEvents(value)
    .map(event => [event.date ?? "", event.description, event.source ?? ""].join("\t"))
    .join("\n");

const parseTimelineText = (value: string): TimelineEvent[] =>
  value.split("\n").flatMap((line) => {
    const [date, description, ...sourceParts] = line.split("\t");
    if (!description?.trim()) return [];
    const source = sourceParts.join("\t").trim();
    return [{
      date: date?.trim() ? date.trim() : null,
      description: description.trim(),
      source: source ? source : null,
    }];
  });

const resultText = (result: AiResult) => {
  const content = result.reviewed_content ?? result.generated_content;
  if (result.feature === "matter_timeline") {
    return timelineEvents(content.events)
      .map(event =>
        [event.date ?? t("ai.timeline.unknownDate"), event.description, event.source]
          .filter(Boolean)
          .join(" — "),
      )
      .join("\n");
  }
  if (result.feature === "client_message") {
    return [content.subject, content.message].filter(value => typeof value === "string" && value.trim()).join("\n\n");
  }
  if (result.feature === "client_questions") {
    return [
      listText(content.questions),
      listText(content.critical_data),
      listText(content.missing_documents),
    ].filter(Boolean).join("\n\n");
  }
  if (result.feature === "matter_summary") {
    return [
      typeof content.summary === "string" ? content.summary : "",
      typeof content.matter_status === "string" ? content.matter_status : "",
      listText(content.key_facts),
      listText(content.pending_items),
      listText(content.next_steps),
    ].filter(Boolean).join("\n\n");
  }
  return [
    typeof content.summary === "string" ? content.summary : "",
    listText(content.relevant_facts),
    listText(content.critical_data),
    listText(content.missing_documents),
    listText(content.next_steps),
  ].filter(Boolean).join("\n\n");
};

const editableText = (result: AiResult) => {
  const content = result.reviewed_content ?? result.generated_content;
  if (result.feature === "client_message")
    return typeof content.message === "string" ? content.message : "";
  if (result.feature === "client_questions") return listText(content.questions);
  if (result.feature === "matter_timeline") return timelineText(content.events);
  return typeof content.summary === "string" ? content.summary : "";
};

const reviewedContent = (result: AiResult, edited: string) => {
  const content = { ...(result.reviewed_content ?? result.generated_content) };
  if (result.feature === "client_message") return { ...content, message: edited };
  if (result.feature === "client_questions") {
    return {
      ...content,
      questions: edited.split("\n").map(value => value.trim()).filter(Boolean),
    };
  }
  if (result.feature === "matter_timeline") return { ...content, events: parseTimelineText(edited) };
  return { ...content, summary: edited };
};

const TimelineDetails = ({ result }: { result: AiResult }) => {
  if (result.feature !== "matter_timeline") return null;
  const content = result.reviewed_content ?? result.generated_content;
  return (
    <ol className="grid gap-3">
      {timelineEvents(content.events).map((event, index) => (
        <li className="rounded-xl bg-(--app-surface-muted) p-3" key={`${event.date}-${event.description}-${index}`}>
          <p className="font-medium">{event.date ?? t("ai.timeline.unknownDate")}</p>
          <p>{event.description}</p>
          {event.source
            ? (
                <p className="text-sm text-(--app-subtle)">
                  {t("ai.timeline.source")}
                  :
                  {" "}
                  {event.source}
                </p>
              )
            : null}
        </li>
      ))}
    </ol>
  );
};

const SupportingDetails = ({ result }: { result: AiResult }) => {
  const content = result.reviewed_content ?? result.generated_content;
  const details = [
    [t("ai.review.criticalData"), content.critical_data],
    [t("ai.review.missingDocuments"), content.missing_documents],
    [t("ai.review.relevantFacts"), content.relevant_facts],
    [t("ai.review.nextSteps"), content.next_steps],
    [t("ai.review.keyFacts"), content.key_facts],
    [t("ai.review.pendingItems"), content.pending_items],
  ] as const;
  const visible = details
    .map(([label, value]) => [label, Array.isArray(value) ? value.filter(item => typeof item === "string") : []] as const)
    .filter(([, values]) => values.length);
  if (!visible.length) return null;
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {visible.map(([label, values]) => (
        <section className="rounded-xl bg-(--app-surface-muted) p-3" key={label}>
          <h4 className="font-medium">{label}</h4>
          <ul className="list-disc pl-5">
            {values.map(value => <li key={value}>{value}</li>)}
          </ul>
        </section>
      ))}
    </div>
  );
};

const DEFAULT_MODELS: Record<AiProvider, string> = {
  openai: MODEL_OPTIONS.openai[0].value,
  gemini: MODEL_OPTIONS.gemini[0].value,
};

const ResultCard = ({
  matterId,
  result,
  onRegenerate,
}: {
  matterId: number;
  result: AiResult;
  onRegenerate: (result: AiResult) => void;
}) => {
  const queryClient = useQueryClient();
  const [actionType, setActionType] = useState<AiActionType>("note");
  const [taskDueDate, setTaskDueDate] = useState("");
  const [problemReport, setProblemReport] = useState("");
  const [reviewDirty, setReviewDirty] = useState(false);
  const initial = editableText(result);
  const promptVersion = typeof result.source_snapshot.prompt_version === "string"
    ? result.source_snapshot.prompt_version
    : t("ai.result.notAvailable");
  const refresh = () => queryClient.invalidateQueries({ queryKey: matterAiQueryKey(matterId) });
  const review = useMutation({
    mutationFn: ({ decision, value }: { decision: AiReviewDecision; value: string }) => {
      const content = decision === "rejected" ? undefined : reviewedContent(result, value);
      return reviewMatterAi(matterId, result.id, decision, content, problemReport);
    },
    onSuccess: async () => {
      await refresh();
      setReviewDirty(false);
    },
  });
  const convert = useMutation({
    mutationFn: (value: string) => convertMatterAi(matterId, result.id, actionType, value, taskDueDate),
    onSuccess: async () => {
      const domainQueryKey = actionType === "task"
        ? matterTasksQueryKey(matterId)
        : actionType === "checklist" || actionType === "missing_document"
          ? matterChecklistQueryKey(matterId)
          : matterNotesQueryKey(matterId);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: matterAiQueryKey(matterId) }),
        queryClient.invalidateQueries({ queryKey: domainQueryKey }),
      ]);
    },
  });

  return (
    <li className="grid gap-4 rounded-xl border p-5">
      <div>
        <h3 className="font-semibold">{t(`ai.feature.${result.feature}`)}</h3>
        <p className="text-sm text-(--app-subtle)">
          {result.provider}
          {" · "}
          {result.model}
          {" · "}
          {t(`ai.review.status.${result.review_status}`)}
        </p>
        <details className="mt-2 text-sm">
          <summary>{t("ai.result.provenance")}</summary>
          <dl className="mt-2 grid grid-cols-[max-content_1fr] gap-x-3 gap-y-1">
            <dt>{t("ai.result.sourceVersion")}</dt>
            <dd className="break-all font-mono">{result.source_version}</dd>
            <dt>{t("ai.result.promptVersion")}</dt>
            <dd>{promptVersion}</dd>
            <dt>{t("ai.result.sources")}</dt>
            <dd>{Array.isArray(result.source_snapshot.fields) ? result.source_snapshot.fields.join(", ") : t("ai.result.notAvailable")}</dd>
          </dl>
        </details>
        {result.is_stale ? <p role="status">{t("ai.result.stale")}</p> : null}
      </div>
      <AiHumanReview
        key={`${result.updated_at}-${result.review_status}`}
        initiallyAccepted={result.review_status === "accepted" || result.review_status === "partially_accepted"}
        kind={result.feature === "client_questions" ? "suggestion" : "draft"}
        onDirtyChange={setReviewDirty}
        onCopy={value =>
          void navigator.clipboard.writeText(
            resultText({ ...result, reviewed_content: reviewedContent(result, value) }),
          )}
        onSave={(decision, value) => review.mutate({ decision, value })}
        pending={review.isPending}
        value={initial}
      />
      <SupportingDetails result={result} />
      <TimelineDetails result={result} />
      <button
        className={`${SECONDARY_ACTION_CLASS_NAME} w-fit`}
        onClick={() => onRegenerate(result)}
        type="button"
      >
        {t("ai.result.regenerate")}
      </button>
      <label>
        {t("ai.review.problem")}
        <textarea
          className="mt-1 min-h-20 w-full rounded-xl border p-3"
          maxLength={2000}
          onChange={event => setProblemReport(event.target.value)}
          value={problemReport}
        />
      </label>
      {(result.review_status === "accepted" || result.review_status === "partially_accepted") && !reviewDirty
        ? (
            <div className="flex flex-wrap items-end gap-2">
              <label>
                {t("ai.actions.type")}
                <select
                  className="ml-2 rounded-xl border p-2"
                  onChange={event => setActionType(event.target.value as AiActionType)}
                  value={actionType}
                >
                  {AI_ACTION_TYPES.map(type => (
                    <option key={type} value={type}>{t(`ai.action.${type}`)}</option>
                  ))}
                </select>
              </label>
              {actionType === "task"
                ? (
                    <label>
                      {t("ai.actions.dueDate")}
                      <input
                        className="ml-2 rounded-xl border p-2"
                        onChange={event => setTaskDueDate(event.target.value)}
                        type="date"
                        value={taskDueDate}
                      />
                    </label>
                  )
                : null}
              <button
                className={SECONDARY_ACTION_CLASS_NAME}
                disabled={convert.isPending || (actionType === "task" && !taskDueDate)}
                onClick={() => convert.mutate(resultText(result))}
                type="button"
              >
                {t("ai.actions.convert")}
              </button>
            </div>
          )
        : null}
      {review.isError || convert.isError ? <p role="alert">{t("ai.error.action")}</p> : null}
    </li>
  );
};

export const MatterAiAssistance = ({ matterId }: { matterId: number }) => {
  const queryClient = useQueryClient();
  const results = useQuery(matterAiQueryOptions(matterId));
  const [input, setInput] = useState<AiExecutionInput>({
    feature: "intake_analysis",
    narrative: "",
    provider: "openai",
    model: DEFAULT_MODELS.openai,
    include_matter_description: true,
  });
  const preview = useMutation({ mutationFn: () => previewMatterAi(matterId, input) });
  const execute = useMutation({
    mutationFn: () => {
      if (!preview.data) throw new Error("Context preview is required");
      return executeMatterAi(matterId, input, preview.data.confirmation_token);
    },
    onSuccess: async () => {
      preview.reset();
      await queryClient.invalidateQueries({ queryKey: matterAiQueryKey(matterId) });
    },
  });
  const updateInput = (next: AiExecutionInput) => {
    preview.reset();
    setInput(next);
  };
  const regenerate = (result: AiResult) => {
    updateInput({
      ...input,
      feature: result.feature,
      narrative: "",
      provider: result.provider as AiProvider,
      model: result.model,
      regenerates_result_id: result.id,
    });
    document.getElementById("matter-ai-narrative")?.focus();
  };
  const selectFeature = (feature: AiFeature) =>
    updateInput({ ...input, feature, regenerates_result_id: undefined });

  return (
    <section aria-labelledby="matter-ai-title" className="mt-8 grid gap-5">
      <div>
        <h2 className="text-2xl font-semibold" id="matter-ai-title">{t("ai.title")}</h2>
        <p>{t("ai.subtitle")}</p>
      </div>
      <label>
        {t("ai.feature.label")}
        <select
          className="mt-1 w-full rounded-xl border p-3"
          onChange={event => selectFeature(event.target.value as AiFeature)}
          value={input.feature}
        >
          {([
            "intake_analysis",
            "client_questions",
            "client_message",
            "matter_summary",
            "matter_timeline",
          ] as const).map(feature => (
            <option key={feature} value={feature}>{t(`ai.feature.${feature}`)}</option>
          ))}
        </select>
      </label>
      <label>
        {t("ai.narrative")}
        <textarea
          id="matter-ai-narrative"
          className="mt-1 min-h-40 w-full rounded-xl border p-3"
          maxLength={20000}
          minLength={20}
          onChange={event => updateInput({ ...input, narrative: event.target.value })}
          value={input.narrative}
        />
      </label>
      {input.regenerates_result_id
        ? <p role="status">{t("ai.result.regenerationReady")}</p>
        : null}
      <div className="grid gap-3 sm:grid-cols-2">
        <label>
          {t("ai.provider")}
          <select
            className="mt-1 w-full rounded-xl border p-3"
            onChange={(event) => {
              const provider = event.target.value as AiProvider;
              updateInput({ ...input, provider, model: DEFAULT_MODELS[provider] });
            }}
            value={input.provider}
          >
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
          </select>
        </label>
        <label>
          {t("ai.model")}
          <select
            className="mt-1 w-full rounded-xl border p-3"
            onChange={event => updateInput({ ...input, model: event.target.value })}
            value={input.model}
          >
            {MODEL_OPTIONS[input.provider].map(model => (
              <option key={model.value} value={model.value}>{model.label}</option>
            ))}
          </select>
        </label>
      </div>
      <label className="flex gap-2">
        <input
          checked={input.include_matter_description}
          onChange={event => updateInput({ ...input, include_matter_description: event.target.checked })}
          type="checkbox"
        />
        {t("ai.includeDescription")}
      </label>
      <button
        className={`${SECONDARY_ACTION_CLASS_NAME} w-fit`}
        disabled={preview.isPending || input.narrative.trim().length < 20}
        onClick={() => preview.mutate()}
        type="button"
      >
        {t("ai.preview")}
      </button>
      {preview.data
        ? (
            <aside className="rounded-xl border p-4" aria-label={t("ai.preview.title")}>
              <h3 className="font-semibold">{t("ai.preview.title")}</h3>
              <p>
                {t("ai.preview.included")}
                :
                {" "}
                {preview.data.included_sources.join(", ")}
              </p>
              <p>
                {t("ai.preview.excluded")}
                :
                {" "}
                {preview.data.excluded_sources.join(", ")}
              </p>
              <p>
                {preview.data.character_count}
                {" "}
                {t("ai.preview.characters")}
              </p>
              <p>{preview.data.cost_notice}</p>
              <button
                className={`${ACCENT_ACTION_CLASS_NAME} mt-3`}
                disabled={execute.isPending}
                onClick={() => execute.mutate()}
                type="button"
              >
                {execute.isPending ? t("ai.executing") : t("ai.execute")}
              </button>
            </aside>
          )
        : null}
      {preview.isError || execute.isError ? <p role="alert">{t("ai.error.execute")}</p> : null}
      {results.data?.items.length
        ? (
            <ul className="grid gap-5">
              {results.data.items.map(result => (
                <ResultCard
                  key={result.id}
                  matterId={matterId}
                  onRegenerate={regenerate}
                  result={result}
                />
              ))}
            </ul>
          )
        : <p>{t("ai.results.empty")}</p>}
    </section>
  );
};
