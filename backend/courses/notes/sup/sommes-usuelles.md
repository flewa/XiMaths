---
titre: Sommes et produits usuels
programmes: MPSI, MP2I, PCSI, PTSI, BCPST1, L1
ordre: 24
notion: sommes-recurrence
---

## Cadre et notations

Dans tout le formulaire, $n$ est un entier naturel. Une somme indexée par un ensemble vide vaut $0$, un produit indexé par un ensemble vide vaut $1$. La somme $\sum_{k=p}^{q} a_k$, pour $p \leq q$, compte $q - p + 1$ termes.

Le cours : [Sommes, inégalités et trigonométrie](/rappels/calcul-algebrique) et [Dénombrement](/rappels/denombrement).

## Sommes de puissances d'entiers

$$
\sum_{k=1}^{n} k = \frac{n(n + 1)}{2}, \qquad \sum_{k=1}^{n} k^2 = \frac{n(n + 1)(2n + 1)}{6}, \qquad \sum_{k=1}^{n} k^3 = \left( \frac{n(n + 1)}{2} \right)^2.
$$

Ces trois formules se démontrent par récurrence sur $n$. La première se retrouve aussi en écrivant la somme deux fois, dans l'ordre et à l'envers : chaque paire de termes vaut $n + 1$.

## Sommes géométriques

Pour $q \in \C$ :

$$
\sum_{k=0}^{n} q^k = \frac{1 - q^{n+1}}{1 - q} \quad (q \neq 1), \qquad \sum_{k=0}^{n} 1 = n + 1.
$$

Plus généralement, $\sum_{k=p}^{n} q^k = q^p \, \dfrac{1 - q^{n - p + 1}}{1 - q}$ pour $p \leq n$ et $q \neq 1$ : premier terme, fois $\dfrac{1 - q^{\text{nombre de termes}}}{1 - q}$.

**Factorisation.** Pour $a, b \in \C$ et $n \geq 1$ :

$$
a^n - b^n = (a - b) \sum_{k=0}^{n-1} a^k b^{n-1-k}.
$$

**Série géométrique.** Pour $\lvert q \rvert < 1$, $\sum_{k=0}^{+\infty} q^k = \dfrac{1}{1 - q}$ ; pour $\lvert q \rvert \geq 1$, la série diverge grossièrement.

## Binôme de Newton et coefficients binomiaux

Pour $a, b \in \C$ (plus généralement, deux éléments qui commutent dans un anneau) :

$$
(a + b)^n = \sum_{k=0}^{n} \binom{n}{k} a^k b^{n-k}, \qquad \text{avec} \quad \binom{n}{k} = \frac{n!}{k! \, (n - k)!} \quad (0 \leq k \leq n).
$$

$$
\sum_{k=0}^{n} \binom{n}{k} = 2^n, \qquad \sum_{k=0}^{n} (-1)^k \binom{n}{k} = 0 \quad (n \geq 1).
$$

**Relations utiles.** Pour $1 \leq k \leq n$ :

$$
\binom{n}{k} = \binom{n}{n - k}, \qquad \binom{n}{k - 1} + \binom{n}{k} = \binom{n + 1}{k} \ \text{(Pascal)}, \qquad k \binom{n}{k} = n \binom{n - 1}{k - 1}.
$$

**Vandermonde.** Pour $p, q, n \in \N$, $\sum_{k=0}^{n} \binom{p}{k} \binom{q}{n - k} = \binom{p + q}{n}$, avec la convention $\binom{m}{j} = 0$ si $j > m$.

## Sommes télescopiques

Pour toute suite $(u_k)$ :

$$
\sum_{k=0}^{n-1} (u_{k+1} - u_k) = u_n - u_0.
$$

Exemple : $\dfrac{1}{k(k + 1)} = \dfrac{1}{k} - \dfrac{1}{k + 1}$, donc $\sum_{k=1}^{n} \dfrac{1}{k(k + 1)} = 1 - \dfrac{1}{n + 1}$.

## Produits usuels

$$
n! = \prod_{k=1}^{n} k, \qquad \prod_{k=1}^{n} (2k) = 2^n \, n!, \qquad \prod_{k=1}^{n} (2k - 1) = \frac{(2n)!}{2^n \, n!}, \qquad \prod_{k=1}^{n} \left( 1 + \frac{1}{k} \right) = n + 1.
$$

Le dernier est un produit télescopique : $1 + \frac{1}{k} = \frac{k + 1}{k}$, et les facteurs se simplifient deux à deux. Le logarithme transforme un produit de réels strictement positifs en somme : $\ln \prod a_k = \sum \ln a_k$.

## Sommes trigonométriques

Pour $x \notin 2\pi\Z$, en sommant la suite géométrique $\left( e^{ikx} \right)$ de raison $e^{ix} \neq 1$ :

$$
\sum_{k=0}^{n} e^{ikx} = e^{inx/2} \, \frac{\sin\frac{(n + 1)x}{2}}{\sin\frac{x}{2}},
$$

puis, en prenant parties réelle et imaginaire :

$$
\sum_{k=0}^{n} \cos(kx) = \frac{\cos\frac{nx}{2} \, \sin\frac{(n + 1)x}{2}}{\sin\frac{x}{2}}, \qquad \sum_{k=0}^{n} \sin(kx) = \frac{\sin\frac{nx}{2} \, \sin\frac{(n + 1)x}{2}}{\sin\frac{x}{2}}.
$$

**Racines de l'unité.** Pour $n \geq 2$ et $\omega = e^{2i\pi/n}$, $\sum_{k=0}^{n-1} \omega^k = 0$.

## Sommes doubles

$$
\sum_{i=1}^{n} \sum_{j=1}^{n} a_i b_j = \left( \sum_{i=1}^{n} a_i \right) \left( \sum_{j=1}^{n} b_j \right), \qquad \sum_{i=1}^{n} \sum_{j=i}^{n} a_{i,j} = \sum_{j=1}^{n} \sum_{i=1}^{j} a_{i,j} = \sum_{1 \leq i \leq j \leq n} a_{i,j}.
$$

En particulier, $\sum_{1 \leq i \leq j \leq n} 1 = \dfrac{n(n + 1)}{2}$, et $\left( \sum_{k=1}^{n} a_k \right)^2 = \sum_{k=1}^{n} a_k^2 + 2 \sum_{1 \leq i < j \leq n} a_i a_j$.

## Pièges fréquents

- Le nombre de termes de $\sum_{k=p}^{q}$ est $q - p + 1$, pas $q - p$.
- La formule géométrique suppose $q \neq 1$ ; pour $q = 1$, la somme vaut le nombre de termes.
- $\left( \sum a_k \right)^2 \neq \sum a_k^2$ : il manque les doubles produits.
- Dans un changement d'indice $j = k + 1$, on décale aussi les deux bornes.
