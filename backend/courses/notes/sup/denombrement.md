---
titre: Dénombrement
programmes: MPSI, MP2I
ordre: 17
notion: denombrement
---

## Cadre et notations

Dans toute la fiche, $E$ et $F$ sont des ensembles finis, et $|E|$ (ou $\operatorname{Card} E$) désigne le nombre d'éléments de $E$. Pour $n \in \N$, $[\![1, n]\!]$ a $n$ éléments.

## Cardinaux

> **Proposition.**
>
> 1. Si $A \subset E$, alors $|A| \leq |E|$, avec égalité si et seulement si $A = E$.
> 2. Si $|E| = |F|$, une application $f : E \to F$ est bijective si et seulement si elle est injective, si et seulement si elle est surjective.

> **Proposition (opérations).** Pour des parties $A$ et $B$ d'un ensemble fini :
>
> $$
> |A \cup B| = |A| + |B| - |A \cap B|, \qquad |A \setminus B| = |A| - |A \cap B|, \qquad |\overline{A}| = |E| - |A| \ \ (A \subset E),
> $$
>
> et $|A \cup B| = |A| + |B|$ si $A$ et $B$ sont disjoints. De plus $|E \times F| = |E| \, |F|$, l'ensemble $F^E$ des applications de $E$ dans $F$ a $|F|^{|E|}$ éléments, et l'ensemble $\mathcal{P}(E)$ des parties de $E$ en a $2^{|E|}$.

Plus généralement, le cardinal d'une réunion de parties deux à deux disjointes est la somme de leurs cardinaux. La formule du crible, pour une réunion quelconque de plus de deux parties, n'est pas au programme.

## Listes et combinaisons

Soient $n = |E|$ et $p \in \N$.

> **Théorème.**
>
> 1. Le nombre de **$p$-listes** (ou $p$-uplets) d'éléments de $E$ est $n^p$.
> 2. Le nombre de $p$-listes d'éléments **distincts** de $E$, c'est-à-dire d'applications injectives de $[\![1, p]\!]$ dans $E$, est
>
> $$
> n (n - 1) \cdots (n - p + 1) = \frac{n!}{(n - p)!} \quad \text{si } p \leq n, \qquad 0 \quad \text{si } p > n.
> $$
>
> 3. Le nombre de **permutations** de $E$ (bijections de $E$ sur $E$) est $n!$.
> 4. Le nombre de **parties à $p$ éléments** (ou $p$-combinaisons) de $E$ est $\dbinom{n}{p}$.

**Démonstrations combinatoires.** On retrouve $\sum_{p=0}^{n} \binom{n}{p} = 2^n$ en comptant les parties de $E$ selon leur nombre d'éléments. La **formule de Pascal** $\binom{n}{p} = \binom{n-1}{p-1} + \binom{n-1}{p}$ s'obtient en fixant $a \in E$ et en séparant les parties à $p$ éléments qui contiennent $a$ de celles qui ne le contiennent pas. La formule du binôme s'obtient en développant $(a + b)^n$ : le coefficient de $a^k b^{n-k}$ est le nombre de façons de choisir les $k$ facteurs qui donnent $a$.

**Choisir le bon modèle.** Ordre compté et répétitions permises : $p$-listes, $n^p$. Ordre compté sans répétition : $p$-listes d'éléments distincts. Ordre indifférent sans répétition : parties, $\binom{n}{p}$.

Exemples : le nombre de mots de $5$ lettres sur un alphabet de $26$ lettres est $26^5$ ; le nombre de podiums (or, argent, bronze) parmi $10$ coureurs est $10 \times 9 \times 8 = 720$ ; le nombre de mains de $5$ cartes dans un jeu de $32$ est $\binom{32}{5} = 201\,376$.

## Pièges fréquents

- Compter des listes quand l'ordre est indifférent : on compte alors chaque partie $p!$ fois.
- Oublier les répétitions ou les compter deux fois : un tirage successif avec remise donne des $p$-listes, sans remise des $p$-listes d'éléments distincts.
- Ajouter les cardinaux de deux parties qui ne sont pas disjointes.
