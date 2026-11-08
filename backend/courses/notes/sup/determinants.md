---
titre: Déterminants
programmes: MPSI, PCSI
ordre: 11
notion: determinants
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$, $n \in \N^*$, et $A = (a_{ij}) \in \mathcal{M}_n(\K)$, de colonnes $C_1, \dots, C_n$.

## Définition et propriétés

> **Théorème (définition).** Il existe une unique application $\det : \mathcal{M}_n(\K) \to \K$ qui soit linéaire par rapport à chaque colonne, **alternée** (nulle dès que deux colonnes sont égales) et telle que $\det I_n = 1$.

> **Proposition.** Pour tous $A, B \in \mathcal{M}_n(\K)$ et $\lambda \in \K$ :
>
> 1. $\det(A^\top) = \det A$ ; tout ce qui vaut pour les colonnes vaut donc pour les lignes ;
> 2. $\det(AB) = \det A \, \det B$ ;
> 3. $\det(\lambda A) = \lambda^n \det A$ ;
> 4. $A$ est inversible si et seulement si $\det A \neq 0$, et alors $\det(A^{-1}) = \dfrac{1}{\det A}$.

**Opérations élémentaires.** Échanger deux colonnes change le déterminant en son opposé ; multiplier une colonne par $\lambda$ le multiplie par $\lambda$ ; ajouter à une colonne une combinaison linéaire des **autres** colonnes ne le change pas.

**Attention :** en général, $\det(A + B) \neq \det A + \det B$.

## Calcul

> **Proposition.** Le déterminant d'une matrice triangulaire est le produit de ses coefficients diagonaux. Plus généralement, si $A$ et $D$ sont des matrices carrées :
>
> $$
> \det \begin{pmatrix} A & B \\ 0 & D \end{pmatrix} = \det A \, \det D.
> $$

> **Théorème (développement selon une colonne ou une ligne).** On note $\Delta_{ij}$ le déterminant de la matrice obtenue en supprimant la ligne $i$ et la colonne $j$ de $A$ (le **mineur** d'indice $(i, j)$). Pour tout $j \in [\![1, n]\!]$ et tout $i \in [\![1, n]\!]$ :
>
> $$
> \det A = \sum_{i=1}^{n} (-1)^{i+j} a_{ij} \Delta_{ij} = \sum_{j=1}^{n} (-1)^{i+j} a_{ij} \Delta_{ij}.
> $$
>
> La première somme développe selon la colonne $j$, la seconde selon la ligne $i$.

> **Proposition (comatrice).** La **comatrice** de $A$ est $\operatorname{Com}(A) = \big( (-1)^{i+j} \Delta_{ij} \big)_{1 \leq i, j \leq n}$. Alors
>
> $$
> A \operatorname{Com}(A)^\top = \operatorname{Com}(A)^\top A = \det(A) \, I_n,
> $$
>
> et si $A$ est inversible, $A^{-1} = \dfrac{1}{\det A} \operatorname{Com}(A)^\top$.

> **Déterminant de Vandermonde.** Pour $x_1, \dots, x_n \in \K$ :
>
> $$
> \det \big( x_i^{\, j-1} \big)_{1 \leq i, j \leq n} = \prod_{1 \leq i < j \leq n} (x_j - x_i).
> $$
>
> Il est non nul si et seulement si les $x_i$ sont deux à deux distincts.

## Déterminant d'une famille, d'un endomorphisme

Soit $E$ de dimension $n$, de base $\mathcal{B}$. Le **déterminant dans la base $\mathcal{B}$** d'une famille $(x_1, \dots, x_n)$ de vecteurs de $E$ est le déterminant de la matrice de leurs coordonnées dans $\mathcal{B}$ : la famille est une base de $E$ si et seulement si ce déterminant est non nul.

Deux matrices semblables ont le même déterminant ; le **déterminant d'un endomorphisme** $u$ de $E$ est celui de sa matrice dans n'importe quelle base. On a $\det(v \circ u) = \det v \, \det u$, et $u$ est bijectif si et seulement si $\det u \neq 0$.

## Pièges fréquents

- Écrire $\det(\lambda A) = \lambda \det A$ : le bon facteur est $\lambda^n$.
- Ajouter à une colonne un multiple d'elle-même : c'est une multiplication de la colonne, qui change le déterminant.
- Oublier les signes $(-1)^{i+j}$ dans un développement.
