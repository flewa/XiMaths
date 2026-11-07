"use client";

import Image from "next/image";
import QRCode from "qrcode";
import { useEffect, useEffectEvent, useRef, useState, useSyncExternalStore } from "react";

import { type ApiResult, apiPost } from "@/lib/client-api";
import {
  type PhotoUploadState,
  hourFormat,
  photoCount,
  readUpload,
  removePhoto,
  sendPhoto,
} from "@/lib/photo-upload";

import { FormMessage, secondaryButtonClass } from "./Form";
import { Icon } from "./Icon";

export type PickedPhotos = { token: string | null; count: number };

/** D'où vient l'envoi : une solution libre sur un exercice, ou une session chronométrée. */
export type PhotoSource = { exerciseId: number } | { sessionId: number };

// Écran tactile (téléphone, tablette) : on y prend les photos directement, sans QR code.
const coarse = "(pointer: coarse)";
function subscribe(onChange: () => void) {
  const query = window.matchMedia(coarse);
  query.addEventListener("change", onChange);
  return () => query.removeEventListener("change", onChange);
}

const POLL_MS = 2500;

function qrCode(token: string) {
  return QRCode.toDataURL(`${window.location.origin}/photos/${token}`, {
    width: 352,
    margin: 1,
    errorCorrectionLevel: "M",
  });
}

/** Photos de la copie manuscrite, 3 au plus : prises depuis le téléphone en scannant un
 * QR code, ou ajoutées depuis cet appareil. Le parent reçoit le jeton de l'envoi et le
 * nombre de photos. En temps limité, le QR code s'affiche d'office et le dépôt ferme avec
 * le temps imparti. */
export function CopyPhotoPicker({
  source,
  onChange,
}: {
  source: PhotoSource;
  onChange?: (picked: PickedPhotos) => void;
}) {
  const timed = "sessionId" in source;
  const touch = useSyncExternalStore(subscribe, () => window.matchMedia(coarse).matches, () => false);
  const input = useRef<HTMLInputElement>(null);
  const [upload, setUpload] = useState<PhotoUploadState | null>(null);
  const [qr, setQr] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function update(next: PhotoUploadState) {
    setUpload(next);
    onChange?.({ token: next.token, count: next.photos.length });
  }

  const openPath = timed ? `/training/sessions/${source.sessionId}/photo-upload` : `/exercises/${source.exerciseId}/photo-uploads`;

  async function ensureUpload() {
    if (upload) return upload;
    const opened = await apiPost<PhotoUploadState>(openPath);
    if (!opened.ok) {
      setError(opened.error);
      return null;
    }
    update(opened.data);
    return opened.data;
  }

  async function reopen(current: PhotoUploadState) {
    // Le temps d'une session ne se prolonge pas.
    if (current.timed) return current;
    const reopened = await apiPost<PhotoUploadState>(`/photo-uploads/${encodeURIComponent(current.token)}/reopen`);
    if (!reopened.ok) {
      setError(reopened.error);
      return null;
    }
    update(reopened.data);
    return reopened.data;
  }

  async function showPhone() {
    setError(null);
    let current = await ensureUpload();
    if (current && !current.open) current = await reopen(current);
    if (!current) return;
    setQr(await qrCode(current.token));
  }

  // En temps limité, l'envoi et son QR code sont prêts dès l'arrivée sur la page.
  const prepared = useEffectEvent(async (opened: ApiResult<PhotoUploadState>) => {
    if (!opened.ok) return setError(opened.error);
    update(opened.data);
    if (!window.matchMedia(coarse).matches) setQr(await qrCode(opened.data.token));
  });
  useEffect(() => {
    if (!timed) return;
    let live = true;
    void apiPost<PhotoUploadState>(openPath).then((opened) => {
      if (live) void prepared(opened);
    });
    return () => {
      live = false;
    };
  }, [timed, openPath]);

  async function onFiles(event: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    event.target.value = ""; // pour pouvoir reprendre la même photo
    if (files.length === 0) return;
    setError(null);
    let current = await ensureUpload();
    if (!current) return;
    if (!current.open) current = await reopen(current);
    if (!current) return;
    const room = current.max_photos - current.photos.length;
    if (files.length > room) setError(`3 photos au plus : seules les ${room} premières sont ajoutées.`);
    for (const [index, file] of files.slice(0, room).entries()) {
      setBusy(`Envoi de la photo ${index + 1} sur ${Math.min(files.length, room)}…`);
      const sent = await sendPhoto(current.token, file);
      if (!sent.ok) {
        setError(sent.error);
        break;
      }
    }
    setBusy(null);
    const next = await readUpload(current.token);
    if (next) update(next);
  }

  async function remove(photoId: number) {
    if (!upload) return;
    const removed = await removePhoto(upload.token, photoId);
    if (!removed.ok) setError(removed.error);
    const next = await readUpload(upload.token);
    if (next) update(next);
  }

  // L'ordinateur relit l'envoi pour montrer les photos prises au téléphone : tant que le QR
  // code est affiché, et pendant toute une session chronométrée. Pas d'appel onglet caché.
  const poll = useEffectEvent(async () => {
    if (!upload || document.hidden) return;
    const next = await readUpload(upload.token);
    if (next) update(next);
  });
  const waiting = upload !== null && upload.open && (timed || (qr !== null && upload.photos.length < upload.max_photos));
  useEffect(() => {
    if (!waiting) return;
    const timer = window.setInterval(() => poll(), POLL_MS);
    return () => window.clearInterval(timer);
  }, [waiting]);

  const count = upload?.photos.length ?? 0;
  const full = upload !== null && count >= upload.max_photos;
  const closed = upload !== null && upload.timed && !upload.open;

  return (
    <div className="space-y-3">
      {!closed && (
        <div className="flex flex-wrap gap-2">
          {!touch && !timed && (
            <button type="button" onClick={showPhone} disabled={full} className={secondaryButtonClass}>
              <Icon name="phone" size={16} />
              Depuis mon téléphone
            </button>
          )}
          <button
            type="button"
            onClick={() => input.current?.click()}
            disabled={full || busy !== null}
            className={secondaryButtonClass}
          >
            <Icon name="camera" size={16} />
            {touch ? "Prendre ou choisir des photos" : "Ajouter des fichiers"}
          </button>
          <input ref={input} type="file" accept="image/*" multiple hidden onChange={onFiles} />
        </div>
      )}
      <p className="text-sm text-mute">
        Une page par photo, à plat et bien éclairée, 3 au plus. N&apos;y laisse pas ton nom : les relecteurs voient
        tes photos, puis tout le monde si ta solution est validée.
        {timed && " Les photos doivent arriver avant la fin du temps : garde une minute pour les prendre."}
      </p>

      {closed && (
        <p role="status" className="font-medium text-ink">
          Temps écoulé : le dépôt de photos est fermé.
        </p>
      )}

      {qr && upload && !full && !closed && (
        <div className="flex flex-wrap items-center gap-5 rounded-xl border border-hairline p-4">
          <Image
            unoptimized
            src={qr}
            width={176}
            height={176}
            alt="QR code de la page d'envoi des photos"
            className="rounded-lg bg-white p-2"
          />
          <div className="min-w-0 flex-1 basis-56 space-y-2 text-sm">
            <p className="font-medium text-ink">Scanne ce code avec l&apos;appareil photo de ton téléphone.</p>
            <p className="text-body">
              Photographie tes pages : elles apparaissent ici au fur et à mesure. Pas besoin de te connecter sur le
              téléphone.
            </p>
            <p aria-live="polite" className="text-mute">
              {photoCount(count)} sur {upload.max_photos} ·{" "}
              {upload.open
                ? `${timed ? "photos acceptées" : "code valable"} jusqu'à ${hourFormat.format(new Date(upload.expires_at))}`
                : "code expiré"}
            </p>
            <p className="flex flex-wrap gap-x-4 gap-y-1">
              {!upload.open && !timed && (
                <button type="button" onClick={() => reopen(upload)} className="underline underline-offset-4">
                  Prolonger de 30 minutes
                </button>
              )}
              {!timed && (
                <button
                  type="button"
                  onClick={() => setQr(null)}
                  className="text-mute underline underline-offset-4 hover:text-ink"
                >
                  Masquer le QR code
                </button>
              )}
            </p>
          </div>
        </div>
      )}

      {busy && (
        <p aria-live="polite" className="text-sm text-mute">
          {busy}
        </p>
      )}
      {upload && count > 0 && (
        <ol aria-label="Photos de ta copie" className="flex flex-wrap gap-3">
          {upload.photos.map((photo, index) => (
            <li key={photo.id} className="space-y-1">
              <a
                href={photo.url}
                target="_blank"
                rel="noopener"
                className="block w-fit overflow-hidden rounded-lg border border-hairline bg-white"
              >
                <Image
                  unoptimized
                  src={photo.url}
                  width={photo.width}
                  height={photo.height}
                  alt={`Page ${index + 1} de ta copie`}
                  className="h-32 w-auto"
                />
              </a>
              {!closed && (
                <button
                  type="button"
                  onClick={() => remove(photo.id)}
                  className="inline-flex items-center gap-1 text-sm text-mute hover:text-ink"
                >
                  <Icon name="close" size={14} />
                  Retirer la page {index + 1}
                </button>
              )}
            </li>
          ))}
        </ol>
      )}
      <FormMessage error={error} />
    </div>
  );
}
