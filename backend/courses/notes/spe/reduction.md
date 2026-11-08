---
titre: Réduction des endomorphismes
programmes: MP, PSI
ordre: 7
notion: reduction
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$, $E$ est un $\K$-espace vectoriel de **dimension finie** $n \geq 1$, $u \in \mathcal{L}(E)$ et $A \in \mathcal{M}_n(\K)$. Les énoncés sur $u$ valent pour $A$, vue comme l'endomorphisme $X \mapsto AX$ de $\mathcal{M}_{n,1}(\K)$.

## Sous-espaces stables

Un sous-espace $F$ de $E$ est **stable** par $u$ si $u(F) \subset F$ ; $u$ induit alors un endomorphisme $u_F$ de $F$. Si $F$ est stable et si $\mathcal{B}$ est une base de $E$ obtenue en complétant une base de $F$, la matrice de $u$ dans $\mathcal{B}$ est triangulaire par blocs.

Si $u$ et $v$ commutent, $\operatorname{Ker} v$ et $\operatorname{Im} v$ sont stables par $u$ ; en particulier, les sous-espaces propres de $v$ sont stables par $u$.

## Éléments propres

> **Définition.** Un scalaire $\lambda \in \K$ est **valeur propre** de $u$ si $\operatorname{Ker}(u - \lambda \, \mathrm{id}_E) \neq \{0\}$. Un **vecteur propre** associé est un vecteur $x \neq 0$ tel que $u(x) = \lambda x$. Le **sous-espace propre** associé est $E_\lambda(u) = \operatorname{Ker}(u - \lambda \, \mathrm{id}_E)$. L'ensemble des valeurs propres est le **spectre** $\operatorname{Sp}(u)$.

> **Théorème.** Des sous-espaces propres associés à des valeurs propres deux à deux distinctes sont en somme directe. En particulier, une famille de vecteurs propres associés à des valeurs propres deux à deux distinctes est libre, et $u$ a au plus $n$ valeurs propres.

## Polynôme caractéristique

> **Définition.** Le **polynôme caractéristique** de $A$ est $\chi_A = \det(X I_n - A)$. Deux matrices semblables ont le même polynôme caractéristique, ce qui définit $\chi_u$.

> **Proposition.**
>
> 1. $\chi_A$ est unitaire de degré $n$ et $\chi_A = X^n - \operatorname{tr}(A) X^{n-1} + \dots + (-1)^n \det A$.
> 2. Les valeurs propres de $u$ sont exactement les racines de $\chi_u$ dans $\K$.
> 3. Si $\lambda$ est valeur propre de multiplicité $m_\lambda$ dans $\chi_u$, alors $1 \leq \dim E_\lambda(u) \leq m_\lambda$.

## Diagonalisation

> **Définition.** L'endomorphisme $u$ est **diagonalisable** s'il existe une base de $E$ formée de vecteurs propres de $u$. La matrice $A$ est diagonalisable si elle est semblable à une matrice diagonale.

> **Théorème.** Les assertions suivantes sont équivalentes :
>
> 1. $u$ est diagonalisable ;
> 2. $E = \bigoplus_{\lambda \in \operatorname{Sp}(u)} E_\lambda(u)$ ;
> 3. $\sum_{\lambda \in \operatorname{Sp}(u)} \dim E_\lambda(u) = n$ ;
> 4. $\chi_u$ est scindé sur $\K$ et $\dim E_\lambda(u) = m_\lambda$ pour toute valeur propre $\lambda$ ;
> 5. $u$ admet un polynôme annulateur scindé sur $\K$ à racines simples.

> **Corollaire.** Si $\chi_u$ est scindé sur $\K$ à racines simples ($u$ a $n$ valeurs propres distinctes), alors $u$ est diagonalisable, et ses sous-espaces propres sont des droites.

Cette condition est suffisante, pas nécessaire : $\mathrm{id}_E$ est diagonalisable et n'a qu'une valeur propre.

## Trigonalisation

> **Théorème.** L'endomorphisme $u$ est **trigonalisable** (il existe une base dans laquelle sa matrice est triangulaire supérieure) si et seulement si $\chi_u$ est scindé sur $\K$. En particulier, toute matrice de $\mathcal{M}_n(\C)$ est trigonalisable.

Si $\chi_u$ est scindé, de racines $\lambda_1, \dots, \lambda_n$ répétées selon leur multiplicité, alors $\operatorname{tr} u = \sum_{i=1}^{n} \lambda_i$ et $\det u = \prod_{i=1}^{n} \lambda_i$.

## Polynômes d'endomorphismes

Pour $P = \sum_{k} a_k X^k \in \K[X]$, on pose $P(u) = \sum_{k} a_k u^k$, avec $u^0 = \mathrm{id}_E$. On a $(PQ)(u) = P(u) \circ Q(u)$. Un polynôme $P$ est **annulateur** de $u$ si $P(u) = 0$.

> **Proposition.** Si $P$ est annulateur de $u$, toute valeur propre de $u$ est racine de $P$. La réciproque est fausse : $X(X - 1)$ annule $\mathrm{id}_E$, et $0$ n'est pas valeur propre de $\mathrm{id}_E$.

> **Théorème de Cayley-Hamilton.** $\chi_u(u) = 0$.

> **Définition (polynôme minimal).** Les polynômes annulateurs de $u$ sont les multiples d'un unique polynôme unitaire $\mu_u$, le **polynôme minimal** de $u$. Ses racines dans $\K$ sont exactement les valeurs propres de $u$, et $\mu_u$ divise $\chi_u$.

> **Lemme des noyaux.** Si $P_1, \dots, P_r \in \K[X]$ sont deux à deux premiers entre eux, alors
>
> $$
> \operatorname{Ker} \big( (P_1 P_2 \cdots P_r)(u) \big) = \bigoplus_{i=1}^{r} \operatorname{Ker} P_i(u).
> $$

> **Proposition.** Si $u$ est diagonalisable et si $F$ est un sous-espace stable par $u$, l'endomorphisme induit $u_F$ est diagonalisable.

## Endomorphismes nilpotents

L'endomorphisme $u$ est **nilpotent** s'il existe $p \in \N$ tel que $u^p = 0$ ; le plus petit tel $p$ est son **indice**, et il vérifie $p \leq n$. Les assertions suivantes sont équivalentes : $u$ est nilpotent ; $\chi_u = X^n$ ; $u$ est trigonalisable avec une diagonale nulle. Un endomorphisme nilpotent et diagonalisable est nul.

## Pièges fréquents

- Oublier que la diagonalisabilité dépend du corps : la matrice de rotation $\begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix}$ n'a pas de valeur propre réelle, mais elle est diagonalisable dans $\mathcal{M}_2(\C)$.
- Conclure qu'une matrice n'est pas diagonalisable parce qu'elle a une valeur propre multiple.
- Confondre « racine d'un polynôme annulateur » et « valeur propre ».
- Écrire $\chi_A(A) = \det(A I_n - A) = 0$ pour « démontrer » Cayley-Hamilton : la substitution n'a pas de sens.
