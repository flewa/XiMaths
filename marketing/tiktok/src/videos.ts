// Les douze vidéos : un besoin chacune. Ce fichier est la seule source du texte :
// la voix (scripts/voice.ts), les sous-titres, les scènes et SCRIPTS.md en sortent.
//
// Dans `text` des scènes « title » : *mot* ressort en couleur, ~mot~ est barré, et un
// saut de ligne coupe la ligne. Les formules des scènes « proof » sont en LaTeX.

export type Accent = "green" | "orange" | "red" | "blue";

export type Visual =
  | { kind: "title"; text: string; kicker?: string; accent?: Accent; size?: number }
  | {
      kind: "phone";
      shot: string;
      /** Élément de la capture sur lequel la caméra zoome (clé du manifeste). */
      focus?: string;
      label?: string;
      tap?: string;
    }
  | {
      kind: "reviewers";
      title?: string;
      verdicts?: boolean;
      /** La solution relue, en LaTeX, et le commentaire d'un relecteur. */
      lines?: string[];
      note?: string;
    }
  | { kind: "timer"; minutes: number; label?: string; extra?: string }
  | {
      kind: "proof";
      /** Phrase-choc au-dessus de la copie, avec le balisage des titres. */
      headline?: string;
      title?: string;
      lines: string[];
      marks?: { line: number; type: "cross" | "check" | "question"; note?: string }[];
      stamp?: string;
    }
  | {
      kind: "handwriting";
      /** Ce qui est écrit sur la copie. */
      lines: string[];
      /** Avec la transcription : le texte tapé dans l'éditeur, puis son aperçu en LaTeX. */
      source?: string;
      preview?: string[];
    }
  | { kind: "streakBreak"; days: number }
  | { kind: "weeks"; mode: "weekly" | "joker" }
  | { kind: "skills"; chapters: { name: string; value: number }[]; next?: string }
  | { kind: "chat"; text: string; verdict: string }
  | { kind: "leaderboard"; rows: { name: string; points: number; you?: boolean }[] }
  | { kind: "goal"; title: string; done: number; target: number; deadline: string }
  | {
      kind: "chips";
      title?: string;
      items: string[];
      accent?: Accent;
      /** Case devant chaque élément, « [✓] » par défaut ; « (x) » et « ( ) » pour un choix. */
      marks?: string[];
      colors?: Accent[];
    }
  | { kind: "cta"; prompt: string; line: string };

export type Scene = {
  /** Texte dit par la voix off, et sous-titré mot à mot. */
  voice: string;
  visual: Visual;
  /** Les scènes « title » montrent déjà leur texte : pas de sous-titres par défaut. */
  captions?: boolean;
};

export type Video = {
  id: string;
  need: string;
  audience: string;
  scenes: Scene[];
  /** Légende TikTok, avec les mots-clés de recherche. */
  caption: string;
  hashtags: string[];
};

export const VIDEOS: Video[] = [
  {
    id: "01-prepa-relue",
    need: "Progresser en prépa : avoir un retour sur ses rédactions, pas seulement en colle",
    audience: "Prépa (MPSI, MP, PSI…)",
    scenes: [
      {
        voice: "En prépa, tu rédiges des dizaines de démonstrations par semaine.",
        visual: { kind: "title", kicker: "prépa ~ semaine 12", text: "Des *dizaines*\nde démos\npar semaine." },
      },
      {
        voice: "Et à part en colle, presque personne ne les relit.",
        visual: { kind: "title", text: "Relues :\n~toutes~ *presque aucune*", accent: "red" },
      },
      {
        voice: "Sur XiMaths, tu choisis ta filière, MPSI, MP, PSI, et tu tombes sur des exos de ton niveau.",
        visual: { kind: "phone", shot: "catalogue", focus: "levels", label: "ta filière, ton niveau" },
      },
      {
        voice: "Tu proposes ta solution, et trois étudiants tirés au sort la relisent.",
        visual: { kind: "reviewers", title: "3 relecteurs tirés au sort" },
      },
      {
        voice: "Correcte, avec lacunes ou incorrecte : tu as trois verdicts, et leurs commentaires.",
        visual: { kind: "reviewers", title: "3 verdicts + commentaires", verdicts: true },
      },
      {
        voice: "XiMaths, lien en bio. Ta prochaine démo sera relue.",
        visual: { kind: "cta", prompt: "ximaths ~ fil --niveau MP", line: "Ta prochaine démo sera relue." },
      },
    ],
    caption:
      "Prépa : tes démos méritent mieux qu'une colle par semaine. Exercices MPSI, MP, PSI relus par 3 étudiants tirés au sort.",
    hashtags: ["prepa", "mpsi", "prepamp", "psi", "mathsprepa", "etudiant", "cpge"],
  },
  {
    id: "02-l1-rediger",
    need: "En L1, apprendre à rédiger une démonstration qui rapporte tous les points",
    audience: "Licence 1 et 2",
    scenes: [
      {
        voice: "Le résultat est juste. Et pourtant : deux sur cinq.",
        visual: {
          kind: "proof",
          title: "Exercice 3",
          lines: [
            "u_{n+1} - u_n = \\frac{1}{(n+1)^2} > 0",
            "\\text{donc } (u_n) \\text{ converge.}",
            "\\boxed{\\ell = 2}",
          ],
          marks: [{ line: 1, type: "question", note: "majorée ?" }],
          stamp: "2/5",
        },
      },
      {
        voice: "En L1, ce qui coûte des points, c'est souvent la rédaction.",
        visual: {
          kind: "title",
          kicker: "licence ~ L1",
          text: "Ce qui coûte des points :\nla *rédaction*.",
          accent: "orange",
        },
      },
      {
        voice: "Sur XiMaths, tu rédiges en LaTeX avec l'aperçu en direct.",
        visual: { kind: "phone", shot: "solution", focus: "preview", label: "aperçu en direct" },
      },
      {
        voice: "Trois autres étudiants relisent ta démo, et te disent ce qui manque.",
        visual: { kind: "reviewers", title: "relue par 3 étudiants", verdicts: true },
      },
      {
        voice: "Une hypothèse oubliée, un quantificateur flou : tu le vois avant le partiel.",
        visual: {
          kind: "proof",
          title: "Après relecture",
          lines: ["u_{n+1} - u_n > 0", "u_n \\le 2 \\text{ pour tout } n", "\\text{donc } (u_n) \\text{ converge.}"],
          marks: [
            { line: 0, type: "check" },
            { line: 1, type: "check" },
            { line: 2, type: "check" },
          ],
          stamp: "5/5",
        },
      },
      {
        voice: "XiMaths, lien en bio. Rédige mieux, pas plus.",
        visual: { kind: "cta", prompt: "ximaths ~ fil --niveau L1", line: "Rédige mieux, pas plus." },
      },
    ],
    caption:
      "L1 maths : le résultat juste ne suffit pas, la rédaction compte. Fais relire tes démonstrations par d'autres étudiants.",
    hashtags: ["l1", "licencemaths", "fac", "demonstration", "redaction", "etudiant", "maths"],
  },
  {
    id: "03-preuve-juste",
    need: "Savoir si sa preuve est juste quand le corrigé ne détaille rien",
    audience: "Licence et prépa",
    scenes: [
      {
        voice: "Comment savoir si ta preuve est juste… quand le corrigé fait une ligne ?",
        visual: {
          kind: "proof",
          headline: "Ta preuve\nest *juste* ?",
          title: "Corrigé",
          lines: ["\\text{Immédiat.}"],
          stamp: "?",
        },
      },
      {
        voice: "Sur XiMaths, tu postes ta solution sous l'exercice.",
        visual: { kind: "phone", shot: "solution", focus: "editor", label: "ta solution ici" },
      },
      {
        voice: "Trois pairs tirés au sort la relisent. Chacun a soixante-douze heures.",
        visual: { kind: "reviewers", title: "3 pairs · 72 h chacun" },
      },
      {
        voice: "Correcte, correcte avec lacunes, ou incorrecte. Toujours avec un commentaire.",
        visual: {
          kind: "chips",
          title: "Verdict de chaque relecteur",
          items: ["Correcte", "Correcte avec lacunes", "Incorrecte"],
          marks: ["[✓]", "[~]", "[✗]"],
          colors: ["green", "orange", "red"],
        },
      },
      {
        voice: "Et une fois validée, ta solution aide le suivant qui bloque.",
        visual: { kind: "phone", shot: "exercice", focus: "solutions", label: "solution validée" },
      },
      {
        voice: "XiMaths, lien en bio. Arrête de deviner.",
        visual: { kind: "cta", prompt: "ximaths ~ relectures", line: "Arrête de deviner." },
      },
    ],
    caption:
      "Ta preuve est juste ? Plus besoin de deviner : 3 étudiants relisent ta solution et te donnent un verdict commenté.",
    hashtags: ["maths", "demonstration", "prepa", "licence", "correction", "etudiant", "revisions"],
  },
  {
    id: "04-defi-chrono",
    need: "S'entraîner en conditions d'examen, tous les jours",
    audience: "Prépa et licence, avant DS, partiels ou concours",
    scenes: [
      {
        voice: "Trente minutes. Un exercice. Une seule tentative.",
        visual: { kind: "timer", minutes: 30, label: "défi du jour" },
        captions: true,
      },
      {
        voice: "C'est le défi du jour sur XiMaths. Un par niveau, chaque jour.",
        visual: { kind: "phone", shot: "defi", focus: "challenge", label: "un défi par niveau" },
      },
      {
        voice: "L'énoncé est tiré pour toi. Tiers-temps ? Tu as quarante minutes.",
        visual: { kind: "timer", minutes: 40, label: "tiers-temps", extra: "+10 min" },
        captions: true,
      },
      {
        voice: "Pas d'IA pendant le défi : ta justification est relue par trois membres.",
        visual: { kind: "title", kicker: "règle ~ défi", text: "IA *interdite*.\nRelu par 3 membres.", accent: "red" },
      },
      {
        voice: "Et tes points comptent dans le classement de la semaine.",
        visual: { kind: "phone", shot: "classements", focus: "board", label: "classement de la semaine" },
      },
      {
        voice: "Lien en bio. Demain, nouveau défi. Trente minutes.",
        visual: { kind: "cta", prompt: "ximaths ~ defi --aujourd-hui", line: "Demain, nouveau défi." },
      },
    ],
    caption:
      "Défi du jour : 30 minutes, 1 exercice, 1 tentative. Entraîne-toi en conditions de DS, partiel ou concours, tous les jours.",
    hashtags: ["defi", "chrono", "concours", "partiels", "prepa", "maths", "entrainement"],
  },
  {
    id: "05-photo-copie",
    need: "Rédiger à la main sans perdre une heure à taper du LaTeX",
    audience: "Tous niveaux",
    scenes: [
      {
        voice: "Tu détestes taper du LaTeX ? Prends ta copie en photo.",
        visual: {
          kind: "title",
          kicker: "latex ~ flemme",
          text: "\\frac{1}{n^2}… *non*.\nPrends ta copie\nen photo.",
          accent: "green",
        },
      },
      {
        voice: "Tu rédiges sur papier, comme en DS.",
        visual: {
          kind: "handwriting",
          lines: ["On a 1/n² ≤ 1/(n(n-1))", "pour n ≥ 2,", "donc la série converge."],
        },
      },
      {
        voice: "XiMaths la transcrit en texte et en LaTeX, directement dans l'éditeur.",
        visual: {
          kind: "handwriting",
          lines: ["On a 1/n² ≤ 1/(n(n-1))", "pour n ≥ 2,", "donc la série converge."],
          source: "On a $\\frac{1}{n^2} \\le \\frac{1}{n(n-1)}$ pour $n \\ge 2$, donc la série converge.",
          preview: [
            "\\text{On a } \\frac{1}{n^2} \\le \\frac{1}{n(n-1)} \\text{ pour } n \\ge 2,",
            "\\text{donc la série converge.}",
          ],
        },
      },
      {
        voice: "L'IA ne corrige rien : elle recopie, même tes erreurs.",
        visual: {
          kind: "title",
          kicker: "transcription",
          text: "L'IA ne corrige *rien*.\nElle recopie.",
          accent: "orange",
        },
      },
      {
        voice: "Ensuite, ce sont trois étudiants qui relisent ta solution.",
        visual: {
          kind: "reviewers",
          title: "relue par 3 étudiants",
          verdicts: true,
          lines: [
            "\\tfrac{1}{n^2} \\le \\tfrac{1}{n(n-1)} \\text{ pour } n \\ge 2,",
            "\\text{donc la série converge.}",
          ],
          note: "« et ∑ 1/(n(n−1)) ? »",
        },
      },
      {
        voice: "XiMaths, lien en bio. Ta copie en LaTeX, sans taper une ligne.",
        visual: { kind: "cta", prompt: "ximaths ~ photo --copie", line: "Ta copie en LaTeX." },
      },
    ],
    caption:
      "Rédige à la main, XiMaths transcrit ta copie en LaTeX. L'IA recopie, elle ne corrige pas : ce sont des étudiants qui relisent.",
    hashtags: ["latex", "maths", "etudiant", "prepa", "fac", "copie", "astuce"],
  },
  {
    id: "06-serie-hebdo",
    need: "Être régulier sans culpabiliser pendant les partiels",
    audience: "Tous niveaux",
    scenes: [
      {
        voice: "Ta série de quarante-sept jours vient de mourir. Pendant tes partiels.",
        visual: { kind: "streakBreak", days: 47 },
        captions: true,
      },
      {
        voice: "Sur XiMaths, la série est hebdomadaire. C'est toi qui choisis ton rythme.",
        visual: { kind: "weeks", mode: "weekly" },
      },
      {
        voice: "Une solution, une relecture ou quinze minutes de chrono : ta journée compte.",
        visual: {
          kind: "chips",
          title: "Un jour actif",
          items: ["1 solution", "1 relecture", "15 min de chrono"],
          accent: "green",
        },
      },
      {
        voice: "Une semaine t'échappe ? Deux jokers par mois protègent ta série.",
        visual: { kind: "weeks", mode: "joker" },
      },
      {
        voice: "Partiels, concours, vacances : tu la mets en pause, jusqu'à quatre semaines.",
        visual: { kind: "phone", shot: "progression", focus: "pause", label: "pause jusqu'à 4 semaines" },
      },
      {
        voice: "XiMaths, lien en bio. Régulier, pas esclave.",
        visual: { kind: "cta", prompt: "ximaths ~ progression", line: "Régulier, pas esclave." },
      },
    ],
    caption:
      "Une série de révisions qui ne casse pas pendant tes partiels : hebdomadaire, avec 2 jokers par mois et une pause jusqu'à 4 semaines.",
    hashtags: ["revisions", "motivation", "partiels", "etudiant", "productivite", "maths", "studytok"],
  },
  {
    id: "07-carte-competences",
    need: "Savoir quels chapitres réviser en priorité",
    audience: "Tous niveaux",
    scenes: [
      {
        voice: "Tu révises tout… ou tu révises ce qui te manque ?",
        visual: {
          kind: "title",
          kicker: "révisions ~ chapitres",
          text: "Tu révises *tout* ?\nOu ce qui te *manque* ?",
          accent: "orange",
        },
      },
      {
        voice: "XiMaths te dessine une carte de tes compétences, chapitre par chapitre.",
        visual: {
          kind: "skills",
          chapters: [
            { name: "Suites", value: 4.2 },
            { name: "Séries", value: 3.1 },
            { name: "Intégration", value: 1.4 },
            { name: "Algèbre linéaire", value: 2.6 },
            { name: "Probabilités", value: 0.6 },
          ],
        },
      },
      {
        voice: "Chaque solution validée remplit la carte, selon la difficulté de l'exercice.",
        visual: { kind: "phone", shot: "progression", focus: "skills", label: "ta carte de compétences" },
      },
      {
        voice: "Et dans chaque chapitre, elle te propose l'exercice d'un cran au-dessus.",
        visual: {
          kind: "skills",
          chapters: [
            { name: "Suites", value: 4.2 },
            { name: "Séries", value: 3.1 },
            { name: "Intégration", value: 1.4 },
            { name: "Algèbre linéaire", value: 2.6 },
            { name: "Probabilités", value: 0.6 },
          ],
          next: "Intégration",
        },
      },
      {
        voice: "Lien en bio. Révise moins, révise mieux.",
        visual: { kind: "cta", prompt: "ximaths ~ progression --carte", line: "Révise moins, révise mieux." },
      },
    ],
    caption:
      "Quels chapitres réviser ? Ta carte de compétences en maths, chapitre par chapitre, et l'exercice suivant d'un cran au-dessus.",
    hashtags: ["revisions", "maths", "methode", "partiels", "prepa", "licence", "studytok"],
  },
  {
    id: "08-indications",
    need: "Se débloquer sur un exercice sans se gâcher la solution",
    audience: "Tous niveaux",
    scenes: [
      {
        voice: "Bloqué sur un exo ? Surtout, n'ouvre pas le corrigé.",
        visual: {
          kind: "title",
          kicker: "bloqué ~ exo 7",
          text: "Bloqué ?\nN'ouvre *pas*\nle corrigé.",
          accent: "red",
        },
      },
      {
        voice: "Le corrigé te donne tout. Et tu n'apprends pas à chercher.",
        visual: { kind: "title", text: "Le corrigé\ndonne *tout*.\nTu ne cherches\nplus.", accent: "red" },
      },
      {
        voice: "Sur XiMaths, les exercices ont des indications. Une par une.",
        visual: { kind: "phone", shot: "exercice", focus: "hints", label: "indications" },
      },
      {
        voice: "Tu ouvres la première, et tu cherches encore. La suivante, seulement si besoin.",
        visual: { kind: "phone", shot: "exercice-indication", focus: "hints", label: "indication 1", tap: "hints" },
      },
      {
        voice: "En chrono, chaque indication coûte dix pour cent de bonus de rapidité.",
        visual: {
          kind: "chips",
          title: "En chrono",
          items: ["Indication 1 · −10 % de bonus", "Indication 2 · −10 % de bonus"],
          marks: ["[+]", "[+]"],
          accent: "orange",
        },
      },
      {
        voice: "XiMaths, lien en bio. Cherche d'abord.",
        visual: { kind: "cta", prompt: "ximaths ~ exercice --indication 1", line: "Cherche d'abord." },
      },
    ],
    caption:
      "Bloqué sur un exercice de maths ? Des indications progressives plutôt que le corrigé : tu apprends à chercher.",
    hashtags: ["maths", "exercice", "methode", "prepa", "licence", "etudiant", "revisions"],
  },
  {
    id: "09-ia-humains",
    need: "Avoir des solutions fiables, relues par des humains",
    audience: "Tous niveaux",
    scenes: [
      {
        voice: "L'IA t'a sorti une démo fausse. Avec beaucoup d'assurance.",
        visual: { kind: "chat", text: "On a 1/n ≥ 1/n², donc la série ∑ 1/n² diverge. ∎", verdict: "faux" },
        captions: true,
      },
      {
        voice: "En maths, une preuve fausse bien rédigée, c'est le pire des pièges.",
        visual: {
          kind: "title",
          kicker: "attention",
          text: "Une preuve *fausse*\nbien rédigée :\nle pire piège.",
          accent: "red",
        },
      },
      {
        voice: "Sur XiMaths, chaque solution est relue par trois étudiants. Des humains.",
        visual: {
          kind: "reviewers",
          title: "3 humains relisent",
          verdicts: true,
          lines: [
            "\\tfrac{1}{n^2} \\le \\tfrac{1}{n(n-1)} \\text{ pour } n \\ge 2,",
            "\\text{donc } \\textstyle\\sum \\tfrac{1}{n^2} \\text{ converge.}",
          ],
          note: "« et ∑ 1/(n(n−1)) ? »",
        },
      },
      {
        voice: "Pendant le défi du jour, l'IA est interdite.",
        visual: { kind: "phone", shot: "defi", focus: "ai", label: "IA interdite" },
      },
      {
        voice: "Ailleurs, tu peux t'en servir. Mais tu le déclares.",
        visual: {
          kind: "chips",
          title: "As-tu utilisé une IA ?",
          items: ["Aucune", "Relecture ou mise en forme", "Aide sur une idée", "Solution générée"],
          marks: ["(x)", "( )", "( )", "( )"],
          accent: "blue",
        },
      },
      {
        voice: "XiMaths. Des maths relues par des humains. Lien en bio.",
        visual: { kind: "cta", prompt: "ximaths ~ relu --par-des-humains", line: "Des maths relues par des humains." },
      },
    ],
    caption:
      "Une IA peut écrire une preuve fausse avec aplomb. Sur XiMaths, chaque solution est relue par 3 étudiants, et l'usage de l'IA est déclaré.",
    hashtags: ["ia", "maths", "etudiant", "prepa", "licence", "demonstration", "chatbot"],
  },
  {
    id: "10-publier",
    need: "Partager ses exercices et être reconnu pour ses contributions",
    audience: "Étudiants avancés, khôlleurs, enseignants",
    scenes: [
      {
        voice: "T'as un exo de colle génial qui dort dans ton classeur ?",
        visual: {
          kind: "title",
          kicker: "classeur ~ exos",
          text: "Ton meilleur exo\n*dort* dans un classeur ?",
          accent: "orange",
        },
      },
      {
        voice: "Publie-le sur XiMaths.",
        visual: { kind: "title", text: "*Publie-le.*", accent: "green", size: 128 },
      },
      {
        voice: "Énoncé en LaTeX, indications, niveau et chapitre.",
        visual: { kind: "phone", shot: "editeur", focus: "preview", label: "énoncé + aperçu" },
      },
      {
        voice: "Il est comparé aux exercices existants pour éviter les doublons, puis ouvert à tous.",
        visual: {
          kind: "chips",
          title: "Avant publication",
          items: ["Doublons vérifiés", "Ouvert à la communauté", "Licence CC BY-SA"],
          accent: "green",
        },
      },
      {
        voice:
          "Tes contributions rapportent des points, et font monter ton niveau de contributeur, jusqu'au niveau trente.",
        visual: { kind: "phone", shot: "progression", focus: "contributor", label: "niveau de contributeur" },
      },
      {
        voice: "Lien en bio. Ton exo mérite mieux qu'un classeur.",
        visual: { kind: "cta", prompt: "ximaths ~ exercices --nouveau", line: "Ton exo mérite mieux." },
      },
    ],
    caption:
      "Khôlleurs, étudiants, profs : publiez vos meilleurs exercices de maths sous licence libre, et montez en niveau de contributeur.",
    hashtags: ["maths", "colle", "prepa", "prof", "exercices", "partage", "licence"],
  },
  {
    id: "11-classements",
    need: "Se motiver par une compétition saine, à son niveau",
    audience: "Tous niveaux",
    scenes: [
      {
        voice: "Ton pote dit qu'il est meilleur que toi en maths ? Prouve-le.",
        visual: {
          kind: "leaderboard",
          rows: [
            { name: "ton pote", points: 340 },
            { name: "toi", points: 310, you: true },
            { name: "relecteur2", points: 280 },
          ],
        },
        captions: true,
      },
      {
        voice: "XiMaths a un classement par niveau, chaque semaine, du lundi au dimanche.",
        visual: { kind: "phone", shot: "classements", focus: "tabs", label: "L1 · L2 · MP · PSI…" },
      },
      {
        voice: "Les points viennent de tes solutions validées, de tes relectures et des défis du jour.",
        visual: {
          kind: "chips",
          title: "Tes points",
          items: ["Solutions validées", "Relectures", "Défis du jour"],
          accent: "green",
        },
      },
      {
        voice: "Un exercice de M2 fait marquer en M2. Chacun joue à son niveau.",
        visual: { kind: "phone", shot: "classements", focus: "board", label: "chacun à son niveau" },
      },
      {
        voice: "Lien en bio. Rendez-vous lundi.",
        visual: { kind: "cta", prompt: "ximaths ~ classements --semaine", line: "Rendez-vous lundi." },
      },
    ],
    caption:
      "Un classement de maths par niveau, remis à zéro chaque lundi. Solutions validées, relectures, défis du jour : prouve-le.",
    hashtags: ["maths", "classement", "defi", "prepa", "licence", "etudiant", "motivation"],
  },
  {
    id: "12-objectif-partiels",
    need: "Préparer partiels et concours avec un objectif daté",
    audience: "Licence et prépa",
    scenes: [
      {
        voice: "Partiels dans trois semaines. Tu fais comment ?",
        visual: {
          kind: "title",
          kicker: "partiels ~ J-21",
          text: "Partiels dans\n*3 semaines*.",
          accent: "red",
          size: 120,
        },
      },
      {
        voice: "Sur XiMaths, tu te fixes un objectif, avec une date.",
        visual: { kind: "phone", shot: "progression", focus: "goals", label: "tes objectifs" },
      },
      {
        voice: "Par exemple : quinze exercices d'analyse, d'ici le dix janvier.",
        visual: { kind: "goal", title: "Partiel d'analyse", done: 9, target: 15, deadline: "d'ici le 10 janvier" },
      },
      {
        voice: "Pour les oraux : trois exercices chronométrés par semaine.",
        visual: { kind: "goal", title: "Oraux · chrono", done: 2, target: 3, deadline: "cette semaine" },
      },
      {
        voice: "Et la carte de compétences te montre où tu en es.",
        visual: { kind: "phone", shot: "progression", focus: "skills", label: "où tu en es" },
      },
      {
        voice: "Lien en bio. Trois semaines, c'est assez.",
        visual: { kind: "cta", prompt: "ximaths ~ objectif --partiels", line: "Trois semaines, c'est assez." },
      },
    ],
    caption:
      "Partiels ou concours dans 3 semaines : fixe-toi un objectif daté en maths, et suis ta progression chapitre par chapitre.",
    hashtags: ["partiels", "revisions", "concours", "oraux", "maths", "etudiant", "studytok"],
  },
];
