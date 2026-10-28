import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { SignupForm } from "@/components/AuthForms";
import { ApiUnavailable } from "@/components/ExerciseMeta";
import { fetchLevels, fetchMe } from "@/lib/api";

export const metadata: Metadata = { title: "Créer un compte" };

export default async function SignupPage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchLevels()]);
  } catch (error) {
    console.error(error);
    return <ApiUnavailable />;
  }
  const [me, levels] = data;
  if (me) redirect("/");
  return (
    <div className="mx-auto max-w-sm">
      <h1>Créer un compte</h1>
      <p className="mt-2 text-body">
        Pour publier des exercices, proposer des solutions et relire celles des autres.
      </p>
      <div className="mt-6">
        <SignupForm levels={levels} />
      </div>
    </div>
  );
}
