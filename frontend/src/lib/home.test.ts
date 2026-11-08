import { describe, expect, it } from "vitest";

import type { DailyChallenge, Skill } from "./api";
import type { CourseNoteSummary } from "./api";
import { dayLabel, homeHref, homeView, nextSkill, openChallenge, suggestedNotes } from "./home";

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

describe("vues de l'accueil", () => {
  it("garde le niveau d'un onglet à l'autre et omet les valeurs par défaut", () => {
    expect(homeHref("pour-toi", undefined)).toBe("/");
    expect(homeHref("tendance", undefined)).toBe("/?vue=tendance");
    expect(homeHref("sans-solution", "MP")).toBe("/?niveau=MP&vue=sans-solution");
    expect(homeHref("pour-toi", "tous")).toBe("/?niveau=tous");
  });

  it("revient au fil pour une vue inconnue", () => {
    expect(homeView("nouveaux").sort).toBe("recent");
    expect(homeView("nimporte").value).toBe("pour-toi");
    expect(homeView(undefined).sort).toBeNull();
  });
});

describe("suggestedNotes", () => {
  const note = (slug: string, cycle: "sup" | "spe", topic: string, published = true) =>
    ({ slug, cycle, topic_name: topic, published }) as CourseNoteSummary;
  const notes = [
    note("complexes", "sup", "Nombres complexes"),
    note("polynomes", "sup", "Polynômes"),
    note("series", "spe", "Séries entières"),
    note("reduction", "spe", "Réduction des endomorphismes"),
    note("brouillon", "spe", "Séries numériques", false),
  ];

  it("propose d'abord les notions du fil, puis le cycle du niveau, jamais un brouillon", () => {
    const slugs = (year: number | null, topics: string[]) =>
      suggestedNotes(notes, { year, topics }).map((item) => item.slug);
    expect(slugs(2, ["Polynômes", "Séries numériques"])).toEqual(["polynomes", "series", "reduction"]);
    expect(slugs(1, [])).toEqual(["complexes", "polynomes", "series"]);
    expect(slugs(null, ["Réduction des endomorphismes"])).toEqual(["reduction", "complexes", "polynomes"]);
  });
});

describe("dayLabel", () => {
  it("écrit le jour à l'heure de Paris, avec une majuscule", () => {
    expect(dayLabel(new Date("2026-11-08T12:00:00Z"))).toBe("Dimanche 8 novembre");
    // 23 h 30 à Paris le 7, déjà le 8 en temps universel ? Non : 22 h 30 UTC le 7 est 23 h 30 à Paris.
    expect(dayLabel(new Date("2026-11-07T22:30:00Z"))).toBe("Samedi 7 novembre");
    expect(dayLabel(new Date("2026-11-07T23:30:00Z"))).toBe("Dimanche 8 novembre");
  });
});

describe("vues de l'accueil", () => {
  it("garde le niveau d'un onglet à l'autre et omet les valeurs par défaut", () => {
    expect(homeHref("pour-toi", undefined)).toBe("/");
    expect(homeHref("tendance", undefined)).toBe("/?vue=tendance");
    expect(homeHref("sans-solution", "MP")).toBe("/?niveau=MP&vue=sans-solution");
    expect(homeHref("pour-toi", "tous")).toBe("/?niveau=tous");
  });

  it("revient au fil pour une vue inconnue", () => {
    expect(homeView("nouveaux").sort).toBe("recent");
    expect(homeView("nimporte").value).toBe("pour-toi");
    expect(homeView(undefined).sort).toBeNull();
  });
});

describe("suggestedNotes", () => {
  const note = (slug: string, cycle: "sup" | "spe", topic: string, published = true) =>
    ({ slug, cycle, topic_name: topic, published }) as CourseNoteSummary;
  const notes = [
    note("complexes", "sup", "Nombres complexes"),
    note("polynomes", "sup", "Polynômes"),
    note("series", "spe", "Séries entières"),
    note("reduction", "spe", "Réduction des endomorphismes"),
    note("brouillon", "spe", "Séries numériques", false),
  ];

  it("propose d'abord les notions du fil, puis le cycle du niveau, jamais un brouillon", () => {
    const slugs = (year: number | null, topics: string[]) =>
      suggestedNotes(notes, { year, topics }).map((item) => item.slug);
    expect(slugs(2, ["Polynômes", "Séries numériques"])).toEqual(["polynomes", "series", "reduction"]);
    expect(slugs(1, [])).toEqual(["complexes", "polynomes", "series"]);
    expect(slugs(null, ["Réduction des endomorphismes"])).toEqual(["reduction", "complexes", "polynomes"]);
  });
});

describe("dayLabel", () => {
  it("écrit le jour à l'heure de Paris, avec une majuscule", () => {
    expect(dayLabel(new Date("2026-11-08T12:00:00Z"))).toBe("Dimanche 8 novembre");
    // En novembre, Paris a une heure d'avance sur le temps universel.
    expect(dayLabel(new Date("2026-11-07T22:30:00Z"))).toBe("Samedi 7 novembre");
    expect(dayLabel(new Date("2026-11-07T23:30:00Z"))).toBe("Dimanche 8 novembre");
  });
});
