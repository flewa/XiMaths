import type { Metadata } from "next";

import { ResetPasswordForm } from "@/components/AuthForms";
import { FormMessage } from "@/components/Form";

export const metadata: Metadata = { title: "Nouveau mot de passe", robots: { index: false } };

export default async function NewPasswordPage({
  searchParams,
}: {
  searchParams: Promise<{ uid?: string; token?: string }>;
}) {
  const { uid, token } = await searchParams;
  return (
    <div className="mx-auto max-w-sm">
      <h1>Nouveau mot de passe</h1>
      <div className="mt-6">
        {uid && token ? (
          <ResetPasswordForm uid={uid} token={token} />
        ) : (
          <FormMessage error="Ce lien est incomplet. Ouvre le lien complet reçu par email." />
        )}
      </div>
    </div>
  );
}
