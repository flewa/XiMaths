import { describe, expect, it } from "vitest";

import { ordinal, progressBar, weekRange } from "./labels";

describe("ordinal", () => {
  it("writes 1er then 2e, 3e…", () => {
    expect([1, 2, 11].map(ordinal)).toEqual(["1er", "2e", "11e"]);
  });
});

describe("weekRange", () => {
  it("names the month once inside a month", () => {
    expect(weekRange("2026-10-19", "2026-10-25")).toBe("du 19 au 25 octobre");
  });

  it("names both months across a month, with 1er", () => {
    expect(weekRange("2026-10-26", "2026-11-01")).toBe("du 26 octobre au 1er novembre");
  });
});

describe("progressBar", () => {
  it("fills in proportion and caps at the target", () => {
    expect(progressBar(5, 10, 10)).toBe("[#####-----]");
    expect(progressBar(0, 10, 4)).toBe("[----]");
    expect(progressBar(12, 10, 4)).toBe("[####]");
  });
});
