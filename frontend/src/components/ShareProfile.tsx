"use client";

import { useState } from "react";

import { secondaryButtonClass } from "./Form";

/** Partager son profil (groupe de classe, messagerie) : le menu de partage du téléphone,
 * sinon l'adresse copiée. */
export function ShareProfile({ username }: { username: string }) {
  const [copied, setCopied] = useState(false);

  async function share() {
    const url = new URL(`/membres/${encodeURIComponent(username)}`, window.location.origin).toString();
    try {
      if (navigator.share && window.matchMedia("(pointer: coarse)").matches) {
        await navigator.share({ title: `${username} sur XiMaths`, url });
        return;
      }
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2500);
    } catch {
      // Partage annulé, ou presse-papiers refusé : rien à signaler.
    }
  }

  return (
    <>
      <button type="button" onClick={share} className={secondaryButtonClass}>
        {copied ? "Lien copié" : "Partager mon profil"}
      </button>
      <span className="sr-only" aria-live="polite">
        {copied ? "Lien de ton profil copié." : ""}
      </span>
    </>
  );
}
