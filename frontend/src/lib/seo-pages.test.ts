import { describe, expect, it } from "vitest";

import { NOTION_INTROS, chaptersOf, notionsOf, ofChapter, topicIntro } from "./seo-pages";

const topics = [
  { name: "Analyse", slug: "analyse", parent: null, exercises: 40 },
  { name: "Séries entières", slug: "series-entieres", parent: "analyse", exercises: 4 },
  { name: "Calcul intégral", slug: "calcul-integral", parent: "analyse", exercises: 7 },
  { name: "Séries de Fourier", slug: "series-de-fourier", parent: "analyse", exercises: 0 },
  { name: "Algèbre", slug: "algebre", parent: null, exercises: 20 },
];

describe("ofChapter", () => {
  it("met « d' » devant une voyelle ou un h, « de » sinon", () => {
    expect(ofChapter("Analyse")).toBe("d'analyse");
    expect(ofChapter("Équations différentielles")).toBe("d'équations différentielles");
    expect(ofChapter("Séries entières")).toBe("de séries entières");
  });

  it("ne passe en minuscule que l'initiale : noms propres et sigles restent", () => {
    expect(ofChapter("Séries de Fourier")).toBe("de séries de Fourier");
    expect(ofChapter("Divisibilité, PGCD et Bézout")).toBe("de divisibilité, PGCD et Bézout");
    expect(ofChapter("Intégration de Lebesgue")).toBe("d'intégration de Lebesgue");
  });
});

describe("chapitres et notions", () => {
  it("garde les chapitres seuls pour la barre latérale", () => {
    expect(chaptersOf(topics).map((topic) => topic.slug)).toEqual(["analyse", "algebre"]);
  });

  it("liste les notions non vides d'un chapitre, les plus fournies d'abord", () => {
    expect(notionsOf(topics, "analyse").map((topic) => topic.slug)).toEqual(["calcul-integral", "series-entieres"]);
  });

  it("trouve le texte d'introduction d'un chapitre comme d'une notion", () => {
    expect(topicIntro("analyse")).toContain("Suites");
    expect(topicIntro("series-entieres")).toBe(NOTION_INTROS["series-entieres"]);
    expect(topicIntro("inconnu")).toBe("");
  });
});
