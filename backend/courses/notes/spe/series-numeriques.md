---
titre: Séries numériques et familles sommables
programmes: MP, PSI
ordre: 1
notion: series-numeriques
---

## Cadre et notations

Dans toute la fiche, $(u_n)_{n \in \N}$ et $(v_n)_{n \in \N}$ sont des suites complexes. La **série** $\sum u_n$ est la suite de ses **sommes partielles** $S_n = \sum_{k=0}^{n} u_k$. Elle **converge** si $(S_n)$ a une limite finie $S$, appelée **somme** de la série et notée $\sum_{n=0}^{+\infty} u_n$ ; le **reste** d'ordre $n$ est alors $R_n = S - S_n = \sum_{k=n+1}^{+\infty} u_k$, et $R_n \to 0$. La **nature** d'une série est le fait qu'elle converge ou diverge.

## Premières propriétés

> **Proposition (divergence grossière).** Si $\sum u_n$ converge, alors $u_n \to 0$. La réciproque est fausse : $\sum_{n \geq 1} \frac{1}{n}$ diverge.

> **Proposition (lien suite-série).** La suite $(a_n)$ converge si et seulement si la série $\sum (a_{n+1} - a_n)$ converge.

> **Proposition (séries géométriques).** Pour $q \in \C$, la série $\sum q^n$ converge si et seulement si $|q| < 1$, et alors $\sum_{n=0}^{+\infty} q^n = \dfrac{1}{1 - q}$.

## Séries à termes positifs

Dans cette section, $u_n \geq 0$ et $v_n \geq 0$ pour tout $n$.

> **Proposition.** La série $\sum u_n$ converge si et seulement si la suite de ses sommes partielles est majorée.

> **Théorème (comparaison).**
>
> 1. Si $u_n \leq v_n$ à partir d'un certain rang : si $\sum v_n$ converge, alors $\sum u_n$ converge ; si $\sum u_n$ diverge, alors $\sum v_n$ diverge.
> 2. Si $u_n = O(v_n)$ (en particulier si $u_n = o(v_n)$) et si $\sum v_n$ converge, alors $\sum u_n$ converge.
> 3. Si $u_n \sim v_n$, alors $\sum u_n$ et $\sum v_n$ ont la même nature.

> **Proposition (séries de Riemann).** Pour $\alpha \in \R$, la série $\sum_{n \geq 1} \dfrac{1}{n^\alpha}$ converge si et seulement si $\alpha > 1$.

> **Théorème (comparaison série-intégrale).** Soit $f : [n_0, +\infty[ \, \to \R_+$ continue par morceaux et **décroissante**. Pour tout entier $n \geq n_0 + 1$ :
>
> $$
> \int_{n}^{n+1} f(t) \, dt \leq f(n) \leq \int_{n-1}^{n} f(t) \, dt.
> $$
>
> La série $\sum f(n)$ converge si et seulement si $x \mapsto \int_{n_0}^{x} f(t) \, dt$ est majorée sur $[n_0, +\infty[$, c'est-à-dire si et seulement si l'intégrale $\int_{n_0}^{+\infty} f$ converge.

## Convergence absolue

> **Théorème.** Si $\sum |u_n|$ converge, alors $\sum u_n$ converge, et $\left| \sum_{n=0}^{+\infty} u_n \right| \leq \sum_{n=0}^{+\infty} |u_n|$.

Une série convergente qui ne converge pas absolument est dite **semi-convergente**. Pour une série à termes de signe quelconque, le théorème de comparaison s'applique à $\sum |u_n|$ : si $u_n = O(v_n)$ avec $v_n \geq 0$ et $\sum v_n$ convergente, alors $\sum u_n$ converge absolument.

> **Règle de d'Alembert.** Si $u_n \neq 0$ à partir d'un certain rang et $\dfrac{|u_{n+1}|}{|u_n|} \to \ell \in [0, +\infty]$ :
>
> 1. si $\ell < 1$, la série $\sum u_n$ converge absolument ;
> 2. si $\ell > 1$, elle diverge grossièrement ;
> 3. si $\ell = 1$, on ne peut pas conclure : $\sum \frac{1}{n}$ diverge et $\sum \frac{1}{n^2}$ converge.

> **Théorème (séries alternées).** Soit $(a_n)$ une suite réelle **décroissante** de limite nulle. Alors la série $\sum (-1)^n a_n$ converge ; son reste $R_n = \sum_{k=n+1}^{+\infty} (-1)^k a_k$ vérifie $|R_n| \leq a_{n+1}$ et a le signe de $(-1)^{n+1}$.

## Sommation des relations de comparaison

> **Théorème.** Soit $(v_n)$ une suite **positive**.
>
> 1. Si $\sum v_n$ converge et si $u_n = o(v_n)$ (resp. $O(v_n)$), alors $\sum u_n$ converge et $\sum_{k=n+1}^{+\infty} u_k = o\left( \sum_{k=n+1}^{+\infty} v_k \right)$ (resp. $O$).
> 2. Si $\sum v_n$ diverge et si $u_n = o(v_n)$ (resp. $O(v_n)$), alors $\sum_{k=0}^{n} u_k = o\left( \sum_{k=0}^{n} v_k \right)$ (resp. $O$).
> 3. Si $u_n \sim v_n$ : en cas de convergence, les restes sont équivalents ; en cas de divergence, les sommes partielles sont équivalentes.

## Produit de Cauchy

> **Théorème.** Si $\sum a_n$ et $\sum b_n$ convergent **absolument**, alors, avec $c_n = \sum_{k=0}^{n} a_k b_{n-k}$, la série $\sum c_n$ converge absolument et
>
> $$
> \sum_{n=0}^{+\infty} c_n = \left( \sum_{n=0}^{+\infty} a_n \right) \left( \sum_{n=0}^{+\infty} b_n \right).
> $$

## Familles sommables

Dans cette section, $I$ est un ensemble **dénombrable** (en bijection avec $\N$).

> **Définition.**
>
> 1. Pour une famille $(u_i)_{i \in I}$ d'éléments de $[0, +\infty]$, sa somme est $\sum_{i \in I} u_i = \sup \left\{ \sum_{i \in J} u_i : J \subset I, \ J \text{ fini} \right\} \in [0, +\infty]$. La famille est **sommable** si cette somme est finie.
> 2. Une famille $(u_i)_{i \in I}$ de nombres complexes est **sommable** si la famille $(|u_i|)_{i \in I}$ l'est.

Pour $I = \N$, la famille $(u_n)$ est sommable si et seulement si la série $\sum u_n$ converge absolument, et les deux sommes coïncident. La somme d'une famille sommable ne dépend pas de l'ordre de ses termes.

> **Théorème (sommation par paquets).** Soit $(I_k)_{k \in K}$ une partition de $I$ en parties ($K$ fini ou dénombrable).
>
> 1. Pour une famille d'éléments de $[0, +\infty]$, on a toujours, dans $[0, +\infty]$ : $\sum_{i \in I} u_i = \sum_{k \in K} \left( \sum_{i \in I_k} u_i \right)$.
> 2. Pour une famille complexe **sommable**, chaque sous-famille $(u_i)_{i \in I_k}$ est sommable, la famille des sommes est sommable, et la même égalité a lieu.

> **Théorème (Fubini pour les séries doubles).** Soit $(u_{m,n})_{(m,n) \in \N^2}$ une famille complexe. Si $\sum_{m=0}^{+\infty} \left( \sum_{n=0}^{+\infty} |u_{m,n}| \right) < +\infty$, la famille est sommable et
>
> $$
> \sum_{m=0}^{+\infty} \sum_{n=0}^{+\infty} u_{m,n} = \sum_{n=0}^{+\infty} \sum_{m=0}^{+\infty} u_{m,n}.
> $$
>
> Pour une famille d'éléments de $[0, +\infty]$, l'interversion est toujours permise, sans hypothèse.

## Pièges fréquents

- Conclure à la convergence de $\sum u_n$ parce que $u_n \to 0$.
- Utiliser les équivalents pour une série dont le terme général n'est pas de signe constant : $u_n = \frac{(-1)^n}{\sqrt{n}}$ et $v_n = \frac{(-1)^n}{\sqrt{n}} + \frac{1}{n}$ sont équivalents, $\sum u_n$ converge et $\sum v_n$ diverge.
- Appliquer le critère des séries alternées sans vérifier que $(a_n)$ est décroissante.
- Intervertir deux sommes sans avoir vérifié la sommabilité (ou la positivité).
