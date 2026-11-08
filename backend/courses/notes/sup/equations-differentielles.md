---
titre: Équations différentielles linéaires
programmes: MPSI, PCSI
ordre: 7
notion: equations-differentielles
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$, $I$ est un intervalle, et les fonctions $a, b, f : I \to \K$ sont **continues**. Une **solution** sur $I$ d'une équation différentielle est une fonction dérivable (deux fois dérivable pour l'ordre 2) sur $I$ qui vérifie l'équation en tout point de $I$.

## Équations du premier ordre

On considère l'équation $(E) : y' + a(x) y = b(x)$ et l'équation homogène associée $(H) : y' + a(x) y = 0$.

> **Théorème.** Soit $A$ une primitive de $a$ sur $I$.
>
> 1. Les solutions de $(H)$ sur $I$ sont les fonctions $x \mapsto \lambda e^{-A(x)}$, $\lambda \in \K$.
> 2. Si $y_p$ est une solution de $(E)$ sur $I$, les solutions de $(E)$ sur $I$ sont les fonctions $y_p + y_h$, où $y_h$ décrit les solutions de $(H)$.
> 3. **Problème de Cauchy :** pour tous $x_0 \in I$ et $y_0 \in \K$, il existe une unique solution $y$ de $(E)$ sur $I$ telle que $y(x_0) = y_0$.

**Variation de la constante.** La fonction $y : x \mapsto \lambda(x) e^{-A(x)}$, avec $\lambda$ dérivable sur $I$, est solution de $(E)$ si et seulement si $\lambda'(x) = b(x) e^{A(x)}$ pour tout $x \in I$.

**Principe de superposition.** Si $y_1$ est solution de $y' + a y = b_1$ et $y_2$ de $y' + a y = b_2$, alors $\lambda y_1 + \mu y_2$ est solution de $y' + a y = \lambda b_1 + \mu b_2$.

**Équation non normalisée.** Pour $\alpha(x) y' + \beta(x) y = \gamma(x)$, on résout sur chaque intervalle où $\alpha$ ne s'annule pas, en divisant par $\alpha$. Aux points où $\alpha$ s'annule, on étudie à part le **raccordement** des solutions : il peut n'y avoir aucune solution sur l'intervalle entier, ou une infinité.

## Équations du second ordre à coefficients constants

Soient $p, q \in \K$ et $(E) : y'' + p y' + q y = f(x)$, d'équation homogène $(H) : y'' + p y' + q y = 0$. L'**équation caractéristique** est $r^2 + p r + q = 0$.

> **Théorème (solutions complexes).** On suppose $\K = \C$.
>
> 1. Si l'équation caractéristique a deux racines distinctes $r_1$ et $r_2$, les solutions de $(H)$ sur $\R$ sont les fonctions $x \mapsto \lambda e^{r_1 x} + \mu e^{r_2 x}$, $(\lambda, \mu) \in \C^2$.
> 2. Si elle a une racine double $r$, ce sont les fonctions $x \mapsto (\lambda + \mu x) e^{r x}$, $(\lambda, \mu) \in \C^2$.

> **Théorème (solutions réelles).** On suppose $p, q \in \R$ et on cherche les solutions à valeurs réelles. Soit $\Delta = p^2 - 4q$.
>
> 1. Si $\Delta > 0$, de racines réelles $r_1 \neq r_2$ : $x \mapsto \lambda e^{r_1 x} + \mu e^{r_2 x}$, $(\lambda, \mu) \in \R^2$.
> 2. Si $\Delta = 0$, de racine double $r$ : $x \mapsto (\lambda + \mu x) e^{r x}$, $(\lambda, \mu) \in \R^2$.
> 3. Si $\Delta < 0$, de racines $\alpha \pm i\omega$ avec $\alpha \in \R$ et $\omega > 0$ : $x \mapsto e^{\alpha x} \big( \lambda \cos(\omega x) + \mu \sin(\omega x) \big)$, $(\lambda, \mu) \in \R^2$.

> **Théorème.** Les solutions de $(E)$ sur $I$ sont les $y_p + y_h$, où $y_p$ est une solution particulière de $(E)$ sur $I$ et $y_h$ décrit les solutions de $(H)$. Pour tous $x_0 \in I$ et $(y_0, y_1) \in \K^2$, il existe une unique solution $y$ de $(E)$ sur $I$ telle que $y(x_0) = y_0$ et $y'(x_0) = y_1$.

**Second membre $f(x) = A e^{m x}$** ($A, m \in \C$). Il existe une solution particulière de la forme $x \mapsto B x^k e^{m x}$ avec $B \in \C$, où $k = 0$ si $m$ n'est pas racine de l'équation caractéristique, $k = 1$ si $m$ en est racine simple, $k = 2$ si $m$ en est racine double. Pour $f(x) = A \cos(\omega x)$ ou $A \sin(\omega x)$ avec $p, q, A, \omega$ réels, on résout avec $A e^{i\omega x}$ puis on prend la partie réelle ou la partie imaginaire.

## Pièges fréquents

- Résoudre $\alpha(x) y' + \beta(x) y = \gamma(x)$ sans se placer sur un intervalle où $\alpha$ ne s'annule pas.
- Écrire les solutions réelles avec des constantes complexes, ou l'inverse.
- Oublier le facteur $x^k$ quand le coefficient $m$ du second membre est racine de l'équation caractéristique.
- Ajuster les constantes d'un problème de Cauchy sur la solution homogène seule, avant d'avoir ajouté la solution particulière.
