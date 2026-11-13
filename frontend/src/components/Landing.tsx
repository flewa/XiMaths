import { Caveat } from "next/font/google";
import Link from "next/link";

import { Brand } from "./SidebarNav";

// L'écriture à la main de la copie : chargée seulement sur cette page.
const hand = Caveat({ subsets: ["latin", "latin-ext"], weight: ["500", "600", "700"] });

/** Le bouton principal de la page : plus grand que ceux du reste du site, c'est la seule action. */
const mainAction =
  "inline-flex min-h-12 items-center justify-center rounded-lg bg-accent px-6 text-base font-semibold text-accent-ink hover:brightness-110";

/**
 * L'accueil d'un visiteur, réduit à l'essentiel : ce qu'est le site en une phrase, une action,
 * et, à côté, une copie à petits carreaux corrigée au stylo rouge, qui le montre sans un mot.
 * Ni barre latérale ni barre du bas (la classe « landing » les masque, voir le gabarit) : le
 * catalogue est à un clic.
 */
export function Landing() {
  return (
    <div className="landing page-wide">
      <header className="flex items-center justify-between sm:-mt-6">
        <Brand />
        <Link
          href="/connexion"
          className="inline-flex min-h-10 items-center rounded-lg px-3 text-[15px] font-medium text-ink hover:bg-hover"
        >
          Se connecter
        </Link>
      </header>

      <div className="mt-10 grid gap-14 sm:mt-16 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-center xl:gap-16">
        <section aria-labelledby="accroche">
          <h1 id="accroche" className="landing-title">
            Ta copie de maths, corrigée par d&apos;autres étudiants.
          </h1>
          <p className="mt-6 max-w-[40ch] text-lg leading-relaxed text-body">
            Des exercices de la L1 au M2 et en prépa. Écris ta solution à la main, envoie une photo&nbsp;:
            trois relecteurs te disent ce qui est juste.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-x-6 gap-y-3">
            <Link href="/inscription" className={mainAction}>
              Créer un compte
            </Link>
            <Link
              href="/exercices"
              className="inline-flex min-h-12 items-center text-base font-medium text-ink underline decoration-hairline-strong underline-offset-4 hover:decoration-ink"
            >
              Voir les exercices
            </Link>
          </div>
          <p className="mt-4 text-sm text-mute">Gratuit et sans publicité.</p>
        </section>

        <CorrectedCopy />
      </div>
    </div>
  );
}

/** Une copie d'étudiant : la preuve à l'encre bleue, les relecteurs au stylo rouge. */
function CorrectedCopy() {
  return (
    <figure
      role="img"
      aria-label="Une copie manuscrite qui démontre que racine de 2 est irrationnel, corrigée au stylo rouge : trois coches, une remarque, et « Juste ! 3 relecteurs sur 3 »."
      className={`${hand.className} copy-sheet`}
    >
      <div className="copy-ink">
        <p className="copy-title">Montrer que √2 est irrationnel.</p>
        <p>&nbsp;</p>
        <p>Supposons √2 = p/q, avec p/q irréductible.</p>
        <p>Alors p² = 2q², donc p² est pair,</p>
        <p>donc p est pair : p = 2k.</p>
        <p>Alors 4k² = 2q², soit q² = 2k² :</p>
        <p>q est pair aussi.</p>
        <p>p et q pairs : contradiction.</p>
      </div>
      <span className="copy-red copy-check" style={{ top: "calc(150px * var(--s))" }}>
        ✓
      </span>
      <svg className="copy-wave" viewBox="0 0 230 10" preserveAspectRatio="none">
        <path
          d="M2 6 Q 12 0 22 6 T 42 6 T 62 6 T 82 6 T 102 6 T 122 6 T 142 6 T 162 6 T 182 6 T 202 6 T 222 6"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
      </svg>
      <span className="copy-red copy-note">
        Justifie&nbsp;: si p est
        <br />
        impair, p² aussi.
      </span>
      <span className="copy-red copy-check" style={{ top: "calc(222px * var(--s))" }}>
        ✓
      </span>
      <span className="copy-red copy-check" style={{ top: "calc(294px * var(--s))" }}>
        ✓
      </span>
      <span className="copy-red copy-verdict">Juste ! 3 relecteurs sur 3</span>
    </figure>
  );
}
