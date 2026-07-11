import { useQuery } from "@tanstack/react-query";

import { dashboardQueryOptions } from "@/features/dashboard/api";
import { useSession } from "@/shared/auth/session";
import { appendRequestIdDiagnostic, getApiErrorRequestId } from "@/shared/api/errors";
import { t } from "@/shared/i18n/ui-text";

export const DashboardPage = () => {
  const { data: user } = useSession();
  const summary = useQuery(dashboardQueryOptions());
  if (summary.isPending) return <main className="p-8"><p>{t("dashboard.loading")}</p></main>;
  if (summary.isError) return <main className="p-8"><h1>{t("dashboard.error.title")}</h1><p>{appendRequestIdDiagnostic(t("dashboard.error.body"), getApiErrorRequestId(summary.error))}</p><button type="button" onClick={() => void summary.refetch()}>{t("dashboard.retry")}</button></main>;
  if (!summary.data || !user) return null;
  const metrics = [[t("dashboard.clients"), summary.data.clients], [t("dashboard.matters"), summary.data.active_matters], [t("dashboard.tasks"), summary.data.pending_tasks]] as const;
  return <main className="mx-auto max-w-6xl p-6 sm:p-10">
    <p className="mono-label text-[var(--app-subtle)]">{t("dashboard.badge")}</p>
    <h1 className="mt-3 text-4xl font-semibold">{t("dashboard.greeting", { displayName: user.display_name })}</h1>
    <p className="mt-2 text-[var(--app-subtle)]">{t("dashboard.firm", { firmName: summary.data.firm_name })}</p>
    <section aria-label={t("dashboard.summary")} className="mt-8 grid gap-4 sm:grid-cols-3">{metrics.map(([label, metric]) => <article className="rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] p-5" key={label}><h2>{label}</h2><p className="mt-2 text-3xl font-semibold">{metric.value}</p><p className="text-sm text-[var(--app-subtle)]">{metric.available ? t("dashboard.available") : t("dashboard.comingSoon")}</p></article>)}</section>
    <section className="mt-8 rounded-2xl border border-[var(--app-border)] p-5"><h2 className="text-xl font-semibold">{t("dashboard.upcoming")}</h2><p className="mt-3 text-[var(--app-subtle)]">{t("dashboard.upcoming.empty")}</p></section>
    <section className="mt-8 rounded-2xl border border-[var(--app-border)] p-5"><h2 className="text-xl font-semibold">{t("dashboard.ai")}</h2><p className="mt-3 text-[var(--app-subtle)]">{t("dashboard.ai.notAvailable")}</p></section>
    <section className="mt-8"><h2 className="text-xl font-semibold">{t("dashboard.actions")}</h2><div className="mt-3 flex flex-wrap gap-3">{["dashboard.action.client", "dashboard.action.matter", "dashboard.action.intake"].map((key) => <button className="rounded-full border px-4 py-2" disabled key={key} type="button">{t(key as "dashboard.action.client")} · {t("dashboard.comingSoon")}</button>)}</div></section>
  </main>;
};
