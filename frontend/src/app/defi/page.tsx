import type { Metadata } from "next";
import Link from "next/link";

import { ApiUnavailable, Difficulty, logApiError } from "@/components/ExerciseMeta";
import { FormMessage } from "@/components/Form";
import { Tag } from "@/components/Tag";
import { ChallengeStart } from "@/components/Training";
import { type DailyChallenge, type Me, fetchDailyChallenges, fetchMe } from "@/lib/api";

export const metadata: Metadata = {
  title: "Défi du jour",
  description: "Un défi chronométré par niveau, chaque jour : 30 minutes, une seule tentative, un énoncé tiré pour toi.",
};

const RULES = [
  "30 minutes (40 avec un tiers-temps), une seule tentative, jusqu'à minuit. Abandonner consomme la tentative, sans autre pénalité.",
  "Ton énoncé est tiré pour toi : les autres ont d'autres valeurs. Partager sa méthode reste permis, c'est de l'apprentissage.",
  "Cours personnel autorisé, IA interdite. Le collage depuis l'extérieur est désactivé ; les sorties d'onglet sont comptées, jamais pénalisées.",
  "Le chrono ne s'arrête pas si tu fermes l'onglet : la session se reprend, et ta dernière version est rendue à l'échéance.",
  "Barème : 20 × la difficulté. 60 % dès que ta réponse est reconnue juste, 40 % quand ta justification est validée par les pairs. Bonus de rapidité jusqu'à ×1,25 ; chaque indication ouverte en retire 10 %.",
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
  if (attempt.status === "abandonnee") return <p className="text-mute">[-] Abandonné : à demain.</p>;
  return (
    <p>
      {attempt.answer_correct ? `[+] Réponse juste : +${attempt.answer_points} points` : "[-] Réponse non reconnue"}
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
        <h2 className="font-bold">
          {challenge.level_name} <span className="font-normal text-mute">· {challenge.exercise_title}</span>
        </h2>
        {challenge.attempt && <Tag strong>{ATTEMPT_LABELS[challenge.attempt.status]}</Tag>}
      </div>
      <p className="mt-1 text-sm text-mute">
        <Difficulty value={challenge.difficulty} /> · jusqu&apos;à {challenge.points_max} points ·{" "}
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
  // Le niveau déclaré d'abord : c'est le défi de tes pairs.
  const ordered = [...challenges].sort(
    (a, b) => Number(b.level === me?.declared_level) - Number(a.level === me?.declared_level),
  );

  return (
    <div className="max-w-[720px]">
      <h1>Défi du jour</h1>
      <p className="mt-2 text-body">
        Un exercice par niveau, chaque jour, compté dans le classement de la semaine. Tu peux relever
        celui de n&apos;importe quel niveau : les points comptent pour le niveau de l&apos;exercice.
      </p>

      <ul className="mt-6 space-y-2 text-body">
        {RULES.map((rule) => (
          <li key={rule} className="flex gap-2">
            <span className="shrink-0 text-mute">[+]</span>
            <span>{rule}</span>
          </li>
        ))}
      </ul>

      {ordered.length === 0 ? (
        <p className="mt-10 text-mute">Pas de défi ouvert pour l&apos;instant. Les défis ouvrent chaque jour à minuit.</p>
      ) : (
        <ul className="mt-10 divide-y divide-hairline border-y border-hairline">
          {ordered.map((challenge) => (
            <ChallengeCard key={challenge.id} challenge={challenge} me={me} />
          ))}
        </ul>
      )}
      {me && (
        <p className="mt-6 text-sm text-mute">
          Être prévenu à l&apos;ouverture :{" "}
          <Link href="/reglages" className="underline underline-offset-4">
            réglages
          </Link>
          .
        </p>
      )}
    </div>
  );
}
