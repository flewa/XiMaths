---
titre: Probabilités sur un univers fini
programmes: MPSI, PCSI
ordre: 12
notion: probabilites-conditionnelles
---

## Cadre et notations

Dans toute la fiche, $\Omega$ est un ensemble fini non vide (l'**univers**) ; les **événements** sont les parties de $\Omega$. Pour un événement $A$, on note $\overline{A} = \Omega \setminus A$ son contraire. Pour un ensemble fini $A$, $|A|$ désigne son nombre d'éléments.

## Probabilité

> **Définition.** Une **probabilité** sur $\Omega$ est une application $P : \mathcal{P}(\Omega) \to [0, 1]$ telle que $P(\Omega) = 1$ et $P(A \cup B) = P(A) + P(B)$ pour tous événements $A$ et $B$ **disjoints**.

> **Proposition.** Pour tous événements $A$ et $B$ :
>
> $$
> P(\varnothing) = 0, \qquad P(\overline{A}) = 1 - P(A), \qquad A \subset B \implies P(A) \leq P(B), \qquad P(A \cup B) = P(A) + P(B) - P(A \cap B).
> $$

Une probabilité est déterminée par les valeurs $p_\omega = P(\{\omega\})$, qui sont des réels positifs de somme $1$, et réciproquement toute telle famille définit une probabilité. La **probabilité uniforme** est donnée par $P(A) = \dfrac{|A|}{|\Omega|}$.

## Probabilités conditionnelles

> **Définition.** Soit $B$ un événement tel que $P(B) > 0$. La **probabilité de $A$ sachant $B$** est $P_B(A) = P(A \mid B) = \dfrac{P(A \cap B)}{P(B)}$. L'application $P_B$ est une probabilité sur $\Omega$.

> **Formule des probabilités composées.** Si $P(A_1 \cap \dots \cap A_{m-1}) > 0$, alors
>
> $$
> P(A_1 \cap \dots \cap A_m) = P(A_1) \, P_{A_1}(A_2) \, P_{A_1 \cap A_2}(A_3) \cdots P_{A_1 \cap \dots \cap A_{m-1}}(A_m).
> $$

Un **système complet d'événements** est une famille $(A_1, \dots, A_m)$ d'événements deux à deux disjoints dont la réunion est $\Omega$.

> **Formule des probabilités totales.** Si $(A_1, \dots, A_m)$ est un système complet d'événements, alors pour tout événement $B$ :
>
> $$
> P(B) = \sum_{i=1}^{m} P(B \cap A_i) = \sum_{i=1}^{m} P(A_i) \, P_{A_i}(B),
> $$
>
> où, dans la seconde somme, un terme tel que $P(A_i) = 0$ est compté comme nul.

> **Formule de Bayes.** Si $P(A) > 0$ et $P(B) > 0$ :
>
> $$
> P_B(A) = \frac{P_A(B) \, P(A)}{P(B)}.
> $$

## Indépendance

> **Définition.** Deux événements $A$ et $B$ sont **indépendants** si $P(A \cap B) = P(A) P(B)$. Des événements $A_1, \dots, A_m$ sont **mutuellement indépendants** si, pour toute partie $J$ de $[\![1, m]\!]$, $P\left( \bigcap_{j \in J} A_j \right) = \prod_{j \in J} P(A_j)$.

L'indépendance mutuelle entraîne l'indépendance deux à deux ; la réciproque est fausse. Exemple : deux lancers d'une pièce équilibrée, $A$ = « le premier donne pile », $B$ = « le second donne pile », $C$ = « les deux donnent le même résultat » ; les événements sont deux à deux indépendants, mais $P(A \cap B \cap C) = \frac{1}{4} \neq \frac{1}{8}$.

## Variables aléatoires

Une **variable aléatoire** est une application $X : \Omega \to E$ ; sa **loi** est la probabilité $P_X$ sur $X(\Omega)$ définie par $P_X(\{x\}) = P(X = x)$.

> **Définition.** Soit $X$ une variable aléatoire réelle. Son **espérance** est $E(X) = \sum_{x \in X(\Omega)} x \, P(X = x)$, sa **variance** est $V(X) = E\big( (X - E(X))^2 \big)$ et son écart type est $\sigma(X) = \sqrt{V(X)}$.

> **Proposition.**
>
> 1. **Linéarité :** $E(aX + bY) = a E(X) + b E(Y)$ ; **positivité :** si $X \geq 0$, alors $E(X) \geq 0$.
> 2. **Formule de transfert :** pour $f : X(\Omega) \to \R$, $E\big( f(X) \big) = \sum_{x \in X(\Omega)} f(x) \, P(X = x)$.
> 3. **Formule de König-Huygens :** $V(X) = E(X^2) - E(X)^2$, et $V(aX + b) = a^2 V(X)$.

**Lois usuelles**, pour $p \in [0, 1]$ et $m \in \N^*$ :

- **Bernoulli** $\mathcal{B}(p)$ : $P(X = 1) = p$ et $P(X = 0) = 1 - p$ ; $E(X) = p$ et $V(X) = p(1 - p)$.
- **Binomiale** $\mathcal{B}(m, p)$ : $P(X = k) = \binom{m}{k} p^k (1 - p)^{m-k}$ pour $k \in [\![0, m]\!]$ ; $E(X) = mp$ et $V(X) = mp(1 - p)$.
- **Uniforme** sur $[\![1, m]\!]$ : $P(X = k) = \frac{1}{m}$ pour $k \in [\![1, m]\!]$ ; $E(X) = \frac{m + 1}{2}$ et $V(X) = \frac{m^2 - 1}{12}$.

Le nombre de succès dans $m$ répétitions indépendantes d'une épreuve de Bernoulli de paramètre $p$ suit la loi $\mathcal{B}(m, p)$.

Deux variables aléatoires $X$ et $Y$ sont **indépendantes** si $P(X = x, Y = y) = P(X = x) P(Y = y)$ pour tous $x \in X(\Omega)$ et $y \in Y(\Omega)$. Dans ce cas, pour des variables réelles, $E(XY) = E(X) E(Y)$ et $V(X + Y) = V(X) + V(Y)$. En général, $V(X + Y) = V(X) + V(Y) + 2 \operatorname{Cov}(X, Y)$, avec $\operatorname{Cov}(X, Y) = E(XY) - E(X) E(Y)$.

> **Inégalité de Markov.** Si $X \geq 0$ et $a > 0$, alors $P(X \geq a) \leq \dfrac{E(X)}{a}$.

> **Inégalité de Bienaymé-Tchebychev.** Pour tout $\varepsilon > 0$, $P\big( |X - E(X)| \geq \varepsilon \big) \leq \dfrac{V(X)}{\varepsilon^2}$.

## Pièges fréquents

- Confondre événements **indépendants** et événements **incompatibles** : deux événements incompatibles de probabilités non nulles ne sont jamais indépendants.
- Confondre $P_B(A)$ et $P_A(B)$ ; la formule de Bayes passe de l'une à l'autre.
- Écrire $E(XY) = E(X) E(Y)$ ou $V(X + Y) = V(X) + V(Y)$ sans indépendance.
