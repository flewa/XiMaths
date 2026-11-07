import type { Metadata } from "next";

import { PhoneUpload } from "@/components/PhoneUpload";

type Props = { params: Promise<{ token: string }> };

// Le jeton ouvre le dépôt de photos pendant 30 minutes : la page n'a rien à faire dans un moteur.
export const metadata: Metadata = {
  title: "Envoyer des photos de ta copie",
  robots: { index: false, follow: false },
};

export default async function PhotoUploadPage({ params }: Props) {
  const { token } = await params;
  return <PhoneUpload token={token} />;
}
