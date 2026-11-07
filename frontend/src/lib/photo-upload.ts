/** Envoi de photos de copie : le jeton du QR code ouvre le dépôt depuis le téléphone,
 * l'ordinateur voit arriver les photos en relisant l'envoi (voir content/photos.py). */

import type { CopyPhoto } from "./api";
import { apiDelete, apiUpload } from "./client-api";
import { prepareImage } from "./image";

export type PhotoUploadState = {
  token: string;
  exercise_id: number;
  exercise_title: string;
  expires_at: string;
  /** Dépôt encore ouvert (30 minutes, prolongeables depuis l'ordinateur ; en temps
   * limité, jusqu'à la fin du temps imparti et une minute de grâce). */
  open: boolean;
  max_photos: number;
  /** Envoi d'une session chronométrée (entraînement ou défi). */
  timed: boolean;
  photos: CopyPhoto[];
};

const path = (token: string) => `/photo-uploads/${encodeURIComponent(token)}`;

/** État de l'envoi, ou null s'il n'existe pas (ou plus) ou si le réseau manque. */
export async function readUpload(token: string): Promise<PhotoUploadState | null> {
  try {
    const response = await fetch(`/api${path(token)}`, { cache: "no-store", credentials: "same-origin" });
    return response.ok ? ((await response.json()) as PhotoUploadState) : null;
  } catch {
    return null;
  }
}

/** Dépose une photo, réduite par le navigateur quand il sait la lire ; le serveur la
 * redresse et la réencode de toute façon, sans ses métadonnées. */
export async function sendPhoto(token: string, file: File) {
  const image = (await prepareImage(file)) ?? file;
  const form = new FormData();
  form.append("photo", image, "copie.jpg");
  return apiUpload<CopyPhoto>(`${path(token)}/photos`, form);
}

export function removePhoto(token: string, photoId: number) {
  return apiDelete(`${path(token)}/photos/${photoId}`);
}

export const hourFormat = new Intl.DateTimeFormat("fr-FR", { hour: "2-digit", minute: "2-digit" });

export function photoCount(count: number) {
  return `${count} photo${count > 1 ? "s" : ""}`;
}
