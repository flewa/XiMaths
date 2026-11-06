// Pages d'entrée par niveau et par chapitre : adresses, titres et textes d'introduction.

/** /niveaux/mpsi ↔ MPSI. */
export function levelPath(code: string) {
  return `/niveaux/${code.toLowerCase()}`;
}

export function chapterPath(slug: string) {
  return `/chapitres/${slug}`;
}

/** Ce que couvre chaque niveau, en une phrase : le texte qu'un moteur de recherche lit
 * en premier, et ce qu'un visiteur vérifie avant de chercher plus loin. */
export const LEVEL_INTROS: Record<string, string> = {
  L1: "Récurrence, applications, suites, limites, nombres complexes, premiers calculs d'algèbre linéaire : les bases de la première année de licence.",
  L2: "Séries numériques et entières, convergence uniforme, réduction des endomorphismes, intégrales généralisées : le cœur de la deuxième année.",
  L3: "Topologie des espaces métriques, intégration de Lebesgue, espaces de suites, intégrales à paramètre : les exercices de troisième année.",
  M1: "Analyse complexe, théorème des résidus, algèbre commutative, probabilités et lois des grands nombres : le niveau master 1.",
  M2: "Martingales, calcul d'Itô, espaces de Sobolev, problèmes elliptiques : des exercices de master 2.",
  MPSI: "Calcul, suites, polynômes, nombres complexes, dénombrement : tout le programme de MPSI, de la rentrée aux colles.",
  MP2I: "Arithmétique, dénombrement, algèbre et analyse de première année : les exercices de MP2I.",
  PCSI: "Équations différentielles, développements limités, complexes, intégration : les outils mathématiques de PCSI.",
  PTSI: "Géométrie du plan et de l'espace, courbes paramétrées, calcul intégral : les exercices de PTSI.",
  MP: "Réduction, séries entières, intégrales à paramètre, espaces préhilbertiens : les grands classiques de MP.",
  PC: "Algèbre linéaire, équations différentielles, intégrales multiples, fonctions de plusieurs variables : les exercices de PC.",
  PSI: "Probabilités discrètes, réduction, séries, fonctions de plusieurs variables : le programme de PSI.",
  PT: "Intégrales, équations différentielles, géométrie différentielle des courbes et des surfaces : les exercices de PT.",
};

/** Le nom d'un chapitre précédé de « de » ou « d' ». */
export function ofChapter(name: string) {
  return /^[aeéèêiouyh]/i.test(name) ? `d'${name.toLowerCase()}` : `de ${name.toLowerCase()}`;
}

export const CHAPTER_INTROS: Record<string, string> = {
  algebre: "Groupes, anneaux, idéaux, polynômes, racines de l'unité, dénombrement : les structures algébriques de la licence au master.",
  "algebre-lineaire": "Espaces vectoriels, rang, déterminants, réduction, diagonalisation, espaces euclidiens : l'algèbre linéaire sous toutes ses formes.",
  analyse: "Suites, séries, limites, intégrales, équations différentielles, séries entières, résidus : de la première limite à l'analyse fonctionnelle.",
  arithmetique: "Divisibilité, pgcd et Bézout, congruences, nombres premiers, petit théorème de Fermat : l'arithmétique des entiers.",
  geometrie: "Distances, produit vectoriel, rotations, courbes paramétrées, courbure, plans tangents : la géométrie du plan et de l'espace.",
  probabilites: "Lois discrètes et à densité, espérance, inégalités, marches aléatoires, martingales, mouvement brownien.",
  topologie: "Espaces métriques, compacité, complétude, théorème de Baire, ensembles remarquables comme celui de Cantor.",
};
