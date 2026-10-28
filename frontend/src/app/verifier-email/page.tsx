import type { Metadata } from "next";

import { VerifyEmail } from "@/components/AuthForms";
import { FormMessage } from "@/components/Form";

export const metadata: Metadata = { title: "Confirmation de l'adresse email" };

export default async function VerifyEmailPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token } = await searchParams;
  return (
    <div className="mx-auto max-w-sm">
      <h1>Confirmation de l&apos;adresse</h1>
      <div className="mt-6">
        {token ? (
          <VerifyEmail token={token} />
        ) : (
          <FormMessage error="Ce lien est incomplet. Ouvre le lien complet reçu par email." />
        )}
      </div>
    </div>
  );
}
