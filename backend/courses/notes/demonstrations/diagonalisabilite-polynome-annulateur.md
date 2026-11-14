---
titre: Diagonalisabilité et polynôme annulateur scindé à racines simples
programmes: MP, MPI, L2
statut: au-programme
ordre: 2
notion: reduction
---

## Énoncé

> **Théorème.** Soient $E$ un $\K$-espace vectoriel de dimension finie $n \geq 1$ et $u \in \mathcal{L}(E)$. Les assertions suivantes sont équivalentes :
>
> 1. $u$ est diagonalisable ;
> 2. $u$ annule un polynôme **simplement scindé** sur $\K$, c'est-à-dire scindé à racines simples ;
> 3. le polynôme minimal $\pi_u$ de $u$ est simplement scindé.

## Idée

Dans une base de vecteurs propres, le polynôme $\prod (X - \lambda)$, pris sur les valeurs propres distinctes, tue chaque vecteur de base. Réciproquement, le lemme des noyaux découpe $E$ selon les racines du polynôme annulateur, et chaque morceau est un sous-espace propre.

## Démonstration

**(1) ⟹ (2).** Soient $\lambda_1, \dots, \lambda_p$ les valeurs propres **distinctes** de $u$ et $P = \prod_{i=1}^{p} (X - \lambda_i)$, simplement scindé. Soit $(e_1, \dots, e_n)$ une base de vecteurs propres, avec $u(e_j) = \mu_j e_j$ et $\mu_j \in \{ \lambda_1, \dots, \lambda_p \}$. Pour tout polynôme $Q$, $Q(u)(e_j) = Q(\mu_j) e_j$ (par récurrence sur les puissances, puis par linéarité). Donc $P(u)(e_j) = P(\mu_j) e_j = 0$ pour tout $j$ : l'endomorphisme $P(u)$ est nul sur une base, il est nul.

**(2) ⟹ (1).** Soit $P = \prod_{i=1}^{p} (X - a_i)$, avec $a_1, \dots, a_p$ distincts, tel que $P(u) = 0$. Les polynômes $X - a_i$ sont deux à deux premiers entre eux (deux polynômes de degré $1$ de racines distinctes n'ont pas de diviseur commun non constant). Le lemme des noyaux donne

$$
E = \operatorname{Ker} P(u) = \bigoplus_{i=1}^{p} \operatorname{Ker}(u - a_i \, \mathrm{id}_E).
$$

Chaque $\operatorname{Ker}(u - a_i \, \mathrm{id}_E)$ non réduit à $\{0\}$ est le sous-espace propre associé à la valeur propre $a_i$ ; les autres sont nuls et on les retire de la somme. En réunissant des bases de ces sous-espaces, on obtient une base de $E$ formée de vecteurs propres : $u$ est diagonalisable.

**(2) ⟺ (3).** Le polynôme minimal annule $u$, donc (3) entraîne (2). Réciproquement, $\pi_u$ divise tout polynôme annulateur de $u$ ; si $P$ annule $u$ et est simplement scindé, ses diviseurs unitaires sont des produits de certains des $X - a_i$, donc simplement scindés, et $\pi_u$ l'est.

## Remarques

- **Endomorphisme induit.** Si $u$ est diagonalisable et si $F$ est un sous-espace stable par $u$, l'endomorphisme $u_F$ induit sur $F$ annule le même polynôme simplement scindé : il est diagonalisable. Ce corollaire sert à co-diagonaliser deux endomorphismes diagonalisables qui commutent.
- **Projecteurs et symétries.** Un projecteur annule $X^2 - X = X(X - 1)$, une symétrie annule $X^2 - 1 = (X - 1)(X + 1)$ : ils sont diagonalisables.
- **Sur $\R$, attention au corps.** La matrice de rotation $\begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix}$ annule $X^2 + 1$, simplement scindé sur $\C$ mais pas sur $\R$ : elle est diagonalisable dans $\mathcal{M}_2(\C)$, pas dans $\mathcal{M}_2(\R)$.
