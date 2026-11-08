"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import type { BadgeInfo, Me, ProfileOptions, Topic } from "@/lib/api";
import { apiPut } from "@/lib/client-api";
import { AVATAR_COLOR_NAMES, AVATAR_TINTS } from "@/lib/profile-art";

import { Avatar } from "./Avatar";
import { BadgeMedal } from "./BadgeMedal";
import { Field, FormMessage, SubmitButton, inputClass } from "./Form";

const BIO_MAX = 200;
const FEATURED_MAX = 3;
const TOPICS_MAX = 3;

const legend = "mb-2 font-medium";
const choice =
  "cursor-pointer rounded-lg ring-offset-2 ring-offset-canvas has-[:checked]:ring-2 has-[:checked]:ring-ink has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-accent";

/** Le profil public : avatar, présentation, vitrine de badges, chapitres favoris. */
export function ProfileForm({
  me,
  options,
  badges,
  topics,
}: {
  me: Me;
  options: ProfileOptions;
  badges: BadgeInfo[];
  topics: Topic[];
}) {
  const router = useRouter();
  const [color, setColor] = useState(me.avatar.color);
  const [symbol, setSymbol] = useState(me.avatar.custom_symbol ? me.avatar.symbol : "");
  const [bio, setBio] = useState(me.bio);
  const [featured, setFeatured] = useState<string[]>(me.featured_badges);
  const [favorites, setFavorites] = useState<string[]>(me.favorite_topics);
  const [result, setResult] = useState<{ error?: string; success?: string }>({});
  const [pending, setPending] = useState(false);

  const owned = badges.filter((badge) => badge.awarded_at);
  const chapters = topics.filter((topic) => topic.parent === null);
  const initial = me.username.slice(0, 1).toUpperCase();
  const preview = { color, symbol: symbol || initial, custom_symbol: Boolean(symbol) };

  function toggle(list: string[], value: string, max: number) {
    if (list.includes(value)) return list.filter((item) => item !== value);
    return list.length < max ? [...list, value] : list;
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    const saved = await apiPut("/auth/profile", {
      bio,
      avatar_color: color,
      avatar_symbol: symbol,
      featured_badges: featured,
      favorite_topics: favorites,
    });
    setPending(false);
    setResult(saved.ok ? { success: "Profil enregistré." } : { error: saved.error });
    if (saved.ok) router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="space-y-7">
      <div className="flex flex-wrap items-center gap-5">
        <Avatar avatar={preview} size={72} label="Aperçu de ton avatar" />
        <p className="text-sm text-mute">
          Ton avatar apparaît sur ton profil, dans les classements et à côté de ton pseudo.
        </p>
      </div>

      <fieldset>
        <legend className={legend}>Couleur</legend>
        <div className="flex flex-wrap gap-2">
          {options.colors.map((name) => (
            <label key={name} className={choice} title={AVATAR_COLOR_NAMES[name] ?? name}>
              <input
                type="radio"
                name="avatar_color"
                value={name}
                checked={color === name}
                onChange={() => setColor(name)}
                className="sr-only"
              />
              <span className="block size-9 rounded-lg" style={{ background: AVATAR_TINTS[name] }} />
              <span className="sr-only">{AVATAR_COLOR_NAMES[name] ?? name}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend className={legend}>Symbole</legend>
        <div className="flex flex-wrap gap-2">
          {["", ...options.symbols].map((value) => (
            <label key={value || "initiale"} className={choice}>
              <input
                type="radio"
                name="avatar_symbol"
                value={value}
                checked={symbol === value}
                onChange={() => setSymbol(value)}
                className="sr-only"
              />
              <span className="grid size-9 place-items-center rounded-lg bg-surface-card font-serif text-lg text-ink">
                {value || initial}
              </span>
              {!value && <span className="sr-only">Ton initiale</span>}
            </label>
          ))}
        </div>
      </fieldset>

      <Field
        label="Présentation"
        htmlFor="bio"
        hint={`${bio.length} / ${BIO_MAX} caractères. Ta filière, ce que tu aimes en maths… Pas de lien, ni de nom complet.`}
      >
        <textarea
          id="bio"
          rows={3}
          maxLength={BIO_MAX}
          value={bio}
          onChange={(event) => setBio(event.target.value)}
          className={inputClass}
        />
      </Field>

      <fieldset>
        <legend className={legend}>
          Vitrine <span className="font-normal text-mute">· {featured.length} sur {FEATURED_MAX}</span>
        </legend>
        {owned.length === 0 ? (
          <p className="text-sm text-mute">Tes badges apparaîtront ici dès que tu en auras obtenu un.</p>
        ) : (
          <div className="flex flex-wrap gap-3">
            {owned.map((badge) => {
              const on = featured.includes(badge.slug);
              const full = !on && featured.length >= FEATURED_MAX;
              return (
                <button
                  key={badge.slug}
                  type="button"
                  aria-pressed={on}
                  disabled={full}
                  onClick={() => setFeatured(toggle(featured, badge.slug, FEATURED_MAX))}
                  className={`flex w-24 flex-col items-center gap-1.5 rounded-xl border p-2 text-xs ${
                    on ? "border-ink bg-surface-card text-ink" : "border-hairline text-mute hover:text-ink"
                  } disabled:opacity-40`}
                >
                  <BadgeMedal slug={badge.slug} size={44} />
                  {badge.name}
                </button>
              );
            })}
          </div>
        )}
      </fieldset>

      <fieldset>
        <legend className={legend}>
          Chapitres favoris <span className="font-normal text-mute">· {favorites.length} sur {TOPICS_MAX}</span>
        </legend>
        <div className="space-y-3">
          {chapters.map((chapter) => (
            <div key={chapter.slug} className="flex flex-wrap items-center gap-1.5 text-sm">
              {[chapter, ...topics.filter((topic) => topic.parent === chapter.slug)].map((topic) => {
                const on = favorites.includes(topic.slug);
                return (
                  <button
                    key={topic.slug}
                    type="button"
                    aria-pressed={on}
                    disabled={!on && favorites.length >= TOPICS_MAX}
                    onClick={() => setFavorites(toggle(favorites, topic.slug, TOPICS_MAX))}
                    className={`rounded-full px-3 py-1 ${
                      on ? "bg-ink text-canvas" : "bg-surface-card text-body hover:text-ink"
                    } ${topic.parent === null ? "font-semibold" : ""} disabled:opacity-40`}
                  >
                    {topic.name}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </fieldset>

      <FormMessage error={result.error} success={result.success} />
      <SubmitButton pending={pending}>Enregistrer mon profil</SubmitButton>
    </form>
  );
}
