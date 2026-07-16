import { describe, expect, it } from "vitest";

import {
  ACTION_BASE_CLASS_NAME,
  DANGER_ACTION_CLASS_NAME,
  INLINE_ACTION_CLASS_NAME,
  NAV_ACTION_CLASS_NAME,
  QUIET_ACTION_CLASS_NAME,
} from "./actionStyles";

describe("shared action styles", () => {
  it("provides the shared base class to every action hierarchy", () => {
    expect(ACTION_BASE_CLASS_NAME).toBe("landing-link");
    expect(DANGER_ACTION_CLASS_NAME).toContain(ACTION_BASE_CLASS_NAME);
    expect(QUIET_ACTION_CLASS_NAME).toContain(ACTION_BASE_CLASS_NAME);
  });

  it("gives quiet and navigation actions a persistent non-color cue", () => {
    expect(QUIET_ACTION_CLASS_NAME).toContain("app-action-quiet");
    expect(INLINE_ACTION_CLASS_NAME).toBe("app-action-quiet");
    expect(INLINE_ACTION_CLASS_NAME).not.toContain(ACTION_BASE_CLASS_NAME);
    expect(NAV_ACTION_CLASS_NAME).toContain("app-action-nav");
  });

  it("distinguishes destructive actions with border, background, and weight", () => {
    expect(DANGER_ACTION_CLASS_NAME).toContain("app-action-danger");
    expect(DANGER_ACTION_CLASS_NAME).not.toBe(QUIET_ACTION_CLASS_NAME);
  });
});
