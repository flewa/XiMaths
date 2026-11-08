---
titre: Nombres réels et suites numériques
programmes: MPSI, PCSI
ordre: 2
notion: suites-numeriques
---

## Cadre et notations

Sauf mention contraire, les suites sont réelles : $u = (u_n)_{n \in \N} \in \R^{\N}$. Une propriété est vraie **à partir d'un certain rang** s'il existe $N \in \N$ tel qu'elle soit vraie pour tout $n \geq N$.

## Borne supérieure

> **Définition.** Soit $A$ une partie de $\R$. Un réel $M$ **majore** $A$ si $a \leq M$ pour tout $a \in A$. La **borne supérieure** de $A$, notée $\sup A$, est, si elle existe, le plus petit des majorants de $A$.

> **Théorème (propriété de la borne supérieure).** Toute partie non vide et majorée de $\R$ admet une borne supérieure.

> **Proposition (caractérisation).** Soient $A$ une partie non vide de $\R$ et $M \in \R$. Les assertions suivantes sont équivalentes :
>
> 1. $M = \sup A$ ;
> 2. $M$ majore $A$ et, pour tout $\varepsilon > 0$, il existe $a \in A$ tel que $a > M - \varepsilon$ ;
> 3. $M$ majore $A$ et il existe une suite d'éléments de $A$ qui converge vers $M$.

On définit de même la borne inférieure $\inf A$, plus grand des minorants. Une borne supérieure n'est pas forcément un plus grand élément : $\sup \, ]0, 1[ \, = 1 \notin \, ]0, 1[$.

**Partie entière.** Pour tout $x \in \R$, il existe un unique $n \in \Z$ tel que $n \leq x < n + 1$ ; on le note $\lfloor x \rfloor$.

**Densité.** Tout intervalle $]a, b[$ avec $a < b$ contient au moins un rationnel et au moins un irrationnel.

## Convergence

> **Définition.** La suite $u$ **converge** vers $\ell \in \R$ si
>
> $$
> \forall \varepsilon > 0, \ \exists N \in \N, \ \forall n \geq N, \ |u_n - \ell| \leq \varepsilon.
> $$
>
> Le réel $\ell$ est alors unique : c'est la limite de $u$. La suite $u$ **tend vers $+\infty$** si $\forall A \in \R, \ \exists N \in \N, \ \forall n \geq N, \ u_n \geq A$.

> **Proposition.** Toute suite convergente est bornée. La réciproque est fausse : $\big( (-1)^n \big)$ est bornée et diverge.

> **Proposition (passage à la limite dans les inégalités).** Si $u_n \leq v_n$ à partir d'un certain rang et si $u$ et $v$ convergent vers $\ell$ et $\ell'$, alors $\ell \leq \ell'$.

Les inégalités strictes deviennent larges : $\frac{1}{n+1} > 0$ pour tout $n$, mais la limite est $0$.

> **Théorème (encadrement).** Si $v_n \leq u_n \leq w_n$ à partir d'un certain rang et si $v$ et $w$ convergent vers le même réel $\ell$, alors $u$ converge vers $\ell$. Si $u_n \geq v_n$ à partir d'un certain rang et si $v$ tend vers $+\infty$, alors $u$ tend vers $+\infty$.

## Suites monotones

> **Théorème (limite monotone).** Soit $u$ une suite croissante.
>
> 1. Si $u$ est majorée, elle converge vers $\sup \{ u_n : n \in \N \}$.
> 2. Sinon, elle tend vers $+\infty$.

> **Théorème (suites adjacentes).** Si $u$ est croissante, $v$ décroissante et $v_n - u_n \to 0$, alors $u$ et $v$ convergent vers une même limite $\ell$, et $u_n \leq \ell \leq v_n$ pour tout $n \in \N$.

## Suites extraites

Une **suite extraite** de $u$ est une suite $(u_{\varphi(n)})_{n \in \N}$, où $\varphi : \N \to \N$ est strictement croissante.

> **Proposition.**
>
> 1. Si $u$ converge vers $\ell$, toute suite extraite de $u$ converge vers $\ell$.
> 2. Si $(u_{2n})$ et $(u_{2n+1})$ convergent vers le même réel $\ell$, alors $u$ converge vers $\ell$.

Pour montrer qu'une suite diverge, il suffit d'exhiber deux suites extraites de limites différentes.

> **Théorème (Bolzano-Weierstrass).** Toute suite réelle bornée admet une suite extraite convergente. Il en va de même pour toute suite complexe bornée.

## Suites usuelles

**Suites géométriques.** Pour $q \in \R$ : si $|q| < 1$, $q^n \to 0$ ; si $q = 1$, la suite est constante ; si $q > 1$, $q^n \to +\infty$ ; si $q \leq -1$, $(q^n)$ n'a pas de limite.

**Suites arithmético-géométriques.** Si $u_{n+1} = a u_n + b$ pour tout $n$, avec $a \neq 1$, on pose $\ell = \frac{b}{1 - a}$ ; alors $u_n - \ell = a^n (u_0 - \ell)$ pour tout $n \in \N$.

> **Proposition (récurrences linéaires d'ordre 2).** Soient $a, b \in \C$ avec $b \neq 0$, et $u \in \C^{\N}$ telle que $u_{n+2} = a u_{n+1} + b u_n$ pour tout $n \in \N$. On note $r^2 = a r + b$ l'équation caractéristique.
>
> 1. Si elle a deux racines distinctes $r_1$ et $r_2$, il existe $\lambda, \mu \in \C$ tels que $u_n = \lambda r_1^n + \mu r_2^n$ pour tout $n$.
> 2. Si elle a une racine double $r$, il existe $\lambda, \mu \in \C$ tels que $u_n = (\lambda + \mu n) r^n$ pour tout $n$.
>
> Si $a$, $b$ et $u$ sont réels et si les racines sont $\rho e^{\pm i\theta}$ avec $\rho > 0$ et $\theta \in \, ]0, \pi[$, il existe $\lambda, \mu \in \R$ tels que $u_n = \rho^n \big( \lambda \cos(n\theta) + \mu \sin(n\theta) \big)$.

## Suites définies par $u_{n+1} = f(u_n)$

Soient $I$ un intervalle, $f : I \to \R$ telle que $f(I) \subset I$, et $u_0 \in I$. La suite définie par $u_{n+1} = f(u_n)$ est alors bien définie, à valeurs dans $I$.

> **Proposition.** Si $u$ converge vers un réel $\ell \in I$ et si $f$ est continue en $\ell$, alors $f(\ell) = \ell$.

- Si $f$ est croissante sur $I$, la suite $u$ est monotone : croissante si $u_1 \geq u_0$, décroissante si $u_1 \leq u_0$.
- Si $f$ est décroissante sur $I$, les suites $(u_{2n})$ et $(u_{2n+1})$ sont monotones, de sens contraires.

## Suites complexes

Une suite complexe $u$ converge vers $\ell \in \C$ si $|u_n - \ell| \to 0$ ; c'est le cas si et seulement si $(\operatorname{Re} u_n)$ et $(\operatorname{Im} u_n)$ convergent vers $\operatorname{Re} \ell$ et $\operatorname{Im} \ell$. Pour $q \in \C$ : si $|q| < 1$, $q^n \to 0$ ; si $|q| \geq 1$ et $q \neq 1$, la suite $(q^n)$ diverge.

## Pièges fréquents

- Écrire $\lim u_n$ avant d'avoir prouvé que la limite existe.
- Conclure $f(\ell) = \ell$ sans vérifier que $\ell \in I$ et que $f$ est continue en $\ell$.
- Croire qu'une suite croissante converge : il faut qu'elle soit majorée.
- Garder une inégalité stricte après un passage à la limite.
