#!/usr/bin/env node
// Fiches de révision en PDF : une par fiche de cours et par démonstration, dans
// public/fiches-pdf/<slug>.pdf, servies telles quelles par le site.
//
// On imprime les pages du site lui-même (mise en page d'impression de globals.css) : le PDF
// a exactement les formules du site. Il faut donc le site lancé en local, fiches publiées :
//
//   BASE_URL=http://localhost:3000 node scripts/fiches-pdf.mjs          # fiches modifiées
//   BASE_URL=http://localhost:3000 node scripts/fiches-pdf.mjs --all    # toutes
//
// Le manifeste src/lib/fiches-pdf.json garde l'empreinte du texte de chaque fiche : un test
// échoue si une fiche change sans que son PDF soit refait.
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

// Playwright n'est pas une dépendance du site : celui de la machine qui génère les PDF.
const { chromium } = createRequire(import.meta.url)("playwright");

const BASE = process.env.BASE_URL ?? "http://localhost:3000";
// Les liens du PDF mènent au site en ligne, pas à la copie locale qui l'a imprimé.
const SITE = "https://ximaths.fr";
const NOTES = fileURLToPath(new URL("../../backend/courses/notes/", import.meta.url));
const OUT = fileURLToPath(new URL("../public/fiches-pdf/", import.meta.url));
const MANIFEST = fileURLToPath(new URL("../src/lib/fiches-pdf.json", import.meta.url));
// Largeur utile d'une page A4 avec 15 mm de marge de chaque côté, en pixels CSS (96 ppp).
const PAGE_WIDTH = Math.round(((210 - 30) / 25.4) * 96);

const FOLDERS = [
  { folder: "sup", base: "/rappels/" },
  { folder: "spe", base: "/rappels/" },
  { folder: "demonstrations", base: "/demonstrations/" },
];

function notes() {
  return FOLDERS.flatMap(({ folder, base }) =>
    readdirSync(`${NOTES}${folder}`)
      .filter((name) => name.endsWith(".md"))
      .map((name) => {
        const slug = name.replace(/\.md$/, "");
        const text = readFileSync(`${NOTES}${folder}/${name}`, "utf8");
        return { slug, path: `${base}${slug}`, hash: createHash("sha256").update(text).digest("hex") };
      }),
  );
}

const footer = (path) => `
  <div style="width:100%; padding:0 15mm; display:flex; justify-content:space-between;
              font-family:Helvetica,Arial,sans-serif; font-size:7.5px; color:#777;">
    <span>XiMaths · ximaths.fr${path}</span>
    <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
  </div>`;

async function main() {
  const all = process.argv.includes("--all");
  const manifest = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, "utf8")) : {};
  mkdirSync(OUT, { recursive: true });
  const todo = notes().filter(
    (note) => all || manifest[note.slug]?.hash !== note.hash || !existsSync(`${OUT}${note.slug}.pdf`),
  );
  console.log(`${todo.length} PDF à faire.`);

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: PAGE_WIDTH, height: 1100 } });
  for (const note of todo) {
    const response = await page.goto(`${BASE}${note.path}`, { waitUntil: "networkidle" });
    if (!response?.ok()) throw new Error(`${note.path} : ${response?.status()} (fiche publiée ?)`);
    await page.emulateMedia({ media: "print", colorScheme: "light" });
    await page.evaluate(() => document.fonts.ready);
    const fitted = await page.evaluate((site) => {
      // Liens absolus vers le site en ligne.
      for (const link of document.querySelectorAll("a[href]")) {
        const url = new URL(link.getAttribute("href"), location.href);
        if (url.origin === location.origin) link.setAttribute("href", `${site}${url.pathname}${url.search}${url.hash}`);
      }
      // Une formule plus large que la page est réduite pour tenir, au lieu d'être coupée.
      let count = 0;
      for (const formula of document.querySelectorAll(".katex-display")) {
        const ratio = formula.clientWidth / formula.scrollWidth;
        if (ratio < 0.999) {
          formula.style.zoom = String(Math.max(ratio, 0.5));
          count += 1;
        }
      }
      return count;
    }, SITE);
    const file = `${OUT}${note.slug}.pdf`;
    await page.pdf({
      path: file,
      preferCSSPageSize: true,
      printBackground: true,
      displayHeaderFooter: true,
      headerTemplate: "<span></span>",
      footerTemplate: footer(note.path),
    });
    manifest[note.slug] = { hash: note.hash, path: note.path };
    console.log(`${note.slug}.pdf · ${Math.round(statSync(file).size / 1024)} Ko · ${fitted} formule(s) réduite(s)`);
  }
  await browser.close();

  // Les fiches supprimées sortent du manifeste.
  const known = new Set(notes().map((note) => note.slug));
  const sorted = Object.fromEntries(
    Object.entries(manifest)
      .filter(([slug]) => known.has(slug))
      .sort(([a], [b]) => a.localeCompare(b)),
  );
  writeFileSync(MANIFEST, `${JSON.stringify(sorted, null, 2)}\n`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
