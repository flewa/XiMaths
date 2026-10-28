import Link from "next/link";

import { fetchMe, type Me } from "@/lib/api";

import { LogoutButton, MobileMenu, VerifyBanner } from "./AccountControls";
import { primaryButtonClass } from "./Form";

function NavLinks({ me }: { me: Me | null }) {
  const link = "hover:underline underline-offset-4";
  return (
    <>
      <Link href="/exercices" className={link}>
        Parcourir
      </Link>
      <Link href="/classements" className={link}>
        Classements
      </Link>
      {me ? (
        <>
          <Link href="/relectures" className={link}>
            Relectures{me.pending_reviews > 0 && <span className="text-mute"> [{me.pending_reviews}]</span>}
          </Link>
          <Link href={`/membres/${encodeURIComponent(me.username)}`} className={`text-mute ${link}`}>
            {me.username} · {me.points} pts
          </Link>
          <LogoutButton />
        </>
      ) : (
        <Link href="/connexion" className={link}>
          Se connecter
        </Link>
      )}
    </>
  );
}

export async function SiteHeader() {
  const me = await fetchMe().catch(() => null);
  return (
    <header className="border-b border-hairline">
      <div className="mx-auto flex h-14 max-w-[960px] items-center justify-between gap-4 px-4">
        <Link href="/" className="shrink-0 font-bold">
          [ξ] XiMaths
        </Link>
        <nav aria-label="Navigation" className="hidden items-center gap-6 font-medium md:flex">
          <NavLinks me={me} />
        </nav>
        <div className="flex items-center gap-4">
          <Link
            href={me ? "/exercices/nouveau" : "/inscription"}
            className={`${primaryButtonClass} whitespace-nowrap`}
          >
            {me ? "Publier" : "Créer un compte"}
          </Link>
          <MobileMenu>
            <NavLinks me={me} />
          </MobileMenu>
        </div>
      </div>
      {me && !me.email_verified && <VerifyBanner email={me.email} />}
    </header>
  );
}
