import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { GoogleButton, LoginForm } from "@/components/AuthForms";
import { FormMessage } from "@/components/Form";
import { fetchMe, fetchProviders, nullOnError } from "@/lib/api";
import { safeNext } from "@/lib/safe-next";

export const metadata: Metadata = { title: "Connexion", robots: { index: false } };

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ suivant?: string; erreur?: string }>;
}) {
  const { suivant, erreur } = await searchParams;
  const next = safeNext(suivant);
  if (await fetchMe().catch(nullOnError)) redirect(next);
  const providers = await fetchProviders().catch(() => ({ google: false }));
  return (
    <div className="mx-auto max-w-sm">
      <h1>Connexion</h1>
      {erreur === "google" && (
        <div className="mt-4">
          <FormMessage error="La connexion avec Google n'a pas abouti. Réessaie, ou connecte-toi avec ton mot de passe." />
        </div>
      )}
      {providers.google && (
        <div className="mt-6 border-b border-hairline pb-6">
          <GoogleButton next={next} />
        </div>
      )}
      <div className="mt-6">
        <LoginForm next={next} />
      </div>
    </div>
  );
}
