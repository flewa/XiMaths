---
titre: Probabilités sur un univers fini
programmes: MPSI, MP2I, PCSI
ordre: 18
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

Par convention, on pose $P(A \mid B) P(B) = 0$ quand $P(B) = 0$.

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

Si $P(B) > 0$, $A$ et $B$ sont indépendants si et seulement si $P(A \mid B) = P(A)$. Si $A$ et $B$ sont indépendants, $A$ et $\overline{B}$ le sont aussi ; plus généralement, remplacer certains des $A_i$ par leurs contraires préserve l'indépendance mutuelle.

L'indépendance mutuelle entraîne l'indépendance deux à deux ; la réciproque est fausse. Exemple : deux lancers d'une pièce équilibrée, $A$ = « le premier donne pile », $B$ = « le second donne pile », $C$ = « les deux donnent le même résultat » ; les événements sont deux à deux indépendants, mais $P(A \cap B \cap C) = \frac{1}{4} \neq \frac{1}{8}$.

## Variables aléatoires

Une **variable aléatoire** est une application $X : \Omega \to E$. Pour $A \subset E$, on note $\{ X \in A \}$ ou $(X \in A)$ l'événement $X^{-1}(A)$. La **loi** de $X$ est la probabilité $P_X$ sur $X(\Omega)$ donnée par $P_X(A) = P(X \in A)$ ; elle est déterminée par les $P(X = x)$, $x \in X(\Omega)$. On note $X \sim Y$ si $X$ et $Y$ ont la même loi ; alors $f(X) \sim f(Y)$ pour toute fonction $f$. Si $P(A) > 0$, la **loi conditionnelle** de $X$ sachant $A$ est la loi de $X$ pour la probabilité $P_A$.

**Couples.** Un couple $(X, Y)$ est une variable aléatoire à valeurs dans un produit. Sa **loi conjointe** est donnée par les $P(X = x, Y = y)$ ; ses **lois marginales** sont celles de $X$ et de $Y$, avec $P(X = x) = \sum_{y \in Y(\Omega)} P(X = x, Y = y)$. Les lois marginales ne déterminent pas la loi conjointe. Tout s'étend aux $n$-uplets de variables aléatoires.

> **Définition.** Soit $X$ une variable aléatoire réelle. Son **espérance** est $E(X) = \sum_{x \in X(\Omega)} x \, P(X = x) = \sum_{\omega \in \Omega} X(\omega) P(\{\omega\})$, sa **variance** est $V(X) = E\big( (X - E(X))^2 \big)$ et son écart type est $\sigma(X) = \sqrt{V(X)}$. La variable $X$ est **centrée** si $E(X) = 0$ ; si $\sigma(X) > 0$, la variable $\dfrac{X - E(X)}{\sigma(X)}$ est centrée réduite.

L'espérance se définit de même pour une variable complexe. Pour un événement $A$, $E(\mathbf{1}_A) = P(A)$.

> **Proposition.**
>
> 1. **Linéarité :** $E(aX + bY) = a E(X) + b E(Y)$ ; **positivité :** si $X \geq 0$, alors $E(X) \geq 0$ ; **croissance :** si $X \leq Y$, alors $E(X) \leq E(Y)$ ; $|E(X)| \leq E(|X|)$.
> 2. **Formule de transfert :** pour $f : X(\Omega) \to \R$, $E\big( f(X) \big) = \sum_{x \in X(\Omega)} f(x) \, P(X = x)$.
> 3. **Formule de König-Huygens :** $V(X) = E(X^2) - E(X)^2$, et $V(aX + b) = a^2 V(X)$.

**Lois usuelles**, pour $p \in [0, 1]$ et $m \in \N^*$ :

- **Bernoulli** $\mathcal{B}(p)$ : $P(X = 1) = p$ et $P(X = 0) = 1 - p$ ; $E(X) = p$ et $V(X) = p(1 - p)$.
- **Binomiale** $\mathcal{B}(m, p)$ : $P(X = k) = \binom{m}{k} p^k (1 - p)^{m-k}$ pour $k \in [\![0, m]\!]$ ; $E(X) = mp$ et $V(X) = mp(1 - p)$.
- **Uniforme** sur $[\![1, m]\!]$ : $P(X = k) = \frac{1}{m}$ pour $k \in [\![1, m]\!]$ ; $E(X) = \frac{m + 1}{2}$ et $V(X) = \frac{m^2 - 1}{12}$.

Le nombre de succès dans $m$ répétitions indépendantes d'une épreuve de Bernoulli de paramètre $p$ suit la loi $\mathcal{B}(m, p)$.

Deux variables aléatoires $X$ et $Y$ sont **indépendantes** si les événements $(X \in A)$ et $(Y \in B)$ sont indépendants pour toutes parties $A$ et $B$, ce qui équivaut à $P(X = x, Y = y) = P(X = x) P(Y = y)$ pour tous $x \in X(\Omega)$ et $y \in Y(\Omega)$. Les variables $X_1, \dots, X_n$ sont (mutuellement) indépendantes si les événements $(X_1 \in A_1), \dots, (X_n \in A_n)$ le sont pour toutes parties $A_i$ ; c'est ainsi qu'on modélise $n$ expériences indépendantes.

> **Proposition.**
>
> 1. Si $X$ et $Y$ sont indépendantes, $f(X)$ et $g(Y)$ le sont.
> 2. **Lemme des coalitions :** si $X_1, \dots, X_n$ sont indépendantes, alors $f(X_1, \dots, X_m)$ et $g(X_{m+1}, \dots, X_n)$ sont indépendantes.
> 3. Si $X_1, \dots, X_n$ sont indépendantes et suivent la loi $\mathcal{B}(p)$, alors $X_1 + \dots + X_n \sim \mathcal{B}(n, p)$.
> 4. Si $X$ et $Y$ sont indépendantes, $E(XY) = E(X) E(Y)$.

La **covariance** est $\operatorname{Cov}(X, Y) = E\big( (X - E(X))(Y - E(Y)) \big) = E(XY) - E(X) E(Y)$ ; deux variables de covariance nulle sont dites **décorrélées**. Des variables indépendantes sont décorrélées ; la réciproque est fausse. En général,

$$
V\left( \sum_{i=1}^{n} X_i \right) = \sum_{i=1}^{n} V(X_i) + 2 \sum_{1 \leq i < j \leq n} \operatorname{Cov}(X_i, X_j),
$$

donc la variance d'une somme de variables deux à deux décorrélées est la somme des variances. On retrouve $V(X) = np(1 - p)$ pour $X \sim \mathcal{B}(n, p)$.

> **Inégalité de Markov.** Si $X \geq 0$ et $a > 0$, alors $P(X \geq a) \leq \dfrac{E(X)}{a}$.

> **Inégalité de Bienaymé-Tchebychev.** Pour tout $\varepsilon > 0$, $P\big( |X - E(X)| \geq \varepsilon \big) \leq \dfrac{V(X)}{\varepsilon^2}$.

**Moyenne empirique.** Si $X_1, \dots, X_n$ sont indépendantes, de même loi, d'espérance $m$ et de variance $\sigma^2$, et si $\overline{X}_n = \frac{X_1 + \dots + X_n}{n}$, alors $E(\overline{X}_n) = m$, $V(\overline{X}_n) = \frac{\sigma^2}{n}$, et

$$
P\big( |\overline{X}_n - m| \geq \varepsilon \big) \leq \frac{\sigma^2}{n \varepsilon^2}.
$$

Ainsi, la fréquence d'un événement sur $n$ répétitions indépendantes est proche de sa probabilité avec une probabilité qui tend vers $1$ : c'est l'interprétation fréquentiste.

## Pièges fréquents

- Confondre événements **indépendants** et événements **incompatibles** : deux événements incompatibles de probabilités non nulles ne sont jamais indépendants.
- Confondre $P_B(A)$ et $P_A(B)$ ; la formule de Bayes passe de l'une à l'autre.
- Écrire $E(XY) = E(X) E(Y)$ ou $V(X + Y) = V(X) + V(Y)$ sans indépendance.
