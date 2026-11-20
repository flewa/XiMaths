import { describe, expect, it } from "vitest";

import { safeNext } from "./safe-next";

describe("safeNext", () => {
  it("garde une adresse du site", () => {
    expect(safeNext("/exercices/192#ta-solution")).toBe("/exercices/192#ta-solution");
  });

  it("refuse une adresse extérieure ou absente", () => {
    expect(safeNext("//exemple.com")).toBe("/");
    expect(safeNext("https://exemple.com")).toBe("/");
    expect(safeNext(undefined)).toBe("/");
  });
});
