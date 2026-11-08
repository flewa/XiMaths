---
titre: Espaces préhilbertiens et euclidiens
programmes: MP, PSI
ordre: 8
notion: espaces-euclidiens
---

## Cadre et notations

Dans toute la fiche, $E$ est un **$\R$-espace vectoriel**. Un **produit scalaire** sur $E$ est une forme bilinéaire symétrique $\langle \cdot, \cdot \rangle$ **définie positive** : $\langle x, x \rangle \geq 0$ pour tout $x$, avec égalité si et seulement si $x = 0$. Muni d'un produit scalaire, $E$ est un espace **préhilbertien réel** ; il est **euclidien** s'il est de plus de dimension finie. La norme associée est $\|x\| = \sqrt{\langle x, x \rangle}$.

Exemples : $\langle x, y \rangle = \sum_{i=1}^{n} x_i y_i$ sur $\R^n$ ; $\langle A, B \rangle = \operatorname{tr}(A^\top B)$ sur $\mathcal{M}_n(\R)$ ; $\langle f, g \rangle = \int_a^b f g$ sur $\mathcal{C}([a, b], \R)$, avec $a < b$.

## Inégalités et identités

> **Inégalité de Cauchy-Schwarz.** Pour tous $x, y \in E$ : $|\langle x, y \rangle| \leq \|x\| \, \|y\|$, avec égalité si et seulement si $x$ et $y$ sont colinéaires.

> **Identités.** Pour tous $x, y \in E$ :
>
> $$
> \|x + y\|^2 = \|x\|^2 + 2 \langle x, y \rangle + \|y\|^2, \qquad \langle x, y \rangle = \frac{1}{2} \left( \|x + y\|^2 - \|x\|^2 - \|y\|^2 \right).
> $$
>
> **Pythagore :** $\|x + y\|^2 = \|x\|^2 + \|y\|^2$ si et seulement si $\langle x, y \rangle = 0$.

## Orthogonalité

Une famille $(e_1, \dots, e_p)$ est **orthonormée** si $\langle e_i, e_j \rangle = 1$ pour $i = j$ et $0$ sinon. Une famille orthonormée est libre.

> **Théorème (orthonormalisation de Gram-Schmidt).** Soit $(x_1, \dots, x_p)$ une famille libre de $E$. Il existe une unique famille orthonormée $(e_1, \dots, e_p)$ telle que, pour tout $k \in [\![1, p]\!]$, $\operatorname{Vect}(e_1, \dots, e_k) = \operatorname{Vect}(x_1, \dots, x_k)$ et $\langle e_k, x_k \rangle > 0$.

Tout espace euclidien admet donc des bases orthonormées. Dans une base orthonormée $(e_1, \dots, e_n)$ : $x = \sum_{i=1}^{n} \langle x, e_i \rangle e_i$, $\langle x, y \rangle = \sum_{i=1}^{n} x_i y_i$ et $\|x\|^2 = \sum_{i=1}^{n} x_i^2$, où $x_i$ et $y_i$ sont les coordonnées de $x$ et $y$.

Pour une partie $A$ de $E$, l'**orthogonal** $A^\perp = \{ x \in E : \forall a \in A, \ \langle x, a \rangle = 0 \}$ est un sous-espace de $E$.

> **Théorème (projection orthogonale).** Soit $F$ un sous-espace de **dimension finie** de $E$, de base orthonormée $(e_1, \dots, e_p)$. Alors $E = F \oplus F^\perp$. Le projeté orthogonal de $x \in E$ sur $F$ est
>
> $$
> p_F(x) = \sum_{i=1}^{p} \langle x, e_i \rangle e_i,
> $$
>
> et c'est l'unique point de $F$ qui réalise la distance de $x$ à $F$ : $d(x, F) = \min_{y \in F} \|x - y\| = \|x - p_F(x)\|$.

Si $E$ est euclidien de dimension $n$ : $\dim F^\perp = n - \dim F$ et $(F^\perp)^\perp = F$.

> **Théorème de représentation.** Si $E$ est euclidien, pour toute forme linéaire $\varphi$ sur $E$, il existe un unique $a \in E$ tel que $\varphi(x) = \langle a, x \rangle$ pour tout $x \in E$.

## Isométries vectorielles

Dans la suite, $E$ est euclidien de dimension $n \geq 1$.

> **Théorème.** Pour $u \in \mathcal{L}(E)$, les assertions suivantes sont équivalentes :
>
> 1. $\|u(x)\| = \|x\|$ pour tout $x \in E$ ($u$ est une **isométrie vectorielle**) ;
> 2. $\langle u(x), u(y) \rangle = \langle x, y \rangle$ pour tous $x, y \in E$ ;
> 3. $u$ envoie une (toute) base orthonormée sur une base orthonormée ;
> 4. la matrice $M$ de $u$ dans une base **orthonormée** vérifie $M^\top M = I_n$.

Les matrices $M \in \mathcal{M}_n(\R)$ telles que $M^\top M = I_n$ forment le **groupe orthogonal** $O_n(\R)$ ; elles vérifient $\det M = \pm 1$, et celles de déterminant $1$ forment $SO_n(\R)$. Les éléments de $O_2(\R)$ sont les matrices

$$
\begin{pmatrix} \cos \theta & -\sin \theta \\ \sin \theta & \cos \theta \end{pmatrix} \ (\text{rotations, dans } SO_2(\R)), \qquad \begin{pmatrix} \cos \theta & \sin \theta \\ \sin \theta & -\cos \theta \end{pmatrix} \ (\text{réflexions}), \qquad \theta \in \R.
$$

## Endomorphismes symétriques

> **Définition.** Un endomorphisme $u$ de $E$ est **symétrique** si $\langle u(x), y \rangle = \langle x, u(y) \rangle$ pour tous $x, y \in E$ ; c'est le cas si et seulement si sa matrice dans une base **orthonormée** est symétrique.

> **Théorème spectral.** Si $u$ est un endomorphisme symétrique de l'espace euclidien $E$, il existe une base orthonormée de $E$ formée de vecteurs propres de $u$ ; ses sous-espaces propres sont deux à deux orthogonaux. Version matricielle : pour toute $S \in \mathcal{S}_n(\R)$, il existe $P \in O_n(\R)$ et $D$ diagonale réelle telles que
>
> $$
> S = P D P^\top.
> $$

Une matrice $S \in \mathcal{S}_n(\R)$ est **positive** ($S \in \mathcal{S}_n^+(\R)$) si $X^\top S X \geq 0$ pour tout $X \in \mathcal{M}_{n,1}(\R)$, ce qui équivaut à $\operatorname{Sp}(S) \subset \R_+$ ; elle est **définie positive** ($S \in \mathcal{S}_n^{++}(\R)$) si $X^\top S X > 0$ pour tout $X \neq 0$, ce qui équivaut à $\operatorname{Sp}(S) \subset \R_+^*$.

## Pièges fréquents

- Lire le produit scalaire, ou la symétrie d'un endomorphisme, sur les coordonnées dans une base qui n'est pas orthonormée.
- Appliquer le théorème spectral à une matrice symétrique **complexe** : $\begin{pmatrix} 1 & i \\ i & -1 \end{pmatrix}$ est symétrique, non nulle, de carré nul ; elle n'est pas diagonalisable.
- Oublier que $E = F \oplus F^\perp$ peut tomber en défaut si $F$ est de dimension infinie.
