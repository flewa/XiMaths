---
titre: Arithmétique dans ℤ
programmes: MPSI, MP2I
ordre: 9
notion: divisibilite-pgcd
---

## Cadre et notations

Dans toute la fiche, les lettres $a, b, c, n, m$ désignent des entiers relatifs. On dit que $a$ **divise** $b$, noté $a \mid b$, s'il existe $k \in \Z$ tel que $b = ka$. On a $a \mid b$ et $b \mid a$ si et seulement si $a = \pm b$ ($a$ et $b$ sont **associés**).

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

> **Proposition.**
>
> 1. Si $a \mid n$, $b \mid n$ et $a \wedge b = 1$, alors $ab \mid n$.
> 2. Si $a \wedge n = 1$ et $b \wedge n = 1$, alors $ab \wedge n = 1$.
> 3. Pour $k \in \N^*$, $(ka) \wedge (kb) = k (a \wedge b)$.

Un couple de Bézout s'obtient par l'**algorithme d'Euclide étendu**, en remontant les divisions successives. Tout rationnel s'écrit de façon unique $\frac{p}{q}$ avec $p \in \Z$, $q \in \N^*$ et $p \wedge q = 1$ : c'est sa **forme irréductible**.

**Plusieurs entiers.** Le PGCD de $a_1, \dots, a_r$ est le plus grand diviseur commun positif (s'ils ne sont pas tous nuls), et il existe $u_1, \dots, u_r \in \Z$ tels que $a_1 u_1 + \dots + a_r u_r = a_1 \wedge \dots \wedge a_r$. Les $a_i$ sont **premiers entre eux dans leur ensemble** si ce PGCD vaut $1$, et **deux à deux premiers entre eux** si $a_i \wedge a_j = 1$ pour tous $i \neq j$. La seconde condition est plus forte : $6$, $10$ et $15$ sont premiers entre eux dans leur ensemble, mais pas deux à deux.

Le **PPCM** de $a$ et $b$, noté $a \vee b$, est le plus petit entier naturel multiple commun de $a$ et $b$ ($0$ si $a$ ou $b$ est nul). Pour tous $a, b \in \N$ : $(a \wedge b)(a \vee b) = ab$.

## Nombres premiers

Un entier $p \geq 2$ est **premier** si ses seuls diviseurs positifs sont $1$ et $p$. Il y a une infinité de nombres premiers. Le **crible d'Ératosthène** donne les nombres premiers jusqu'à $N$ : on barre les multiples stricts de chaque entier non barré, jusqu'à $\sqrt{N}$.

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
