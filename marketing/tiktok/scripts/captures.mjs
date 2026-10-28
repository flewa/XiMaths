// Captures de l'application sur téléphone (390 × 844, densité 3), pour les vidéos.
// Il faut XiMaths lancé avec la base de démonstration : `./dev.sh` à la racine du dépôt.
//
//   npm run captures                     # toutes
//   npm run captures -- exercice defi    # seulement celles-ci
//
// Écrit public/shots/<nom>.png et public/shots/manifest.json : la taille de chaque page
// et la position des éléments sur lesquels les scènes zooment, en pixels CSS.
// Le script crée un objectif pour lea s'il n'en a pas : il ne touche à rien d'autre.
import { createRequire } from "node:module";
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Playwright n'est pas une dépendance du projet : celui de la machine sert (npm i -g playwright).
const { chromium } = createRequire(import.meta.url)("playwright");

const BASE = process.env.XIMATHS_URL ?? "http://localhost:3000";
// Mot de passe des comptes de démonstration (seed_demo), pas un secret.
const PASSWORD = process.env.DEMO_PASSWORD ?? "demo-ximaths-2026";
const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "public", "shots");
const PHONE = { width: 390, height: 844 };
const SCALE = 3;
// Au-delà, la capture pèse lourd pour rien : les scènes ne défilent pas plus bas.
const MAX_HEIGHT = 3800;

const SOLUTION = [
  "La suite est croissante : $u_{n+1} - u_n = \\frac{1}{(n+1)^2} > 0$.",
  "",
  "Elle est majorée par $2$, car $\\frac{1}{k^2} \\le \\frac{1}{k-1} - \\frac{1}{k}$ pour $k \\ge 2$.",
  "",
  "Croissante et majorée, $(u_n)$ converge.",
].join("\n");

const STATEMENT = [
  "Soit $A \\in \\mathcal{M}_n(\\mathbb{R})$ nilpotente.",
  "",
  "Montrer que $I - A$ est inversible et que",
  "",
  "$$(I - A)^{-1} = \\sum_{k=0}^{n-1} A^k.$$",
].join("\n");

// L'aperçu suit le bloc de l'éditeur.
const PREVIEW =
  '.cm-editor >> nth=0 >> xpath=ancestor::div[contains(@class, "space-y-1.5")][1]/following-sibling::*[1]';

/** [nom, compte, chemin, préparation, éléments à repérer] */
const SHOTS = [
  ["catalogue", "yanis", "/exercices?niveau=PSI", null, { levels: 'nav[aria-label="Filtrer par niveau"]' }],
  [
    "exercice",
    "lea",
    "/exercices/3",
    null,
    {
      statement: "section[aria-labelledby=enonce]",
      hints: "section[aria-labelledby=indications]",
      form: "section[aria-labelledby=ta-solution]",
      solutions: "section[aria-labelledby=solutions]",
    },
  ],
  [
    "exercice-indication",
    "lea",
    "/exercices/3",
    async (page) => {
      await page.locator("section[aria-labelledby=indications] summary").first().click();
    },
    { hints: "section[aria-labelledby=indications]" },
  ],
  [
    "solution",
    "lea",
    "/exercices/2",
    async (page) => {
      const editor = page.locator("section[aria-labelledby=ta-solution] .cm-content").first();
      await editor.click();
      await page.keyboard.insertText(SOLUTION);
      await page.waitForTimeout(600);
    },
    { form: "section[aria-labelledby=ta-solution]", editor: ".cm-editor >> nth=0", preview: PREVIEW },
  ],
  [
    "defi",
    "lea",
    "/defi",
    null,
    { rules: "main ul >> nth=0", ai: "main ul >> nth=0 >> li >> nth=2", challenge: "main ul >> nth=1" },
  ],
  [
    "classements",
    "lea",
    "/classements",
    null,
    { tabs: 'nav[aria-label="Choisir un classement"]', board: "main table" },
  ],
  [
    "progression",
    "lea",
    "/progression",
    async (page) => {
      if (await page.getByText("Aucun objectif en cours").count()) {
        await page.selectOption("#goal-kind", "solutions");
        await page.fill("#goal-target", "15");
        const year = new Date().getMonth() >= 9 ? new Date().getFullYear() + 1 : new Date().getFullYear();
        await page.fill("#goal-deadline", `${year}-01-10`);
        await page.selectOption("#goal-topic", { label: "Analyse" });
        await page.getByLabel("Intitulé (facultatif)").fill("Partiel d'analyse");
        await page.getByRole("button", { name: "Ajouter l'objectif" }).click();
        await page.getByText("Partiel d'analyse").first().waitFor();
        await page.reload({ waitUntil: "networkidle" });
      }
    },
    {
      week: "section[aria-labelledby=this-week]",
      contributor: ["section[aria-labelledby=skills] h2", "section[aria-labelledby=skills] > p >> nth=1"],
      skills: "section[aria-labelledby=skills] ul",
      pause: [
        "section[aria-labelledby=settings] >> text=Examens ou vacances",
        "section[aria-labelledby=settings] form >> nth=1",
      ],
      goals: [
        "section[aria-labelledby=goals] h2",
        "section[aria-labelledby=goals] h2 >> xpath=following-sibling::*[1]",
      ],
    },
  ],
  [
    "editeur",
    "camille",
    "/exercices/nouveau",
    async (page) => {
      await page.fill("#title", "Inverse de I − A pour A nilpotente");
      await page.locator(".cm-content").first().click();
      await page.keyboard.insertText(STATEMENT);
      await page.waitForTimeout(800);
    },
    { editor: ".cm-editor >> nth=0", preview: PREVIEW },
  ],
];

async function login(browser, user) {
  const context = await browser.newContext({
    viewport: PHONE,
    deviceScaleFactor: SCALE,
    isMobile: true,
    hasTouch: true,
    colorScheme: "light",
    locale: "fr-FR",
  });
  if (user !== "anon") {
    const page = await context.newPage();
    await page.goto(`${BASE}/connexion`, { waitUntil: "networkidle" });
    await page.fill('input[name="login"]', user);
    await page.fill('input[name="password"]', PASSWORD);
    await Promise.all([
      page.waitForURL((url) => !url.pathname.startsWith("/connexion")),
      page.click('button[type="submit"]'),
    ]);
    await page.close();
  }
  return context;
}

/** Rectangle d'un élément, ou celui qui englobe plusieurs éléments. */
async function box(page, selectors) {
  const rects = [];
  for (const selector of [selectors].flat()) {
    const rect = await single(page, selector);
    if (!rect) return null;
    rects.push(rect);
  }
  const x = Math.min(...rects.map((r) => r.x));
  const y = Math.min(...rects.map((r) => r.y));
  const w = Math.max(...rects.map((r) => r.x + r.w)) - x;
  const h = Math.max(...rects.map((r) => r.y + r.h)) - y;
  return { x, y, w, h };
}

async function single(page, selector) {
  const locator = page.locator(selector).first();
  if (!(await locator.count())) return null;
  const rect = await locator.evaluate((element) => {
    const r = element.getBoundingClientRect();
    return { x: r.left + window.scrollX, y: r.top + window.scrollY, w: r.width, h: r.height };
  });
  return Object.fromEntries(Object.entries(rect).map(([key, value]) => [key, Math.round(value)]));
}

const only = process.argv.slice(2);
mkdirSync(OUT, { recursive: true });
const manifestPath = join(OUT, "manifest.json");
const manifest = existsSync(manifestPath) ? JSON.parse(readFileSync(manifestPath, "utf8")) : {};
const browser = await chromium.launch();
const contexts = {};

for (const [name, user, path, prepare, targets] of SHOTS) {
  if (only.length && !only.includes(name)) continue;
  contexts[user] ??= await login(browser, user);
  const page = await contexts[user].newPage();
  await page.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
  if (prepare) await prepare(page);
  // Pas de barre d'onglets ni de lien d'évitement sur les captures : le cadre du téléphone
  // les remplace, et la barre fixe se répéterait au défilement.
  await page.addStyleTag({ content: 'nav[aria-label="Navigation principale"]{display:none!important}' });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(400);

  const height = Math.min(await page.evaluate(() => document.documentElement.scrollHeight), MAX_HEIGHT);
  const focus = {};
  for (const [key, selector] of Object.entries(targets)) {
    const rect = await box(page, selector);
    if (rect) focus[key] = rect;
    else console.warn(`  ${name} : « ${key} » introuvable (${selector})`);
  }
  await page.screenshot({
    path: join(OUT, `${name}.png`),
    fullPage: true,
    clip: { x: 0, y: 0, width: PHONE.width, height },
  });
  manifest[name] = { width: PHONE.width, height, scale: SCALE, focus };
  console.log(`${name} : ${PHONE.width} × ${height}, ${Object.keys(focus).join(", ")}`);
  await page.close();
}

writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
await browser.close();
