---
titre: Lemme de décomposition des noyaux
programmes: MP, MPI, L2
statut: au-programme
ordre: 1
notion: reduction
---

## Énoncé

> **Théorème (lemme des noyaux).** Soient $E$ un $\K$-espace vectoriel, $u \in \mathcal{L}(E)$, et $P_1, \dots, P_r \in \K[X]$ deux à deux premiers entre eux, de produit $P = P_1 \cdots P_r$. Alors
>
> $$
> \operatorname{Ker} P(u) = \bigoplus_{i=1}^{r} \operatorname{Ker} P_i(u).
> $$
>
> De plus, les projecteurs associés à cette décomposition sont des polynômes en $u$.

Aucune hypothèse de dimension n'est nécessaire.

## Idée

Une relation de Bézout $U_1 P_1 + U_2 P_2 = 1$, évaluée en $u$, fabrique directement la décomposition de chaque vecteur : $x = U_2(u) P_2(u)(x) + U_1(u) P_1(u)(x)$. On traite deux facteurs, puis on conclut par récurrence.

## Démonstration

On utilise deux faits : $Q \mapsto Q(u)$ est un morphisme d'anneaux de $\K[X]$ dans $\mathcal{L}(E)$, donc $(AB)(u) = A(u) \circ B(u)$ ; et deux polynômes en $u$ commutent, puisque $A(u) \circ B(u) = (AB)(u) = (BA)(u) = B(u) \circ A(u)$.

**Cas de deux facteurs.** Soient $P_1$ et $P_2$ premiers entre eux et $P = P_1 P_2$. Par le théorème de Bézout, il existe $U_1, U_2 \in \K[X]$ tels que $U_1 P_1 + U_2 P_2 = 1$, d'où

$$
U_1(u) \circ P_1(u) + U_2(u) \circ P_2(u) = \mathrm{id}_E. \qquad (\ast)
$$

*Inclusion.* Si $x \in \operatorname{Ker} P_1(u)$, alors $P(u)(x) = P_2(u)\big( P_1(u)(x) \big) = 0$. Donc $\operatorname{Ker} P_1(u) \subset \operatorname{Ker} P(u)$, et de même pour $P_2$.

*La somme est directe.* Si $x \in \operatorname{Ker} P_1(u) \cap \operatorname{Ker} P_2(u)$, la relation $(\ast)$ appliquée à $x$ donne $x = U_1(u)\big( P_1(u)(x) \big) + U_2(u)\big( P_2(u)(x) \big) = 0$.

*La somme est $\operatorname{Ker} P(u)$ tout entier.* Soit $x \in \operatorname{Ker} P(u)$. On pose $x_1 = U_2(u) P_2(u)(x)$ et $x_2 = U_1(u) P_1(u)(x)$, de sorte que $x = x_1 + x_2$ par $(\ast)$. Alors

$$
P_1(u)(x_1) = U_2(u)\big( P_1(u) P_2(u)(x) \big) = U_2(u)\big( P(u)(x) \big) = 0,
$$

donc $x_1 \in \operatorname{Ker} P_1(u)$ ; de même $x_2 \in \operatorname{Ker} P_2(u)$. Ainsi $\operatorname{Ker} P(u) = \operatorname{Ker} P_1(u) \oplus \operatorname{Ker} P_2(u)$, et le projecteur sur $\operatorname{Ker} P_1(u)$ parallèlement à $\operatorname{Ker} P_2(u)$ est la restriction de $U_2(u) P_2(u)$ : c'est un polynôme en $u$.

**Récurrence sur $r$.** Le cas $r = 1$ est évident et le cas $r = 2$ vient d'être traité. Supposons le résultat vrai pour $r - 1 \geq 2$ facteurs, et soient $P_1, \dots, P_r$ deux à deux premiers entre eux. Le polynôme $P_1$ est premier avec $Q = P_2 \cdots P_r$ : un produit de polynômes premiers avec $P_1$ est premier avec $P_1$ (conséquence du lemme de Gauss). Le cas $r = 2$ donne

$$
\operatorname{Ker} P(u) = \operatorname{Ker} P_1(u) \oplus \operatorname{Ker} Q(u),
$$

et l'hypothèse de récurrence, appliquée à $P_2, \dots, P_r$, donne $\operatorname{Ker} Q(u) = \bigoplus_{i=2}^{r} \operatorname{Ker} P_i(u)$. Par associativité des sommes directes, $\operatorname{Ker} P(u) = \bigoplus_{i=1}^{r} \operatorname{Ker} P_i(u)$. Les projecteurs sont des composées de polynômes en $u$, donc des polynômes en $u$.

## Remarques

- Si $P$ annule $u$, alors $\operatorname{Ker} P(u) = E$ : on obtient une décomposition de tout l'espace en sous-espaces stables par $u$. C'est le point de départ de la caractérisation des endomorphismes diagonalisables et des sous-espaces caractéristiques.
- L'hypothèse « deux à deux premiers entre eux » est indispensable : pour $u = 0$ et $P_1 = P_2 = X$, on a $\operatorname{Ker} P_1(u) = \operatorname{Ker} P_2(u) = E$, et la somme n'est pas directe dès que $E \neq \{0\}$.
