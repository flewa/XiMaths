import Link from "next/link";

import { fetchMe, nullOnError, type Me } from "@/lib/api";

import { AccountMenu, LogoutButton, MobileMenu, VerifyBanner } from "./AccountControls";
import { BottomNav } from "./BottomNav";
import { primaryButtonClass } from "./Form";

const link = "whitespace-nowrap hover:underline underline-offset-4";

/** Pages du compte : menu déroulant sur ordinateur, liste dans le menu mobile. */
function AccountLinks({ me }: { me: Me }) {
  return (
    <>
      <span className="text-sm text-mute">{me.points} points</span>
      <Link href={`/membres/${encodeURIComponent(me.username)}`} className={link}>
        Mon profil
      </Link>
      <Link href="/progression" className={link}>
        Ma progression
      </Link>
      <Link href="/reglages" className={link}>
        Réglages
      </Link>
      <Link href="/signalements" className={link}>
        Mes signalements
      </Link>
      <Link href="/questions" className={link}>
        Mes questions
      </Link>
      <Link href="/decisions" className={link}>
        Mes décisions
      </Link>
      <LogoutButton />
    </>
  );
}

function NavLinks({ me }: { me: Me | null }) {
  return (
    <>
      <Link href="/exercices" className={link}>
        Parcourir
      </Link>
      <Link href="/defi" className={link}>
        Défi
      </Link>
      <Link href="/classements" className={link}>
        Classements
      </Link>
      {me ? (
        <>
          <Link href="/relectures" className={link}>
            Relectures{me.pending_reviews > 0 && <span className="text-mute"> [{me.pending_reviews}]</span>}
          </Link>
          <Link href="/notifications" className={link} aria-label={`Notifications, ${me.unread_notifications} non lues`}>
            [•]{me.unread_notifications > 0 && <span className="font-bold"> {me.unread_notifications}</span>}
          </Link>
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
  const me = await fetchMe().catch(nullOnError);
  return (
    <header className="border-b border-hairline">
      <div className="mx-auto flex h-14 max-w-[960px] items-center justify-between gap-4 px-4">
        <Link href="/" className="shrink-0 font-bold">
          [ξ] XiMaths
        </Link>
        <nav aria-label="Navigation" className="hidden items-center gap-5 font-medium lg:flex">
          <NavLinks me={me} />
          {me && (
            <AccountMenu label={me.username}>
              <AccountLinks me={me} />
            </AccountMenu>
          )}
        </nav>
        <div className="flex items-center gap-4">
          <div className="hidden lg:block">
            <Link href={me ? "/exercices/nouveau" : "/inscription"} className={`${primaryButtonClass} whitespace-nowrap`}>
              {me ? "Publier" : "Créer un compte"}
            </Link>
          </div>
          {/* Sur mobile, Publier passe dans la barre du bas ; restent les notifications et le menu. */}
          {me ? (
            <Link
              href="/notifications"
              aria-label={`Notifications, ${me.unread_notifications} non lues`}
              className="whitespace-nowrap py-2 font-medium lg:hidden"
            >
              [•]{me.unread_notifications > 0 && <span className="font-bold"> {me.unread_notifications}</span>}
            </Link>
          ) : (
            <div className="lg:hidden">
              <Link href="/inscription" className={`${primaryButtonClass} whitespace-nowrap`}>
                S&apos;inscrire
              </Link>
            </div>
          )}
          <MobileMenu>
            <NavLinks me={me} />
            {me && <AccountLinks me={me} />}
          </MobileMenu>
        </div>
      </div>
      {me && !me.email_verified && <VerifyBanner email={me.email} />}
      <BottomNav signedIn={me !== null} />
    </header>
  );
}
