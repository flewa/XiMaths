---
titre: Séries numériques et familles sommables
programmes: MPSI, MP2I
ordre: 20
notion: series-numeriques
---

## Cadre et notations

Dans toute la fiche, $(u_n)_{n \in \N}$ et $(v_n)_{n \in \N}$ sont des suites réelles ou complexes. La **série** $\sum u_n$ est la suite de ses **sommes partielles** $S_n = \sum_{k=0}^{n} u_k$. Elle **converge** si $(S_n)$ a une limite finie, sa **somme** $\sum_{n=0}^{+\infty} u_n$ ; sinon elle **diverge**. Si elle converge, son **reste** d'ordre $n$ est $R_n = \sum_{k=n+1}^{+\infty} u_k$, et $R_n \to 0$.

## Premières propriétés

> **Proposition.**
>
> 1. Si $\sum u_n$ et $\sum v_n$ convergent, $\sum (\lambda u_n + \mu v_n)$ converge et sa somme est $\lambda \sum u_n + \mu \sum v_n$.
> 2. Si $\sum u_n$ converge, alors $u_n \to 0$. Si $(u_n)$ ne tend pas vers $0$, la série **diverge grossièrement**.
> 3. **Lien suite-série :** la suite $(u_n)$ et la série télescopique $\sum (u_{n+1} - u_n)$ sont de même nature.

> **Proposition (séries géométriques et exponentielle).** Pour $z \in \C$, la série $\sum z^n$ converge si et seulement si $|z| < 1$, et alors $\sum_{n=0}^{+\infty} z^n = \dfrac{1}{1 - z}$. Pour tout $z \in \C$, $e^z = \sum_{n=0}^{+\infty} \dfrac{z^n}{n!}$.

La réciproque du point 2 est fausse : $\frac{1}{n} \to 0$ mais $\sum \frac{1}{n}$ diverge.

## Séries à termes positifs

Dans cette section, $u_n \geq 0$ et $v_n \geq 0$ pour tout $n$.

> **Théorème.**
>
> 1. $\sum u_n$ converge si et seulement si $(S_n)$ est majorée.
> 2. **Comparaison :** si $u_n \leq v_n$ pour tout $n$ et si $\sum v_n$ converge, alors $\sum u_n$ converge ; si $\sum u_n$ diverge, $\sum v_n$ diverge.
> 3. **Équivalents :** si $u_n \sim v_n$, les séries $\sum u_n$ et $\sum v_n$ sont de même nature.

> **Comparaison série-intégrale.** Si $f : [0, +\infty[ \, \to \R_+$ est continue par morceaux et décroissante, alors pour tout $k \geq 1$,
>
> $$
> \int_{k}^{k+1} f(t) \, dt \leq f(k) \leq \int_{k-1}^{k} f(t) \, dt,
> $$
>
> ce qui encadre les sommes partielles de $\sum f(n)$ par des intégrales (méthode des rectangles).

> **Théorème (séries de Riemann).** Pour $\alpha \in \R$, la série $\sum_{n \geq 1} \dfrac{1}{n^\alpha}$ converge si et seulement si $\alpha > 1$.

Exemple : $\sum_{k=1}^{n} \frac{1}{k} = \ln n + O(1)$, donc $\sum_{k=1}^{n} \frac{1}{k} \sim \ln n$.

## Convergence absolue et séries alternées

La série $\sum u_n$ est **absolument convergente** si $\sum |u_n|$ converge.

> **Théorème.**
>
> 1. Une série absolument convergente est convergente, et $\left| \sum_{n=0}^{+\infty} u_n \right| \leq \sum_{n=0}^{+\infty} |u_n|$.
> 2. Si $v_n \geq 0$, si $u_n = O(v_n)$ et si $\sum v_n$ converge, alors $\sum u_n$ est absolument convergente, donc convergente.

> **Théorème (séries alternées).** Si $(a_n)$ est une suite réelle qui **décroît vers $0$**, la série $\sum (-1)^n a_n$ converge. Son reste $R_n$ est du signe de son premier terme $(-1)^{n+1} a_{n+1}$, et $|R_n| \leq a_{n+1}$.

Exemple : $\sum \frac{(-1)^n}{n+1}$ converge sans converger absolument.

## Familles sommables de réels positifs

On calcule dans $[0, +\infty]$ avec les conventions $x + (+\infty) = +\infty$ et $x \leq +\infty$. Soit $I$ un ensemble et $(u_i)_{i \in I}$ une famille d'éléments de $[0, +\infty]$. Sa **somme** est

$$
\sum_{i \in I} u_i = \sup \left\{ \sum_{i \in F} u_i : F \subset I, \ F \text{ fini} \right\} \in [0, +\infty].
$$

Pour $I = \N$, c'est la somme de la série si elle converge, et $+\infty$ sinon. La famille est **sommable** si cette somme est finie.

> **Théorème.** Pour des familles d'éléments de $[0, +\infty]$ :
>
> 1. la somme ne dépend pas de l'ordre des termes : $\sum_{i \in I} u_{\sigma(i)} = \sum_{i \in I} u_i$ pour toute bijection $\sigma$ de $I$ ;
> 2. $\sum (u_i + v_i) = \sum u_i + \sum v_i$ et $\sum \lambda u_i = \lambda \sum u_i$ pour $\lambda \in \R_+$ ;
> 3. **sommation par paquets :** si $I$ est la réunion disjointe des $I_j$, $j \in J$, alors $\sum_{i \in I} u_i = \sum_{j \in J} \left( \sum_{i \in I_j} u_i \right)$ ;
> 4. **Fubini positif :** $\sum_{(m, n) \in A \times B} u_{m,n} = \sum_{m \in A} \sum_{n \in B} u_{m,n} = \sum_{n \in B} \sum_{m \in A} u_{m,n}$.

Ces égalités ont lieu dans $[0, +\infty]$, sans hypothèse : on les utilise pour **démontrer** la sommabilité.

## Familles sommables de complexes

Une famille $(u_i)_{i \in I}$ de complexes est **sommable** si $\sum_{i \in I} |u_i| < +\infty$ ; on note $\ell^1(I)$ l'ensemble de ces familles. Pour $I = \N$, c'est la convergence absolue de la série.

> **Théorème.** Soient $(u_i)$ et $(v_i)$ des familles de complexes indexées par $I$.
>
> 1. Si $|u_i| \leq w_i$ pour tout $i$, avec $(w_i)$ sommable, alors $(u_i)$ est sommable ; une sous-famille d'une famille sommable est sommable.
> 2. La somme d'une famille sommable est invariante par permutation, et la somme est linéaire sur $\ell^1(I)$.
> 3. Pour tout $\varepsilon > 0$, il existe une partie finie $F$ de $I$ telle que $\left| \sum_{i \in I} u_i - \sum_{i \in F} u_i \right| \leq \varepsilon$.
> 4. **Sommation par paquets et Fubini :** si $(u_i)$ est sommable, les égalités des points 3 et 4 de la section précédente restent vraies.
> 5. Si $(a_i)_{i \in I}$ et $(b_j)_{j \in J}$ sont sommables, $(a_i b_j)_{(i, j) \in I \times J}$ l'est et $\sum_{(i, j)} a_i b_j = \left( \sum_{i} a_i \right) \left( \sum_{j} b_j \right)$.

> **Produit de Cauchy.** Si $\sum a_n$ et $\sum b_n$ convergent absolument, la série de terme général $c_n = \sum_{k=0}^{n} a_k b_{n-k}$ converge absolument et
>
> $$
> \sum_{n=0}^{+\infty} c_n = \left( \sum_{n=0}^{+\infty} a_n \right) \left( \sum_{n=0}^{+\infty} b_n \right).
> $$

On en déduit $e^{z + w} = e^z e^w$ pour tous $z, w \in \C$.

## Pièges fréquents

- Conclure à la convergence de $\sum u_n$ parce que $u_n \to 0$.
- Utiliser les équivalents ou la comparaison pour des séries qui ne sont pas de signe constant : $\frac{(-1)^n}{\sqrt{n}} \sim \frac{(-1)^n}{\sqrt{n}} + \frac{1}{n}$, et la première série converge alors que la seconde diverge.
- Regrouper ou réordonner les termes d'une série qui ne converge pas absolument.
- Appliquer Fubini à une famille de signe quelconque sans avoir prouvé qu'elle est sommable.
