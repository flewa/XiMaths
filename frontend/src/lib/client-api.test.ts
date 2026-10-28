import { describe, expect, it } from "vitest";

import { errorMessage } from "./client-api";

describe("errorMessage", () => {
  it("repeats the API's own message", () => {
    expect(errorMessage(409, { detail: "Tu as déjà fait appel de cette décision." })).toBe(
      "Tu as déjà fait appel de cette décision.",
    );
  });

  it("names the invalid fields of a validation error, once each", () => {
    const body = { detail: [{ loc: ["body", "payload", "body"] }, { loc: ["body", "payload", "body"] }, { loc: ["body", "payload", "title"] }] };
    expect(errorMessage(422, body)).toBe("Vérifie ces champs : solution, titre.");
  });

  it("asks to wait when rate limited", () => {
    expect(errorMessage(429, null)).toMatch(/quelques minutes/);
  });
});
