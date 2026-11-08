---
titre: Dérivation
programmes: MPSI, PCSI
ordre: 4
notion: derivation
---

## Cadre et notations

Dans toute la fiche, $I$ est un intervalle, $f : I \to \R$ et $a \in I$. Sauf mention contraire, $a < b$ désignent deux réels.

## Nombre dérivé

> **Définition.** La fonction $f$ est **dérivable en $a$** si le taux d'accroissement $\dfrac{f(x) - f(a)}{x - a}$ admet une limite finie quand $x$ tend vers $a$ avec $x \in I \setminus \{a\}$. Cette limite est notée $f'(a)$.

De façon équivalente, $f$ est dérivable en $a$ si et seulement s'il existe $\ell \in \R$ tel que $f(a + h) = f(a) + \ell h + o(h)$ quand $h \to 0$ ; alors $\ell = f'(a)$.

Dérivable en $a$ $\implies$ continue en $a$. La réciproque est fausse : $x \mapsto |x|$ est continue en $0$ et n'y est pas dérivable.

> **Proposition (opérations).** Si $f$ et $g$ sont dérivables en $a$, alors $f + g$, $fg$ et, si $g(a) \neq 0$, $\frac{f}{g}$ sont dérivables en $a$, avec $(fg)'(a) = f'(a) g(a) + f(a) g'(a)$ et $\left( \frac{f}{g} \right)'(a) = \frac{f'(a) g(a) - f(a) g'(a)}{g(a)^2}$.
>
> Si $f$ est dérivable en $a$ et si $g$, définie sur un intervalle contenant $f(I)$, est dérivable en $f(a)$, alors $g \circ f$ est dérivable en $a$ et $(g \circ f)'(a) = f'(a) \, g'\big( f(a) \big)$.

> **Théorème (dérivée de la réciproque).** Soit $f$ continue et strictement monotone sur $I$, et $b = f(a)$. Si $f$ est dérivable en $a$ et $f'(a) \neq 0$, alors $f^{-1}$ est dérivable en $b$ et
>
> $$
> (f^{-1})'(b) = \frac{1}{f'\big( f^{-1}(b) \big)}.
> $$
>
> Si $f'(a) = 0$, la fonction $f^{-1}$ n'est pas dérivable en $b$ : son graphe y a une tangente verticale.

## Extremums et théorème de Rolle

> **Proposition (condition nécessaire d'extremum local).** Si $f$ admet un extremum local en un point $a$ **intérieur** à $I$ et si $f$ est dérivable en $a$, alors $f'(a) = 0$.

Les deux hypothèses comptent, et la réciproque est fausse :

- $x \mapsto x^3$ a une dérivée nulle en $0$ sans y avoir d'extremum ;
- $x \mapsto x$ sur $[0, 1]$ a un minimum en $0$, extrémité de l'intervalle, où sa dérivée vaut $1$.

> **Théorème (Rolle).** Si $f$ est continue sur $[a, b]$, dérivable sur $]a, b[$, et si $f(a) = f(b)$, il existe $c \in \, ]a, b[$ tel que $f'(c) = 0$.

> **Théorème (accroissements finis).** Si $f$ est continue sur $[a, b]$ et dérivable sur $]a, b[$, il existe $c \in \, ]a, b[$ tel que
>
> $$
> f(b) - f(a) = f'(c) (b - a).
> $$

> **Théorème (inégalité des accroissements finis).** Si $f$ est dérivable sur $I$ et s'il existe $k \in \R_+$ tel que $|f'(x)| \leq k$ pour tout $x \in I$, alors $f$ est $k$-lipschitzienne sur $I$.

## Monotonie

> **Théorème.** Soit $f$ dérivable sur l'intervalle $I$.
>
> 1. $f$ est croissante sur $I$ si et seulement si $f' \geq 0$ sur $I$.
> 2. $f$ est constante sur $I$ si et seulement si $f' = 0$ sur $I$.
> 3. Si $f' \geq 0$ sur $I$ et si $f'$ ne s'annule qu'en un nombre fini de points, alors $f$ est strictement croissante sur $I$.

L'hypothèse « $I$ est un intervalle » est indispensable : la fonction égale à $0$ sur $]{-}\infty, 0[$ et à $1$ sur $]0, +\infty[$ a une dérivée nulle sans être constante sur $\R^*$.

> **Théorème (limite de la dérivée).** Soit $f$ continue sur $I$, dérivable sur $I \setminus \{a\}$. Si $f'(x)$ tend vers $\ell \in \R$ quand $x \to a$, $x \neq a$, alors $f$ est dérivable en $a$ et $f'(a) = \ell$. Si $f'(x)$ tend vers $+\infty$ ou $-\infty$, alors $f$ n'est pas dérivable en $a$.

## Dérivées successives

Pour $n \in \N$, $f$ est de **classe $\mathcal{C}^n$** sur $I$ si elle est $n$ fois dérivable sur $I$ et si $f^{(n)}$ est continue sur $I$ ; elle est de classe $\mathcal{C}^\infty$ si elle est de classe $\mathcal{C}^n$ pour tout $n$.

> **Formule de Leibniz.** Si $f$ et $g$ sont $n$ fois dérivables sur $I$, alors $fg$ l'est aussi et
>
> $$
> (fg)^{(n)} = \sum_{k=0}^{n} \binom{n}{k} f^{(k)} g^{(n-k)}.
> $$

## Convexité

> **Définition.** La fonction $f$ est **convexe** sur $I$ si, pour tous $x, y \in I$ et tout $\lambda \in [0, 1]$,
>
> $$
> f\big( \lambda x + (1 - \lambda) y \big) \leq \lambda f(x) + (1 - \lambda) f(y).
> $$

> **Théorème.**
>
> 1. Si $f$ est dérivable sur $I$ : $f$ est convexe sur $I$ si et seulement si $f'$ est croissante sur $I$. Le graphe d'une fonction convexe dérivable est alors au-dessus de chacune de ses tangentes.
> 2. Si $f$ est deux fois dérivable sur $I$ : $f$ est convexe sur $I$ si et seulement si $f'' \geq 0$ sur $I$.

## Fonctions à valeurs complexes

Pour $f : I \to \C$, on dit que $f$ est dérivable si $\operatorname{Re} f$ et $\operatorname{Im} f$ le sont, et $f' = (\operatorname{Re} f)' + i (\operatorname{Im} f)'$. L'inégalité des accroissements finis reste vraie pour $f$ de classe $\mathcal{C}^1$ sur $I$ : si $|f'| \leq k$ sur $I$, alors $|f(y) - f(x)| \leq k |y - x|$ pour tous $x, y \in I$.

**Le théorème de Rolle et l'égalité des accroissements finis sont faux pour les fonctions à valeurs complexes :** $t \mapsto e^{it}$ prend la même valeur en $0$ et en $2\pi$, et sa dérivée $t \mapsto i e^{it}$ ne s'annule jamais.

## Pièges fréquents

- Chercher les extremums seulement parmi les points où $f'$ s'annule : il faut aussi regarder les extrémités de l'intervalle et les points où $f$ n'est pas dérivable.
- Déduire « $f$ strictement croissante » de « $f' \geq 0$ » : il faut par exemple que $f'$ ne s'annule qu'en un nombre fini de points.
- Appliquer le théorème de la limite de la dérivée sans vérifier la continuité de $f$ en $a$.
