import { describe, expect, it } from "vitest";

import { base64UrlToBytes, isAppleMobile, sameBytes } from "./push";

describe("base64UrlToBytes", () => {
  it("decodes url-safe base64 without padding", () => {
    expect(Array.from(base64UrlToBytes("-_8"))).toEqual([0xfb, 0xff]);
    expect(base64UrlToBytes("BAAA").length).toBe(3);
  });
});

describe("isAppleMobile", () => {
  it("knows iPhones and iPads, even an iPad that says it is a Mac", () => {
    expect(isAppleMobile("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)", "iPhone", 5)).toBe(true);
    expect(isAppleMobile("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "MacIntel", 5)).toBe(true);
    expect(isAppleMobile("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "MacIntel", 0)).toBe(false);
    expect(isAppleMobile("Mozilla/5.0 (Linux; Android 15)", "Linux armv8l", 5)).toBe(false);
  });
});

describe("sameBytes", () => {
  it("compares a subscription key with the server key", () => {
    const key = base64UrlToBytes("BAAA");
    expect(sameBytes(key.slice().buffer, key)).toBe(true);
    expect(sameBytes(new Uint8Array([4, 0, 1]).buffer, key)).toBe(false);
    expect(sameBytes(null, key)).toBe(false);
  });
});
