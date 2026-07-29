import { fireEvent, render, screen } from "@testing-library/react";
import axe from "axe-core";
import { vi } from "vitest";

import { t } from "@/shared/i18n/ui-text";
import { AiHumanReview } from "@/shared/ui/AiHumanReview";

describe("AiHumanReview", () => {
  it("enables copying only after persisted acceptance and invalidates it after edits", async () => {
    const onSave = vi.fn();
    const onCopy = vi.fn();
    const onDirtyChange = vi.fn();
    const view = render(
      <AiHumanReview kind="draft" onCopy={onCopy} onSave={onSave} value='{"summary":"Original"}' />,
    );
    const copy = screen.getByRole("button", { name: t("ai.review.copy") });
    expect(copy).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: t("ai.review.accept") }));
    expect(onSave).toHaveBeenCalledWith("accepted", "{\"summary\":\"Original\"}");
    expect(copy).toBeDisabled();
    view.rerender(
      <AiHumanReview
        key="persisted-original"
        initiallyAccepted
        kind="draft"
        onCopy={onCopy}
        onDirtyChange={onDirtyChange}
        onSave={onSave}
        value='{"summary":"Original"}'
      />,
    );
    expect(screen.getByRole("button", { name: t("ai.review.copy") })).toBeEnabled();
    fireEvent.change(screen.getByLabelText(t("ai.review.content")), {
      target: { value: "{\"summary\":\"Editado\"}" },
    });
    expect(screen.getByRole("button", { name: t("ai.review.copy") })).toBeDisabled();
    expect(onDirtyChange).toHaveBeenLastCalledWith(true);
    fireEvent.click(screen.getByRole("button", { name: t("ai.review.accept") }));
    expect(onSave).toHaveBeenLastCalledWith("partially_accepted", "{\"summary\":\"Editado\"}");
    expect(screen.getByRole("button", { name: t("ai.review.copy") })).toBeDisabled();
    view.rerender(
      <AiHumanReview
        key="persisted-edit"
        initiallyAccepted
        kind="draft"
        onCopy={onCopy}
        onDirtyChange={onDirtyChange}
        onSave={onSave}
        value='{"summary":"Editado"}'
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: t("ai.review.copy") }));
    expect(onCopy).toHaveBeenCalledWith("{\"summary\":\"Editado\"}");
    fireEvent.click(screen.getByRole("button", { name: t("ai.review.reject") }));
    expect(onSave).toHaveBeenLastCalledWith("rejected", "{\"summary\":\"Editado\"}");
    expect((await axe.run(view.container)).violations).toHaveLength(0);
  });

  it("restores persisted acceptance after remounting", () => {
    render(
      <AiHumanReview
        initiallyAccepted
        kind="draft"
        onCopy={vi.fn()}
        onSave={vi.fn()}
        value='{"summary":"Revisado"}'
      />,
    );
    expect(screen.getByRole("button", { name: t("ai.review.copy") })).toBeEnabled();
  });
});
