import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { GoogleButton, SignupForm } from "@/components/AuthForms";
import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { fetchLevels, fetchMe, fetchProviders } from "@/lib/api";

export const metadata: Metadata = { title: "Créer un compte" };

export default async function SignupPage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchLevels(), fetchProviders()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, levels, providers] = data;
  if (me) redirect("/");
  return (
    <div className="mx-auto max-w-sm">
      <h1>Créer un compte</h1>
      <p className="mt-2 text-body">
        Pour publier des exercices, proposer des solutions et relire celles des autres.
      </p>
      {providers.google && (
        <div className="mt-6 border-b border-hairline pb-6">
          <GoogleButton next="/" />
        </div>
      )}
      <div className="mt-6">
        <SignupForm levels={levels} />
      </div>
      <p className="mt-6 text-sm text-mute">
        En créant un compte, tu acceptes les{" "}
        <Link href="/cgu" className="underline underline-offset-4">
          conditions d&apos;utilisation
        </Link>{" "}
        ; tes contributions sont publiées sous licence CC BY-SA 4.0.
      </p>
    </div>
  );
}
