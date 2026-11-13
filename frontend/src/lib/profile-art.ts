// Couleurs des avatars et dessin des badges : un symbole mathématique par badge.

/** Teintes des avatars, par nom (accounts/profile.py côté serveur). Claires, avec une encre
 * sombre : lisibles sur fond sombre comme sur fond clair. */
export const AVATAR_TINTS: Record<string, string> = {
  corail: "#f28b82",
  ambre: "#f2c94c",
  jade: "#6fbf8e",
  ciel: "#7aa2f7",
  lavande: "#b39ddb",
  rose: "#f48fb1",
  menthe: "#80cbc4",
  sable: "#d7b98e",
};

export const AVATAR_COLOR_NAMES: Record<string, string> = {
  corail: "Corail",
  ambre: "Ambre",
  jade: "Jade",
  ciel: "Ciel",
  lavande: "Lavande",
  rose: "Rose",
  menthe: "Menthe",
  sable: "Sable",
};

export type BadgeShape = "circle" | "hexagon" | "shield";

export type BadgeArt = {
  glyph: string;
  tint: string;
  shape: BadgeShape;
  meaning: string;
  /** Palier d'une série de badges (bronze, argent, or) : autant de points sous le symbole. */
  tier?: number;
};

const METALS = { bronze: "#c58a5a", argent: "#c9ccd1", or: "#e8c15a" };

/** Un symbole par badge, choisi pour ce qu'il dit : ∃ pour le premier à résoudre (« il
 * existe »), ∀ pour qui touche à tout (« pour tout »), ∎ pour la solution validée (CQFD)… */
export const BADGE_ART: Record<string, BadgeArt> = {
  "premier-pas": { glyph: "ε", tint: AVATAR_TINTS.ciel, shape: "circle", meaning: "un tout petit pas" },
  valide: { glyph: "∎", tint: AVATAR_TINTS.jade, shape: "hexagon", meaning: "CQFD" },
  pionnier: { glyph: "∃", tint: AVATAR_TINTS.corail, shape: "hexagon", meaning: "il existe, et c'était toi" },
  auteur: { glyph: "∑", tint: AVATAR_TINTS.ambre, shape: "shield", meaning: "la somme de tes solveurs" },
  "relecteur-fiable": { glyph: "≡", tint: AVATAR_TINTS.lavande, shape: "shield", meaning: "en accord avec le consensus" },
  "touche-a-tout": { glyph: "∀", tint: AVATAR_TINTS.menthe, shape: "hexagon", meaning: "pour tout chapitre" },
  elegance: { glyph: "φ", tint: AVATAR_TINTS.rose, shape: "hexagon", meaning: "le nombre d'or" },
  "chasseur-de-doublons": { glyph: "≅", tint: AVATAR_TINTS.sable, shape: "shield", meaning: "isomorphes" },
  "sous-pression": { glyph: "Δt", tint: AVATAR_TINTS.corail, shape: "circle", meaning: "contre la montre" },
  "etudiant-verifie": { glyph: "∈", tint: AVATAR_TINTS.ciel, shape: "shield", meaning: "appartient à un établissement" },
  "regulier-bronze": { glyph: "∫", tint: METALS.bronze, shape: "circle", meaning: "l'effort qui s'accumule", tier: 1 },
  "regulier-argent": { glyph: "∫", tint: METALS.argent, shape: "circle", meaning: "l'effort qui s'accumule", tier: 2 },
  "regulier-or": { glyph: "∫", tint: METALS.or, shape: "circle", meaning: "l'effort qui s'accumule", tier: 3 },
};

export const FALLBACK_ART: BadgeArt = { glyph: "★", tint: AVATAR_TINTS.sable, shape: "circle", meaning: "" };

/** Couleurs des trois premières places : or, argent, bronze. */
export const PODIUM_TINTS = [METALS.or, METALS.argent, METALS.bronze];
