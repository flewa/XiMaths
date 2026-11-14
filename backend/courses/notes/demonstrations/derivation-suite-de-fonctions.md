---
titre: Dérivation de la limite d'une suite de fonctions
programmes: MP, MPI, L2
statut: au-programme
ordre: 7
notion: suites-series-fonctions
---

## Énoncé

> **Théorème.** Soient $I$ un intervalle de $\R$ et $(u_n)$ une suite de fonctions de classe $\mathcal{C}^1$ sur $I$, à valeurs dans $\K$. On suppose que :
>
> 1. $(u_n)$ converge **simplement** sur $I$ vers une fonction $u$ ;
> 2. $(u_n')$ converge **uniformément sur tout segment** de $I$ vers une fonction $v$.
>
> Alors $u$ est de classe $\mathcal{C}^1$ sur $I$, $u' = v$, et $(u_n)$ converge vers $u$ uniformément sur tout segment de $I$.

## Idée

On écrit chaque $u_n$ comme intégrale de sa dérivée, $u_n(x) = u_n(a) + \int_a^x u_n'$, et on passe à la limite : la convergence uniforme permet d'échanger limite et intégrale sur un segment. On obtient $u(x) = u(a) + \int_a^x v$, et le théorème fondamental de l'analyse conclut.

## Démonstration

Fixons $a \in I$.

**Étape 1 : $v$ est continue sur $I$.** Tout point $x_0$ de $I$ appartient à un segment $S \subset I$ qui est un voisinage de $x_0$ dans $I$. Sur $S$, les fonctions continues $u_n'$ convergent uniformément vers $v$, donc $v$ est continue sur $S$, en particulier en $x_0$ (théorème de continuité d'une limite uniforme).

**Étape 2 : passage à la limite dans l'intégrale.** Pour $x \in I$, notons $S_x$ le segment d'extrémités $a$ et $x$, inclus dans $I$ car $I$ est un intervalle. Comme $u_n$ est de classe $\mathcal{C}^1$, $u_n(x) = u_n(a) + \int_a^x u_n'(t) \, dt$. De plus

$$
\left| \int_a^x u_n'(t) \, dt - \int_a^x v(t) \, dt \right| \leq |x - a| \, \sup_{t \in S_x} |u_n'(t) - v(t)| \xrightarrow[n \to +\infty]{} 0,
$$

par convergence uniforme de $(u_n')$ sur le segment $S_x$. En faisant tendre $n$ vers $+\infty$ et en utilisant la convergence simple de $(u_n)$ en $x$ et en $a$ :

$$
u(x) = u(a) + \int_a^x v(t) \, dt \qquad \text{pour tout } x \in I.
$$

**Étape 3 : régularité.** Comme $v$ est continue sur l'intervalle $I$, la fonction $x \mapsto \int_a^x v(t) \, dt$ est de classe $\mathcal{C}^1$, de dérivée $v$ (théorème fondamental de l'analyse). Donc $u$ est de classe $\mathcal{C}^1$ et $u' = v$.

**Étape 4 : convergence uniforme sur les segments.** Soit $[c, d]$ un segment de $I$, et $S = [\min(a, c), \max(a, d)]$, segment de $I$ qui contient $a$ et $[c, d]$. Pour $x \in [c, d]$, en soustrayant les formules intégrales de $u_n$ et de $u$ :

$$
\lvert u_n(x) - u(x) \rvert \leq |u_n(a) - u(a)| + \left| \int_a^x (u_n' - v) \right| \leq |u_n(a) - u(a)| + \ell(S) \sup_{S} |u_n' - v|,
$$

où $\ell(S)$ est la longueur de $S$. Le majorant ne dépend pas de $x$ et tend vers $0$ : la convergence est uniforme sur $[c, d]$.

## Remarques

- **L'hypothèse porte sur les dérivées.** La convergence uniforme de $(u_n)$ ne suffit pas : $u_n(x) = \frac{\sin(nx)}{\sqrt{n}}$ converge uniformément vers $0$ sur $\R$, mais $u_n'(x) = \sqrt{n} \cos(nx)$ ne converge même pas simplement (en $x = 0$, elle tend vers $+\infty$).
- On peut affaiblir l'hypothèse 1 : il suffit que $(u_n(a))$ converge pour **un** point $a$ de $I$. La formule $u_n(x) = u_n(a) + \int_a^x u_n'$ donne alors la convergence simple partout.
- **Pour les séries de fonctions**, on applique le théorème aux sommes partielles : si $\sum u_n$ converge simplement et si $\sum u_n'$ converge uniformément sur tout segment, la somme est de classe $\mathcal{C}^1$ et se dérive terme à terme.
