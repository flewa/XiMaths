---
titre: Équations et systèmes différentiels linéaires
programmes: MP, PSI
ordre: 9
notion: equations-differentielles
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$, $n \in \N^*$, $I$ est un intervalle, et $A : I \to \mathcal{M}_n(\K)$, $B : I \to \mathcal{M}_{n,1}(\K)$ sont **continues**. On étudie le système $(S) : X' = A(t) X + B(t)$, et le système homogène $(S_0) : X' = A(t) X$. Une solution est une fonction $X : I \to \mathcal{M}_{n,1}(\K)$ dérivable qui vérifie le système en tout point de $I$.

## Théorème de Cauchy linéaire et structure

> **Théorème de Cauchy linéaire.** Pour tous $t_0 \in I$ et $X_0 \in \mathcal{M}_{n,1}(\K)$, il existe une unique solution $X$ de $(S)$ **définie sur $I$ tout entier** telle que $X(t_0) = X_0$.

> **Théorème (structure).**
>
> 1. L'ensemble $\mathcal{S}_0$ des solutions de $(S_0)$ sur $I$ est un sous-espace vectoriel de dimension $n$ ; pour tout $t_0 \in I$, l'application $X \mapsto X(t_0)$ est un isomorphisme de $\mathcal{S}_0$ sur $\mathcal{M}_{n,1}(\K)$.
> 2. Les solutions de $(S)$ sur $I$ sont les $X_p + X_0$, où $X_p$ est une solution particulière de $(S)$ et $X_0$ décrit $\mathcal{S}_0$.

## Systèmes à coefficients constants

Dans cette section, $A \in \mathcal{M}_n(\K)$ est une matrice constante.

> **Définition (exponentielle de matrice).** Pour $M \in \mathcal{M}_n(\K)$, la série $\sum \frac{M^k}{k!}$ converge ; sa somme est notée $e^M$ ou $\exp(M)$.

> **Proposition.**
>
> 1. Si $M$ et $N$ commutent, alors $e^{M + N} = e^M e^N$ ; en particulier $e^M$ est inversible, d'inverse $e^{-M}$.
> 2. Pour $P \in GL_n(\K)$, $e^{P M P^{-1}} = P e^M P^{-1}$ ; pour $D = \operatorname{diag}(\lambda_1, \dots, \lambda_n)$, $e^D = \operatorname{diag}(e^{\lambda_1}, \dots, e^{\lambda_n})$.
> 3. La fonction $t \mapsto e^{tA}$ est de classe $\mathcal{C}^1$ sur $\R$, de dérivée $t \mapsto A e^{tA} = e^{tA} A$.

> **Théorème.** La solution de $X' = AX$ sur $\R$ telle que $X(t_0) = X_0$ est $t \mapsto e^{(t - t_0) A} X_0$.

**En pratique, si $A$ est diagonalisable** : soit $(V_1, \dots, V_n)$ une base de vecteurs propres, associés aux valeurs propres $\lambda_1, \dots, \lambda_n$. Les solutions de $X' = AX$ sont les fonctions $t \mapsto \sum_{i=1}^{n} c_i e^{\lambda_i t} V_i$, $(c_1, \dots, c_n) \in \K^n$. Si $A$ est seulement trigonalisable, on pose $X = PY$ avec $P^{-1} A P$ triangulaire, et on résout le système triangulaire en $Y$ en partant de la dernière ligne.

## Équations scalaires d'ordre 2

Soient $a, b, c : I \to \K$ continues, et $(E) : y'' + a(t) y' + b(t) y = c(t)$, d'équation homogène $(E_0)$. En posant $X = \begin{pmatrix} y \\ y' \end{pmatrix}$, $(E)$ s'écrit comme un système de taille $2$ ; d'où :

> **Théorème.**
>
> 1. Pour tous $t_0 \in I$ et $(y_0, y_1) \in \K^2$, il existe une unique solution de $(E)$ sur $I$ telle que $y(t_0) = y_0$ et $y'(t_0) = y_1$.
> 2. Les solutions de $(E_0)$ sur $I$ forment un espace vectoriel de dimension $2$ ; celles de $(E)$ sont les $y_p + y_0$, avec $y_p$ solution particulière et $y_0$ solution de $(E_0)$.

> **Wronskien.** Pour deux solutions $y_1, y_2$ de $(E_0)$, on pose $W = y_1 y_2' - y_1' y_2$. Alors $W' = -a W$ sur $I$ ; $W$ est donc soit identiquement nul, soit ne s'annule jamais sur $I$. Le couple $(y_1, y_2)$ est une base de l'espace des solutions de $(E_0)$ si et seulement si $W(t_0) \neq 0$ pour un (tout) $t_0 \in I$.

**Variation des constantes.** Si $(y_1, y_2)$ est une base des solutions de $(E_0)$, on cherche une solution de $(E)$ sous la forme $y = \lambda_1 y_1 + \lambda_2 y_2$, avec $\lambda_1, \lambda_2$ dérivables telles que

$$
\lambda_1' y_1 + \lambda_2' y_2 = 0 \qquad \text{et} \qquad \lambda_1' y_1' + \lambda_2' y_2' = c.
$$

Ce système en $(\lambda_1', \lambda_2')$ a pour déterminant le wronskien, qui ne s'annule pas.

**Une solution connue.** Si $y_1$ est une solution de $(E_0)$ qui ne s'annule pas sur un intervalle $J \subset I$, on cherche les solutions sous la forme $y = z y_1$ : l'équation obtenue est du premier ordre en $z'$.

**Solutions développables en série entière.** On cherche $y(t) = \sum a_n t^n$, on obtient une relation de récurrence sur les $a_n$, on détermine le rayon de convergence $R$, puis on vérifie que la somme est solution sur $]{-}R, R[ \, \cap \, I$.

## Pièges fréquents

- Appliquer le théorème de Cauchy linéaire à $\alpha(t) y'' + \beta(t) y' + \gamma(t) y = \delta(t)$ sur un intervalle où $\alpha$ s'annule : l'équation doit d'abord être mise sous forme normalisée.
- Écrire $e^{A + B} = e^A e^B$ pour des matrices qui ne commutent pas.
- Conclure que deux solutions forment une base parce qu'elles ne sont pas proportionnelles en un point : il faut un wronskien non nul.
