---
titre: Matrices
programmes: MPSI, PCSI
ordre: 10
notion: calcul-matriciel
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$ et $n, p, q \in \N^*$. On note $\mathcal{M}_{n,p}(\K)$ l'ensemble des matrices à $n$ lignes et $p$ colonnes, $\mathcal{M}_n(\K) = \mathcal{M}_{n,n}(\K)$, $I_n$ la matrice identité et $A^\top$ la transposée de $A$.

## Produit matriciel

Pour $A = (a_{ij}) \in \mathcal{M}_{n,p}(\K)$ et $B = (b_{jk}) \in \mathcal{M}_{p,q}(\K)$, le produit $AB \in \mathcal{M}_{n,q}(\K)$ a pour coefficients $(AB)_{ik} = \sum_{j=1}^{p} a_{ij} b_{jk}$. Le produit est associatif, distributif par rapport à l'addition, et $(AB)^\top = B^\top A^\top$.

**Le produit n'est pas commutatif, et $\mathcal{M}_n(\K)$ a des diviseurs de zéro** pour $n \geq 2$ : avec $A = \begin{pmatrix} 0 & 1 \\ 0 & 0 \end{pmatrix}$, on a $A \neq 0$ et $A^2 = 0$.

> **Formule du binôme.** Si $A, B \in \mathcal{M}_n(\K)$ **commutent** ($AB = BA$), alors pour tout $m \in \N$ :
>
> $$
> (A + B)^m = \sum_{k=0}^{m} \binom{m}{k} A^k B^{m-k}.
> $$

## Matrice d'une application linéaire

Soient $E$ et $F$ de dimensions $p$ et $n$, munis de bases $\mathcal{B} = (e_1, \dots, e_p)$ et $\mathcal{C}$. La matrice $\operatorname{Mat}_{\mathcal{B}, \mathcal{C}}(u) \in \mathcal{M}_{n,p}(\K)$ de $u \in \mathcal{L}(E, F)$ a pour $j$-ième colonne les coordonnées de $u(e_j)$ dans $\mathcal{C}$. L'application $u \mapsto \operatorname{Mat}_{\mathcal{B}, \mathcal{C}}(u)$ est un isomorphisme de $\mathcal{L}(E, F)$ sur $\mathcal{M}_{n,p}(\K)$, et la matrice d'une composée est le produit des matrices : $\operatorname{Mat}_{\mathcal{B}, \mathcal{D}}(v \circ u) = \operatorname{Mat}_{\mathcal{C}, \mathcal{D}}(v) \operatorname{Mat}_{\mathcal{B}, \mathcal{C}}(u)$.

## Matrices inversibles

> **Définition.** Une matrice $A \in \mathcal{M}_n(\K)$ est **inversible** s'il existe $B \in \mathcal{M}_n(\K)$ telle que $AB = BA = I_n$. Cette matrice $B$ est unique, notée $A^{-1}$. L'ensemble des matrices inversibles est noté $GL_n(\K)$.

> **Théorème.** Pour $A \in \mathcal{M}_n(\K)$, les assertions suivantes sont équivalentes :
>
> 1. $A$ est inversible ;
> 2. il existe $B \in \mathcal{M}_n(\K)$ telle que $AB = I_n$ (ou telle que $BA = I_n$) ;
> 3. pour $X \in \mathcal{M}_{n,1}(\K)$, $AX = 0$ entraîne $X = 0$ ;
> 4. $\operatorname{rg} A = n$ ;
> 5. les colonnes de $A$ forment une base de $\mathcal{M}_{n,1}(\K)$ ;
> 6. $\det A \neq 0$.

Si $A, B \in GL_n(\K)$, alors $AB \in GL_n(\K)$ et $(AB)^{-1} = B^{-1} A^{-1}$ ; de plus $A^\top \in GL_n(\K)$ et $(A^\top)^{-1} = (A^{-1})^\top$.

## Changement de base

Soient $\mathcal{B}$ et $\mathcal{B}'$ deux bases de $E$ (dimension $n$). La **matrice de passage** $P = P_{\mathcal{B}}^{\mathcal{B}'}$ a pour colonnes les coordonnées des vecteurs de $\mathcal{B}'$ dans $\mathcal{B}$ ; elle est inversible.

> **Proposition.** Si $X$ et $X'$ sont les colonnes des coordonnées d'un même vecteur dans $\mathcal{B}$ et $\mathcal{B}'$, alors $X = P X'$. Pour $u \in \mathcal{L}(E)$, avec $A = \operatorname{Mat}_{\mathcal{B}}(u)$ et $A' = \operatorname{Mat}_{\mathcal{B}'}(u)$ :
>
> $$
> A' = P^{-1} A P.
> $$

Deux matrices $A, A' \in \mathcal{M}_n(\K)$ sont **semblables** s'il existe $P \in GL_n(\K)$ telle que $A' = P^{-1} A P$.

## Trace

La trace de $A \in \mathcal{M}_n(\K)$ est la somme de ses coefficients diagonaux. Elle est linéaire, et $\operatorname{tr}(AB) = \operatorname{tr}(BA)$ pour $A \in \mathcal{M}_{n,p}(\K)$ et $B \in \mathcal{M}_{p,n}(\K)$. Deux matrices semblables ont donc la même trace, ce qui définit la trace d'un endomorphisme.

**Attention :** $\operatorname{tr}(ABC) = \operatorname{tr}(CAB) = \operatorname{tr}(BCA)$, mais en général $\operatorname{tr}(ABC) \neq \operatorname{tr}(BAC)$.

## Rang et systèmes linéaires

Le **rang** de $A \in \mathcal{M}_{n,p}(\K)$ est la dimension de l'espace engendré par ses colonnes. On a $\operatorname{rg} A = \operatorname{rg} A^\top$ ; le rang ne change pas quand on multiplie $A$ à gauche ou à droite par une matrice inversible, donc ni par les opérations élémentaires sur les lignes ou les colonnes. Une matrice est de rang $r$ si et seulement si elle est équivalente à $J_r = \begin{pmatrix} I_r & 0 \\ 0 & 0 \end{pmatrix}$.

> **Proposition (systèmes linéaires).** Soient $A \in \mathcal{M}_{n,p}(\K)$ et $B \in \mathcal{M}_{n,1}(\K)$. L'ensemble des solutions de $AX = B$ est vide, ou de la forme $X_0 + \operatorname{Ker} A = \{ X_0 + Y : AY = 0 \}$ où $X_0$ est une solution particulière. Si $n = p$ et $A$ est inversible, l'unique solution est $X = A^{-1} B$ (système de Cramer).

La méthode du pivot de Gauss transforme le système, par opérations élémentaires sur les lignes, en un système échelonné équivalent.

## Pièges fréquents

- Développer $(A + B)^2$ en $A^2 + 2AB + B^2$ sans vérifier que $A$ et $B$ commutent : en général, $(A + B)^2 = A^2 + AB + BA + B^2$.
- Simplifier $AB = AC$ en $B = C$ sans savoir que $A$ est inversible.
- Écrire la matrice de passage à l'envers : ses colonnes sont les vecteurs de la **nouvelle** base, exprimés dans l'**ancienne**.
