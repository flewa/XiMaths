---
titre: Théorème de Cayley-Hamilton
programmes: MP, MPI, L2
statut: preuve-hors-programme
ordre: 3
notion: reduction
---

## Énoncé

> **Théorème (Cayley-Hamilton).** Soient $E$ un $\K$-espace vectoriel de dimension finie $n \geq 1$ et $u \in \mathcal{L}(E)$, de polynôme caractéristique $\chi_u = \det(X \, \mathrm{id}_E - u)$. Alors $\chi_u(u) = 0$. Matriciellement : pour tout $A \in \mathcal{M}_n(\K)$, $\chi_A(A) = 0$.

Au programme de MP, la démonstration n'est pas exigible.

## Idée

Il suffit de montrer que $\chi_u(u)(x) = 0$ pour chaque vecteur $x$. On regarde le plus petit sous-espace stable contenant $x$, engendré par $x, u(x), u^2(x), \dots$ : la matrice de $u$ y est une matrice compagnon, dont on calcule le polynôme caractéristique, et ce polynôme divise $\chi_u$.

## Démonstration

Soit $x \in E$ non nul ($\chi_u(u)(0) = 0$ est évident).

**Étape 1 : le sous-espace cyclique.** Comme $E$ est de dimension $n$, la famille $(x, u(x), \dots, u^n(x))$ est liée. Soit $p \geq 1$ le plus grand entier tel que $(x, u(x), \dots, u^{p-1}(x))$ soit libre. Alors $u^p(x)$ est combinaison linéaire des vecteurs précédents : il existe $a_0, \dots, a_{p-1} \in \K$ tels que

$$
u^p(x) + a_{p-1} u^{p-1}(x) + \dots + a_1 u(x) + a_0 x = 0. \qquad (\ast)
$$

Posons $Q = X^p + a_{p-1} X^{p-1} + \dots + a_0$ : la relation $(\ast)$ s'écrit $Q(u)(x) = 0$. Le sous-espace $F = \operatorname{Vect}(x, u(x), \dots, u^{p-1}(x))$ est stable par $u$ : $u$ envoie $u^k(x)$ sur $u^{k+1}(x) \in F$ pour $k < p - 1$, et $u^p(x) \in F$ par $(\ast)$.

**Étape 2 : la matrice compagnon.** Dans la base $\mathcal{B}_F = (x, u(x), \dots, u^{p-1}(x))$, l'endomorphisme $u_F$ induit par $u$ sur $F$ a pour matrice

$$
C = \begin{pmatrix} 0 & 0 & \cdots & 0 & -a_0 \\ 1 & 0 & \cdots & 0 & -a_1 \\ 0 & 1 & \ddots & \vdots & \vdots \\ \vdots & & \ddots & 0 & -a_{p-2} \\ 0 & \cdots & 0 & 1 & -a_{p-1} \end{pmatrix}.
$$

Montrons par récurrence sur $p$ que $\det(X I_p - C) = Q$. Pour $p = 1$, $C = (-a_0)$ et $\det(X + a_0) = X + a_0$. Pour $p \geq 2$, développons $\det(X I_p - C)$ selon sa première ligne, qui ne contient que $X$ en position $(1, 1)$ et $a_0$ en position $(1, p)$ :

- le mineur d'indice $(1, 1)$ est le déterminant de même forme de taille $p - 1$, associé à $a_1, \dots, a_{p-1}$ ; par hypothèse de récurrence, il vaut $X^{p-1} + a_{p-1} X^{p-2} + \dots + a_1$ ;
- le mineur d'indice $(1, p)$ est le déterminant d'une matrice triangulaire de taille $p - 1$ dont la diagonale ne contient que des $-1$ : il vaut $(-1)^{p-1}$, et son cofacteur vaut $(-1)^{1+p} (-1)^{p-1} = 1$.

Donc $\det(X I_p - C) = X \left( X^{p-1} + a_{p-1} X^{p-2} + \dots + a_1 \right) + a_0 = Q$, c'est-à-dire $\chi_{u_F} = Q$.

**Étape 3 : $Q$ divise $\chi_u$.** Complétons $\mathcal{B}_F$ en une base $\mathcal{B}$ de $E$. Comme $F$ est stable par $u$, la matrice de $u$ dans $\mathcal{B}$ est triangulaire par blocs :

$$
\operatorname{Mat}_{\mathcal{B}}(u) = \begin{pmatrix} C & B \\ 0 & D \end{pmatrix}, \qquad \text{donc} \qquad \chi_u = \det(X I_p - C) \det(X I_{n-p} - D) = Q \, \chi_D.
$$

**Étape 4 : conclusion.** Les polynômes en $u$ commutent, donc

$$
\chi_u(u)(x) = \big( \chi_D(u) \circ Q(u) \big)(x) = \chi_D(u)\big( Q(u)(x) \big) = \chi_D(u)(0) = 0.
$$

Ceci vaut pour tout $x \in E$ : $\chi_u(u) = 0$.

## Remarques

- **Piège classique :** « $\chi_A(A) = \det(A I_n - A) = \det(0) = 0$ » est faux. Dans $\chi_A(X) = \det(X I_n - A)$, on ne peut pas remplacer $X$ par une matrice à l'intérieur du déterminant : $\chi_A(A)$ est une matrice, $\det(0)$ un scalaire.
- **Conséquences.** Le polynôme minimal divise $\chi_u$, donc il est de degré au plus $n$, et les valeurs propres sont exactement ses racines. Pour $A$ inversible, $\chi_A(A) = 0$ exprime $A^{-1}$ comme polynôme en $A$ : si $\chi_A = X^n + \dots + c_1 X + c_0$ avec $c_0 = (-1)^n \det A \neq 0$, alors $A^{-1} = -\frac{1}{c_0} \left( A^{n-1} + \dots + c_1 I_n \right)$.
