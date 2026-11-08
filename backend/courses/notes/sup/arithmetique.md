---
titre: Arithmétique dans ℤ
programmes: MPSI
ordre: 13
notion: divisibilite-pgcd
---

## Cadre et notations

Dans toute la fiche, les lettres $a, b, c, n, m$ désignent des entiers relatifs. On dit que $a$ **divise** $b$, noté $a \mid b$, s'il existe $k \in \Z$ tel que $b = ka$.

## Division euclidienne

> **Théorème.** Pour tous $a \in \Z$ et $b \in \N^*$, il existe un unique couple $(q, r) \in \Z^2$ tel que
>
> $$
> a = bq + r \qquad \text{et} \qquad 0 \leq r < b.
> $$

## PGCD et relation de Bézout

> **Définition.** Pour $(a, b) \neq (0, 0)$, le **PGCD** de $a$ et $b$, noté $a \wedge b$, est le plus grand entier naturel qui divise à la fois $a$ et $b$. On pose $0 \wedge 0 = 0$. Les entiers $a$ et $b$ sont **premiers entre eux** si $a \wedge b = 1$.

> **Proposition.** Pour tous $a, b \in \Z$ : $a\Z + b\Z = (a \wedge b)\Z$. Les diviseurs communs à $a$ et $b$ sont exactement les diviseurs de $a \wedge b$. Si $b \neq 0$ et si $r$ est le reste de la division de $a$ par $|b|$, alors $a \wedge b = b \wedge r$ : c'est l'**algorithme d'Euclide**.

> **Théorème (Bézout).**
>
> 1. Pour tous $a, b \in \Z$, il existe $u, v \in \Z$ tels que $au + bv = a \wedge b$.
> 2. Les entiers $a$ et $b$ sont premiers entre eux si et seulement s'il existe $u, v \in \Z$ tels que $au + bv = 1$.

> **Lemme de Gauss.** Si $a \mid bc$ et si $a \wedge b = 1$, alors $a \mid c$.

> **Proposition.** Si $a \mid n$, $b \mid n$ et $a \wedge b = 1$, alors $ab \mid n$.

Le **PPCM** de $a$ et $b$, noté $a \vee b$, est le plus petit entier naturel multiple commun de $a$ et $b$ ($0$ si $a$ ou $b$ est nul). Pour tous $a, b \in \N$ : $(a \wedge b)(a \vee b) = ab$.

## Nombres premiers

Un entier $p \geq 2$ est **premier** si ses seuls diviseurs positifs sont $1$ et $p$. Il y a une infinité de nombres premiers.

> **Proposition.** Si $p$ est premier et $p \mid ab$, alors $p \mid a$ ou $p \mid b$.

> **Théorème fondamental de l'arithmétique.** Tout entier $n \geq 2$ s'écrit de façon unique, à l'ordre des facteurs près, comme produit de nombres premiers :
>
> $$
> n = \prod_{p \text{ premier}} p^{v_p(n)},
> $$
>
> où les **valuations** $v_p(n) \in \N$ sont nulles sauf pour un nombre fini de $p$. Pour $a, b \geq 1$ : $a \mid b$ si et seulement si $v_p(a) \leq v_p(b)$ pour tout $p$ premier ; $v_p(a \wedge b) = \min\big( v_p(a), v_p(b) \big)$ et $v_p(a \vee b) = \max\big( v_p(a), v_p(b) \big)$.

## Congruences

Dans cette section, $n \in \N^*$. On note $a \equiv b \ [n]$ si $n \mid a - b$.

> **Proposition.** La congruence modulo $n$ est une relation d'équivalence, compatible avec l'addition et la multiplication : si $a \equiv b \ [n]$ et $c \equiv d \ [n]$, alors $a + c \equiv b + d \ [n]$ et $ac \equiv bd \ [n]$.

> **Proposition (inverse modulo $n$).** Il existe $u \in \Z$ tel que $au \equiv 1 \ [n]$ si et seulement si $a \wedge n = 1$. Un tel $u$ s'obtient par une relation de Bézout.

> **Petit théorème de Fermat.** Soit $p$ premier. Pour tout $a \in \Z$, $a^p \equiv a \ [p]$ ; si de plus $p \nmid a$, alors $a^{p-1} \equiv 1 \ [p]$.

## Pièges fréquents

- Déduire $a \mid b$ ou $a \mid c$ de $a \mid bc$ : c'est faux si $a$ n'est pas premier ($6 \mid 3 \times 4$).
- Simplifier une congruence par un entier non premier avec le module : $2 \times 3 \equiv 2 \times 1 \ [4]$, mais $3 \not\equiv 1 \ [4]$.
- Oublier que les coefficients $u$ et $v$ de Bézout ne sont pas uniques.
