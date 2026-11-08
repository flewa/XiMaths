---
titre: Intégration sur un intervalle quelconque
programmes: MP, PSI
ordre: 4
notion: integrales-generalisees
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$, $I$ est un intervalle, et les fonctions sont **continues par morceaux** sur $I$ (c'est-à-dire sur tout segment inclus dans $I$), à valeurs dans $\K$. On note $a < b$ les extrémités de $I$, avec $a \in \R \cup \{-\infty\}$ et $b \in \R \cup \{+\infty\}$.

## Intégrales convergentes

> **Définition.**
>
> 1. Pour $f$ continue par morceaux sur $[a, b[$, l'intégrale $\int_a^b f$ **converge** si $x \mapsto \int_a^x f$ admet une limite finie quand $x \to b^-$ ; cette limite est notée $\int_a^b f$. Définition analogue sur $]a, b]$.
> 2. Sur $]a, b[$, l'intégrale $\int_a^b f$ converge si, pour un $c \in \, ]a, b[$, les intégrales $\int_a^c f$ et $\int_c^b f$ convergent toutes les deux ; on pose alors $\int_a^b f = \int_a^c f + \int_c^b f$, qui ne dépend pas de $c$.

Les deux extrémités s'étudient **séparément** : $\int_{-A}^{A} t \, dt = 0$ pour tout $A > 0$, mais $\int_{-\infty}^{+\infty} t \, dt$ diverge.

> **Proposition (intégrales de référence).**
>
> 1. $\int_1^{+\infty} \dfrac{dt}{t^\alpha}$ converge si et seulement si $\alpha > 1$.
> 2. $\int_0^1 \dfrac{dt}{t^\alpha}$ converge si et seulement si $\alpha < 1$.
> 3. Pour $\alpha \in \R$, $\int_0^{+\infty} e^{-\alpha t} \, dt$ converge si et seulement si $\alpha > 0$.
> 4. $\int_0^1 \ln t \, dt$ converge et vaut $-1$.

## Fonctions positives

> **Proposition.** Si $f \geq 0$ sur $[a, b[$, l'intégrale $\int_a^b f$ converge si et seulement si $x \mapsto \int_a^x f$ est majorée sur $[a, b[$.

> **Théorème (comparaison).** Soient $f, g$ positives sur $[a, b[$.
>
> 1. Si $f \leq g$ sur $[a, b[$ et si $\int_a^b g$ converge, alors $\int_a^b f$ converge.
> 2. Si $f(x) = O\big( g(x) \big)$ quand $x \to b$ et si $\int_a^b g$ converge, alors $\int_a^b f$ converge.
> 3. Si $f(x) \sim g(x)$ quand $x \to b$, les intégrales $\int_a^b f$ et $\int_a^b g$ ont la même nature.

## Fonctions intégrables

> **Définition.** La fonction $f$ est **intégrable** sur $I$ si l'intégrale de $|f|$ sur $I$ converge.

> **Proposition.** Si $f$ est intégrable sur $I$, son intégrale sur $I$ converge et $\left| \int_I f \right| \leq \int_I |f|$. Si $|f| \leq g$ sur $I$ avec $g$ intégrable sur $I$, alors $f$ est intégrable sur $I$.

La réciproque est fausse : l'intégrale $\int_1^{+\infty} \frac{\sin t}{t} \, dt$ converge, mais $t \mapsto \frac{\sin t}{t}$ n'est pas intégrable sur $[1, +\infty[$.

> **Proposition (stricte positivité).** Si $f$ est **continue**, positive et intégrable sur $I$, et si $\int_I f = 0$, alors $f$ est nulle sur $I$.

## Calcul

> **Intégration par parties.** Soient $u, v$ de classe $\mathcal{C}^1$ sur $]a, b[$. Si le produit $uv$ a des limites finies en $a$ et en $b$, alors les intégrales $\int_a^b u' v$ et $\int_a^b u v'$ ont la même nature, et en cas de convergence :
>
> $$
> \int_a^b u'(t) v(t) \, dt = \big[ u v \big]_a^b - \int_a^b u(t) v'(t) \, dt, \qquad \text{où } \big[ u v \big]_a^b = \lim_{b^-} uv - \lim_{a^+} uv.
> $$

> **Changement de variable.** Soient $\varphi : \, ]\alpha, \beta[ \, \to \, ]a, b[$ une bijection de classe $\mathcal{C}^1$, **strictement croissante**, et $f$ continue sur $]a, b[$. Les intégrales $\int_a^b f(x) \, dx$ et $\int_\alpha^\beta f\big( \varphi(t) \big) \varphi'(t) \, dt$ ont la même nature et, en cas de convergence, sont égales. Si $\varphi$ est strictement décroissante, la même conclusion vaut avec $\int_\beta^\alpha$.

## Pièges fréquents

- Croire que $f(t) \to 0$ quand $t \to +\infty$ si $\int_0^{+\infty} f$ converge : c'est faux, même pour $f$ continue et positive (des « pics » de plus en plus étroits).
- Calculer $\lim_{A \to +\infty} \int_{-A}^{A} f$ au lieu d'étudier les deux extrémités séparément.
- Faire une intégration par parties dont un des termes diverge : on la fait sur un segment $[x, y]$, puis on passe à la limite.
- Utiliser un équivalent pour une fonction qui n'est pas de signe constant.
