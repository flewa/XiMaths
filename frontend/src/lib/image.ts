/** Taille d'une image ramenée dans un carré de `max` pixels, proportions gardées. */
export function fitWithin(width: number, height: number, max: number) {
  const scale = Math.min(1, max / Math.max(width, height));
  return { width: Math.round(width * scale), height: Math.round(height * scale) };
}

// Bord le plus long lu par Claude ; au-delà, l'image serait réduite de son côté.
const MAX_EDGE = 2576;

/** Photo réduite et recompressée en JPEG avant l'envoi : quelques centaines de Ko au
 * lieu de plusieurs Mo, l'orientation de l'appareil appliquée. null si le navigateur
 * ne sait pas lire le format (HEIC hors Safari, par exemple). */
export async function prepareImage(file: Blob): Promise<Blob | null> {
  let bitmap: ImageBitmap;
  try {
    bitmap = await createImageBitmap(file, { imageOrientation: "from-image" });
  } catch {
    return null;
  }
  const { width, height } = fitWithin(bitmap.width, bitmap.height, MAX_EDGE);
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  canvas.getContext("2d")?.drawImage(bitmap, 0, 0, width, height);
  bitmap.close();
  return new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.85));
}
