import { useQuery } from "@tanstack/react-query";

import { aiInsightsQueryOptions } from "@/features/ai-insights/api";
import { t } from "@/shared/i18n/ui-text";

const Metric = ({ label, value }: { label: string; value: string | number }) => (
  <div className="rounded-xl border p-4">
    <dt className="text-sm text-(--app-subtle)">{label}</dt>
    <dd className="mt-1 text-2xl font-semibold">{value}</dd>
  </div>
);

export const AiInsightsPage = () => {
  const query = useQuery(aiInsightsQueryOptions());
  if (query.isPending) return <main className="page-shell"><p>{t("aiInsights.loading")}</p></main>;
  if (query.isError || !query.data) return <main className="page-shell"><h1>{t("aiInsights.error")}</h1></main>;
  const { operational: op, product } = query.data;
  return (
    <main className="page-shell">
      <p className="mono-label text-(--app-subtle)">{t("aiInsights.badge")}</p>
      <h1>{t("aiInsights.title")}</h1>
      <p className="mt-2 text-(--app-subtle)">{t("aiInsights.subtitle")}</p>
      <h2 className="mt-8 text-xl font-semibold">{t("aiInsights.operational")}</h2>
      <dl className="mt-4 grid gap-3 sm:grid-cols-3">
        <Metric label={t("aiInsights.jobs")} value={op.total_jobs} />
        <Metric label={t("aiInsights.success")} value={`${op.success_rate}%`} />
        <Metric label={t("aiInsights.errors")} value={op.failed_jobs} />
        <Metric label={t("aiInsights.latency")} value={`${op.average_latency_ms} ms`} />
        <Metric label={t("aiInsights.tokens")} value={op.estimated_input_tokens + op.estimated_output_tokens} />
        <Metric label={t("aiInsights.retries")} value={op.retry_count} />
        <Metric label={t("aiInsights.stuck")} value={op.stuck_jobs} />
        <Metric label={t("aiInsights.cost")} value={op.cost_usd === null ? t("aiInsights.costUnavailable") : `$${op.cost_usd}`} />
        <Metric label={t("aiInsights.costCoverage")} value={`${op.cost_coverage_percent}%`} />
      </dl>
      <h2 className="mt-8 text-xl font-semibold">{t("aiInsights.product")}</h2>
      <dl className="mt-4 grid gap-3 sm:grid-cols-3">
        <Metric label={t("aiInsights.results")} value={product.total_results} />
        <Metric label={t("aiInsights.accepted")} value={product.accepted_results + product.partially_accepted_results} />
        <Metric label={t("aiInsights.edited")} value={product.edited_results} />
        <Metric label={t("aiInsights.converted")} value={product.converted_results} />
        <Metric label={t("aiInsights.regenerated")} value={product.regenerated_results} />
        <Metric label={t("aiInsights.abandoned")} value={product.abandoned_results} />
      </dl>
      <h2 className="mt-8 text-xl font-semibold">{t("aiInsights.feedback")}</h2>
      {product.feedback.length
        ? (
            <ul>
              {product.feedback.map(item => (
                <li key={item.name}>
                  {t(`ai.feedback.${item.name}`)}
                  :
                  {" "}
                  {item.count}
                </li>
              ))}
            </ul>
          )
        : <p>{t("aiInsights.feedbackEmpty")}</p>}
    </main>
  );
};
