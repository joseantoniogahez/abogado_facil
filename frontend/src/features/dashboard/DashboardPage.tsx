import { useQuery } from "@tanstack/react-query";

import { dashboardQueryOptions } from "@/features/dashboard/api";
import { appendRequestIdDiagnostic, getApiErrorRequestId } from "@/shared/api/errors";
import { useSession } from "@/shared/auth/session";
import { t } from "@/shared/i18n/ui-text";
import { SECONDARY_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";

export const DashboardPage = () => {
  const { data: user } = useSession();
  const summary = useQuery(dashboardQueryOptions());
  if (summary.isPending)
    return (
      <main className="p-8">
        <p>{t("dashboard.loading")}</p>
      </main>
    );
  if (summary.isError)
    return (
      <main className="p-8">
        <h1>{t("dashboard.error.title")}</h1>
        <p>
          {appendRequestIdDiagnostic(
            t("dashboard.error.body"),
            getApiErrorRequestId(summary.error),
          )}
        </p>
        <button
          className={`${SECONDARY_ACTION_CLASS_NAME} mt-4`}
          type="button"
          onClick={() => void summary.refetch()}
        >
          {t("dashboard.retry")}
        </button>
      </main>
    );
  if (!summary.data || !user) return null;
  const metrics = [
    [t("dashboard.clients"), summary.data.clients],
    [t("dashboard.matters"), summary.data.active_matters],
    [t("dashboard.tasks"), summary.data.pending_tasks],
  ] as const;
  return (
    <main className="mx-auto max-w-6xl p-6 sm:p-10">
      <p className="mono-label text-[var(--app-subtle)]">{t("dashboard.badge")}</p>
      <h1 className="mt-3 text-4xl font-semibold">
        {t("dashboard.greeting", { displayName: user.display_name })}
      </h1>
      <p className="mt-2 text-[var(--app-subtle)]">
        {t("dashboard.firm", { firmName: summary.data.firm_name })}
      </p>
      <section aria-label={t("dashboard.summary")} className="mt-8 grid gap-4 sm:grid-cols-3">
        {metrics.map(([label, metric]) => (
          <article
            className="rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] p-5"
            key={label}
          >
            <h2>{label}</h2>
            <p className="mt-2 text-3xl font-semibold">{metric.value}</p>
            <p className="text-sm text-[var(--app-subtle)]">
              {metric.available ? t("dashboard.available") : t("dashboard.comingSoon")}
            </p>
          </article>
        ))}
      </section>
      <section className="mt-8 rounded-2xl border border-[var(--app-border)] p-5">
        <h2 className="text-xl font-semibold">{t("dashboard.upcoming")}</h2>
        {summary.data.upcoming_tasks.length
          ? (
              <ul className="mt-3 grid gap-3">
                {summary.data.upcoming_tasks.map(task => (
                  <li key={task.id}>
                    <a className={SECONDARY_ACTION_CLASS_NAME} href={`/matters/${task.matter_id}`}>
                      {task.title}
                      {" "}
                      ·
                      {task.due_date}
                      {" "}
                      ·
                      {task.matter_title}
                    </a>
                  </li>
                ))}
              </ul>
            )
          : <p className="mt-3 text-[var(--app-subtle)]">{t("dashboard.upcoming.empty")}</p>}
      </section>
      <section className="mt-8 rounded-2xl border border-[var(--app-border)] p-5">
        <h2 className="text-xl font-semibold">{t("dashboard.ai")}</h2>
        <p className="mt-3 text-[var(--app-subtle)]">{t("dashboard.ai.notAvailable")}</p>
      </section>
      <section className="mt-8">
        <h2 className="text-xl font-semibold">{t("dashboard.actions")}</h2>
        <div className="mt-3 flex flex-wrap gap-3">
          <a className={SECONDARY_ACTION_CLASS_NAME} href="/clients/new">
            {t("dashboard.action.client")}
          </a>
          <a className={SECONDARY_ACTION_CLASS_NAME} href="/matters/new">
            {t("dashboard.action.matter")}
          </a>
          <button className={SECONDARY_ACTION_CLASS_NAME} disabled type="button">
            {t("dashboard.action.intake")}
            {" "}
            ·
            {t("dashboard.comingSoon")}
          </button>
        </div>
      </section>
    </main>
  );
};
