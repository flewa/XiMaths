import { describe, expect, it } from "vitest";

import { oneDecimal, ordinal, plural, progressBar, relativeTime, weekRange } from "./labels";

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

describe("oneDecimal", () => {
  it("writes one decimal with a comma", () => {
    expect([2.4, 3, 0.62].map((value) => oneDecimal.format(value))).toEqual(["2,4", "3,0", "0,6"]);
  });
});

describe("plural", () => {
  it("keeps 0 and 1 singular, as French does", () => {
    expect([0, 1, 2].map((n) => plural(n, "tendance"))).toEqual(["0 tendance", "1 tendance", "2 tendances"]);
    expect(plural(3, "relecture à rendre", "relectures à rendre")).toBe("3 relectures à rendre");
  });
});

describe("relativeTime", () => {
  const now = "2026-10-28T12:00:00Z";
  it("counts minutes, hours, then days, then gives the date", () => {
    expect(relativeTime("2026-10-28T11:59:40Z", now)).toBe("à l'instant");
    expect(relativeTime("2026-10-28T11:55:00Z", now)).toBe("il y a 5 min");
    expect(relativeTime("2026-10-28T09:00:00Z", now)).toBe("il y a 3 h");
    expect(relativeTime("2026-10-27T10:00:00Z", now)).toBe("hier");
    expect(relativeTime("2026-10-24T12:00:00Z", now)).toBe("il y a 4 jours");
    expect(relativeTime("2026-10-01T12:00:00Z", now)).toBe("1 octobre 2026");
  });
});
