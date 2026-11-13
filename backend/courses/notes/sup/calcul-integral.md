---
titre: Intégration sur un segment
programmes: MPSI, MP2I, PCSI
ordre: 16
notion: calcul-integral
---

## Cadre et notations

Dans toute la fiche, $a < b$ sont deux réels et $I$ est un intervalle. Une fonction $f : [a, b] \to \R$ est **continue par morceaux** s'il existe une subdivision $a = x_0 < x_1 < \dots < x_p = b$ telle que, pour tout $i \in [\![1, p]\!]$, la restriction de $f$ à $]x_{i-1}, x_i[$ soit continue et admette des limites finies en $x_{i-1}$ et en $x_i$.

Les fonctions continues par morceaux sur $[a, b]$ forment un espace vectoriel et un anneau. Leur intégrale $\int_a^b f$ est définie (le programme n'impose pas de construction ; on utilise la continuité uniforme des fonctions continues sur un segment, théorème de Heine) et s'interprète comme une aire algébrique. On pose $\int_b^a f = -\int_a^b f$ et $\int_a^a f = 0$.

## Propriétés de l'intégrale

> **Proposition.** Soient $f, g$ continues par morceaux sur $[a, b]$ et $\lambda, \mu \in \R$.
>
> 1. **Linéarité :** $\int_a^b (\lambda f + \mu g) = \lambda \int_a^b f + \mu \int_a^b g$.
> 2. **Relation de Chasles :** pour $c \in [a, b]$, $\int_a^b f = \int_a^c f + \int_c^b f$.
> 3. **Positivité et croissance :** si $f \geq 0$ sur $[a, b]$, alors $\int_a^b f \geq 0$ ; si $f \leq g$ sur $[a, b]$, alors $\int_a^b f \leq \int_a^b g$.
> 4. **Inégalité triangulaire :** $\left| \int_a^b f \right| \leq \int_a^b |f|$.

Ces inégalités supposent les bornes **dans l'ordre croissant** ($a < b$).

> **Théorème (stricte positivité).** Si $f$ est **continue** sur $[a, b]$, positive, et si $\int_a^b f = 0$, alors $f$ est nulle sur $[a, b]$.

La continuité est nécessaire : la fonction nulle sauf en un point, où elle vaut $1$, est positive, continue par morceaux, d'intégrale nulle.

**Parité, périodicité, valeur moyenne.** Pour $f$ continue par morceaux sur $[-a, a]$ : si $f$ est paire, $\int_{-a}^{a} f = 2 \int_0^a f$ ; si $f$ est impaire, $\int_{-a}^{a} f = 0$. Si $f$ est $T$-périodique, $\int_{c}^{c+T} f = \int_0^T f$ pour tout $c \in \R$. La **valeur moyenne** de $f$ sur $[a, b]$ est $\dfrac{1}{b - a} \int_a^b f$.

> **Inégalité de Cauchy-Schwarz.** Pour $f, g$ continues par morceaux sur $[a, b]$ :
>
> $$
> \left( \int_a^b f g \right)^2 \leq \left( \int_a^b f^2 \right) \left( \int_a^b g^2 \right).
> $$

> **Théorème (sommes de Riemann).** Si $f$ est continue par morceaux sur $[a, b]$, alors
>
> $$
> \frac{b - a}{n} \sum_{k=0}^{n-1} f\left( a + k \, \frac{b - a}{n} \right) \xrightarrow[n \to +\infty]{} \int_a^b f,
> $$
>
> et de même avec la somme pour $k$ allant de $1$ à $n$.

## Intégrale et primitives

> **Théorème fondamental de l'analyse.** Soient $f$ **continue** sur l'intervalle $I$ et $x_0 \in I$. La fonction $F : x \mapsto \int_{x_0}^{x} f(t) \, dt$ est de classe $\mathcal{C}^1$ sur $I$, et $F' = f$ : c'est l'unique primitive de $f$ sur $I$ qui s'annule en $x_0$. Pour toute primitive $G$ de $f$ sur $I$ et tous $\alpha, \beta \in I$ :
>
> $$
> \int_\alpha^\beta f(t) \, dt = G(\beta) - G(\alpha).
> $$

En particulier, toute fonction continue sur un intervalle possède des primitives, et deux primitives diffèrent d'une constante.

> **Intégration par parties.** Si $u$ et $v$ sont de classe $\mathcal{C}^1$ sur $[a, b]$ :
>
> $$
> \int_a^b u'(t) v(t) \, dt = \big[ u v \big]_a^b - \int_a^b u(t) v'(t) \, dt.
> $$

> **Changement de variable.** Soient $\varphi : [\alpha, \beta] \to I$ de classe $\mathcal{C}^1$ et $f$ continue sur $I$. Alors
>
> $$
> \int_{\varphi(\alpha)}^{\varphi(\beta)} f(x) \, dx = \int_\alpha^\beta f\big( \varphi(t) \big) \, \varphi'(t) \, dt.
> $$
>
> La fonction $\varphi$ n'a pas besoin d'être bijective.

## Formules de Taylor

> **Formule de Taylor avec reste intégral.** Si $f$ est de classe $\mathcal{C}^{n+1}$ sur $I$ et $x_0, x \in I$ :
>
> $$
> f(x) = \sum_{k=0}^{n} \frac{f^{(k)}(x_0)}{k!} (x - x_0)^k + \int_{x_0}^{x} \frac{(x - t)^n}{n!} f^{(n+1)}(t) \, dt.
> $$

> **Inégalité de Taylor-Lagrange.** Sous les mêmes hypothèses, si $|f^{(n+1)}| \leq M$ sur le segment d'extrémités $x_0$ et $x$, alors
>
> $$
> \left| f(x) - \sum_{k=0}^{n} \frac{f^{(k)}(x_0)}{k!} (x - x_0)^k \right| \leq \frac{M \, |x - x_0|^{n+1}}{(n+1)!}.
> $$

## Fonctions à valeurs complexes

Pour $f : [a, b] \to \C$ continue par morceaux, $\int_a^b f = \int_a^b \operatorname{Re} f + i \int_a^b \operatorname{Im} f$. Linéarité, Chasles, théorème fondamental, intégration par parties, changement de variable et inégalité $\left| \int_a^b f \right| \leq \int_a^b |f|$ restent vrais ; la croissance n'a pas de sens.

## Primitives usuelles

Sur tout intervalle où l'expression est définie, avec $\alpha \in \R \setminus \{-1\}$ et $\lambda \in \C^*$ :

$$
\int x^\alpha \, dx = \frac{x^{\alpha+1}}{\alpha + 1}, \qquad \int \frac{dx}{x} = \ln|x|, \qquad \int e^{\lambda x} \, dx = \frac{e^{\lambda x}}{\lambda},
$$

$$
\int \frac{dx}{1 + x^2} = \arctan x, \qquad \int \frac{dx}{\sqrt{1 - x^2}} = \arcsin x \ \text{ sur } ]{-}1, 1[, \qquad \int \tan x \, dx = -\ln|\cos x|,
$$

$$
\int \frac{dx}{\cos^2 x} = \tan x, \qquad \int \operatorname{ch} x \, dx = \operatorname{sh} x, \qquad \int \operatorname{sh} x \, dx = \operatorname{ch} x.
$$

Chaque égalité donne **une** primitive ; les autres en diffèrent d'une constante, sur chaque intervalle.

**Méthodes.**

- $x \mapsto e^{ax} \cos(bx)$ et $x \mapsto e^{ax} \sin(bx)$ ($a, b$ réels, $(a, b) \neq (0, 0)$) : ce sont les parties réelle et imaginaire de $x \mapsto e^{(a + ib)x}$, qui a pour primitive $x \mapsto \dfrac{e^{(a + ib)x}}{a + ib}$.
- $x \mapsto \dfrac{1}{ax^2 + bx + c}$ avec $a \neq 0$ : si le trinôme a deux racines réelles distinctes $r_1, r_2$, on décompose $\dfrac{1}{a(x - r_1)(x - r_2)} = \dfrac{1}{a(r_1 - r_2)} \left( \dfrac{1}{x - r_1} - \dfrac{1}{x - r_2} \right)$ et on obtient des logarithmes ; s'il a une racine double $r$, une primitive est $x \mapsto -\dfrac{1}{a(x - r)}$ ; s'il n'a pas de racine réelle, on écrit sa forme canonique $a \big( (x + \alpha)^2 + \beta^2 \big)$ avec $\beta > 0$, et une primitive est $x \mapsto \dfrac{1}{a\beta} \arctan\left( \dfrac{x + \alpha}{\beta} \right)$.
- On reconnaît les dérivées de composées : $\dfrac{u'}{u}$ a pour primitive $\ln|u|$, $u' e^u$ a pour primitive $e^u$, $u' u^\alpha$ ($\alpha \neq -1$) a pour primitive $\dfrac{u^{\alpha + 1}}{\alpha + 1}$.

## Pièges fréquents

- Écrire $\int_a^b f \leq \int_a^b g$ avec $a > b$.
- Oublier de changer les bornes dans un changement de variable.
- Écrire $\int \frac{dx}{x} = \ln|x| + C$ sur $\R^*$ avec une seule constante : $\R^*$ n'est pas un intervalle, la constante peut différer sur $]{-}\infty, 0[$ et sur $]0, +\infty[$.
