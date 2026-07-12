import axe from "axe-core";
import { render, screen } from "@testing-library/react";

import { t } from "@/shared/i18n/ui-text";
import { AiGeneratedContentNotice } from "@/shared/ui/AiGeneratedContentNotice";

describe("AiGeneratedContentNotice", () => {
  it.each([
    ["draft", "legal.ai.status.draft"],
    ["suggestion", "legal.ai.status.suggestion"],
  ] as const)("identifies %s content and keeps the complete warning visible", (kind, statusKey) => {
    render(<AiGeneratedContentNotice id={`ai-${kind}-notice`} kind={kind} />);

    const notice = screen.getByRole("complementary", { name: t(statusKey) });
    expect(notice).toHaveTextContent(t(statusKey));
    expect(notice).toHaveTextContent(t("legal.ai.disclaimer.contextual"));
    expect(notice).toHaveAttribute("id", `ai-${kind}-notice`);
  });

  it("has no obvious accessibility violations", async () => {
    const view = render(<AiGeneratedContentNotice id="ai-accessible-notice" kind="draft" />);

    expect((await axe.run(view.container)).violations).toHaveLength(0);
  });
});
