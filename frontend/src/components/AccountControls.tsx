"use client";

import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

import { apiPost } from "@/lib/client-api";

export function LogoutButton() {
  const router = useRouter();
  return (
    <button
      type="button"
      className="text-mute hover:text-ink"
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

/** Menu repliable sous 768 px. Il se referme à chaque changement de page. */
export function MobileMenu({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <details key={pathname} className="plain relative md:hidden">
      <summary className="font-medium">[≡] Menu</summary>
      <div className="absolute right-0 top-full z-10 mt-3 flex w-56 flex-col border border-hairline bg-canvas py-2 [&>*]:px-4 [&>*]:py-2 [&>*]:text-left">
        {children}
      </div>
    </details>
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
    <div className="border-t border-hairline bg-surface-card">
      <p className="mx-auto max-w-[960px] px-4 py-2 text-sm leading-relaxed">
        [!] Confirme ton adresse <strong>{email}</strong> pour publier, résoudre et voter : le lien
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
      </p>
    </div>
  );
}
