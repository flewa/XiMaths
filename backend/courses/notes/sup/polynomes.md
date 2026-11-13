---
titre: Polynômes et fractions rationnelles
programmes: MPSI, MP2I, PCSI
ordre: 11
notion: polynomes
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$. On note $\K[X]$ l'ensemble des polynômes à coefficients dans $\K$, et $\K_n[X]$ celui des polynômes de degré au plus $n$. Par convention, $\deg 0 = -\infty$. Pour $P = \sum_{k=0}^{n} a_k X^k$ et $x \in \K$, $P(x) = \sum_{k=0}^{n} a_k x^k$.

## Degré et division euclidienne

> **Proposition.** Pour tous $P, Q \in \K[X]$ : $\deg(PQ) = \deg P + \deg Q$ et $\deg(P + Q) \leq \max(\deg P, \deg Q)$, avec égalité si $\deg P \neq \deg Q$. En particulier, $PQ = 0$ entraîne $P = 0$ ou $Q = 0$ : l'anneau $\K[X]$ est intègre.

La **composée** de $P = \sum a_k X^k$ par $Q$ est $P \circ Q = \sum a_k Q^k$ ; si $P \neq 0$ et si $Q$ n'est pas constant, $\deg(P \circ Q) = \deg P \times \deg Q$. Deux polynômes $A$ et $B$ sont **associés** ($A \mid B$ et $B \mid A$) si et seulement s'il existe $\lambda \in \K^*$ tel que $A = \lambda B$.

> **Théorème (division euclidienne).** Pour tous $A, B \in \K[X]$ avec $B \neq 0$, il existe un unique couple $(Q, R) \in \K[X]^2$ tel que
>
> $$
> A = BQ + R \qquad \text{et} \qquad \deg R < \deg B.
> $$

## Racines

> **Proposition.** Soient $P \in \K[X]$ et $a \in \K$. Le reste de la division de $P$ par $X - a$ est $P(a)$ ; donc $a$ est racine de $P$ si et seulement si $(X - a)$ divise $P$.

**Méthode de Horner.** Pour évaluer $P = a_n X^n + \dots + a_0$ en $x$, on calcule $b_n = a_n$, puis $b_k = b_{k+1} x + a_k$ pour $k$ de $n - 1$ à $0$ : on obtient $P(x) = b_0$ avec $n$ multiplications.

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

Dans $\C[X]$, $A$ divise $B$ si et seulement si toute racine de $A$ est racine de $B$ avec une multiplicité au moins égale ; deux polynômes de $\C[X]$ sont premiers entre eux si et seulement s'ils n'ont pas de racine commune. Pour $n \in \N^*$ :

$$
X^n - 1 = \prod_{k=0}^{n-1} \left( X - e^{\frac{2ik\pi}{n}} \right).
$$

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
>
> Les polynômes $Q \in \K[X]$ tels que $Q(x_i) = y_i$ pour tout $i$ sont les $P + A \prod_{j=0}^{n} (X - x_j)$, avec $A \in \K[X]$.

## Arithmétique dans $\K[X]$

La division euclidienne, l'algorithme d'Euclide (étendu), la relation de Bézout et le lemme de Gauss se transposent de $\Z$ à $\K[X]$. Un **PGCD** de $A$ et $B$ (non tous deux nuls) est un diviseur commun de degré maximal ; ils sont tous associés, et l'unique PGCD unitaire est noté $A \wedge B$. Les diviseurs communs à $A$ et $B$ sont les diviseurs de $A \wedge B$. On définit de même le PPCM unitaire $A \vee B$, le PGCD d'un nombre fini de polynômes, et les polynômes premiers entre eux dans leur ensemble ou deux à deux. En particulier, deux polynômes $A$ et $B$ sont premiers entre eux si et seulement s'il existe $U, V \in \K[X]$ tels que $AU + BV = 1$, et si $A$ divise $BC$ avec $A$ et $B$ premiers entre eux, alors $A$ divise $C$.

## Fractions rationnelles

Une **fraction rationnelle** est un quotient $F = \dfrac{P}{Q}$ avec $P, Q \in \K[X]$, $Q \neq 0$ ; elles forment un corps, noté $\K(X)$. Toute fraction non nulle a une **forme irréductible** $\frac{P}{Q}$ avec $P \wedge Q = 1$. Son **degré** est $\deg F = \deg P - \deg Q$ (indépendant de l'écriture). Sous forme irréductible, les **zéros** de $F$ sont les racines de $P$ et ses **pôles** les racines de $Q$, avec leurs multiplicités. La **partie entière** de $F$ est le quotient $E$ de la division euclidienne de $P$ par $Q$ : $F = E + \frac{R}{Q}$ avec $\deg R < \deg Q$.

> **Théorème (décomposition en éléments simples).** Soit $F = \frac{P}{Q}$ sous forme irréductible, de partie entière $E$.
>
> 1. **Sur $\C$ :** si $Q = \lambda \prod_{k=1}^{r} (X - z_k)^{m_k}$ avec des $z_k$ distincts, il existe des complexes uniques $a_{k,j}$ tels que
>
> $$
> F = E + \sum_{k=1}^{r} \sum_{j=1}^{m_k} \frac{a_{k,j}}{(X - z_k)^j}.
> $$
>
> 2. **Sur $\R$ :** si $Q$ est réel, ses facteurs irréductibles sont des $(X - a)^m$ et des $(X^2 + pX + q)^m$ avec $p^2 - 4q < 0$ ; la décomposition comporte des termes $\frac{c}{(X - a)^j}$ et des termes $\frac{bX + c}{(X^2 + pX + q)^j}$, $1 \leq j \leq m$, à coefficients réels uniques.

**Calcul des coefficients.** Si $\lambda$ est un **pôle simple**, le coefficient de $\frac{1}{X - \lambda}$ est $\frac{P(\lambda)}{Q'(\lambda)}$ (ou la valeur en $\lambda$ de $(X - \lambda) F$). Si $P$ est scindé, de racines distinctes $z_1, \dots, z_r$ de multiplicités $m_1, \dots, m_r$ :

$$
\frac{P'}{P} = \sum_{k=1}^{r} \frac{m_k}{X - z_k}.
$$

La décomposition sert à calculer des primitives de fonctions rationnelles et des dérivées $k$-ièmes. Exemple : $\dfrac{1}{X^2 - 1} = \dfrac{1}{2} \left( \dfrac{1}{X - 1} - \dfrac{1}{X + 1} \right)$.

## Pièges fréquents

- Oublier que $\deg 0 = -\infty$ dans les calculs de degré.
- Croire qu'un polynôme réel de degré $n$ a $n$ racines réelles : $X^2 + 1$ n'en a aucune.
- Confondre « $P$ a $n$ racines distinctes » et « $P$ a $n$ racines comptées avec multiplicité ».
- Confondre le polynôme $P$ et la fonction $x \mapsto P(x)$ dans un raisonnement de degré ou de dérivation formelle : sur $\K = \R$ ou $\C$, ils se déterminent l'un l'autre, mais les définitions sont différentes.
