---
titre: Une limite uniforme de fonctions continues est continue
programmes: MP, MPI, L2
statut: au-programme
ordre: 6
notion: suites-series-fonctions
---

## Énoncé

> **Théorème.** Soient $A$ une partie d'un espace vectoriel normé $E$, $a \in A$, et $(f_n)$ une suite de fonctions de $A$ dans $\K$ qui converge **uniformément** sur $A$ vers $f$. Si chaque $f_n$ est continue en $a$, alors $f$ est continue en $a$. En particulier, toute limite uniforme sur $A$ de fonctions continues sur $A$ est continue sur $A$.

La convergence uniforme signifie : $\sup_{x \in A} |f_n(x) - f(x)| \to 0$.

## Idée

On passe de $f(x)$ à $f(a)$ en faisant un détour par $f_N$ : $f(x) - f(a) = \big( f(x) - f_N(x) \big) + \big( f_N(x) - f_N(a) \big) + \big( f_N(a) - f(a) \big)$. La convergence uniforme contrôle le premier et le dernier terme **sans dépendre de $x$**, la continuité de $f_N$ contrôle celui du milieu. C'est l'argument « en $\varepsilon / 3$ ».

## Démonstration

Soit $\varepsilon > 0$.

**Choix de $N$.** Par convergence uniforme, il existe $N \in \N$ tel que $|f_N(y) - f(y)| \leq \frac{\varepsilon}{3}$ pour **tout** $y \in A$. On fixe cet entier $N$.

**Choix de $\delta$.** La fonction $f_N$ est continue en $a$ : il existe $\delta > 0$ tel que, pour tout $x \in A$ vérifiant $\|x - a\| \leq \delta$, on ait $|f_N(x) - f_N(a)| \leq \frac{\varepsilon}{3}$.

**Conclusion.** Pour tout $x \in A$ tel que $\|x - a\| \leq \delta$ :

$$
\lvert f(x) - f(a) \rvert \leq |f(x) - f_N(x)| + |f_N(x) - f_N(a)| + |f_N(a) - f(a)| \leq \frac{\varepsilon}{3} + \frac{\varepsilon}{3} + \frac{\varepsilon}{3} = \varepsilon.
$$

Donc $f$ est continue en $a$.

Le premier terme est majoré **parce que** l'entier $N$ convient pour tous les points de $A$ à la fois, y compris pour $x$, qui n'est choisi qu'après $N$. Avec une convergence seulement simple, l'entier dépendrait de $x$, et l'argument tomberait.

## Remarques

- **La convergence simple ne suffit pas.** Les fonctions $f_n : x \mapsto x^n$ sont continues sur $[0, 1]$ et convergent simplement vers la fonction nulle sur $[0, 1[$, égale à $1$ en $1$ : la limite n'est pas continue. Par contraposée, la convergence n'est pas uniforme sur $[0, 1]$.
- **Version locale.** La continuité est une propriété locale : il suffit que la convergence soit uniforme sur un voisinage de chaque point, par exemple sur tout segment inclus dans un intervalle $I$, pour que la limite soit continue sur $I$. C'est ainsi qu'on montre la continuité de $\zeta : s \mapsto \sum_{n \geq 1} n^{-s}$ sur $]1, +\infty[$, avec une convergence normale sur chaque $[a, +\infty[$, $a > 1$, mais pas sur $]1, +\infty[$ tout entier.
- Le même argument donne le théorème pour des fonctions à valeurs dans un espace vectoriel normé de dimension finie.
