import type { Metadata } from "next";
import Link from "next/link";

import { FormMessage } from "@/components/Form";

export const metadata: Metadata = { title: "Désabonnement", robots: { index: false } };

export default async function UnsubscribedPage({ searchParams }: { searchParams: Promise<{ ok?: string }> }) {
  const { ok } = await searchParams;
  return (
    <div className="mx-auto max-w-sm">
      <h1>Désabonnement</h1>
      <div className="mt-6 space-y-4">
        {ok ? (
          <FormMessage success="C'est fait : tu ne recevras plus d'emails de XiMaths, ni immédiats ni résumés." />
        ) : (
          <FormMessage error="Ce lien n'est pas valable. Tu peux régler tes emails dans les réglages." />
        )}
        <Link href="/reglages" className="block underline underline-offset-4">
          Régler mes emails
        </Link>
      </div>
    </div>
  );
}
