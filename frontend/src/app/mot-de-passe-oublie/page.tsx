import type { Metadata } from "next";

import { ForgotPasswordForm } from "@/components/AuthForms";

export const metadata: Metadata = { title: "Mot de passe oublié", robots: { index: false } };

export default function ForgotPasswordPage() {
  return (
    <div className="mx-auto max-w-sm">
      <h1>Mot de passe oublié</h1>
      <p className="mt-2 text-body">Indique ton adresse : tu recevras un lien pour en choisir un nouveau.</p>
      <div className="mt-6">
        <ForgotPasswordForm />
      </div>
    </div>
  );
}
