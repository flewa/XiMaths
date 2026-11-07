import Image from "next/image";

import type { CopyPhoto } from "@/lib/api";

/** Pages d'une copie manuscrite, dans l'ordre. Chaque page s'ouvre en grand dans un
 * nouvel onglet. `unoptimized` : le navigateur charge la photo lui-même, avec sa session,
 * et l'API vérifie qu'il a le droit de la voir. */
export function CopyPhotoList({ photos, compact = false }: { photos: CopyPhoto[]; compact?: boolean }) {
  if (photos.length === 0) return null;
  return (
    <ol
      aria-label={photos.length > 1 ? `Copie manuscrite, ${photos.length} pages` : "Copie manuscrite"}
      className={compact ? "my-3 flex flex-wrap gap-2" : "my-3 space-y-3"}
    >
      {photos.map((photo, index) => (
        <li key={photo.id}>
          <a
            href={photo.url}
            target="_blank"
            rel="noopener"
            className="block w-fit overflow-hidden rounded-lg border border-hairline bg-white hover:border-hairline-strong"
          >
            <Image
              unoptimized
              src={photo.url}
              width={photo.width}
              height={photo.height}
              alt={`Page ${index + 1} de la copie`}
              loading="lazy"
              className={compact ? "h-28 w-auto" : "h-auto w-full max-w-[640px]"}
            />
          </a>
        </li>
      ))}
    </ol>
  );
}
