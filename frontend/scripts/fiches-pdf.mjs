#!/usr/bin/env node
// Fiches de révision en PDF, composées en LaTeX : une par fiche de cours, formulaire et
// démonstration, dans public/fiches-pdf/<slug>.pdf, servies telles quelles par le site.
//
// Chaque fiche tient sur deux pages au plus : on compose en 10 pt, puis en 9 pt et 8 pt si
// elle déborde. Il faut pandoc et une distribution LaTeX (pdflatex, babel français, extarticle,
// adjustbox, mdframed, qrcode, titlesec, enumitem, fancyhdr, lastpage), mais pas le site :
//
//   node scripts/fiches-pdf.mjs          # fiches modifiées depuis le dernier passage
//   node scripts/fiches-pdf.mjs --all    # toutes
//
// Le manifeste src/lib/fiches-pdf.json garde l'empreinte du texte de chaque fiche et son
// nombre de pages : un test échoue si une fiche change sans que son PDF soit refait, ou si un
// PDF dépasse deux pages.
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const SITE = "https://ximaths.fr";
const HOST = "ximaths.fr";
const NOTES = fileURLToPath(new URL("../../backend/courses/notes/", import.meta.url));
const OUT = fileURLToPath(new URL("../public/fiches-pdf/", import.meta.url));
const MANIFEST = fileURLToPath(new URL("../src/lib/fiches-pdf.json", import.meta.url));
const MAX_PAGES = 2;
// Du plus confortable au plus serré : on garde le premier qui tient sur deux pages.
const SIZES = [10, 9, 8];

const FOLDERS = [
  { folder: "sup", base: "/rappels/", cycle: "Première année" },
  { folder: "spe", base: "/rappels/", cycle: "Deuxième année" },
  { folder: "demonstrations", base: "/demonstrations/", cycle: "Démonstration" },
];

// Les formulaires, comme sur le site (src/lib/course-notes.ts).
const FORMULA_SHEETS = new Set([
  "derivees-primitives-usuelles",
  "sommes-usuelles",
  "limites-equivalents-usuels",
  "inegalites-classiques",
]);

function frontMatter(text) {
  const end = text.indexOf("\n---\n", 4);
  const fields = Object.fromEntries(
    text
      .slice(4, end)
      .split("\n")
      .map((line) => line.split(/:\s*/, 2))
      .filter((pair) => pair.length === 2),
  );
  return { fields, body: text.slice(end + 5) };
}

function notes() {
  return FOLDERS.flatMap(({ folder, base, cycle }) =>
    readdirSync(`${NOTES}${folder}`)
      .filter((name) => name.endsWith(".md"))
      .map((name) => {
        const slug = name.replace(/\.md$/, "");
        const text = readFileSync(`${NOTES}${folder}/${name}`, "utf8");
        const { fields, body } = frontMatter(text);
        const kind =
          folder === "demonstrations"
            ? "Démonstration"
            : slug.startsWith("formulaire-") || FORMULA_SHEETS.has(slug)
              ? "Formulaire"
              : "Résumé de cours";
        return {
          slug,
          path: `${base}${slug}`,
          kind,
          cycle,
          title: fields.titre,
          programs: fields.programmes,
          topic: fields.notion || null,
          body,
          hash: createHash("sha256").update(text).digest("hex"),
        };
      }),
  );
}

/** Échappe un texte brut (titre, programme) pour LaTeX. */
function tex(text) {
  return text
    .replace(/\\/g, "\\textbackslash{}")
    .replace(/([&%#_{}])/g, "\\$1")
    .replace(/\$/g, "\\$");
}

/** Titre d'une fiche : ses formules restent des formules. */
function texTitle(text) {
  return text
    .split(/(\$[^$]+\$)/)
    .map((part, index) => (index % 2 ? part : tex(part)))
    .join("");
}

/** Le corps en LaTeX, par pandoc ; les formules en bloc se réduisent si elles débordent. */
function bodyToLatex(markdown) {
  const absolute = markdown.replace(/\]\(\//g, `](${SITE}/`);
  const latex = execFileSync(
    "pandoc",
    ["--from=markdown+tex_math_dollars-auto_identifiers-implicit_figures", "--to=latex", "--wrap=preserve"],
    { input: absolute, encoding: "utf8" },
  );
  // \[ … \] → \formule{…}, sans toucher aux « \\[1ex] » des tableaux. Les interlignes
  // de tableau, élargis pour l'écran, reviennent à la mesure de LaTeX (\arraystretch).
  return latex
    .replace(/(?<!\\)\\\[([\s\S]*?)(?<!\\)\\\]/g, (_, formula) => `\\formule{${formula.trim()}}`)
    .replace(/\\\\\[\d+(?:\.\d+)?ex\]/g, "\\\\[0.8ex]");
}

function document(note, size) {
  const url = `${SITE}${note.path}`;
  const practice = note.topic ? `${HOST}/chapitres/${note.topic}` : `${HOST}/exercices`;
  return String.raw`\documentclass[${size}pt,a4paper]{extarticle}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[french]{babel}
\usepackage{amsmath,amssymb,mathtools}
\usepackage[a4paper,left=13mm,right=13mm,top=12mm,bottom=15mm,footskip=7mm]{geometry}
\usepackage[dvipsnames]{xcolor}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{adjustbox}
\usepackage{mdframed}
\usepackage{qrcode}
\usepackage{fancyhdr}
\usepackage{lastpage}
\usepackage{newunicodechar}
\usepackage[colorlinks,linkcolor=corail,urlcolor=corail,pdftitle={${tex(note.title)} · ${note.kind} · XiMaths},pdfauthor={XiMaths}]{hyperref}

\definecolor{corail}{HTML}{B8372E}
\definecolor{fond}{HTML}{F5F5F3}
\newcommand{\R}{\mathbb{R}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\C}{\mathbb{C}}
\newcommand{\K}{\mathbb{K}}
\newunicodechar{⟹}{\ensuremath{\Longrightarrow}}
\newunicodechar{⟺}{\ensuremath{\Longleftrightarrow}}
\newunicodechar{ℤ}{\ensuremath{\mathbb{Z}}}
\newunicodechar{ℝ}{\ensuremath{\mathbb{R}}}
\newunicodechar{σ}{\ensuremath{\sigma}}
\newunicodechar{π}{\ensuremath{\pi}}
\newunicodechar{ő}{\H{o}}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% Une fiche de révision : dense, sans retrait, des intertitres serrés.
\setlength{\parindent}{0pt}
\setlength{\parskip}{2.5pt plus 1pt}
\setlist{nosep,leftmargin=1.4em}
\titleformat{\subsection}{\normalfont\large\bfseries\color{corail}}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{7pt plus 2pt}{2pt}
\titleformat{\subsubsection}{\normalfont\normalsize\bfseries}{}{0pt}{}
\titlespacing*{\subsubsection}{0pt}{5pt plus 1pt}{1pt}
\setcounter{secnumdepth}{0}

% Formule en bloc : centrée, réduite pour tenir dans la largeur si besoin.
\renewcommand{\arraystretch}{1.3}
\newcommand{\formule}[1]{\par\vspace{2pt}{\centering\adjustbox{max width=\linewidth}{$\displaystyle #1$}\par}\vspace{2pt}}

% Définitions et théorèmes (les citations du Markdown) : un filet corail sur fond gris.
\renewenvironment{quote}{\begin{mdframed}[topline=false,bottomline=false,rightline=false,linewidth=1.4pt,linecolor=corail,backgroundcolor=fond,innerleftmargin=6pt,innerrightmargin=5pt,innertopmargin=3pt,innerbottommargin=3pt,skipabove=4pt,skipbelow=4pt]}{\end{mdframed}}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[L]{\scriptsize\color{gray}XiMaths · \href{${url}}{${HOST}${note.path}} · des exercices corrigés par d'autres étudiants : ${practice}}
\fancyfoot[R]{\scriptsize\color{gray}\thepage/\pageref*{LastPage}}

\begin{document}
\begin{minipage}[t]{0.8\linewidth}
{\small\color{corail}\textbf{XiMaths} · ${note.kind} · ${note.cycle}}\par\smallskip
{\LARGE\bfseries ${texTitle(note.title)}\par}\smallskip
{\small ${tex(note.programs)}}
\end{minipage}\hfill
\begin{minipage}[t]{0.17\linewidth}\raggedleft
\href{${url}}{\qrcode[height=1.6cm]{${url}}}\par
{\tiny ${HOST}}
\end{minipage}
\par\medskip\hrule\medskip

${bodyToLatex(note.body)}
\end{document}
`;
}

function pages(pdf) {
  const info = execFileSync("pdfinfo", [pdf], { encoding: "utf8" });
  return Number(/Pages:\s+(\d+)/.exec(info)[1]);
}

/** Compose la fiche au premier corps qui tient sur deux pages ; renvoie le corps et les pages. */
function build(note) {
  const dir = mkdtempSync(join(tmpdir(), "fiche-"));
  try {
    let last;
    for (const size of SIZES) {
      writeFileSync(join(dir, "fiche.tex"), document(note, size));
      for (let run = 0; run < 2; run++) {
        // Deux passes : la seconde connaît le nombre total de pages (LastPage).
        try {
          execFileSync("pdflatex", ["-interaction=nonstopmode", "-halt-on-error", "fiche.tex"], {
            cwd: dir,
            stdio: "pipe",
          });
        } catch (error) {
          const log = readFileSync(join(dir, "fiche.log"), "utf8");
          const line = log.split("\n").findIndex((text) => text.startsWith("!"));
          throw new Error(`${note.slug} : LaTeX refuse la fiche\n${log.split("\n").slice(line, line + 8).join("\n")}`, {
            cause: error,
          });
        }
      }
      last = { size, pages: pages(join(dir, "fiche.pdf")) };
      if (last.pages <= MAX_PAGES) break;
    }
    copyFileSync(join(dir, "fiche.pdf"), `${OUT}${note.slug}.pdf`);
    return last;
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

function main() {
  const all = process.argv.includes("--all");
  const manifest = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, "utf8")) : {};
  mkdirSync(OUT, { recursive: true });
  const everything = notes();
  const todo = everything.filter(
    (note) =>
      all ||
      manifest[note.slug]?.hash !== note.hash ||
      manifest[note.slug]?.engine !== "latex" ||
      !existsSync(`${OUT}${note.slug}.pdf`),
  );
  console.log(`${todo.length} PDF à faire.`);
  const tooLong = [];
  for (const note of todo) {
    const { size, pages: count } = build(note);
    manifest[note.slug] = { hash: note.hash, path: note.path, engine: "latex", size, pages: count };
    const kb = Math.round(statSync(`${OUT}${note.slug}.pdf`).size / 1024);
    console.log(`${note.slug}.pdf · ${count} page(s) · ${size} pt · ${kb} Ko`);
    if (count > MAX_PAGES) tooLong.push(note.slug);
  }

  // Les fiches supprimées sortent du manifeste.
  const known = new Set(everything.map((note) => note.slug));
  const sorted = Object.fromEntries(
    Object.entries(manifest)
      .filter(([slug]) => known.has(slug))
      .sort(([a], [b]) => a.localeCompare(b)),
  );
  writeFileSync(MANIFEST, `${JSON.stringify(sorted, null, 2)}\n`);
  if (tooLong.length > 0) {
    console.error(`Plus de ${MAX_PAGES} pages même en ${SIZES.at(-1)} pt : ${tooLong.join(", ")}`);
    process.exitCode = 1;
  }
}

main();
