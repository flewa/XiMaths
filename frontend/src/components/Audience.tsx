"use client";

import Script from "next/script";
import { useSyncExternalStore } from "react";

import { type AudiencePayload, OPT_OUT_KEY, beforeSend } from "@/lib/audience";

declare global {
  interface Window {
    ximathsAudience?: (type: string, payload: AudiencePayload) => AudiencePayload;
  }
}

// Posé dès le chargement de ce module, donc avant que le script de mesure n'envoie quoi que
// ce soit : Umami l'appelle avant chaque envoi, par son nom (data-before-send).
if (typeof window !== "undefined") window.ximathsAudience = beforeSend;

/** Mesure d'audience : Umami, sur le serveur de XiMaths, sans cookie. Le script et les
 * visites passent par /mesure/ sur le site même (voir Caddyfile). */
export function AudienceTracker({ websiteId, domain }: { websiteId: string; domain: string }) {
  return (
    <Script
      src="/mesure/script.js"
      data-website-id={websiteId}
      data-domains={domain}
      data-before-send="ximathsAudience"
      data-do-not-track="true"
    />
  );
}

// Le choix de l'appareil, relu à chaque changement, ici ou dans un autre onglet.
const listeners = new Set<() => void>();
function subscribe(listener: () => void) {
  listeners.add(listener);
  window.addEventListener("storage", listener);
  return () => {
    listeners.delete(listener);
    window.removeEventListener("storage", listener);
  };
}
function optedOut() {
  try {
    return window.localStorage.getItem(OPT_OUT_KEY) !== null;
  } catch {
    return false;
  }
}

/** Ne plus compter les visites de cet appareil, ou de nouveau. */
export function AudienceOptOut() {
  const off = useSyncExternalStore(subscribe, optedOut, () => null);
  if (off === null) return null;

  function toggle() {
    try {
      if (off) window.localStorage.removeItem(OPT_OUT_KEY);
      else window.localStorage.setItem(OPT_OUT_KEY, "1");
    } catch {
      // Stockage bloqué (navigation privée stricte) : rien à retenir.
    }
    listeners.forEach((listener) => listener());
  }

  return (
    <p className="flex flex-wrap items-center gap-x-3 gap-y-1">
      <span role="status">
        {off ? "Tes visites ne sont pas comptées sur cet appareil." : "Tes visites sont comptées sur cet appareil."}
      </span>
      <button type="button" onClick={toggle} className="underline underline-offset-4">
        {off ? "Les compter de nouveau" : "Ne plus les compter"}
      </button>
    </p>
  );
}
