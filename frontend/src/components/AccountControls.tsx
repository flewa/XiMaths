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
      <p className="mx-auto flex max-w-[860px] gap-2.5 px-5 py-2.5 text-sm leading-relaxed sm:px-10">
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
