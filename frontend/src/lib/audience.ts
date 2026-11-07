// Mesure d'audience (Umami, sur le serveur de XiMaths) : ce que les pages lui envoient.

/** Ce qu'Umami s'apprête à envoyer (seuls les champs retouchés ici sont typés). */
export type AudiencePayload = { url?: string; referrer?: string } & Record<string, unknown>;

/** Clé de l'appareil qui coupe la mesure : le script d'Umami la lit avant chaque envoi. */
export const OPT_OUT_KEY = "umami.disabled";

const BASE = "https://adresse.invalid";

/** Une adresse sans ce qui peut porter un secret : les paramètres (jeton de vérification
 * d'email, de nouveau mot de passe…), sauf ceux de campagne (utm_…), et le jeton d'une page
 * d'envoi de photos. Adresse absolue ou chemin, rendue sous la même forme. */
export function cleanAddress(address: string | undefined): string | undefined {
  if (!address) return address;
  let url: URL;
  try {
    url = new URL(address, BASE);
  } catch {
    return address;
  }
  url.pathname = url.pathname.replace(/^\/photos\/[^/]+/, "/photos/");
  for (const key of [...url.searchParams.keys()]) {
    if (!key.startsWith("utm_")) url.searchParams.delete(key);
  }
  url.hash = "";
  return url.origin === BASE ? `${url.pathname}${url.search}` : url.toString();
}

/** Appelée par Umami avant chaque envoi (data-before-send). */
export function beforeSend(_type: string, payload: AudiencePayload): AudiencePayload {
  return { ...payload, url: cleanAddress(payload.url), referrer: cleanAddress(payload.referrer) };
}
