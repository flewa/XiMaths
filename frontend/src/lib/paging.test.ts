import { describe, expect, it } from "vitest";

import { PAGE_STEP, shownCount } from "@/components/ExerciseList";

describe("shownCount", () => {
  it("montre une tranche par défaut, puis des multiples de la tranche", () => {
    expect(shownCount(undefined)).toBe(PAGE_STEP);
    expect(shownCount("abc")).toBe(PAGE_STEP);
    expect(shownCount("10")).toBe(PAGE_STEP);
    expect(shownCount("60")).toBe(60);
    expect(shownCount("61")).toBe(90);
    // Une adresse fantaisiste ne fait pas tout charger.
    expect(shownCount("999999")).toBe(2000);
  });
});
