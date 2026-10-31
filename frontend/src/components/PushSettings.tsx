"use client";

import { useEffect, useState } from "react";

import { apiPost } from "@/lib/client-api";
import { base64UrlToBytes, isAppleMobile, sameBytes } from "@/lib/push";

import { FormMessage, primaryButtonClass, secondaryButtonClass } from "./Form";

type State = "loading" | "unsupported" | "install-first" | "denied" | "off" | "on";

async function currentSubscription() {
  const registration = await navigator.serviceWorker.getRegistration("/");
  return (await registration?.pushManager.getSubscription()) ?? null;
}

async function detect(): Promise<State> {
  if (!("serviceWorker" in navigator && "PushManager" in window && "Notification" in window)) {
    // Sur iPhone et iPad, le push n'existe que dans la PWA installée.
    return isAppleMobile(navigator.userAgent, navigator.platform, navigator.maxTouchPoints)
      ? "install-first"
      : "unsupported";
  }
  if (Notification.permission === "denied") return "denied";
  const subscription = await currentSubscription();
  if (!subscription) return "off";
  // Un navigateur partagé peut être abonné pour un autre compte.
  const status = await apiPost<{ active: boolean }>("/push/status", { endpoint: subscription.endpoint });
  return status.ok && status.data.active ? "on" : "off";
}

/** Notifications push sur ce navigateur. `publicKey` : la clé VAPID du serveur. */
export function PushSettings({ publicKey }: { publicKey: string }) {
  const [state, setState] = useState<State>("loading");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    detect().then(setState, () => setState("unsupported"));
  }, []);

  async function enable() {
    setPending(true);
    setError(null);
    try {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        setState(permission === "denied" ? "denied" : "off");
        return;
      }
      await navigator.serviceWorker.register("/sw.js", { scope: "/", updateViaCache: "none" });
      const registration = await navigator.serviceWorker.ready;
      const key = base64UrlToBytes(publicKey);
      let subscription = await registration.pushManager.getSubscription();
      // Abonnement d'avant un changement de clés VAPID : il ne servirait plus.
      if (subscription && !sameBytes(subscription.options.applicationServerKey, key)) {
        await subscription.unsubscribe();
        subscription = null;
      }
      subscription ??= await registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: key });
      const saved = await apiPost("/push/subscriptions", subscription.toJSON());
      if (!saved.ok) {
        await subscription.unsubscribe();
        setError(saved.error);
        return;
      }
      setState("on");
    } catch {
      setError("Le navigateur a refusé l'abonnement. Réessaie, ou essaie un autre navigateur.");
    } finally {
      setPending(false);
    }
  }

  async function disable() {
    setPending(true);
    setError(null);
    try {
      const subscription = await currentSubscription();
      if (subscription) {
        await apiPost("/push/unsubscribe", { endpoint: subscription.endpoint });
        await subscription.unsubscribe();
      }
      setState("off");
    } catch {
      setError("Impossible de désactiver les notifications. Réessaie.");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-body">
        Une notification par jour au plus, jamais entre 22 h et 8 h : relecture attribuée, solution validée ou
        à compléter, exercice résolu, question de compréhension, bilan de la semaine, et le défi du jour si tu
        l&apos;as demandé. Le reste attend dans tes notifications.
      </p>
      {state === "loading" && <p className="text-mute">…</p>}
      {state === "unsupported" && <p className="text-mute">Ce navigateur ne gère pas les notifications push.</p>}
      {state === "install-first" && (
        <p className="text-mute">
          Sur iPhone et iPad, ajoute d&apos;abord XiMaths à l&apos;écran d&apos;accueil (Partager, puis «&nbsp;Sur
          l&apos;écran d&apos;accueil&nbsp;»), ouvre-le depuis son icône, et reviens ici.
        </p>
      )}
      {state === "denied" && (
        <p className="text-mute">
          Les notifications de ce site sont bloquées dans ton navigateur : autorise-les dans ses réglages, puis
          recharge la page.
        </p>
      )}
      {state === "on" && (
        <>
          <p>[x] Activées sur cet appareil.</p>
          <button type="button" onClick={disable} disabled={pending} className={secondaryButtonClass}>
            {pending ? "Un instant…" : "Désactiver sur cet appareil"}
          </button>
        </>
      )}
      {state === "off" && (
        <button type="button" onClick={enable} disabled={pending} className={primaryButtonClass}>
          {pending ? "Un instant…" : "Activer sur cet appareil"}
        </button>
      )}
      <FormMessage error={error} />
    </div>
  );
}
