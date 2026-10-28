import { describe, expect, it } from "vitest";

import { fitWithin } from "./image";

describe("fitWithin", () => {
  it("shrinks the long edge to the limit and keeps the ratio", () => {
    expect(fitWithin(4032, 3024, 2576)).toEqual({ width: 2576, height: 1932 });
    expect(fitWithin(3000, 6000, 2576)).toEqual({ width: 1288, height: 2576 });
  });

  it("never enlarges a small photo", () => {
    expect(fitWithin(800, 600, 2576)).toEqual({ width: 800, height: 600 });
  });
});
