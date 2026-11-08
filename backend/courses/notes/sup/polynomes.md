---
titre: Polynômes
programmes: MPSI, PCSI
ordre: 8
notion: polynomes
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$. On note $\K[X]$ l'ensemble des polynômes à coefficients dans $\K$, et $\K_n[X]$ celui des polynômes de degré au plus $n$. Par convention, $\deg 0 = -\infty$. Pour $P = \sum_{k=0}^{n} a_k X^k$ et $x \in \K$, $P(x) = \sum_{k=0}^{n} a_k x^k$.

## Degré et division euclidienne

> **Proposition.** Pour tous $P, Q \in \K[X]$ : $\deg(PQ) = \deg P + \deg Q$ et $\deg(P + Q) \leq \max(\deg P, \deg Q)$, avec égalité si $\deg P \neq \deg Q$.

> **Théorème (division euclidienne).** Pour tous $A, B \in \K[X]$ avec $B \neq 0$, il existe un unique couple $(Q, R) \in \K[X]^2$ tel que
>
> $$
> A = BQ + R \qquad \text{et} \qquad \deg R < \deg B.
> $$

## Racines

> **Proposition.** Soient $P \in \K[X]$ et $a \in \K$. Le reste de la division de $P$ par $X - a$ est $P(a)$ ; donc $a$ est racine de $P$ si et seulement si $(X - a)$ divise $P$.

> **Définition.** Soient $P \in \K[X]$ non nul, $a \in \K$ et $m \in \N^*$. Le scalaire $a$ est **racine de multiplicité $m$** de $P$ si $(X - a)^m$ divise $P$ et $(X - a)^{m+1}$ ne divise pas $P$.

> **Théorème (caractérisation par les dérivées).** Soient $P \in \K[X]$ non nul, $a \in \K$ et $m \in \N^*$. Le scalaire $a$ est racine de multiplicité $m$ de $P$ si et seulement si
>
> $$
> P(a) = P'(a) = \dots = P^{(m-1)}(a) = 0 \qquad \text{et} \qquad P^{(m)}(a) \neq 0.
> $$

> **Théorème.** Un polynôme non nul de degré $n$ a au plus $n$ racines, comptées avec leur multiplicité. En conséquence, un polynôme de $\K_n[X]$ qui a au moins $n + 1$ racines distinctes est nul, et un polynôme qui a une infinité de racines est nul.

> **Formule de Taylor pour les polynômes.** Pour tous $P \in \K[X]$ et $a \in \K$ :
>
> $$
> P = \sum_{k=0}^{\deg P} \frac{P^{(k)}(a)}{k!} (X - a)^k.
> $$

## Factorisation

> **Théorème (d'Alembert-Gauss).** Tout polynôme non constant de $\C[X]$ admet au moins une racine dans $\C$.

> **Corollaire.**
>
> 1. Tout polynôme $P \in \C[X]$ de degré $n \geq 1$ est **scindé** : $P = \lambda \prod_{k=1}^{n} (X - z_k)$, où $\lambda$ est le coefficient dominant de $P$ et $z_1, \dots, z_n$ ses racines, répétées selon leur multiplicité. Les polynômes irréductibles de $\C[X]$ sont ceux de degré $1$.
> 2. Les polynômes irréductibles de $\R[X]$ sont ceux de degré $1$ et ceux de degré $2$ à discriminant strictement négatif. Tout polynôme non constant de $\R[X]$ est produit de son coefficient dominant et de polynômes irréductibles unitaires.

> **Proposition.** Si $P \in \R[X]$ et si $z \in \C$ est racine de $P$ de multiplicité $m$, alors $\overline{z}$ est racine de $P$ de même multiplicité $m$.

> **Relations entre coefficients et racines.** Soit $P = \sum_{k=0}^{n} a_k X^k$ de degré $n \geq 1$, scindé, de racines $x_1, \dots, x_n$ répétées selon leur multiplicité. Pour $k \in [\![1, n]\!]$, on note $\sigma_k = \sum_{1 \leq i_1 < \dots < i_k \leq n} x_{i_1} \cdots x_{i_k}$. Alors
>
> $$
> \sigma_k = (-1)^k \frac{a_{n-k}}{a_n} ; \qquad \text{en particulier} \quad \sum_{i=1}^{n} x_i = -\frac{a_{n-1}}{a_n}, \qquad \prod_{i=1}^{n} x_i = (-1)^n \frac{a_0}{a_n}.
> $$

## Interpolation de Lagrange

> **Théorème.** Soient $n \in \N$, des scalaires $x_0, \dots, x_n$ **deux à deux distincts** et $y_0, \dots, y_n \in \K$. Il existe un unique $P \in \K_n[X]$ tel que $P(x_i) = y_i$ pour tout $i \in [\![0, n]\!]$ :
>
> $$
> P = \sum_{i=0}^{n} y_i L_i, \qquad \text{où} \quad L_i = \prod_{\substack{0 \leq j \leq n \\ j \neq i}} \frac{X - x_j}{x_i - x_j}.
> $$

## Arithmétique dans $\K[X]$

La divisibilité, le PGCD (unitaire), la relation de Bézout et le lemme de Gauss se transposent de $\Z$ à $\K[X]$ : deux polynômes $A$ et $B$ sont premiers entre eux si et seulement s'il existe $U, V \in \K[X]$ tels que $AU + BV = 1$, et si $A$ divise $BC$ avec $A$ et $B$ premiers entre eux, alors $A$ divise $C$.

## Pièges fréquents

- Oublier que $\deg 0 = -\infty$ dans les calculs de degré.
- Croire qu'un polynôme réel de degré $n$ a $n$ racines réelles : $X^2 + 1$ n'en a aucune.
- Confondre « $P$ a $n$ racines distinctes » et « $P$ a $n$ racines comptées avec multiplicité ».
- Confondre le polynôme $P$ et la fonction $x \mapsto P(x)$ dans un raisonnement de degré ou de dérivation formelle : sur $\K = \R$ ou $\C$, ils se déterminent l'un l'autre, mais les définitions sont différentes.
