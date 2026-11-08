---
titre: Espaces vectoriels normés
programmes: MP, PSI
ordre: 6
notion: espaces-vectoriels-normes
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$ et $E$, $F$ sont des $\K$-espaces vectoriels.

## Normes

> **Définition.** Une **norme** sur $E$ est une application $N : E \to \R_+$ telle que, pour tous $x, y \in E$ et $\lambda \in \K$ :
>
> 1. **séparation :** $N(x) = 0 \implies x = 0$ ;
> 2. **homogénéité :** $N(\lambda x) = |\lambda| \, N(x)$ ;
> 3. **inégalité triangulaire :** $N(x + y) \leq N(x) + N(y)$.

On note souvent $\|x\|$ ; la **distance** associée est $d(x, y) = \|x - y\|$. On a toujours $\big| \|x\| - \|y\| \big| \leq \|x - y\|$. La **boule ouverte** de centre $a$ et de rayon $r > 0$ est $B(a, r) = \{ x \in E : \|x - a\| < r \}$, la boule fermée $B_f(a, r)$ est définie avec $\leq$.

Sur $\K^n$, pour $x = (x_1, \dots, x_n)$ :

$$
\|x\|_1 = \sum_{i=1}^{n} |x_i|, \qquad \|x\|_2 = \left( \sum_{i=1}^{n} |x_i|^2 \right)^{1/2}, \qquad \|x\|_\infty = \max_{1 \leq i \leq n} |x_i|.
$$

> **Définition.** Deux normes $N$ et $N'$ sur $E$ sont **équivalentes** s'il existe $\alpha, \beta > 0$ tels que $\alpha N \leq N' \leq \beta N$.

> **Théorème.** Sur un espace vectoriel de **dimension finie**, toutes les normes sont équivalentes.

En dimension infinie, c'est faux : sur $\mathcal{C}([0, 1], \R)$, avec $f_n(t) = t^n$, on a $\|f_n\|_\infty = 1$ et $\|f_n\|_1 = \int_0^1 |f_n| = \frac{1}{n+1}$, donc il n'existe pas de $\beta > 0$ tel que $\|\cdot\|_\infty \leq \beta \|\cdot\|_1$.

## Suites

Une suite $(x_n)$ d'éléments de $E$ **converge** vers $\ell \in E$ si $\|x_n - \ell\| \to 0$. En dimension finie, cette notion ne dépend pas de la norme, et une suite converge si et seulement si chacune de ses suites de coordonnées dans une base converge.

## Topologie

Soit $A$ une partie de $E$.

> **Définition.**
>
> 1. $A$ est **ouverte** si, pour tout $a \in A$, il existe $r > 0$ tel que $B(a, r) \subset A$.
> 2. $A$ est **fermée** si son complémentaire $E \setminus A$ est ouvert.
> 3. Un point $x \in E$ est **adhérent** à $A$ s'il existe une suite d'éléments de $A$ qui converge vers $x$ ; l'**adhérence** $\overline{A}$ est l'ensemble de ces points. $A$ est **dense** dans $E$ si $\overline{A} = E$.

> **Proposition (caractérisation séquentielle des fermés).** La partie $A$ est fermée si et seulement si, pour toute suite d'éléments de $A$ qui converge dans $E$, la limite appartient à $A$.

Une réunion quelconque d'ouverts est ouverte, une intersection **finie** d'ouverts est ouverte ; dualement pour les fermés. En dimension finie, ces notions ne dépendent pas de la norme.

## Limites et continuité

Soient $A \subset E$, $f : A \to F$ et $a$ un point adhérent à $A$. La fonction $f$ tend vers $\ell \in F$ en $a$ si $\forall \varepsilon > 0, \ \exists \delta > 0, \ \forall x \in A, \ \|x - a\| \leq \delta \implies \|f(x) - \ell\| \leq \varepsilon$. La caractérisation séquentielle des limites et de la continuité reste vraie.

> **Proposition.** Si $f : E \to F$ est continue, l'image réciproque par $f$ d'un ouvert (resp. d'un fermé) de $F$ est un ouvert (resp. un fermé) de $E$.

Exemple : si $f : E \to \R$ est continue, $\{ x \in E : f(x) > 0 \}$ est ouvert et $\{ x \in E : f(x) = 0 \}$ est fermé.

> **Théorème (continuité des applications linéaires).** Soit $u \in \mathcal{L}(E, F)$. L'application $u$ est continue sur $E$ si et seulement s'il existe $C \geq 0$ tel que $\|u(x)\| \leq C \|x\|$ pour tout $x \in E$. Si $E$ est de **dimension finie**, toute application linéaire de $E$ dans $F$ est continue.

## Compacité

> **Définition.** Une partie $K$ de $E$ est **compacte** si toute suite d'éléments de $K$ admet une suite extraite qui converge vers un élément de $K$.

> **Proposition.** Une partie compacte est fermée et bornée.

> **Théorème.** Si $E$ est de **dimension finie**, les parties compactes de $E$ sont exactement les parties fermées et bornées.

En dimension infinie, la boule unité fermée n'est jamais compacte.

> **Théorème.** Soient $K$ une partie compacte de $E$ et $f : K \to F$ continue.
>
> 1. $f(K)$ est compacte.
> 2. **(bornes atteintes)** Si $F = \R$ et $K \neq \varnothing$, $f$ est bornée et atteint ses bornes.
> 3. **(Heine)** $f$ est uniformément continue sur $K$.

## Connexité par arcs

Une partie $A$ de $E$ est **connexe par arcs** si, pour tous $x, y \in A$, il existe une application continue $\gamma : [0, 1] \to A$ telle que $\gamma(0) = x$ et $\gamma(1) = y$. Les parties convexes sont connexes par arcs ; les parties connexes par arcs de $\R$ sont les intervalles.

> **Théorème (valeurs intermédiaires).** L'image d'une partie connexe par arcs par une application continue est connexe par arcs. En particulier, si $A$ est connexe par arcs et $f : A \to \R$ continue, $f(A)$ est un intervalle.

## Pièges fréquents

- Utiliser l'équivalence des normes, ou « fermé et borné $\iff$ compact », en dimension infinie.
- Croire qu'une partie qui n'est pas ouverte est fermée : $[0, 1[$ n'est ni ouverte ni fermée dans $\R$, et $\R$ est à la fois ouvert et fermé.
- Oublier que l'intersection d'une infinité d'ouverts n'est pas toujours ouverte : $\bigcap_{n \geq 1} \, ]{-}\frac{1}{n}, \frac{1}{n}[ \, = \{0\}$.
