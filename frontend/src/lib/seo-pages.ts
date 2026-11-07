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

/** Le nom d'un chapitre ou d'une notion précédé de « de » ou « d' ». Seule l'initiale
 * passe en minuscule : « séries de Fourier », « divisibilité, PGCD et Bézout ». */
export function ofChapter(name: string) {
  const lower = name.charAt(0).toLowerCase() + name.slice(1);
  return /^[aeéèêiouyh]/i.test(name) ? `d'${lower}` : `de ${lower}`;
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

/** Ce que travaille chaque notion (sous-chapitre), en une phrase : le texte de sa page. */
export const NOTION_INTROS: Record<string, string> = {
  "nombres-reels":
    "Borne supérieure, partie entière, densité des rationnels, équations fonctionnelles : les propriétés des réels sur lesquelles repose l'analyse de première année.",
  "fonctions-usuelles":
    "Arctangente, fonctions hyperboliques, partie entière, logarithme et exponentielle : identités, équations et études de fonctions usuelles.",
  "limites-continuite":
    "Limites de fonctions, formes indéterminées, théorème des valeurs intermédiaires et points fixes : la continuité en pratique.",
  derivation:
    "Formule de Leibniz, théorème des accroissements finis, inégalités par étude de fonction, dérivées de fonctions réciproques.",
  "developpements-limites":
    "Développements limités, équivalents et calculs de limites, du DL de la tangente à la vitesse de convergence d'une suite.",
  "suites-numeriques":
    "Suites récurrentes, méthode de Héron, monotonie et convergence, équivalents par le théorème de Cesàro.",
  "calcul-integral":
    "Intégration par parties, primitives de fractions rationnelles, linéarisation, intégrales de Wallis, calculs d'aires.",
  "integrales-generalisees":
    "Convergence et calcul d'intégrales sur un intervalle ouvert ou non borné : intégrale de Dirichlet, fonction Gamma, théorème des résidus.",
  "integrales-a-parametre":
    "Continuité et dérivation sous le signe intégrale, hypothèse de domination : intégrale de Gauss, transformée de Fourier de la gaussienne.",
  "equations-differentielles":
    "Équations linéaires du premier et du second ordre, résonance, équation d'Euler, systèmes différentiels à coefficients constants.",
  "series-numeriques":
    "Nature et somme d'une série : règle de d'Alembert, séries alternées, développement asymptotique du terme général, série de Leibniz.",
  "series-entieres":
    "Rayon de convergence, séries lacunaires, calcul de sommes par dérivation ou intégration terme à terme.",
  "suites-series-fonctions":
    "Convergence simple et convergence uniforme, contre-exemples classiques, interversion des limites.",
  "series-de-fourier":
    "Coefficients de Fourier, théorème de Dirichlet, égalité de Parseval, et la somme des 1/n² qu'on en déduit.",
  "fonctions-plusieurs-variables":
    "Points critiques, hessienne et extremums, intégrales doubles en coordonnées polaires.",
  "integration-lebesgue":
    "Convergence dominée, intégration terme à terme, lemme de Riemann-Lebesgue, ensembles de mesure nulle.",
  "analyse-fonctionnelle":
    "Opérateurs sur les espaces de fonctions, distributions, espaces de Sobolev, théorème de Lax-Milgram, inégalité de Poincaré.",
  "nombres-complexes":
    "Forme exponentielle, équations du second degré dans C, racines de l'unité, linéarisation par les formules d'Euler.",
  "sommes-recurrence": "Raisonnement par récurrence, sommes télescopiques, coefficients binomiaux et formule du binôme.",
  denombrement: "Anagrammes, chemins dans une grille, surjections, coefficients binomiaux : compter sans rien oublier ni compter deux fois.",
  "ensembles-applications": "Injections, surjections, images directes et réciproques, relations d'équivalence.",
  polynomes: "Racines multiples, factorisation dans R[X] et C[X], idéaux des anneaux de polynômes.",
  "groupes-anneaux":
    "Sous-groupes de Z, théorème de Lagrange, groupe symétrique, Z/nZ et ses inversibles, idéaux premiers et maximaux.",
  "divisibilite-pgcd": "Algorithme d'Euclide, relation de Bézout, équations diophantiennes, nombre de diviseurs.",
  congruences: "Calculs modulo n, petit théorème de Fermat, indicatrice d'Euler, nombres pseudo-premiers.",
  "calcul-matriciel": "Puissances de matrices, formule du binôme, commutant, inverse par un polynôme annulateur.",
  "applications-lineaires": "Noyau, image, théorème du rang, rang d'une matrice selon un paramètre.",
  determinants: "Calcul de déterminants par opérations sur les lignes et les colonnes, déterminants à paramètre et inversibilité.",
  reduction: "Valeurs propres, diagonalisation, matrices non diagonalisables, projecteurs, polynômes annulateurs.",
  "espaces-euclidiens":
    "Produit scalaire, projection orthogonale, matrices symétriques et théorème spectral, rotations de l'espace.",
  "espaces-vectoriels-normes":
    "Normes équivalentes ou non, compacité en dimension finie, distance à un fermé, boule unité de ℓ².",
  "espaces-metriques": "Compacité, théorème de Baire, isométries, ensemble triadique de Cantor.",
  "probabilites-conditionnelles":
    "Formule de Bayes, probabilités totales, conditionnement par le premier pas, absence de mémoire.",
  "variables-aleatoires-discretes":
    "Espérance, variance, covariance, lois géométrique, binomiale et de Poisson, fonctions génératrices.",
  "theoremes-limites": "Inégalité de Bienaymé-Tchebychev, loi forte des grands nombres, convergence en loi.",
  "marches-aleatoires":
    "Marche aléatoire simple, ruine du joueur, processus de Poisson, mouvement brownien et formule d'Itô.",
  "geometrie-plan-espace": "Distances, produit vectoriel et aires, rotations de l'espace, plans tangents.",
  "courbes-coniques": "Longueur d'arcs paramétrés (cycloïde, astroïde), courbure, coniques et aire d'une ellipse.",
};

/** Texte d'introduction d'un chapitre ou d'une notion. */
export function topicIntro(slug: string) {
  return CHAPTER_INTROS[slug] ?? NOTION_INTROS[slug] ?? "";
}

/** Les sept chapitres, sans les notions qui les détaillent. */
export function chaptersOf<T extends { parent: string | null }>(topics: T[]) {
  return topics.filter((topic) => topic.parent === null);
}

/** Les notions d'un chapitre qui ont des exercices, les plus fournies d'abord. */
export function notionsOf<T extends { parent: string | null; exercises: number; name: string }>(
  topics: T[],
  chapter: string,
) {
  return topics
    .filter((topic) => topic.parent === chapter && topic.exercises > 0)
    .sort((a, b) => b.exercises - a.exercises || a.name.localeCompare(b.name, "fr"));
}
