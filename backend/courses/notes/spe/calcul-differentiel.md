---
titre: Calcul différentiel
programmes: MP, PSI
ordre: 11
notion: fonctions-plusieurs-variables
---

## Cadre et notations

Dans toute la fiche, $U$ est un **ouvert** de $\R^n$, $f : U \to \R^p$ et $a \in U$. On munit $\R^n$ de sa structure euclidienne usuelle ; $(e_1, \dots, e_n)$ est sa base canonique, et pour $h \in \R^n$ on note $h = (h_1, \dots, h_n)$. Les énoncés s'étendent à des espaces vectoriels normés de dimension finie.

## Dérivées partielles et différentielle

> **Définition.**
>
> 1. Pour $v \in \R^n$, la **dérivée de $f$ en $a$ selon $v$** est, si elle existe, $D_v f(a) = \lim_{t \to 0} \dfrac{f(a + t v) - f(a)}{t}$. Les **dérivées partielles** sont $\dfrac{\partial f}{\partial x_i}(a) = D_{e_i} f(a)$.
> 2. La fonction $f$ est **différentiable en $a$** s'il existe une application linéaire $L : \R^n \to \R^p$ telle que, quand $h \to 0$,
>
> $$
> f(a + h) = f(a) + L(h) + o(\|h\|).
> $$
>
> Cette application est alors unique : c'est la **différentielle** de $f$ en $a$, notée $df(a)$.

> **Proposition.** Si $f$ est différentiable en $a$, alors $f$ est continue en $a$, admet une dérivée selon tout vecteur $v$, et
>
> $$
> D_v f(a) = df(a)(v), \qquad df(a)(h) = \sum_{i=1}^{n} h_i \frac{\partial f}{\partial x_i}(a).
> $$

La réciproque est fausse : la fonction définie sur $\R^2$ par $f(x, y) = \dfrac{xy}{x^2 + y^2}$ si $(x, y) \neq (0, 0)$ et $f(0, 0) = 0$ admet deux dérivées partielles nulles en $(0, 0)$, sans y être continue (elle vaut $\frac{1}{2}$ sur la droite $y = x$ privée de l'origine).

> **Définition et théorème (classe $\mathcal{C}^1$).** La fonction $f$ est de **classe $\mathcal{C}^1$** sur $U$ si ses dérivées partielles existent et sont continues sur $U$. Une fonction de classe $\mathcal{C}^1$ sur $U$ est différentiable en tout point de $U$.

## Règle de la chaîne

> **Théorème.** Soient $f : U \to \R^p$ différentiable en $a$, $V$ un ouvert de $\R^p$ contenant $f(U)$, et $g : V \to \R^q$ différentiable en $f(a)$. Alors $g \circ f$ est différentiable en $a$ et
>
> $$
> d(g \circ f)(a) = dg\big( f(a) \big) \circ df(a).
> $$
>
> Les matrices jacobiennes se multiplient : $J_{g \circ f}(a) = J_g\big( f(a) \big) \, J_f(a)$.

Cas d'une courbe : si $\gamma : I \to U$ est dérivable sur un intervalle $I$ et si $f : U \to \R$ est différentiable, alors $(f \circ \gamma)'(t) = df\big( \gamma(t) \big)\big( \gamma'(t) \big) = \sum_{i=1}^{n} \gamma_i'(t) \, \dfrac{\partial f}{\partial x_i}\big( \gamma(t) \big)$.

## Gradient et points critiques

Dans cette section, $f : U \to \R$. Si $f$ est différentiable en $a$, son **gradient** $\nabla f(a)$ est l'unique vecteur tel que $df(a)(h) = \langle \nabla f(a), h \rangle$ pour tout $h \in \R^n$ ; dans la base canonique, $\nabla f(a) = \left( \frac{\partial f}{\partial x_1}(a), \dots, \frac{\partial f}{\partial x_n}(a) \right)$. Un **point critique** est un point $a$ tel que $\nabla f(a) = 0$.

> **Théorème (condition nécessaire d'extremum local).** Si $f$ est différentiable en $a$ et admet un extremum local en $a$, et si $a$ appartient à l'**ouvert** $U$, alors $\nabla f(a) = 0$.

La réciproque est fausse : $(x, y) \mapsto x^2 - y^2$ a un point critique en $(0, 0)$, qui n'est pas un extremum (point col). Sur une partie qui n'est pas ouverte, un extremum peut être atteint au bord en un point non critique.

## Ordre 2

> **Théorème de Schwarz.** Si $f$ est de classe $\mathcal{C}^2$ sur $U$, alors pour tous $i, j \in [\![1, n]\!]$ : $\dfrac{\partial^2 f}{\partial x_i \partial x_j} = \dfrac{\partial^2 f}{\partial x_j \partial x_i}$.

Pour $f : U \to \R$ de classe $\mathcal{C}^2$, la **matrice hessienne** $H_f(a) = \left( \frac{\partial^2 f}{\partial x_i \partial x_j}(a) \right)_{1 \leq i, j \leq n}$ est donc symétrique réelle, et (formule de Taylor-Young à l'ordre 2) :

$$
f(a + h) = f(a) + \langle \nabla f(a), h \rangle + \frac{1}{2} h^\top H_f(a) h + o(\|h\|^2).
$$

> **Théorème.** Soient $f : U \to \R$ de classe $\mathcal{C}^2$ et $a$ un point critique de $f$.
>
> 1. Si $H_f(a) \in \mathcal{S}_n^{++}(\R)$ (valeurs propres toutes strictement positives), $f$ admet un minimum local strict en $a$.
> 2. Si toutes les valeurs propres de $H_f(a)$ sont strictement négatives, $f$ admet un maximum local strict en $a$.
> 3. Si $H_f(a)$ a une valeur propre strictement positive et une valeur propre strictement négative, $f$ n'a pas d'extremum local en $a$.
> 4. Dans les autres cas (une valeur propre nulle), on ne peut pas conclure sans étude supplémentaire.

Pour $n = 2$, avec $r = \frac{\partial^2 f}{\partial x^2}(a)$, $s = \frac{\partial^2 f}{\partial x \partial y}(a)$ et $t = \frac{\partial^2 f}{\partial y^2}(a)$ : si $rt - s^2 > 0$, il y a un extremum local strict (un minimum si $r > 0$, un maximum si $r < 0$) ; si $rt - s^2 < 0$, il n'y a pas d'extremum ; si $rt - s^2 = 0$, on ne peut pas conclure.

## Pièges fréquents

- Conclure à la différentiabilité (ou à la continuité) parce que les dérivées partielles existent.
- Chercher les extremums d'une fonction sur un fermé seulement parmi ses points critiques : il faut aussi étudier le bord.
- Conclure « minimum local » d'un point critique où la hessienne est seulement positive (avec une valeur propre nulle) : $(x, y) \mapsto x^2 - y^4$ a une hessienne positive en $(0, 0)$ sans y avoir de minimum.
