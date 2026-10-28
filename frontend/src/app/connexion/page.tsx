import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { LoginForm } from "@/components/AuthForms";
import { fetchMe } from "@/lib/api";

export const metadata: Metadata = { title: "Connexion" };

/** Seules les adresses internes sont acceptées comme destination après connexion. */
function safeNext(next: string | undefined) {
  return next && next.startsWith("/") && !next.startsWith("//") ? next : "/";
}

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ suivant?: string }>;
}) {
  const next = safeNext((await searchParams).suivant);
  if (await fetchMe().catch(() => null)) redirect(next);
  return (
    <div className="mx-auto max-w-sm">
      <h1>Connexion</h1>
      <div className="mt-6">
        <LoginForm next={next} />
      </div>
    </div>
  );
}
