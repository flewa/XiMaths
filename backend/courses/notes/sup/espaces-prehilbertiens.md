---
titre: Espaces préhilbertiens réels
programmes: MPSI, MP2I
ordre: 19
notion: espaces-euclidiens
---

## Cadre et notations

Dans toute la fiche, $E$ est un $\R$-espace vectoriel. Un **produit scalaire** sur $E$ est une application $(x, y) \mapsto \langle x, y \rangle$ de $E^2$ dans $\R$, bilinéaire, symétrique ($\langle x, y \rangle = \langle y, x \rangle$), positive ($\langle x, x \rangle \geq 0$) et définie ($\langle x, x \rangle = 0 \implies x = 0$). Muni d'un produit scalaire, $E$ est un **espace préhilbertien réel** ; s'il est de dimension finie, c'est un **espace euclidien**. On note aussi $(x \mid y)$ ou $x \cdot y$.

**Exemples.**

- Sur $\R^n$ : $\langle x, y \rangle = \sum_{i=1}^{n} x_i y_i = X^\top Y$ (produit scalaire canonique).
- Sur $\mathcal{M}_{n,p}(\R)$ : $\langle A, B \rangle = \operatorname{tr}(A^\top B) = \sum_{i,j} a_{ij} b_{ij}$.
- Sur $\mathcal{C}([a, b], \R)$, avec $a < b$ : $\langle f, g \rangle = \int_a^b f(t) g(t) \, dt$ ; le caractère défini vient de ce qu'une fonction continue positive d'intégrale nulle est nulle.

## Norme et inégalités

La **norme** associée est $\|x\| = \sqrt{\langle x, x \rangle}$, et la **distance** de $x$ à $y$ est $\|x - y\|$.

> **Proposition (identités).** Pour tous $x, y \in E$ :
>
> $$
> \|x + y\|^2 = \|x\|^2 + \|y\|^2 + 2 \langle x, y \rangle, \qquad \langle x, y \rangle = \frac{1}{4} \left( \|x + y\|^2 - \|x - y\|^2 \right).
> $$
>
> La seconde est la **formule de polarisation** : la norme détermine le produit scalaire.

> **Théorème (inégalité de Cauchy-Schwarz).** Pour tous $x, y \in E$ : $|\langle x, y \rangle| \leq \|x\| \, \|y\|$, avec égalité si et seulement si $x$ et $y$ sont colinéaires.

Exemples : $\left( \sum_{i=1}^{n} x_i y_i \right)^2 \leq \left( \sum_{i=1}^{n} x_i^2 \right) \left( \sum_{i=1}^{n} y_i^2 \right)$ et $\left( \int_a^b f g \right)^2 \leq \int_a^b f^2 \int_a^b g^2$.

> **Théorème (inégalité triangulaire).** Pour tous $x, y \in E$ : $\|x + y\| \leq \|x\| + \|y\|$, avec égalité si et seulement si $x$ et $y$ sont colinéaires **de même sens** (l'un est un multiple positif de l'autre).

## Orthogonalité

Deux vecteurs $x$ et $y$ sont **orthogonaux** si $\langle x, y \rangle = 0$. L'**orthogonal** d'une partie $A$ est $A^\perp = \{ x \in E : \langle x, a \rangle = 0 \text{ pour tout } a \in A \}$ ; c'est un sous-espace vectoriel. Une famille $(e_i)$ est **orthogonale** si ses vecteurs sont deux à deux orthogonaux, **orthonormée** si de plus ils sont de norme $1$.

> **Proposition.**
>
> 1. Toute famille orthogonale de vecteurs non nuls est libre.
> 2. **Pythagore :** si $x_1, \dots, x_p$ sont deux à deux orthogonaux, $\left\| \sum_{i=1}^{p} x_i \right\|^2 = \sum_{i=1}^{p} \|x_i\|^2$.

> **Théorème (Gram-Schmidt).** Soit $(x_1, \dots, x_p)$ une famille libre de $E$. Il existe une unique famille orthonormée $(e_1, \dots, e_p)$ telle que, pour tout $k$, $\operatorname{Vect}(e_1, \dots, e_k) = \operatorname{Vect}(x_1, \dots, x_k)$ et $\langle e_k, x_k \rangle > 0$. On l'obtient par récurrence :
>
> $$
> e_k = \frac{y_k}{\|y_k\|}, \qquad \text{où} \quad y_k = x_k - \sum_{i=1}^{k-1} \langle x_k, e_i \rangle \, e_i.
> $$

## Bases orthonormées

> **Théorème.** Tout espace euclidien non nul admet une base orthonormée, et toute famille orthonormée se complète en une base orthonormée. Si $(e_1, \dots, e_n)$ est une base orthonormée de $E$, alors pour tous $x, y \in E$ :
>
> $$
> x = \sum_{i=1}^{n} \langle x, e_i \rangle \, e_i, \qquad \langle x, y \rangle = \sum_{i=1}^{n} x_i y_i, \qquad \|x\|^2 = \sum_{i=1}^{n} x_i^2,
> $$
>
> où $x_i = \langle x, e_i \rangle$ et $y_i = \langle y, e_i \rangle$ sont les coordonnées de $x$ et $y$.

## Projection orthogonale

Soit $F$ un sous-espace de **dimension finie** de $E$.

> **Théorème.**
>
> 1. $E = F \oplus F^\perp$ : $F^\perp$ est le **supplémentaire orthogonal** de $F$. Si $E$ est de dimension finie, $\dim F^\perp = \dim E - \dim F$ et $(F^\perp)^\perp = F$.
> 2. Le **projeté orthogonal** $p_F(x)$ de $x$ sur $F$ (la projection sur $F$ parallèlement à $F^\perp$) s'écrit, dans une base orthonormée $(e_1, \dots, e_p)$ de $F$ :
>
> $$
> p_F(x) = \sum_{i=1}^{p} \langle x, e_i \rangle \, e_i.
> $$
>
> 3. $p_F(x)$ est l'unique élément de $F$ qui réalise la **distance** de $x$ à $F$ : $d(x, F) = \min_{y \in F} \|x - y\| = \|x - p_F(x)\|$, et $\|x\|^2 = \|p_F(x)\|^2 + d(x, F)^2$.

**Hyperplan.** En dimension finie, si $u \neq 0$, l'hyperplan $H = \operatorname{Vect}(u)^\perp$ a pour **vecteur normal** $u$, et

$$
p_H(x) = x - \frac{\langle x, u \rangle}{\|u\|^2} \, u, \qquad d(x, H) = \frac{|\langle x, u \rangle|}{\|u\|}.
$$

## Pièges fréquents

- Oublier de vérifier le caractère **défini** d'un produit scalaire : $(P, Q) \mapsto \sum_{k=0}^{n} P(k) Q(k)$ est un produit scalaire sur $\R_n[X]$, mais pas sur $\R[X]$.
- Utiliser la formule $p_F(x) = \sum \langle x, e_i \rangle e_i$ avec une base de $F$ qui n'est pas orthonormée.
- Confondre « orthogonal » et « supplémentaire » : deux droites orthogonales de $\R^3$ ne sont pas supplémentaires.
