---
titre: Théorème spectral
programmes: MP, MPI, L2
statut: au-programme
ordre: 4
notion: espaces-euclidiens
---

## Énoncé

> **Théorème spectral.** Soient $E$ un espace euclidien de dimension $n \geq 1$ et $u \in \mathcal{L}(E)$. L'endomorphisme $u$ est **autoadjoint** (c'est-à-dire $\langle u(x), y \rangle = \langle x, u(y) \rangle$ pour tous $x, y \in E$) si et seulement s'il existe une base orthonormée de $E$ formée de vecteurs propres de $u$.
>
> Matriciellement : une matrice $A \in \mathcal{M}_n(\R)$ est symétrique si et seulement s'il existe $P \in O_n(\R)$ et $D$ diagonale réelle telles que $A = P D P^\top$.

## Idée

Trois ingrédients : une matrice symétrique réelle a une valeur propre **réelle** ; l'orthogonal d'un sous-espace stable par $u$ autoadjoint est encore stable ; on conclut par récurrence sur la dimension en retirant une droite propre.

## Démonstration

**Sens réciproque.** Si $\mathcal{B}$ est une base orthonormée de vecteurs propres, la matrice de $u$ dans $\mathcal{B}$ est diagonale, donc symétrique. Or, dans une base orthonormée, $u$ est autoadjoint si et seulement si sa matrice est symétrique : $u$ est autoadjoint.

**Sens direct, étape 1 : une valeur propre réelle.** Soit $A \in \mathcal{S}_n(\R)$ la matrice de $u$ dans une base orthonormée. Le polynôme $\chi_A$ a une racine complexe $\lambda$ (théorème de d'Alembert-Gauss) ; soit $Z \in \C^n$ non nul tel que $AZ = \lambda Z$. Le nombre $s = \overline{Z}^\top A Z$ vérifie

$$
s = \lambda \, \overline{Z}^\top Z = \lambda \sum_{k=1}^{n} |z_k|^2, \qquad \overline{s} = Z^\top A \overline{Z} = \big( Z^\top A \overline{Z} \big)^\top = \overline{Z}^\top A^\top Z = s,
$$

en utilisant que $A$ est réelle, qu'un scalaire est égal à sa transposée, et que $A^\top = A$. Donc $s$ est réel, et $\lambda = \dfrac{s}{\sum |z_k|^2}$ est réel. Comme $\lambda$ est une racine réelle de $\chi_A = \chi_u$, c'est une valeur propre de $u$.

**Étape 2 : orthogonal d'un sous-espace stable.** Soit $F$ un sous-espace stable par $u$. Pour $x \in F^\perp$ et $y \in F$, on a $u(y) \in F$, donc $\langle u(x), y \rangle = \langle x, u(y) \rangle = 0$. Ainsi $u(x) \in F^\perp$ : $F^\perp$ est stable par $u$.

**Étape 3 : récurrence sur $n$.** Pour $n = 1$, tout vecteur unitaire convient. Supposons le résultat vrai en dimension $n - 1$, et soit $u$ autoadjoint sur $E$ de dimension $n \geq 2$. Par l'étape 1, $u$ a une valeur propre réelle $\lambda$ ; soit $e_1$ un vecteur propre associé de norme $1$. La droite $D = \operatorname{Vect}(e_1)$ est stable par $u$, donc $H = D^\perp$, de dimension $n - 1$, l'est aussi (étape 2). L'endomorphisme $u_H$ induit sur $H$ est autoadjoint pour le produit scalaire restreint à $H$. Par hypothèse de récurrence, $H$ a une base orthonormée $(e_2, \dots, e_n)$ de vecteurs propres de $u_H$, donc de $u$. Alors $(e_1, e_2, \dots, e_n)$ est une base orthonormée de $E$ formée de vecteurs propres de $u$.

**Forme matricielle.** Si $A$ est symétrique, l'endomorphisme canoniquement associé est autoadjoint pour le produit scalaire canonique de $\R^n$ ; la matrice de passage $P$ de la base canonique à une base orthonormée de vecteurs propres est orthogonale, et $A = P D P^{-1} = P D P^\top$.

## Remarques

- **Sous-espaces propres orthogonaux.** Si $u(x) = \lambda x$ et $u(y) = \mu y$ avec $\lambda \neq \mu$, alors $\lambda \langle x, y \rangle = \langle u(x), y \rangle = \langle x, u(y) \rangle = \mu \langle x, y \rangle$, donc $\langle x, y \rangle = 0$. Le théorème dit donc aussi que $E$ est la somme directe orthogonale des sous-espaces propres de $u$.
- **Le caractère réel est essentiel.** La matrice complexe symétrique $\begin{pmatrix} 1 & i \\ i & -1 \end{pmatrix}$ est nilpotente non nulle (son carré est nul) : elle n'est pas diagonalisable.
- **Application.** Une matrice symétrique réelle est positive si et seulement si ses valeurs propres sont positives : dans une base orthonormée de vecteurs propres, $X^\top A X = \sum \lambda_k y_k^2$.
