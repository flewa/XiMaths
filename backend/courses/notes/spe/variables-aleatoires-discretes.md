---
titre: Espaces probabilisés et variables aléatoires discrètes
programmes: MP, PSI
ordre: 10
notion: variables-aleatoires-discretes
---

## Cadre et notations

> **Définition.** Soit $\Omega$ un ensemble. Une **tribu** sur $\Omega$ est une partie $\mathcal{A}$ de $\mathcal{P}(\Omega)$ qui contient $\Omega$, est stable par passage au complémentaire et par réunion dénombrable. Une **probabilité** sur $(\Omega, \mathcal{A})$ est une application $P : \mathcal{A} \to [0, 1]$ telle que $P(\Omega) = 1$ et, pour toute suite $(A_n)$ d'événements deux à deux disjoints, $P\left( \bigcup_{n=0}^{+\infty} A_n \right) = \sum_{n=0}^{+\infty} P(A_n)$ (**σ-additivité**).

Dans toute la fiche, $(\Omega, \mathcal{A}, P)$ est un espace probabilisé. Un événement $A$ est **négligeable** si $P(A) = 0$, **presque sûr** si $P(A) = 1$.

## Propriétés de la probabilité

> **Proposition.**
>
> 1. **Continuité croissante :** si $(A_n)$ est croissante pour l'inclusion, $P\left( \bigcup_{n} A_n \right) = \lim_{n \to +\infty} P(A_n)$.
> 2. **Continuité décroissante :** si $(A_n)$ est décroissante, $P\left( \bigcap_{n} A_n \right) = \lim_{n \to +\infty} P(A_n)$.
> 3. **Sous-additivité :** pour toute suite $(A_n)$ d'événements, $P\left( \bigcup_{n} A_n \right) \leq \sum_{n=0}^{+\infty} P(A_n)$, la somme pouvant valoir $+\infty$.

Un **système complet d'événements** est une famille finie ou dénombrable $(A_i)_{i \in I}$ d'événements deux à deux disjoints de réunion $\Omega$. Pour un tel système, la **formule des probabilités totales** s'écrit $P(B) = \sum_{i \in I} P(B \cap A_i) = \sum_{i \in I} P(A_i) P_{A_i}(B)$, les termes tels que $P(A_i) = 0$ étant comptés comme nuls. La formule de Bayes est inchangée.

## Variables aléatoires discrètes

> **Définition.** Une **variable aléatoire discrète** est une application $X : \Omega \to E$ telle que $X(\Omega)$ soit fini ou dénombrable et que $\{X = x\} = X^{-1}(\{x\}) \in \mathcal{A}$ pour tout $x \in X(\Omega)$. Sa **loi** est déterminée par la famille $\big( P(X = x) \big)_{x \in X(\Omega)}$, de somme $1$.

Des variables aléatoires discrètes $X_1, \dots, X_m$ sont **mutuellement indépendantes** si, pour tous $x_1 \in X_1(\Omega), \dots, x_m \in X_m(\Omega)$, $P(X_1 = x_1, \dots, X_m = x_m) = \prod_{i=1}^{m} P(X_i = x_i)$ ; une suite de variables l'est si toute sous-famille finie l'est.

## Espérance et variance

> **Définition.** Une variable aléatoire discrète réelle $X$ est **d'espérance finie** si la famille $\big( x \, P(X = x) \big)_{x \in X(\Omega)}$ est sommable ; son **espérance** est alors $E(X) = \sum_{x \in X(\Omega)} x \, P(X = x)$.

> **Théorème de transfert.** Soit $f : X(\Omega) \to \R$. La variable $f(X)$ est d'espérance finie si et seulement si la famille $\big( f(x) P(X = x) \big)_{x \in X(\Omega)}$ est sommable, et alors $E\big( f(X) \big) = \sum_{x \in X(\Omega)} f(x) \, P(X = x)$.

> **Proposition.**
>
> 1. L'espérance est linéaire, positive et croissante sur les variables d'espérance finie ; si $|X| \leq Y$ avec $Y$ d'espérance finie, $X$ est d'espérance finie.
> 2. Si $X$ est à valeurs dans $\N$ : $E(X) = \sum_{n=1}^{+\infty} P(X \geq n)$, dans $[0, +\infty]$.
> 3. Si $X$ et $Y$ sont indépendantes et d'espérance finie, alors $XY$ est d'espérance finie et $E(XY) = E(X) E(Y)$.

> **Définition (variance).** Si $E(X^2) < +\infty$, alors $X$ est d'espérance finie, et sa **variance** est $V(X) = E\big( (X - E(X))^2 \big) = E(X^2) - E(X)^2$. Pour $a, b \in \R$, $V(aX + b) = a^2 V(X)$.

> **Proposition.** Si $E(X^2)$ et $E(Y^2)$ sont finies : $E(XY)^2 \leq E(X^2) E(Y^2)$ (Cauchy-Schwarz), et $V(X + Y) = V(X) + V(Y) + 2 \operatorname{Cov}(X, Y)$ avec $\operatorname{Cov}(X, Y) = E(XY) - E(X) E(Y)$. Si $X$ et $Y$ sont indépendantes, $\operatorname{Cov}(X, Y) = 0$ ; la réciproque est fausse.

## Lois usuelles

- **Géométrique** $\mathcal{G}(p)$, $p \in \, ]0, 1[$ : $P(X = k) = (1 - p)^{k-1} p$ pour $k \in \N^*$ ; $E(X) = \frac{1}{p}$, $V(X) = \frac{1 - p}{p^2}$. C'est le rang du premier succès dans une suite d'épreuves de Bernoulli indépendantes de paramètre $p$. Elle est **sans mémoire** : $P(X > n + k \mid X > n) = P(X > k)$ pour tous $n, k \in \N$.
- **Poisson** $\mathcal{P}(\lambda)$, $\lambda > 0$ : $P(X = k) = e^{-\lambda} \frac{\lambda^k}{k!}$ pour $k \in \N$ ; $E(X) = V(X) = \lambda$.
- **Bernoulli** et **binomiale** : comme sur un univers fini.

Si $X \sim \mathcal{P}(\lambda)$ et $Y \sim \mathcal{P}(\mu)$ sont indépendantes, alors $X + Y \sim \mathcal{P}(\lambda + \mu)$.

## Fonctions génératrices

> **Définition.** Pour $X$ à valeurs dans $\N$, la **fonction génératrice** de $X$ est $G_X(t) = E(t^X) = \sum_{n=0}^{+\infty} P(X = n) \, t^n$ ; le rayon de convergence de cette série entière est au moins $1$.

> **Proposition.**
>
> 1. $G_X$ détermine la loi de $X$ : $P(X = n) = \dfrac{G_X^{(n)}(0)}{n!}$.
> 2. $X$ est d'espérance finie si et seulement si $G_X$ est dérivable en $1$ (à gauche), et alors $E(X) = G_X'(1)$.
> 3. Si $X$ et $Y$ sont indépendantes, à valeurs dans $\N$, alors $G_{X+Y} = G_X \, G_Y$ sur $[-1, 1]$.

## Inégalités et loi faible des grands nombres

> **Inégalité de Markov.** Si $X$ est positive et d'espérance finie, pour tout $a > 0$ : $P(X \geq a) \leq \dfrac{E(X)}{a}$.

> **Inégalité de Bienaymé-Tchebychev.** Si $E(X^2) < +\infty$, pour tout $\varepsilon > 0$ : $P\big( |X - E(X)| \geq \varepsilon \big) \leq \dfrac{V(X)}{\varepsilon^2}$.

> **Loi faible des grands nombres.** Soit $(X_n)_{n \geq 1}$ une suite de variables aléatoires discrètes réelles, mutuellement indépendantes, de même loi, telles que $E(X_1^2) < +\infty$. On note $m = E(X_1)$ et $S_n = X_1 + \dots + X_n$. Pour tout $\varepsilon > 0$ :
>
> $$
> P\left( \left| \frac{S_n}{n} - m \right| \geq \varepsilon \right) \xrightarrow[n \to +\infty]{} 0.
> $$

## Pièges fréquents

- Écrire $E(X)$ sans avoir vérifié que la somme converge absolument.
- Confondre la loi géométrique sur $\N^*$ (rang du premier succès) avec une variante sur $\N$ (nombre d'échecs avant le premier succès), dont l'espérance est $\frac{1 - p}{p}$.
- Déduire l'indépendance d'une covariance nulle.
