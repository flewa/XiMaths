---
titre: Théorème d'approximation de Weierstrass
programmes: MP, MPI, L2
statut: preuve-hors-programme
ordre: 8
notion: suites-series-fonctions
---

## Énoncé

> **Théorème (Weierstrass).** Toute fonction continue sur un segment $[a, b]$, à valeurs dans $\K$, est limite uniforme sur $[a, b]$ d'une suite de fonctions polynomiales à coefficients dans $\K$.

Au programme de MP, la démonstration n'est pas exigible. On donne ici la preuve de Bernstein, qui fournit des polynômes explicites.

## Idée

Sur $[0, 1]$, on approche $f$ par le **polynôme de Bernstein**

$$
B_n(f)(x) = \sum_{k=0}^{n} f\left( \frac{k}{n} \right) \binom{n}{k} x^k (1 - x)^{n-k},
$$

qui est l'espérance de $f(S_n / n)$ quand $S_n$ suit la loi binomiale $\mathcal{B}(n, x)$. Comme $S_n / n$ se concentre autour de $x$ (sa variance est $\frac{x(1-x)}{n}$), cette espérance est proche de $f(x)$.

## Démonstration

**Réduction à $[0, 1]$.** Si $f$ est continue sur $[a, b]$, la fonction $g : t \mapsto f\big( a + t(b - a) \big)$ est continue sur $[0, 1]$. Si des polynômes $Q_n$ convergent uniformément vers $g$ sur $[0, 1]$, les fonctions $x \mapsto Q_n\left( \frac{x - a}{b - a} \right)$ sont polynomiales et convergent uniformément vers $f$ sur $[a, b]$. On suppose donc $[a, b] = [0, 1]$.

**Étape 1 : trois identités.** Notons $p_{n,k}(x) = \binom{n}{k} x^k (1 - x)^{n-k}$. Pour $x \in [0, 1]$ :

$$
\sum_{k=0}^{n} p_{n,k}(x) = 1, \qquad \sum_{k=0}^{n} k \, p_{n,k}(x) = nx, \qquad \sum_{k=0}^{n} (k - nx)^2 p_{n,k}(x) = n x (1 - x).
$$

La première est la formule du binôme pour $\big( x + (1 - x) \big)^n$. Les deux autres disent qu'une variable $S_n$ de loi $\mathcal{B}(n, x)$ a pour espérance $nx$ et pour variance $nx(1 - x)$. On peut aussi les vérifier sans probabilités, avec $k \binom{n}{k} = n \binom{n-1}{k-1}$ et $k(k-1) \binom{n}{k} = n(n-1) \binom{n-2}{k-2}$, qui donnent $\sum k \, p_{n,k}(x) = nx$ et $\sum k(k-1) p_{n,k}(x) = n(n-1)x^2$. On en tire $\sum (k - nx)^2 p_{n,k}(x) = n(n-1)x^2 + nx - 2nx \cdot nx + n^2 x^2 = nx(1 - x)$.

**Étape 2 : l'estimation.** Soit $\varepsilon > 0$. La fonction $f$ est continue sur le segment $[0, 1]$, donc bornée par un réel $M$ et uniformément continue (théorème de Heine) : il existe $\delta > 0$ tel que $|s - t| \leq \delta$ entraîne $|f(s) - f(t)| \leq \varepsilon$. Pour $x \in [0, 1]$, la première identité donne

$$
\lvert B_n(f)(x) - f(x) \rvert = \left| \sum_{k=0}^{n} \left( f\left( \tfrac{k}{n} \right) - f(x) \right) p_{n,k}(x) \right| \leq \sum_{k=0}^{n} \left| f\left( \tfrac{k}{n} \right) - f(x) \right| p_{n,k}(x).
$$

On coupe la somme en deux :

- pour les $k$ tels que $\left| \frac{k}{n} - x \right| \leq \delta$, chaque terme est au plus $\varepsilon \, p_{n,k}(x)$, et leur somme au plus $\varepsilon$ ;
- pour les autres, $\left| f\left( \frac{k}{n} \right) - f(x) \right| \leq 2M$ et $1 < \dfrac{(k - nx)^2}{n^2 \delta^2}$, donc, par la troisième identité, leur somme est au plus

$$
2M \sum_{k=0}^{n} \frac{(k - nx)^2}{n^2 \delta^2} \, p_{n,k}(x) = \frac{2M \, x(1 - x)}{n \delta^2} \leq \frac{M}{2 n \delta^2}.
$$

Ainsi $\sup_{x \in [0, 1]} |B_n(f)(x) - f(x)| \leq \varepsilon + \dfrac{M}{2n\delta^2}$, qui est inférieur à $2\varepsilon$ dès que $n \geq \dfrac{M}{2\varepsilon\delta^2}$. Les polynômes $B_n(f)$ convergent donc uniformément vers $f$ sur $[0, 1]$.

## Remarques

- Le point clé est l'**uniforme** continuité : $\delta$ ne dépend pas de $x$, donc le majorant non plus.
- **Sur un intervalle non borné, c'est faux :** une limite uniforme sur $\R$ de polynômes est un polynôme (la différence de deux polynômes bornée sur $\R$ est constante), donc $\exp$, par exemple, n'est pas limite uniforme de polynômes sur $\R$.
- Conséquence classique : si $f$ est continue sur $[0, 1]$ et $\int_0^1 f(t) t^n \, dt = 0$ pour tout $n \in \N$, alors $f = 0$. On approche $\overline{f}$ par des polynômes $P_k$ ; alors $\int_0^1 |f|^2 = \lim \int_0^1 f \, P_k = 0$.
