"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiPost } from "@/lib/client-api";

import { Icon } from "./Icon";

export function LogoutButton({ className = "text-mute hover:text-ink" }: { className?: string }) {
  const router = useRouter();
  return (
    <button
      type="button"
      className={className}
      onClick={async () => {
        await apiPost("/auth/logout");
        router.push("/");
        router.refresh();
      }}
    >
      Déconnexion
    </button>
  );
}

/** Masquer ou réafficher sa présence dans les classements. */
export function LeaderboardVisibility({ visible }: { visible: boolean }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  return (
    <p className="text-sm text-mute">
      {visible ? "Tu apparais dans les classements." : "Ta présence dans les classements est masquée."}{" "}
      <button
        type="button"
        className="font-medium underline underline-offset-4"
        onClick={async () => {
          const result = await apiPost("/auth/leaderboard-visibility", { visible: !visible });
          if (result.ok) router.refresh();
          else setError(result.error);
        }}
      >
        {visible ? "Masquer ma présence" : "Réapparaître"}
      </button>
      {error && <span role="alert"> {error}</span>}
    </p>
  );
}

export function VerifyBanner({ email }: { email: string }) {
  const [message, setMessage] = useState<string | null>(null);
  return (
    <div className="border-b border-hairline bg-accent-soft">
      <p className="mx-auto flex max-w-[1180px] gap-2.5 px-5 py-2.5 text-sm leading-relaxed sm:px-10">
        <Icon name="alert" size={17} className="mt-0.5 text-accent-text" />
        <span>
          Confirme ton adresse <strong>{email}</strong> pour publier, résoudre et voter : le lien
          t&apos;a été envoyé par email.{" "}
          {message ?? (
            <button
              type="button"
              className="font-medium underline underline-offset-4"
              onClick={async () => {
                const result = await apiPost("/auth/resend-verification");
                setMessage(result.ok ? "Email renvoyé." : result.error);
              }}
            >
              Renvoyer l&apos;email
            </button>
          )}
        </span>
      </p>
    </div>
  );
}

/** Sur place, là où l'action est bloquée : l'adresse à confirmer et de quoi renvoyer le lien.
 * Le bandeau du haut dit la même chose, mais il est sorti de l'écran quand on arrive ici. */
export function VerifyEmailNotice({ email, action, compact = false }: { email: string; action: string; compact?: boolean }) {
  const [message, setMessage] = useState<string | null>(null);
  const resend = async () => {
    const result = await apiPost("/auth/resend-verification");
    setMessage(result.ok ? `Email renvoyé à ${email}. Pense à regarder dans les indésirables.` : result.error);
  };
  // Une ligne, quand le cadre complet est déjà plus haut sur la même page.
  if (compact) {
    return (
      <p className="text-body">
        Confirme ton adresse email pour {action}.{" "}
        {message ? (
          <span role="status">{message}</span>
        ) : (
          <button type="button" className="font-medium underline underline-offset-4" onClick={resend}>
            Renvoyer l&apos;email
          </button>
        )}
      </p>
    );
  }
  return (
    <div className="rounded-xl bg-accent-soft px-4 py-3 leading-relaxed">
      <p className="flex gap-2.5">
        <Icon name="alert" size={17} className="mt-1 shrink-0 text-accent-text" />
        <span>
          Confirme ton adresse <strong>{email}</strong> pour {action} : clique sur le lien reçu par email.
        </span>
      </p>
      <p className="mt-2 pl-[27px] text-sm">
        {message ? (
          <span role="status">{message}</span>
        ) : (
          <button
            type="button"
            className="inline-flex min-h-8 items-center font-medium underline underline-offset-4"
            onClick={resend}
          >
            Renvoyer l&apos;email
          </button>
        )}
      </p>
    </div>
  );
}
