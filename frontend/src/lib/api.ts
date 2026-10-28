// Client de l'API Django pour les composants serveur. Il transmet les cookies
// du visiteur, pour que Django reconnaisse sa session.
import { cookies } from "next/headers";
import { unstable_rethrow } from "next/navigation";

// 127.0.0.1 plutôt que localhost : Node résout localhost en ::1, où runserver n'écoute pas.
const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

/** Pour un `.catch` : null en cas d'erreur, sauf les signaux internes de Next
 * (rendu dynamique, redirection), qui doivent remonter. */
export function nullOnError(error: unknown): null {
  unstable_rethrow(error);
  return null;
}

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
  /** Recommandée par l'auteur de l'exercice. */
  recommended: boolean;
  /** Solution d'un défi paramétré : l'énoncé tiré pour son auteur. */
  variant_statement: string;
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
  email_notifications: boolean;
  weekly_digest: boolean;
  daily_challenge_notifications: boolean;
  /** Faux pour un compte créé avec Google, tant qu'il n'a pas choisi de mot de passe. */
  has_password: boolean;
  google_linked: boolean;
  unread_notifications: number;
  academic_verified_at: string | null;
  /** Domaine de l'adresse académique vérifiée ; l'adresse elle-même n'est pas gardée. */
  academic_domain: string;
};

export type AppNotification = {
  id: number;
  kind: string;
  title: string;
  body: string;
  url: string;
  created_at: string;
  read: boolean;
};

export type TrainingOptions = {
  durations: number[];
  recommended: number;
  /** 1,33 si le visiteur a déclaré un tiers-temps. */
  extra_time_factor: number | null;
};

export type TrainingStatus = "en_cours" | "en_pause" | "rendue" | "abandonnee";

/** Session chronométrée, entraînement ou défi du jour ; le temps est celui du serveur. */
export type TrainingSession = {
  id: number;
  kind: "entrainement" | "defi";
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
  /** En défi, `hints` ne contient que les indications ouvertes. */
  hint_count: number;
  hints_opened: number;
  challenge_closes_at: string | null;
  points_max: number | null;
  bonus: number | null;
  answer_points: number;
  justification_points: number;
};

export type DailyChallenge = {
  id: number;
  level: string;
  level_name: string;
  exercise_title: string;
  difficulty: number;
  minutes: number;
  points_max: number;
  closes_at: string;
  hint_count: number;
  attempt: {
    session_id: number;
    status: TrainingStatus;
    answer_correct: boolean | null;
    answer_points: number;
    justification_points: number;
  } | null;
};

export type WeekStatus = "atteint" | "joker" | "vacances" | "manque";

export type PersonalGoal = {
  id: number;
  kind: "solutions" | "chrono_semaine";
  title: string;
  target: number;
  done: number;
  deadline: string;
  topic: string | null;
  per_week: boolean;
};

export type Progress = {
  week: string;
  goal_days: number;
  days: { date: string; active: boolean; future: boolean }[];
  active_days: number;
  achieved: boolean;
  streak: number;
  jokers_left: number;
  vacation: { start: string; end: string } | null;
  history: {
    week: string;
    week_start: string;
    goal: number;
    active_days: number;
    status: WeekStatus;
    status_label: string;
  }[];
  goals: PersonalGoal[];
  contributor: ContributorLevel;
  skills: Skill[];
};

/** Niveau de contributeur, de 1 à 30 ; `next` est null au niveau 30. */
export type ContributorLevel = {
  level: number;
  points: number;
  floor: number;
  next: number | null;
};

/** Maîtrise d'un chapitre, de 0 à 5, et l'exercice proposé un cran au-dessus. */
export type Skill = {
  topic: string;
  slug: string;
  mastery: number;
  solved: number;
  target: number;
  next: { id: number; title: string; difficulty: number } | null;
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
export type DecisionType = "sanction" | "report" | "signal";

export type Decision = {
  type: DecisionType;
  id: number;
  title: string;
  reason: string;
  decided_at: string | null;
  ends_at: string | null;
  appeal_deadline: string | null;
  can_appeal: boolean;
  appeal_status: "en_attente" | "maintenue" | "annulee" | null;
  appeal_status_label: string | null;
  appeal_note: string | null;
};

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
  /** null, comme le niveau, si le membre a masqué sa présence dans les classements. */
  points: number | null;
  contributor_level: number | null;
  exercises_published: number;
  solutions_validated: number;
  badges: { slug: string; name: string; criterion: string; awarded_at: string }[];
};

export type SolutionStatus =
  | "held"
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
  /** Solution en vérification : la question neutre, et la réponse déjà donnée. */
  integrity_signal_id: number | null;
  integrity_question: string | null;
  integrity_answer: string | null;
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

export type SitemapEntry = { id: number; updated_at: string };

/** Exercices publiés, sans cookie : le plan du site est le même pour tous et se met en cache. */
export async function fetchSitemap(): Promise<SitemapEntry[]> {
  const response = await fetch(`${API_URL}/api/sitemap`, { next: { revalidate: 3600 } });
  if (!response.ok) throw new Error(`API /sitemap : HTTP ${response.status}`);
  return response.json();
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

export async function fetchDailyChallenges() {
  return (await get<DailyChallenge[]>("/challenges/today")) ?? [];
}

export function fetchProgress() {
  return get<Progress>("/progress");
}

export function fetchTrainingSession(id: string) {
  return get<TrainingSession>(`/training/sessions/${encodeURIComponent(id)}`);
}

export function fetchNotifications() {
  return get<{ unread: number; items: AppNotification[] }>("/notifications");
}

/** La transcription des photos de copie est-elle proposée ? */
export async function fetchTranscriptionAvailable() {
  return (await get<{ available: boolean }>("/transcription"))?.available ?? false;
}

/** Clé VAPID publique ; null si les notifications push ne sont pas configurées. */
export async function fetchPushKey() {
  return (await get<{ public_key: string | null }>("/push/key"))?.public_key ?? null;
}

export async function fetchProviders() {
  return (await get<{ google: boolean }>("/auth/providers")) ?? { google: false };
}

export type Arbitration = {
  solution_id: number;
  exercise_id: number;
  exercise_title: string;
  exercise_statement: string;
  solution_body: string;
  ai_usage: AiUsage;
  reviews: { verdict: string; feedback: string; weight: number }[];
};

export type OpenSolution = {
  solution_id: number;
  exercise_id: number;
  exercise_title: string;
  primary_level: string;
  published_at: string | null;
};

/** null si le visiteur n'est ni expert ni modérateur. */
export function fetchArbitrations() {
  return get<Arbitration[]>("/arbitrations").catch((error: Error) => {
    if (error.message.endsWith("HTTP 403")) return null;
    throw error;
  });
}

export type QuestionStatus =
  | "envoyee"
  | "ouverte"
  | "repondue"
  | "reussie"
  | "insuffisante"
  | "sans_reponse";

/** Question de compréhension : énoncé, solution et question arrivent une fois ouverte. */
export type ComprehensionQuestion = {
  id: number;
  exercise_id: number;
  exercise_title: string;
  status: QuestionStatus;
  status_label: string;
  open_until: string | null;
  answer_until: string | null;
  statement: string | null;
  solution_body: string | null;
  question: string | null;
  answer: string;
  evaluation_note: string;
};

export type QuestionToEvaluate = {
  id: number;
  exercise_title: string;
  statement: string;
  solution_body: string;
  question: string;
  expected_points: string[];
  answer: string;
  answered_at: string;
  llm_assessment: string | null;
  llm_assessment_label: string | null;
  llm_rationale: string;
};

/** Mes questions de compréhension ; null si le visiteur n'est pas connecté. */
export function fetchMyQuestions() {
  return get<ComprehensionQuestion[]>("/questions/mine");
}

/** Réponses à évaluer ; null pour qui n'est ni expert ni modérateur. */
export function fetchQuestionsToEvaluate() {
  return get<QuestionToEvaluate[]>("/questions/to-evaluate").catch((error: Error) => {
    if (error.message.endsWith("HTTP 403")) return null;
    throw error;
  });
}

export async function fetchOpenSolutions() {
  return (await get<OpenSolution[]>("/reviews/open")) ?? [];
}

/** Mes signalements ; null si le visiteur n'est pas connecté. */
export function fetchMyReports() {
  return get<MyReport[]>("/reports/mine");
}

export function fetchMyDecisions() {
  return get<Decision[]>("/decisions/mine");
}

export async function fetchBadges() {
  return (await get<BadgeInfo[]>("/badges")) ?? [];
}

export function fetchMember(username: string) {
  return get<Member>(`/members/${encodeURIComponent(username)}`);
}
