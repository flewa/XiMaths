import { describe, expect, it } from "vitest";

import type { DailyChallenge, Skill } from "./api";
import { nextSkill, openChallenge, weekLine } from "./home";

const skill = (topic: string, solved: number, mastery: number, next = true): Skill => ({
  topic,
  slug: topic,
  mastery,
  solved,
  target: 1,
  next: next ? { id: 1, title: `Exercice de ${topic}`, difficulty: 2 } : null,
});

describe("nextSkill", () => {
  it("continues where the member solved the most, then where they master best", () => {
    expect(nextSkill([skill("algebre", 1, 0.4), skill("analyse", 3, 1.2), skill("topologie", 3, 2)])?.topic).toBe(
      "topologie",
    );
  });

  it("skips chapters with nothing to suggest", () => {
    expect(nextSkill([skill("analyse", 5, 3, false), skill("algebre", 0, 0)])?.topic).toBe("algebre");
    expect(nextSkill([skill("analyse", 5, 3, false)])).toBeNull();
  });
});

describe("openChallenge", () => {
  const challenge = (level: string, attempted: boolean) =>
    ({ level, attempt: attempted ? { session_id: 1 } : null }) as DailyChallenge;

  it("returns the declared level's challenge while it is still to be taken", () => {
    expect(openChallenge([challenge("L2", false), challenge("L1", false)], "L1")?.level).toBe("L1");
    expect(openChallenge([challenge("L1", true)], "L1")).toBeNull();
    expect(openChallenge([challenge("L1", false)], null)).toBeNull();
  });
});

describe("weekLine", () => {
  it("draws active, missed and future days", () => {
    const days = [
      { date: "2026-10-26", active: true, future: false },
      { date: "2026-10-27", active: false, future: false },
      { date: "2026-10-28", active: false, future: true },
    ];
    expect(weekLine(days)).toBe("■ □ ·");
  });
});
