import type { Metadata } from "next";

import { VerifyEmail } from "@/components/AuthForms";
import { FormMessage } from "@/components/Form";

export const metadata: Metadata = { title: "Confirmation de l'adresse email" };

export default async function VerifyEmailPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string; academique?: string }>;
}) {
  const { token, academique } = await searchParams;
  return (
    <div className="mx-auto max-w-sm">
      <h1>Confirmation de l&apos;adresse{academique && " académique"}</h1>
      <div className="mt-6">
        {academique ? (
          <VerifyEmail token={academique} kind="academique" />
        ) : token ? (
          <VerifyEmail token={token} />
        ) : (
          <FormMessage error="Ce lien est incomplet. Ouvre le lien complet reçu par email." />
        )}
      </div>
    </div>
  );
}
