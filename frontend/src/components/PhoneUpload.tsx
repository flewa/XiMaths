"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";

import { type PhotoUploadState, hourFormat, photoCount, readUpload, removePhoto, sendPhoto } from "@/lib/photo-upload";

import { FormMessage, primaryButtonClass, secondaryButtonClass } from "./Form";
import { Icon } from "./Icon";
import { MathText } from "./MathText";

type Loaded = { state: PhotoUploadState | null; token: string };

/** Page ouverte en scannant le QR code : on y photographie sa copie, sans compte. Les
 * photos partent aussitôt vers l'ordinateur, où l'auteur envoie sa solution. */
export function PhoneUpload({ token }: { token: string }) {
  const camera = useRef<HTMLInputElement>(null);
  const gallery = useRef<HTMLInputElement>(null);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    readUpload(token).then((state) => {
      if (live) setLoaded({ state, token });
    });
    return () => {
      live = false;
    };
  }, [token]);

  if (loaded === null || loaded.token !== token) {
    return <p className="mt-8 text-mute">Chargement…</p>;
  }
  const upload = loaded.state;
  if (upload === null) {
    return (
      <div className="mt-8 space-y-2">
        <h1>Lien introuvable</h1>
        <p className="text-body">
          Ce QR code n&apos;existe pas ou date de plus d&apos;un jour. Affiche-en un nouveau sur ton ordinateur, depuis
          la fiche de l&apos;exercice.
        </p>
      </div>
    );
  }

  const count = upload.photos.length;
  const full = count >= upload.max_photos;

  async function refresh() {
    const next = await readUpload(token);
    if (next) setLoaded({ state: next, token });
  }

  async function onFiles(event: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (files.length === 0 || upload === null) return;
    setError(null);
    const room = upload.max_photos - count;
    if (files.length > room) setError(`3 photos au plus : seules les ${room} premières partent.`);
    for (const [index, file] of files.slice(0, room).entries()) {
      setBusy(`Envoi de la photo ${index + 1} sur ${Math.min(files.length, room)}…`);
      const sent = await sendPhoto(token, file);
      if (!sent.ok) {
        setError(sent.error);
        break;
      }
    }
    setBusy(null);
    await refresh();
  }

  async function remove(photoId: number) {
    const removed = await removePhoto(token, photoId);
    if (!removed.ok) setError(removed.error);
    await refresh();
  }

  return (
    <div className="mx-auto mt-6 max-w-md space-y-5">
      <header className="space-y-1">
        <p className="text-sm text-mute">Photos de ta copie</p>
        <h1 className="text-2xl">
          <MathText>{upload.exercise_title}</MathText>
        </h1>
      </header>

      {!upload.open ? (
        <p className="text-body">
          {upload.timed
            ? "Le temps est écoulé : les photos ne sont plus acceptées. Les pages déjà envoyées sont rendues avec ta copie."
            : "Ce QR code a expiré. Sur ton ordinateur, clique sur « Prolonger de 30 minutes », puis recharge cette page."}
        </p>
      ) : full ? (
        <p className="flex gap-2 text-body">
          <Icon name="check" className="mt-0.5 text-accent" />
          <span>
            C&apos;est complet : tes {upload.max_photos} photos sont sur ton ordinateur.{" "}
            {upload.timed ? "Rends ta copie là-bas." : "Termine l'envoi de ta solution là-bas."}
          </span>
        </p>
      ) : (
        <>
          <p className="text-body">
            Une page par photo, à plat et bien éclairée, {upload.max_photos} au plus. N&apos;y laisse pas ton nom.
          </p>
          <div className="grid gap-2">
            <button
              type="button"
              onClick={() => camera.current?.click()}
              disabled={busy !== null}
              className={`${primaryButtonClass} min-h-12`}
            >
              <Icon name="camera" />
              Prendre une photo
            </button>
            <button
              type="button"
              onClick={() => gallery.current?.click()}
              disabled={busy !== null}
              className={`${secondaryButtonClass} min-h-12`}
            >
              Choisir dans la galerie
            </button>
          </div>
          <input ref={camera} type="file" accept="image/*" capture="environment" hidden onChange={onFiles} />
          <input ref={gallery} type="file" accept="image/*" multiple hidden onChange={onFiles} />
        </>
      )}

      {busy && (
        <p aria-live="polite" className="text-sm text-mute">
          {busy}
        </p>
      )}
      <FormMessage error={error} />

      {count > 0 && (
        <section aria-labelledby="recues" className="space-y-2">
          <h2 id="recues" className="text-base">
            {photoCount(count)} sur ton ordinateur
          </h2>
          <ol className="grid grid-cols-3 gap-2">
            {upload.photos.map((photo, index) => (
              <li key={photo.id} className="space-y-1">
                <Image
                  unoptimized
                  src={photo.url}
                  width={photo.width}
                  height={photo.height}
                  alt={`Page ${index + 1} de ta copie`}
                  className="h-auto w-full rounded-lg border border-hairline bg-white"
                />
                <button
                  type="button"
                  onClick={() => remove(photo.id)}
                  className="inline-flex min-h-9 items-center gap-1 text-sm text-mute hover:text-ink"
                >
                  <Icon name="close" size={14} />
                  Retirer
                </button>
              </li>
            ))}
          </ol>
        </section>
      )}

      {upload.open && (
        <p className="text-sm text-mute">
          {upload.timed
            ? `Temps limité : photos acceptées jusqu'à ${hourFormat.format(new Date(upload.expires_at))}, puis une minute de grâce.`
            : `Code valable jusqu'à ${hourFormat.format(new Date(upload.expires_at))}.`}{" "}
          Tu peux fermer cette page une fois tes photos envoyées.
        </p>
      )}
    </div>
  );
}
