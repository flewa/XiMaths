"use client";

import { useEffect, useState } from "react";

import { Icon } from "./Icon";

const pill =
  "inline-flex min-h-8 items-center gap-1.5 rounded-full bg-surface-card px-3 py-1 text-sm text-body hover:bg-hover hover:text-ink";

/** Adresses de partage des réseaux : de simples liens, sans script ni traceur. */
function targets(url: string, text: string, image: string) {
  const u = encodeURIComponent(url);
  const t = encodeURIComponent(text);
  return [
    { name: "WhatsApp", href: `https://wa.me/?text=${encodeURIComponent(`${text} ${url}`)}` },
    { name: "Facebook", href: `https://www.facebook.com/sharer/sharer.php?u=${u}` },
    { name: "X", href: `https://x.com/intent/post?text=${t}&url=${u}` },
    {
      name: "Pinterest",
      href: `https://pinterest.com/pin/create/button/?url=${u}&media=${encodeURIComponent(image)}&description=${t}`,
    },
    { name: "Email", href: `mailto:?subject=${t}&body=${encodeURIComponent(`${text}\n${url}`)}` },
  ];
}

/** Partager un exercice hors de XiMaths. Sur téléphone, le premier bouton ouvre le menu de
 * partage de l'appareil (toutes les applications installées) ; les liens marchent partout. */
export function ExerciseShare({ url, title, image }: { url: string; title: string; image: string }) {
  const text = `${title} — un exercice de maths sur XiMaths`;
  const [native, setNative] = useState(false);
  const [copied, setCopied] = useState(false);

  // Connu seulement dans le navigateur : le serveur rend la version sans ce bouton.
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setNative(typeof navigator.share === "function" && window.matchMedia("(pointer: coarse)").matches);
  }, []);

  async function copy() {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2500);
    } catch {
      // Presse-papiers refusé : l'adresse reste dans la barre du navigateur.
    }
  }

  return (
    <div className="mt-8 flex flex-wrap items-center gap-2">
      <span className="mr-1 inline-flex items-center gap-1.5 text-sm text-mute">
        <Icon name="share" size={16} />
        Partager
      </span>
      {native && (
        <button
          type="button"
          onClick={() => navigator.share({ title, text, url }).catch(() => {})}
          data-umami-event="partage-exercice"
          data-umami-event-via="appareil"
          className={pill}
        >
          Mes applications…
        </button>
      )}
      {/* Sur téléphone, la feuille de partage du système contient déjà toutes les applications. */}
      {!native && targets(url, text, image).map((target) => (
        <a
          key={target.name}
          href={target.href}
          target="_blank"
          rel="noopener noreferrer"
          data-umami-event="partage-exercice"
          data-umami-event-via={target.name.toLowerCase()}
          className={pill}
        >
          {target.name}
        </a>
      ))}
      <button
        type="button"
        onClick={copy}
        data-umami-event="partage-exercice"
        data-umami-event-via="lien"
        className={pill}
      >
        {copied ? "Lien copié" : "Copier le lien"}
      </button>
      <span className="sr-only" aria-live="polite">
        {copied ? "Lien de l'exercice copié." : ""}
      </span>
    </div>
  );
}

const READ_KEY = "ximaths.lus";

/** Signale au serveur que l'énoncé a été ouvert, pour les statistiques de l'exercice. Un membre
 * est compté une fois par le serveur ; un visiteur, une fois par navigateur, grâce à une liste
 * gardée ici même, sans cookie ni identifiant. */
export function ReadBeacon({ exerciseId, member }: { exerciseId: number; member: boolean }) {
  useEffect(() => {
    if (!member) {
      // Noté avant l'envoi : deux affichages rapprochés ne comptent pas deux lectures.
      try {
        const stored = JSON.parse(window.localStorage.getItem(READ_KEY) ?? "[]");
        const seen: number[] = Array.isArray(stored) ? stored : [];
        if (seen.includes(exerciseId)) return;
        window.localStorage.setItem(READ_KEY, JSON.stringify([...seen, exerciseId].slice(-500)));
      } catch {
        // Stockage indisponible (navigation privée) : la lecture sera recomptée, tant pis.
      }
    }
    fetch(`/api/exercises/${exerciseId}/read`, { method: "POST", credentials: "same-origin", keepalive: true }).catch(
      () => {},
    );
  }, [exerciseId, member]);
  return null;
}
