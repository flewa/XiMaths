---
titre: Inégalités classiques
programmes: MPSI, MP2I, PCSI, PTSI, BCPST1, L1
ordre: 26
notion: nombres-reels
---

## Cadre et notations

Les nombres sont réels, sauf mention contraire. Une inégalité **large** ($\leq$) se conserve par passage à la limite ; une inégalité stricte devient large à la limite. Pour chaque inégalité, le **cas d'égalité** compte autant que l'inégalité : c'est lui qui sert dans les exercices d'optimisation.

Le cours : [Sommes, inégalités et trigonométrie](/rappels/calcul-algebrique), [Espaces préhilbertiens réels](/rappels/espaces-prehilbertiens) et [Probabilités sur un univers fini](/rappels/probabilites-univers-fini).

## Valeur absolue et inégalité triangulaire

Pour $x, y \in \C$ (en particulier réels) :

$$
\big\lvert \lvert x \rvert - \lvert y \rvert \big\rvert \leq \lvert x + y \rvert \leq \lvert x \rvert + \lvert y \rvert, \qquad \left\lvert \sum_{k=1}^{n} x_k \right\rvert \leq \sum_{k=1}^{n} \lvert x_k \rvert.
$$

Pour des complexes non nuls, l'égalité $\lvert x + y \rvert = \lvert x \rvert + \lvert y \rvert$ a lieu si et seulement si $x$ et $y$ ont le même argument. Pour $f$ continue par morceaux sur $[a, b]$ avec $a \leq b$ :

$$
\left\lvert \int_a^b f(t) \, dt \right\rvert \leq \int_a^b \lvert f(t) \rvert \, dt \leq (b - a) \sup_{[a, b]} \lvert f \rvert.
$$

## Inégalités usuelles de fonctions

$$
e^x \geq 1 + x \quad (x \in \R), \qquad \ln(1 + x) \leq x \quad (x > -1), \qquad \lvert \sin x \rvert \leq \lvert x \rvert \quad (x \in \R),
$$

$$
\cos x \geq 1 - \frac{x^2}{2} \quad (x \in \R), \qquad \sin x \geq \frac{2}{\pi} x \quad \left( 0 \leq x \leq \frac{\pi}{2} \right), \qquad \arctan x \leq x \quad (x \geq 0).
$$

Les trois premières sont des inégalités de convexité (tangente en $0$), avec égalité seulement en $x = 0$. La minoration de $\sin$ (inégalité de Jordan) vient de la concavité de $\sin$ sur $\left[ 0, \frac{\pi}{2} \right]$ : la courbe est au-dessus de sa corde.

**Bernoulli.** Pour $x \geq -1$ et $n \in \N$, $(1 + x)^n \geq 1 + nx$.

## Moyennes

Pour $a, b \geq 0$ :

$$
\sqrt{ab} \leq \frac{a + b}{2}, \qquad \text{c'est-à-dire} \quad 2ab \leq a^2 + b^2 \ \text{ pour tous réels } a, b,
$$

avec égalité si et seulement si $a = b$ ; cela vient de $(a - b)^2 \geq 0$.

**Moyennes arithmétique, géométrique, harmonique.** Pour $x_1, \dots, x_n > 0$ :

$$
\frac{n}{\dfrac{1}{x_1} + \dots + \dfrac{1}{x_n}} \leq \sqrt[n]{x_1 \cdots x_n} \leq \frac{x_1 + \dots + x_n}{n},
$$

avec égalité si et seulement si les $x_k$ sont tous égaux. L'inégalité de droite découle de la concavité du logarithme.

## Inégalité de Cauchy-Schwarz

**Sommes.** Pour des réels $a_1, \dots, a_n$ et $b_1, \dots, b_n$ :

$$
\left( \sum_{k=1}^{n} a_k b_k \right)^2 \leq \left( \sum_{k=1}^{n} a_k^2 \right) \left( \sum_{k=1}^{n} b_k^2 \right),
$$

avec égalité si et seulement si les familles $(a_k)$ et $(b_k)$ sont proportionnelles. Avec $b_k = 1$ : $\left( \sum a_k \right)^2 \leq n \sum a_k^2$.

**Intégrales.** Pour $f, g$ continues sur $[a, b]$ :

$$
\left( \int_a^b f(t) g(t) \, dt \right)^2 \leq \int_a^b f(t)^2 \, dt \int_a^b g(t)^2 \, dt.
$$

**Espace préhilbertien.** Pour tous $x, y$ : $\lvert \langle x, y \rangle \rvert \leq \lVert x \rVert \, \lVert y \rVert$, avec égalité si et seulement si $x$ et $y$ sont colinéaires.

## Convexité : Jensen et Young

Si $f$ est **convexe** sur un intervalle $I$, pour $x_1, \dots, x_n \in I$ et $\lambda_1, \dots, \lambda_n \geq 0$ de somme $1$ :

$$
f\left( \sum_{k=1}^{n} \lambda_k x_k \right) \leq \sum_{k=1}^{n} \lambda_k f(x_k).
$$

Une fonction convexe est au-dessus de ses tangentes et au-dessous de ses cordes ; une fonction deux fois dérivable est convexe si et seulement si $f'' \geq 0$.

**Young.** Pour $a, b \geq 0$ et $p, q > 1$ tels que $\frac{1}{p} + \frac{1}{q} = 1$ :

$$
ab \leq \frac{a^p}{p} + \frac{b^q}{q}.
$$

Elle se déduit de la concavité du logarithme ; avec $p = q = 2$, on retrouve $ab \leq \frac{a^2 + b^2}{2}$.

## Inégalités en probabilités

Soit $X$ une variable aléatoire réelle.

**Markov.** Si $X \geq 0$ admet une espérance, pour tout $a > 0$ :

$$
P(X \geq a) \leq \frac{E(X)}{a}.
$$

**Bienaymé-Tchebychev.** Si $X$ admet une variance, pour tout $\varepsilon > 0$ :

$$
P\big( \lvert X - E(X) \rvert \geq \varepsilon \big) \leq \frac{V(X)}{\varepsilon^2}.
$$

## Pièges fréquents

- Multiplier les deux membres par un nombre **négatif** renverse l'inégalité ; par un nombre dont on ignore le signe, on ne peut rien conclure.
- On ne **soustrait** pas et on ne **divise** pas deux inégalités membre à membre : de $a \leq b$ et $c \leq d$, on ne tire ni $a - c \leq b - d$ ni $\frac{a}{c} \leq \frac{b}{d}$.
- Élever au carré ne conserve l'ordre qu'entre nombres **positifs** : $-3 \leq 2$ mais $9 > 4$.
- Une inégalité ne vaut que sur l'intervalle indiqué : $\sin x \geq \frac{2}{\pi} x$ est fausse dès que $x > \frac{\pi}{2}$ (par exemple en $x = \pi$).
