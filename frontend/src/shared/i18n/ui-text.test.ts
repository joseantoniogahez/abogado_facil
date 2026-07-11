import { ES_MESSAGES, t } from "@/shared/i18n/ui-text";

describe("ui text translations", () => {
  it("resolves static keys", () => {
    expect(t("auth.login.title")).toBe(ES_MESSAGES["auth.login.title"]);
  });

  it("interpolates dynamic params", () => {
    expect(t("welcome.greeting", { displayName: "Admin" })).toBe("Hola, Admin");
  });

  it("keeps placeholders when params are missing", () => {
    expect(t("welcome.greeting")).toBe("Hola, {displayName}");
  });
});
