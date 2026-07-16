import { Link, Navigate } from "react-router-dom";

import { useSession } from "@/shared/auth/session";
import { t, type UiTextKey } from "@/shared/i18n/ui-text";
import { CenteredMessage } from "@/shared/ui/CenteredMessage";

const MODULES: { body: UiTextKey; title: UiTextKey }[] = [
  {
    title: "landing.modules.clients.title",
    body: "landing.modules.clients.body",
  },
  {
    title: "landing.modules.documents.title",
    body: "landing.modules.documents.body",
  },
  {
    title: "landing.modules.checklists.title",
    body: "landing.modules.checklists.body",
  },
  {
    title: "landing.modules.ai.title",
    body: "landing.modules.ai.body",
  },
  {
    title: "landing.modules.calculators.title",
    body: "landing.modules.calculators.body",
  },
  {
    title: "landing.modules.drafts.title",
    body: "landing.modules.drafts.body",
  },
];

const PREVIEW_ITEMS: { label: UiTextKey; value: UiTextKey }[] = [
  {
    label: "landing.preview.client.label",
    value: "landing.preview.client.value",
  },
  {
    label: "landing.preview.status.label",
    value: "landing.preview.status.value",
  },
  {
    label: "landing.preview.next.label",
    value: "landing.preview.next.value",
  },
];

export const LandingPage = () => {
  const { data: user, isPending } = useSession();

  if (isPending) {
    return <CenteredMessage title={t("landing.loading.title")} />;
  }

  if (user) {
    return <Navigate replace to="/dashboard" />;
  }

  return (
    <main className="landing-page">
      <header className="landing-top">
        <div className="landing-topInner">
          <p className="landing-brand">{t("landing.brand")}</p>
          <nav aria-label={t("landing.nav.label")} className="landing-nav">
            <Link className="landing-link" to="/login">
              {t("landing.cta.login")}
            </Link>
            <Link className="landing-link landing-linkPrimary" to="/register">
              {t("landing.cta.register")}
            </Link>
          </nav>
        </div>
      </header>

      <section className="landing-hero">
        <div className="landing-copy">
          <p className="landing-kicker">{t("landing.hero.eyebrow")}</p>
          <h1 className="landing-title">{t("landing.title")}</h1>
          <p className="landing-subtitle">{t("landing.subtitle")}</p>
          <div className="landing-actions">
            <Link className="landing-link landing-linkDark" to="/register">
              {t("landing.cta.register")}
            </Link>
            <Link className="landing-link" to="/login">
              {t("landing.cta.login")}
            </Link>
          </div>
          <p className="landing-note">{t("landing.hero.disclaimer")}</p>
        </div>

        <aside aria-label={t("landing.preview.label")} className="landing-preview">
          <div className="landing-previewHead">
            <div>
              <p className="landing-previewTitle">{t("landing.preview.title")}</p>
              <p className="landing-previewArea">{t("landing.preview.area")}</p>
            </div>
            <span className="landing-pill">{t("landing.preview.byokBadge")}</span>
          </div>

          <div className="landing-previewBody">
            <dl className="landing-meta">
              {PREVIEW_ITEMS.map(item => (
                <div className="landing-metaItem" key={item.label}>
                  <dt>{t(item.label)}</dt>
                  <dd>{t(item.value)}</dd>
                </div>
              ))}
            </dl>

            <div className="landing-previewGrid">
              <section className="landing-miniPanel" aria-labelledby="landing-preview-timeline">
                <h2 id="landing-preview-timeline">{t("landing.preview.timeline.title")}</h2>
                <ol>
                  <li className="landing-event">
                    <p>{t("landing.preview.timeline.first.date")}</p>
                    <span>{t("landing.preview.timeline.first.body")}</span>
                  </li>
                  <li className="landing-event">
                    <p>{t("landing.preview.timeline.second.date")}</p>
                    <span>{t("landing.preview.timeline.second.body")}</span>
                  </li>
                </ol>
              </section>

              <section className="landing-miniPanel" aria-labelledby="landing-preview-checklist">
                <h2 id="landing-preview-checklist">{t("landing.preview.checklist.title")}</h2>
                <ul>
                  <li>{t("landing.preview.checklist.first")}</li>
                  <li>{t("landing.preview.checklist.second")}</li>
                  <li>{t("landing.preview.checklist.third")}</li>
                </ul>
              </section>
            </div>
          </div>
        </aside>
      </section>

      <section className="landing-modules" aria-labelledby="landing-modules-title">
        <div className="landing-sectionInner">
          <div className="landing-sectionCopy">
            <h2 id="landing-modules-title">{t("landing.modules.title")}</h2>
            <p>{t("landing.modules.subtitle")}</p>
          </div>
          <ul className="landing-moduleGrid">
            {MODULES.map(module => (
              <li className="landing-module" key={module.title}>
                <h3>{t(module.title)}</h3>
                <p>{t(module.body)}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="landing-policy">
        <div className="landing-policyItem">
          <h2>{t("landing.byok.title")}</h2>
          <p>{t("landing.byok.body")}</p>
        </div>
        <div className="landing-policyItem landing-policyLegal">
          <h2>{t("landing.legal.title")}</h2>
          <p>{t("landing.legal.body")}</p>
        </div>
      </section>
    </main>
  );
};
