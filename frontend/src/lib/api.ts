// Client de l'API Django pour les composants serveur. Il transmet les cookies
// du visiteur, pour que Django reconnaisse sa session.
import { cookies } from "next/headers";

// 127.0.0.1 plutôt que localhost : Node résout localhost en ::1, où runserver n'écoute pas.
const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

export type Level = {
  code: string;
  name: string;
  track: string;
  year: number;
};

export type Topic = {
  name: string;
  slug: string;
};

export type ExerciseSummary = {
  id: number;
  title: string;
  difficulty: number;
  primary_level: string;
  levels: string[];
  topics: string[];
  validated_solutions: number;
  votes: number;
  published_at: string;
};

/** Exercice du fil d'accueil, avec la raison de sa présence. */
export type FeedItem = ExerciseSummary & {
  reason: "tendance" | "a_resoudre" | "exploration";
  reason_label: string;
};

export type ExerciseSort = "recent" | "popular" | "unsolved";

export type AiUsage = "aucune" | "relecture" | "aide_idee" | "generee";

export type Solution = {
  id: number;
  author: string | null;
  body: string;
  ai_usage: AiUsage;
  votes: number;
  validated_at: string | null;
};

export type ExerciseLink = { id: number; title: string };

export type ExerciseDetail = ExerciseSummary & {
  statement: string;
  hints: string[];
  author: string | null;
  source_type: string;
  source_reference: string;
  license: string;
  /** Exercice canonique, si celui-ci a été fusionné comme doublon. */
  merged_into: number | null;
  variants: ExerciseLink[];
  solutions: Solution[];
};

export type SimilarityBand = "quasi_copie" | "tres_similaire" | "variante" | "peut_etre_lie";

/** Exercice publié proche d'un énoncé en cours de rédaction. */
export type SimilarExercise = {
  id: number;
  title: string;
  statement: string;
  primary_level: string;
  validated_solutions: number;
  band: SimilarityBand;
  band_label: string;
  score: number | null;
};

export type Me = {
  id: number;
  username: string;
  email: string;
  email_verified: boolean;
  declared_level: string | null;
  trust_level: number;
  points: number;
  pending_reviews: number;
  leaderboard_visible: boolean;
  tiers_temps: boolean;
};

export type TrainingOptions = {
  durations: number[];
  recommended: number;
  /** 1,33 si le visiteur a déclaré un tiers-temps. */
  extra_time_factor: number | null;
};

export type TrainingStatus = "en_cours" | "en_pause" | "rendue" | "abandonnee";

/** Session d'entraînement chronométré ; le temps est celui du serveur. */
export type TrainingSession = {
  id: number;
  exercise_id: number;
  exercise_title: string;
  statement: string;
  hints: string[];
  has_final_answer: boolean;
  status: TrainingStatus;
  duration_s: number;
  extra_time_factor: number;
  limit_s: number;
  elapsed_s: number;
  remaining_s: number;
  pauses_left: number;
  focus_losses: number;
  external_paste_chars: number;
  draft: string;
  final_answer: string;
  answer_correct: boolean | null;
  solution_id: number | null;
  solution_status: SolutionStatus | null;
  median_elapsed_s: number | null;
  self_rating: number | null;
  started_at: string;
  submitted_at: string | null;
};

export type LeaderboardEntry = {
  rank: number;
  username: string;
  declared_level: string | null;
  points: number;
  is_me: boolean;
};

export type Leaderboard = {
  /** "global", un code de niveau, ou "pantheon". */
  board: string;
  board_label: string;
  /** Semaine ISO, « 2026-W44 » ; null pour le Panthéon. */
  week: string | null;
  week_start: string | null;
  week_end: string | null;
  /** Définitif 24 h après la fin de la semaine. */
  final: boolean;
  previous_week: string | null;
  next_week: string | null;
  peers_level: string | null;
  total: number;
  top: LeaderboardEntry[];
  me: {
    rank: number | null;
    points: number | null;
    /** Pourquoi le visiteur n'est pas classé. */
    message: string | null;
    /** Voisins de chaque côté, quand le visiteur est hors du top 50. */
    neighbours: LeaderboardEntry[];
  } | null;
};

export type ReportTarget = "exercise" | "solution";

/** Un de mes signalements, avec son issue. */
export type MyReport = {
  id: number;
  target: ReportTarget;
  exercise_id: number;
  title: string;
  reason: string;
  reason_label: string;
  status: "ouvert" | "confirme" | "rejete";
  status_label: string;
  created_at: string;
  decided_at: string | null;
};

export type BadgeInfo = {
  slug: string;
  name: string;
  criterion: string;
  /** Faux tant que la fonctionnalité dont dépend le badge n'existe pas. */
  available: boolean;
  holders: number;
  awarded_at: string | null;
};

export type Member = {
  username: string;
  declared_level: string | null;
  trust_level: string;
  joined: string;
  /** null si le membre a masqué sa présence dans les classements. */
  points: number | null;
  exercises_published: number;
  solutions_validated: number;
  badges: { slug: string; name: string; criterion: string; awarded_at: string }[];
};

export type SolutionStatus =
  | "under_review"
  | "contested"
  | "validated"
  | "needs_work"
  | "hidden";

export type MySolution = {
  id: number;
  body: string;
  ai_usage: AiUsage;
  status: SolutionStatus;
  published_at: string | null;
  validated_at: string | null;
  feedback: string[];
};

export type ReviewTask = {
  id: number;
  assigned_at: string;
  exercise_id: number;
  exercise_title: string;
  exercise_statement: string;
  primary_level: string;
  solution_body: string;
  ai_usage: AiUsage;
};

/** null pour 401 et 404 ; une erreur pour le reste, dont l'API injoignable. */
async function get<T>(path: string): Promise<T | null> {
  const cookieHeader = (await cookies()).toString();
  const response = await fetch(`${API_URL}/api${path}`, {
    cache: "no-store",
    headers: cookieHeader ? { cookie: cookieHeader } : undefined,
  });
  if (response.status === 401 || response.status === 404) return null;
  if (!response.ok) throw new Error(`API ${path} : HTTP ${response.status}`);
  return (await response.json()) as T;
}

export async function fetchLevels() {
  return (await get<Level[]>("/levels")) ?? [];
}

export async function fetchTopics() {
  return (await get<Topic[]>("/topics")) ?? [];
}

export async function fetchExercises(level?: string, sort: ExerciseSort = "recent") {
  const query = new URLSearchParams({ sort });
  if (level) query.set("level", level);
  return (await get<ExerciseSummary[]>(`/exercises?${query}`)) ?? [];
}

/** Fil d'accueil d'un niveau, ou de tous ; null si le niveau n'existe pas. */
export function fetchFeed(level?: string) {
  return get<FeedItem[]>(`/feed${level ? `?level=${encodeURIComponent(level)}` : ""}`);
}

export function fetchExercise(id: string) {
  return get<ExerciseDetail>(`/exercises/${encodeURIComponent(id)}`);
}

/** Le visiteur connecté, ou null. */
export function fetchMe() {
  return get<Me>("/auth/me");
}

export async function fetchMySolutions(exerciseId: number) {
  return (await get<MySolution[]>(`/exercises/${exerciseId}/my-solutions`)) ?? [];
}

export async function fetchReviewTasks() {
  return (await get<ReviewTask[]>("/reviews")) ?? [];
}

/** null si le classement ou la semaine n'existe pas. */
export async function fetchLeaderboard(params: { board: string; week?: string; peers?: boolean }) {
  const query = new URLSearchParams({ board: params.board });
  if (params.week) query.set("week", params.week);
  if (params.peers) query.set("peers", "true");
  return get<Leaderboard>(`/leaderboards?${query}`).catch((error: Error) => {
    // Semaine mal formée dans l'adresse : traitée comme introuvable.
    if (error.message.endsWith("HTTP 422")) return null;
    throw error;
  });
}

export function fetchTrainingOptions(exerciseId: string) {
  return get<TrainingOptions>(`/training/options/${encodeURIComponent(exerciseId)}`);
}

export function fetchTrainingSession(id: string) {
  return get<TrainingSession>(`/training/sessions/${encodeURIComponent(id)}`);
}

/** Mes signalements ; null si le visiteur n'est pas connecté. */
export function fetchMyReports() {
  return get<MyReport[]>("/reports/mine");
}

export async function fetchBadges() {
  return (await get<BadgeInfo[]>("/badges")) ?? [];
}

export function fetchMember(username: string) {
  return get<Member>(`/members/${encodeURIComponent(username)}`);
}
