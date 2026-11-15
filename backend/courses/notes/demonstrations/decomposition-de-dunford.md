---
titre: Décomposition de Dunford
programmes: MP, MPI, L2
statut: hors-programme
ordre: 15
notion: reduction
---

## Énoncé

> **Théorème (Dunford).** Soient $E$ un $\K$-espace vectoriel de dimension finie $n \geq 1$ et $u \in \mathcal{L}(E)$ dont le polynôme caractéristique est scindé sur $\K$ (c'est toujours le cas si $\K = \C$). Il existe un unique couple $(d, \nu)$ d'endomorphismes de $E$ tel que
>
> $$
> u = d + \nu, \qquad d \text{ diagonalisable}, \qquad \nu \text{ nilpotent}, \qquad d \circ \nu = \nu \circ d.
> $$
>
> De plus, $d$ et $\nu$ sont des polynômes en $u$.

## Idée

Le théorème de Cayley-Hamilton et le lemme des noyaux découpent $E$ en sous-espaces caractéristiques $F_i = \operatorname{Ker}(u - \lambda_i \, \mathrm{id})^{m_i}$. On définit $d$ comme valant $\lambda_i \, \mathrm{id}$ sur chaque $F_i$ ; alors $u - d$ est nilpotent. L'unicité repose sur un fait simple : un endomorphisme à la fois diagonalisable et nilpotent est nul.

## Démonstration

Écrivons $\chi_u = \prod_{i=1}^{r} (X - \lambda_i)^{m_i}$, avec $\lambda_1, \dots, \lambda_r$ distincts, et posons $F_i = \operatorname{Ker}(u - \lambda_i \, \mathrm{id}_E)^{m_i}$.

**Étape 1 : projecteurs polynomiaux.** Par le théorème de Cayley-Hamilton, $\chi_u(u) = 0$ ; les $(X - \lambda_i)^{m_i}$ sont deux à deux premiers entre eux, donc le lemme des noyaux donne $E = \bigoplus_{i=1}^{r} F_i$. Notons $p_i$ le projecteur sur $F_i$ parallèlement à $\bigoplus_{j \neq i} F_j$ ; d'après le lemme des noyaux, chaque $p_i$ est un polynôme en $u$. Chaque $F_i$ est stable par $u$, comme noyau d'un polynôme en $u$.

**Étape 2 : existence.** Posons $d = \sum_{i=1}^{r} \lambda_i p_i$ et $\nu = u - d$. Ce sont des polynômes en $u$, donc ils commutent.

- $d$ est diagonalisable : sur chaque $F_i$, il agit comme $\lambda_i \, \mathrm{id}$, et une base adaptée à la décomposition $E = \bigoplus F_i$ est formée de vecteurs propres de $d$.
- $\nu$ est nilpotent : pour $x \in F_i$, on a $\nu(x) = u(x) - \lambda_i x = (u - \lambda_i \, \mathrm{id})(x)$ et $\nu(x) \in F_i$. Par récurrence, $\nu^m(x) = (u - \lambda_i \, \mathrm{id})^m(x)$, qui est nul pour $m \geq m_i$. Avec $m = \max_i m_i$, $\nu^m$ est nul sur chaque $F_i$, donc sur $E$.

**Étape 3 : unicité.** Soit $(d', \nu')$ un autre couple qui convient. Comme $d'$ commute avec $\nu'$, il commute avec $u = d' + \nu'$, donc avec tout polynôme en $u$, en particulier avec $d$ et $\nu$ ; de même pour $\nu'$. De $d + \nu = d' + \nu'$ on tire

$$
d - d' = \nu' - \nu.
$$

- *$\nu' - \nu$ est nilpotent.* Ils commutent et vérifient $\nu^n = \nu'^n = 0$ (l'indice de nilpotence est au plus $n$). Par la formule du binôme, $(\nu' - \nu)^{2n} = \sum_{k=0}^{2n} \binom{2n}{k} \nu'^k (-\nu)^{2n-k} = 0$, car dans chaque terme $k \geq n$ ou $2n - k \geq n$.
- *$d - d'$ est diagonalisable.* Les endomorphismes $d$ et $d'$ commutent. Chaque sous-espace propre $E_\lambda$ de $d$ est stable par $d'$ (si $d(x) = \lambda x$, alors $d(d'(x)) = d'(d(x)) = \lambda d'(x)$). L'endomorphisme induit par $d'$ sur $E_\lambda$ annule le polynôme simplement scindé qui annule $d'$, donc il est diagonalisable. En réunissant des bases de vecteurs propres de $d'$ dans chaque $E_\lambda$, on obtient une base de $E$ formée de vecteurs propres communs à $d$ et $d'$ : dans cette base, $d - d'$ est diagonal.
- *Conclusion.* $d - d'$ est diagonalisable et nilpotent. Ses valeurs propres sont nulles (si $(d - d')(x) = \mu x$ avec $x \neq 0$, alors $0 = (d - d')^{2n}(x) = \mu^{2n} x$, donc $\mu = 0$), et un endomorphisme diagonalisable dont la seule valeur propre est $0$ est nul. Donc $d = d'$, puis $\nu = \nu'$.

## Remarques

- **La commutation est indispensable.** $\begin{pmatrix} 1 & 1 \\ 0 & 2 \end{pmatrix} = \begin{pmatrix} 1 & 0 \\ 0 & 2 \end{pmatrix} + \begin{pmatrix} 0 & 1 \\ 0 & 0 \end{pmatrix}$ écrit une matrice comme somme d'une diagonale et d'une nilpotente qui **ne commutent pas** ; ce n'est pas sa décomposition de Dunford. Cette matrice a deux valeurs propres distinctes, donc elle est diagonalisable : sa décomposition de Dunford est $d = A$, $\nu = 0$.
- **Application à l'exponentielle.** Si $A = D + N$ (Dunford), alors $e^A = e^D e^N$ car $D$ et $N$ commutent, et $e^N = \sum_{k < n} \frac{N^k}{k!}$ est une somme finie : on calcule ainsi l'exponentielle de toute matrice complexe.
