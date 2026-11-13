import type { Metadata } from "next";
import Link from "next/link";

import { ApiUnavailable, Difficulty, logApiError } from "@/components/ExerciseMeta";
import { FormMessage } from "@/components/Form";
import { Tag } from "@/components/Tag";
import { ChallengeStart } from "@/components/Training";
import { type DailyChallenge, type Me, fetchDailyChallenges, fetchMe } from "@/lib/api";
import { MathText } from "@/components/MathText";
import { PageIntro } from "@/components/PageIntro";

export const metadata: Metadata = {
  title: "Défi du jour",
  description:
    "Un défi chronométré chaque jour, de la 1re année au master : 30 minutes, une seule tentative, un énoncé tiré pour toi, une copie écrite à la main.",
};

const RULES = [
  "30 minutes, une seule tentative, jusqu'à minuit. Abandonner consomme la tentative, sans autre pénalité.",
  "Ton énoncé est tiré pour toi : les autres ont d'autres valeurs. Partager sa méthode reste permis, c'est de l'apprentissage.",
  "Copie écrite à la main sur papier : au départ, scanne le QR code avec ton téléphone, puis photographie tes pages (3 au plus) avant la fin du temps, avec une minute de grâce. Rien ne se tape.",
  "Cours personnel autorisé, IA interdite. Les sorties d'onglet sont comptées, jamais pénalisées.",
  "Le chrono ne s'arrête pas si tu fermes l'onglet : la session se reprend, et les photos arrivées sont rendues à l'échéance.",
  "Barème : 20 × la difficulté, gagnés quand ta copie est validée par les pairs. Bonus de rapidité jusqu'à ×1,25 ; chaque indication ouverte en retire 10 %.",
];

const ATTEMPT_LABELS: Record<string, string> = {
  en_cours: "en cours",
  en_pause: "en cours",
  rendue: "rendu",
  abandonnee: "abandonné",
};

function Attempt({ attempt }: { attempt: NonNullable<DailyChallenge["attempt"]> }) {
  if (attempt.status === "en_cours" || attempt.status === "en_pause") {
    return (
      <Link href={`/entrainement/${attempt.session_id}`} className="underline underline-offset-4">
        [→] Reprendre : le chrono tourne
      </Link>
    );
  }
  if (attempt.status === "abandonnee") return <p className="text-mute">Abandonné : à demain.</p>;
  return (
    <p>
      Rendu
      {" · "}
      <Link href={`/entrainement/${attempt.session_id}`} className="underline underline-offset-4">
        voir mon rendu
      </Link>
    </p>
  );
}

function ChallengeCard({ challenge, me }: { challenge: DailyChallenge; me: Me | null }) {
  return (
    <li className="py-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2>
          {challenge.group_label}{" "}
          <span className="font-normal text-mute">
            · <MathText>{challenge.exercise_title}</MathText>
          </span>
        </h2>
        {challenge.attempt && <Tag strong>{ATTEMPT_LABELS[challenge.attempt.status]}</Tag>}
      </div>
      <p className="mt-1 text-sm text-mute">
        {/* Le défi vaut pour tout le groupe : un exercice de PTSI s'adresse aussi à la MPSI et à la L1. */}
        Exercice de {challenge.level}
        {challenge.group_levels.length > 1 ? ", pour tout le groupe" : ""} · <Difficulty value={challenge.difficulty} /> ·
        jusqu&apos;à{" "}
        {challenge.points_max} points ·{" "}
        {challenge.hint_count} indication{challenge.hint_count > 1 ? "s" : ""}
      </p>
      <div className="mt-3">
        {challenge.attempt ? (
          <Attempt attempt={challenge.attempt} />
        ) : !me ? (
          <Link href="/connexion?suivant=/defi" className="underline underline-offset-4">
            Connecte-toi pour relever le défi
          </Link>
        ) : me.email_verified ? (
          <ChallengeStart challengeId={challenge.id} minutes={challenge.minutes} />
        ) : (
          <FormMessage error="Confirme d'abord ton adresse email : le lien t'a été envoyé à l'inscription." />
        )}
      </div>
    </li>
  );
}

export default async function ChallengePage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchDailyChallenges()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, challenges] = data;
  // Le groupe de ton niveau déclaré d'abord : c'est le défi de tes pairs.
  const mine = (challenge: DailyChallenge) =>
    Boolean(me?.declared_level && challenge.group_levels.includes(me.declared_level));
  const ordered = [...challenges].sort((a, b) => Number(mine(b)) - Number(mine(a)));

  return (
    <div className="max-w-[720px]">
      <h1>Défi du jour</h1>
      <PageIntro id="defi">
        Chaque jour, un exercice pour la 1re année, un pour la 2e, un pour la L3 et un pour le master, comptés
        dans le classement de la semaine. Tu peux relever n&apos;importe lequel : les points comptent pour le
        niveau de l&apos;exercice.
      </PageIntro>

      <p className="mt-3 text-sm text-mute">
        30 minutes, une seule tentative, copie écrite à la main et photographiée. Les règles complètes sont sous la liste.
      </p>

      {/* Les défis d'abord : sur téléphone, les règles repoussaient le premier d'un écran. */}
      {ordered.length === 0 ? (
        <p className="mt-8 text-mute">Pas de défi ouvert pour l&apos;instant. Les défis ouvrent chaque jour à minuit.</p>
      ) : (
        <ul className="mt-6 divide-y divide-hairline border-y border-hairline">
          {ordered.map((challenge) => (
            <ChallengeCard key={challenge.id} challenge={challenge} me={me} />
          ))}
        </ul>
      )}

      <details className="mt-6 rounded-2xl border border-hairline px-4 py-3">
        <summary className="font-medium text-ink">Les règles du défi</summary>
        <ul className="mt-3 space-y-2 text-body">
          {RULES.map((rule) => (
            <li key={rule} className="flex gap-2">
              <span aria-hidden="true" className="mt-[0.6em] size-1.5 shrink-0 rounded-full bg-stone" />
              <span>{rule}</span>
            </li>
          ))}
        </ul>
      </details>
      {me && (
        <p className="mt-6 text-sm text-mute">
          Recevoir une notification à l&apos;ouverture :{" "}
          <Link href="/reglages" className="underline underline-offset-4">
            réglages
          </Link>
          .
        </p>
      )}
    </div>
  );
}
