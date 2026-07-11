import {
  composeDisplayName,
  getPasswordPolicyViolationKeys,
  isNormalizedUsernameValid,
  normalizeUsername,
} from "@/shared/auth/validation";

describe("auth validation helpers", () => {
  it("composes a display name while ignoring an omitted middle name", () => {
    expect(composeDisplayName(" Maria ", "", " Perez ")).toBe("Maria Perez");
    expect(composeDisplayName("Maria", "Elena", "Perez")).toBe("Maria Elena Perez");
  });
  it("normalizes usernames with trim and lowercase", () => {
    expect(normalizeUsername("  Mixed.User  ")).toBe("mixed.user");
  });

  it("validates normalized usernames against the backend-safe pattern", () => {
    expect(isNormalizedUsernameValid("Valid_User-1")).toBe(true);
    expect(isNormalizedUsernameValid("invalid user!")).toBe(false);
  });

  it("returns password policy violation keys", () => {
    expect(getPasswordPolicyViolationKeys("short", "new_user")).toEqual([
      "auth.validation.password.length",
      "auth.validation.password.uppercase",
      "auth.validation.password.number",
    ]);

    expect(getPasswordPolicyViolationKeys("New_User123", "new_user")).toContain(
      "auth.validation.password.containsUsername",
    );
  });
});
