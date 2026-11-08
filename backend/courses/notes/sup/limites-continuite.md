---
titre: Limites et continuité
programmes: MPSI, PCSI
ordre: 3
notion: limites-continuite
---

## Cadre et notations

Dans toute la fiche, $I$ est un intervalle, $f : I \to \R$, et $a$ est un point de $I$ ou une extrémité de $I$ (éventuellement $\pm\infty$). On note $\overline{\R} = \R \cup \{ -\infty, +\infty \}$.

## Limite en un point

> **Définition.** Soient $a \in \R$ un point de $I$ ou une extrémité réelle de $I$, et $\ell \in \R$. On dit que $f$ **tend vers $\ell$ en $a$** si
>
> $$
> \forall \varepsilon > 0, \ \exists \delta > 0, \ \forall x \in I, \ |x - a| \leq \delta \implies |f(x) - \ell| \leq \varepsilon.
> $$
>
> Ce réel $\ell$ est alors unique. Si $a \in I$ et que $f$ admet une limite $\ell$ en $a$, alors $\ell = f(a)$.

Les autres cas s'écrivent de la même façon : par exemple, $f$ tend vers $\ell$ en $+\infty$ si $\forall \varepsilon > 0, \ \exists A \in \R, \ \forall x \in I, \ x \geq A \implies |f(x) - \ell| \leq \varepsilon$. La **limite à droite** en $a$ est la limite en $a$ de la restriction de $f$ à $I \cap \, ]a, +\infty[$.

> **Théorème (caractérisation séquentielle).** Soit $\ell \in \overline{\R}$. La fonction $f$ tend vers $\ell$ en $a$ si et seulement si, pour toute suite $(x_n)$ d'éléments de $I$ qui tend vers $a$, la suite $\big( f(x_n) \big)$ tend vers $\ell$.

Usage typique : pour montrer que $f$ n'a pas de limite en $a$, on exhibe deux suites $(x_n)$ et $(y_n)$ qui tendent vers $a$ et telles que $\big( f(x_n) \big)$ et $\big( f(y_n) \big)$ aient des limites différentes.

> **Théorème (limite monotone).** Soient $a < b$ dans $\overline{\R}$ et $f : \, ]a, b[ \, \to \R$ croissante. Alors $f$ admet en $b$ une limite dans $\overline{\R}$, égale à $\sup_{]a, b[} f$ ; cette limite est finie si et seulement si $f$ est majorée. De même en $a$, avec la borne inférieure.

## Continuité

> **Définition.** La fonction $f$ est **continue en $a \in I$** si $f(x) \to f(a)$ quand $x \to a$. Elle est **continue sur $I$** si elle est continue en tout point de $I$.

Sommes, produits, quotients (dont le dénominateur ne s'annule pas) et composées de fonctions continues sont continues.

**Prolongement par continuité.** Si $a \notin I$ est une extrémité réelle de $I$ et si $f$ a une limite finie $\ell$ en $a$, la fonction définie sur $I \cup \{a\}$ par $f$ sur $I$ et $\ell$ en $a$ est continue en $a$.

## Les grands théorèmes

> **Théorème des valeurs intermédiaires.** Si $f$ est continue sur l'intervalle $I$, alors $f(I)$ est un intervalle. En particulier, si $a, b \in I$ avec $a < b$ et si $f(a) f(b) \leq 0$, il existe $c \in [a, b]$ tel que $f(c) = 0$.

> **Théorème des bornes atteintes.** Soient $a < b$ deux réels. Toute fonction continue sur le segment $[a, b]$ est bornée et atteint ses bornes : $f([a, b])$ est un segment.

> **Théorème de la bijection.** Si $f$ est continue et strictement monotone sur l'intervalle $I$, alors $J = f(I)$ est un intervalle, $f$ réalise une bijection de $I$ sur $J$, et sa réciproque $f^{-1} : J \to I$ est continue et strictement monotone, de même sens que $f$.

## Continuité uniforme

> **Définition.** La fonction $f$ est **uniformément continue** sur $I$ si
>
> $$
> \forall \varepsilon > 0, \ \exists \delta > 0, \ \forall x, y \in I, \ |x - y| \leq \delta \implies |f(x) - f(y)| \leq \varepsilon.
> $$
>
> Elle est **$k$-lipschitzienne** ($k \in \R_+$) si $|f(x) - f(y)| \leq k |x - y|$ pour tous $x, y \in I$.

Lipschitzienne $\implies$ uniformément continue $\implies$ continue. Les réciproques sont fausses : $x \mapsto \sqrt{x}$ est uniformément continue sur $[0, 1]$ sans être lipschitzienne, $x \mapsto x^2$ est continue sur $\R$ sans y être uniformément continue.

> **Théorème (Heine).** Toute fonction continue sur un segment y est uniformément continue.

## Pièges fréquents

- Appliquer le théorème des valeurs intermédiaires sur une réunion d'intervalles : $x \mapsto \frac{1}{x}$ est continue sur $\R^*$, prend les valeurs $-1$ et $1$, et ne s'annule pas.
- Appliquer le théorème des bornes atteintes hors d'un segment : $x \mapsto \frac{1}{x}$ est continue sur $]0, 1]$ et n'y est pas bornée ; $x \mapsto x$ est bornée sur $]0, 1[$ et n'y atteint pas ses bornes.
- Oublier que la bijection réciproque n'est continue que parce que $f$ est définie sur un **intervalle**.
