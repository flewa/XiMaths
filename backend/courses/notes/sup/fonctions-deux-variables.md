---
titre: Fonctions de deux variables
programmes: MPSI, MP2I
ordre: 21
notion: fonctions-plusieurs-variables
---

## Cadre et notations

On munit $\R^2$ de la norme euclidienne $\|(x, y)\| = \sqrt{x^2 + y^2}$. La **boule ouverte** de centre $a$ et de rayon $r > 0$ est $B(a, r) = \{ m \in \R^2 : \|m - a\| < r \}$. Une partie $U$ de $\R^2$ est **ouverte** si, pour tout $a \in U$, il existe $r > 0$ tel que $B(a, r) \subset U$. Dans toute la fiche, $U$ est un ouvert de $\R^2$ et $f : U \to \R$. Le graphe de $f$ est la surface d'équation $z = f(x, y)$.

**Continuité.** La fonction $f$ est continue en $a \in U$ si $f(m) \to f(a)$ quand $\|m - a\| \to 0$. Sommes, produits, quotients et composées de fonctions continues sont continues.

## Dérivées partielles

> **Définition.** Soit $(x_0, y_0) \in U$. La **dérivée partielle** de $f$ par rapport à $x$ en $(x_0, y_0)$, si elle existe, est
>
> $$
> \frac{\partial f}{\partial x}(x_0, y_0) = \lim_{t \to 0} \frac{f(x_0 + t, y_0) - f(x_0, y_0)}{t},
> $$
>
> c'est-à-dire la dérivée en $x_0$ de $x \mapsto f(x, y_0)$ ; de même pour $\dfrac{\partial f}{\partial y}$. La fonction $f$ est de **classe $\mathcal{C}^1$** sur $U$ si ses deux dérivées partielles existent et sont continues sur $U$.

L'existence des dérivées partielles n'entraîne pas la continuité : $f(x, y) = \dfrac{xy}{x^2 + y^2}$, prolongée par $f(0, 0) = 0$, a des dérivées partielles nulles en $(0, 0)$, mais $f(t, t) = \frac{1}{2}$ pour $t \neq 0$, donc $f$ n'est pas continue en $(0, 0)$.

> **Théorème (développement limité à l'ordre 1).** Si $f$ est de classe $\mathcal{C}^1$ sur $U$ et $(x_0, y_0) \in U$, alors, quand $(h, k) \to (0, 0)$,
>
> $$
> f(x_0 + h, y_0 + k) = f(x_0, y_0) + \frac{\partial f}{\partial x}(x_0, y_0) \, h + \frac{\partial f}{\partial y}(x_0, y_0) \, k + o\big( \|(h, k)\| \big).
> $$

Le **plan tangent** à la surface $z = f(x, y)$ au point $(x_0, y_0, f(x_0, y_0))$ a pour équation $z - z_0 = \frac{\partial f}{\partial x}(x_0, y_0)(x - x_0) + \frac{\partial f}{\partial y}(x_0, y_0)(y - y_0)$, avec $z_0 = f(x_0, y_0)$.

## Gradient et règle de la chaîne

Pour $f$ de classe $\mathcal{C}^1$, le **gradient** en $a = (x_0, y_0)$ est le vecteur $\nabla f(a) = \left( \dfrac{\partial f}{\partial x}(a), \dfrac{\partial f}{\partial y}(a) \right)$. Le développement limité s'écrit $f(a + v) = f(a) + \langle \nabla f(a), v \rangle + o(\|v\|)$, et la **dérivée selon le vecteur** $u$ est

$$
\lim_{t \to 0} \frac{f(a + t u) - f(a)}{t} = \langle \nabla f(a), u \rangle.
$$

Si $\nabla f(a) \neq 0$, parmi les vecteurs unitaires $u$, cette dérivée est maximale pour $u = \dfrac{\nabla f(a)}{\|\nabla f(a)\|}$ : le gradient indique la direction dans laquelle $f$ croît le plus vite.

> **Théorème (règle de la chaîne).** Soient $f$ de classe $\mathcal{C}^1$ sur $U$ et $x, y : I \to \R$ de classe $\mathcal{C}^1$ sur un intervalle $I$, avec $(x(t), y(t)) \in U$ pour tout $t$. Alors $g : t \mapsto f\big( x(t), y(t) \big)$ est de classe $\mathcal{C}^1$ et
>
> $$
> g'(t) = \frac{\partial f}{\partial x}\big( x(t), y(t) \big) \, x'(t) + \frac{\partial f}{\partial y}\big( x(t), y(t) \big) \, y'(t) = \big\langle \nabla f(\gamma(t)), \gamma'(t) \big\rangle,
> $$
>
> où $\gamma(t) = (x(t), y(t))$.

Conséquence : le gradient est orthogonal aux **lignes de niveau** de $f$. De même, si $\varphi$ et $\psi$ sont de classe $\mathcal{C}^1$ et si $g(u, v) = f\big( \varphi(u, v), \psi(u, v) \big)$, alors

$$
\frac{\partial g}{\partial u} = \frac{\partial f}{\partial x} \, \frac{\partial \varphi}{\partial u} + \frac{\partial f}{\partial y} \, \frac{\partial \psi}{\partial u},
$$

les dérivées de $f$ étant prises en $\big( \varphi(u, v), \psi(u, v) \big)$ ; de même pour $\dfrac{\partial g}{\partial v}$. Exemple : en coordonnées polaires, $g(r, \theta) = f(r \cos \theta, r \sin \theta)$ vérifie $\dfrac{\partial g}{\partial r} = \cos \theta \, \dfrac{\partial f}{\partial x} + \sin \theta \, \dfrac{\partial f}{\partial y}$.

## Extremums

La fonction $f$ admet un **maximum local** en $a$ s'il existe $r > 0$ tel que $f(m) \leq f(a)$ pour tout $m \in U \cap B(a, r)$ ; maximum **global** si $f(m) \leq f(a)$ pour tout $m \in U$. De même pour les minimums. Un **point critique** de $f$ est un point où $\nabla f$ s'annule.

> **Théorème.** Si $f$ est de classe $\mathcal{C}^1$ sur l'ouvert $U$ et admet un extremum local en $a \in U$, alors $a$ est un point critique : $\nabla f(a) = 0$.

La réciproque est fausse : $(x, y) \mapsto x^2 - y^2$ a un point critique en $(0, 0)$ sans y avoir d'extremum (point col). Pour conclure, on étudie le signe de $f(a + v) - f(a)$ au voisinage de $a$.

## Pièges fréquents

- Déduire la continuité de l'existence des dérivées partielles.
- Chercher les extremums seulement parmi les points critiques quand $f$ est définie sur une partie qui n'est pas ouverte : un extremum peut être atteint au bord.
- Oublier, dans la règle de la chaîne, que les dérivées partielles de $f$ sont évaluées au point $\big( x(t), y(t) \big)$ et non en $t$.
