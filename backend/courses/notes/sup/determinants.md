---
titre: Groupe symétrique et déterminants
programmes: MPSI, MP2I, PCSI
ordre: 15
notion: determinants
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$, $n \in \N^*$, et $A = (a_{ij}) \in \mathcal{M}_n(\K)$, de colonnes $C_1, \dots, C_n$.

## Groupe symétrique

On note $\mathfrak{S}_n$ le groupe des permutations (bijections) de $[\![1, n]\!]$, muni de la composition ; il a $n!$ éléments. Pour $p \geq 2$ éléments distincts $a_1, \dots, a_p$, le **cycle** $(a_1 \ a_2 \ \dots \ a_p)$ envoie $a_1$ sur $a_2$, …, $a_{p-1}$ sur $a_p$, $a_p$ sur $a_1$, et fixe les autres éléments ; son **support** est $\{ a_1, \dots, a_p \}$ et sa longueur $p$. Une **transposition** est un cycle de longueur $2$.

> **Théorème.**
>
> 1. Toute permutation se décompose en produit de cycles à supports disjoints ; cette décomposition est unique à l'ordre près, et ces cycles commutent.
> 2. Toute permutation est un produit de transpositions.
> 3. **Signature :** il existe un unique morphisme de groupes $\varepsilon : \mathfrak{S}_n \to \{ -1, 1 \}$ qui envoie toute transposition sur $-1$. Si $\sigma$ est produit de $k$ transpositions, $\varepsilon(\sigma) = (-1)^k$, et un cycle de longueur $p$ a pour signature $(-1)^{p-1}$.

Exemple : $\sigma = \begin{pmatrix} 1 & 2 & 3 & 4 & 5 \\ 3 & 5 & 1 & 2 & 4 \end{pmatrix} = (1 \ 3)(2 \ 5 \ 4)$, donc $\varepsilon(\sigma) = (-1) \times 1 = -1$.

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

**Formule explicite.** $\det A = \sum_{\sigma \in \mathfrak{S}_n} \varepsilon(\sigma) \prod_{j=1}^{n} a_{\sigma(j) j}$. Pour $n = 2$ : $\det \begin{pmatrix} a & b \\ c & d \end{pmatrix} = ad - bc$. Le déterminant induit un morphisme de groupes de $GL_n(\K)$ dans $\K^*$.

## Calcul

> **Proposition.** Le déterminant d'une matrice triangulaire est le produit de ses coefficients diagonaux. Plus généralement (formule par blocs, hors programme de MPSI, vue en deuxième année), si $A$ et $D$ sont des matrices carrées :
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

Soit $E$ de dimension $n$. Une **forme $n$-linéaire alternée** sur $E$ est une application $f : E^n \to \K$, linéaire par rapport à chaque variable, et nulle dès que deux des vecteurs sont égaux. Elle est alors **antisymétrique** : échanger deux vecteurs change $f$ en son opposé, et plus généralement $f(x_{\sigma(1)}, \dots, x_{\sigma(n)}) = \varepsilon(\sigma) f(x_1, \dots, x_n)$ ; elle est nulle sur toute famille liée.

> **Théorème.** Soit $\mathcal{B}$ une base de $E$. Il existe une unique forme $n$-linéaire alternée $\det_{\mathcal{B}}$ telle que $\det_{\mathcal{B}}(\mathcal{B}) = 1$, et toute forme $n$-linéaire alternée est un multiple de $\det_{\mathcal{B}}$. Le nombre $\det_{\mathcal{B}}(x_1, \dots, x_n)$ est le déterminant de la matrice des coordonnées des $x_j$ dans $\mathcal{B}$. Si $\mathcal{B}'$ est une autre base, $\det_{\mathcal{B}'} = \det_{\mathcal{B}'}(\mathcal{B}) \det_{\mathcal{B}}$.

La famille $(x_1, \dots, x_n)$ est une base de $E$ si et seulement si $\det_{\mathcal{B}}(x_1, \dots, x_n) \neq 0$. Dans la base canonique de $\R^2$ (resp. $\R^3$), le déterminant de deux (resp. trois) vecteurs est l'aire orientée du parallélogramme (resp. le volume orienté du parallélépipède) qu'ils engendrent.

Deux matrices semblables ont le même déterminant ; le **déterminant d'un endomorphisme** $u$ de $E$ est celui de sa matrice dans n'importe quelle base. On a $\det(v \circ u) = \det v \, \det u$, et $u$ est bijectif si et seulement si $\det u \neq 0$.

## Pièges fréquents

- Écrire $\det(\lambda A) = \lambda \det A$ : le bon facteur est $\lambda^n$.
- Ajouter à une colonne un multiple d'elle-même : c'est une multiplication de la colonne, qui change le déterminant.
- Oublier les signes $(-1)^{i+j}$ dans un développement.
