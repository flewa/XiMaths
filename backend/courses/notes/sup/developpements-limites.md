---
titre: Analyse asymptotique
programmes: MPSI, PCSI
ordre: 5
notion: developpements-limites
---

## Cadre et notations

Dans toute la fiche, $I$ est un intervalle, $a$ est un point de $I$ ou une extrémité de $I$ (éventuellement $\pm\infty$), et $f, g, h : I \to \R$. Un **voisinage** de $a$ est un intervalle de la forme $]a - \delta, a + \delta[$ avec $\delta > 0$ si $a \in \R$, de la forme $]A, +\infty[$ si $a = +\infty$.

## Relations de comparaison

> **Définition.** On suppose que $g$ ne s'annule pas sur $V \cap I \setminus \{a\}$ pour un voisinage $V$ de $a$.
>
> 1. $f$ est **négligeable** devant $g$ en $a$, noté $f = o(g)$, si $\dfrac{f(x)}{g(x)} \to 0$ quand $x \to a$, $x \neq a$.
> 2. $f$ est **dominée** par $g$ en $a$, noté $f = O(g)$, si $\dfrac{f}{g}$ est bornée sur $V' \cap I \setminus \{a\}$ pour un voisinage $V'$ de $a$.
> 3. $f$ est **équivalente** à $g$ en $a$, noté $f \sim g$, si $\dfrac{f(x)}{g(x)} \to 1$ quand $x \to a$, $x \neq a$.

Les définitions générales, sans hypothèse sur les zéros de $g$, s'écrivent $f = \varepsilon g$, $f = \beta g$, $f = (1 + \varepsilon) g$ au voisinage de $a$, avec $\varepsilon \to 0$ et $\beta$ bornée. Les mêmes notions existent pour les suites, quand $n \to +\infty$.

> **Proposition (propriétés de l'équivalence).**
>
> 1. $\sim$ est une relation d'équivalence ; si $f \sim g$, alors $f$ et $g$ ont le même signe au voisinage de $a$, et si $g$ a une limite en $a$, $f$ a la même.
> 2. Si $f_1 \sim g_1$ et $f_2 \sim g_2$, alors $f_1 f_2 \sim g_1 g_2$ et, si les quotients sont définis, $\dfrac{f_1}{f_2} \sim \dfrac{g_1}{g_2}$.
> 3. Si $f \sim g$ et si $f, g > 0$ au voisinage de $a$, alors $f^\alpha \sim g^\alpha$ pour tout $\alpha \in \R$ fixé.
> 4. Si $f \sim g$, avec $f, g > 0$ au voisinage de $a$, et si $g$ tend vers $\ell \in [0, +\infty] \setminus \{1\}$, alors $\ln f \sim \ln g$.

**On n'additionne pas des équivalents, et on ne compose pas un équivalent par une fonction :** $x + 1 \sim x$ et $-x \sim -x$ en $+\infty$, mais $(x + 1) + (-x) = 1$ n'est pas équivalent à $0$ ; $x^2 + x \sim x^2$ en $+\infty$, mais $\dfrac{e^{x^2 + x}}{e^{x^2}} = e^x \to +\infty$. Écrire $f \sim 0$ n'a de sens que si $f$ est nulle au voisinage de $a$ : on ne l'écrit pas.

> **Théorème (croissances comparées).** Pour tous $\alpha, \beta > 0$ :
>
> $$
> (\ln x)^\beta = o(x^\alpha) \ \text{et} \ x^\alpha = o(e^{\beta x}) \ \text{en } +\infty, \qquad |\ln x|^\beta = o\left( \frac{1}{x^\alpha} \right) \ \text{en } 0^+.
> $$
>
> Pour les suites : $n^\alpha = o(q^n)$ pour tout $q > 1$, $q^n = o(n!)$ pour tout $q \in \R$, et $n! = o(n^n)$.

## Développements limités

Dans cette section, $a \in \R$ et $n \in \N$.

> **Définition.** La fonction $f$ admet un **développement limité à l'ordre $n$ en $a$** (noté $\mathrm{DL}_n(a)$) s'il existe des réels $c_0, \dots, c_n$ tels que, quand $x \to a$,
>
> $$
> f(x) = \sum_{k=0}^{n} c_k (x - a)^k + o\big( (x - a)^n \big).
> $$
>
> Ces coefficients sont alors uniques ; $\sum_{k=0}^{n} c_k (x - a)^k$ est la **partie régulière** du développement.

Si $f$ admet un $\mathrm{DL}_n(0)$ et est paire (resp. impaire), les coefficients d'indice impair (resp. pair) de sa partie régulière sont nuls.

> **Théorème (Taylor-Young).** Si $f$ est de classe $\mathcal{C}^n$ sur $I$ et $a \in I$, alors
>
> $$
> f(x) = \sum_{k=0}^{n} \frac{f^{(k)}(a)}{k!} (x - a)^k + o\big( (x - a)^n \big) \quad \text{quand } x \to a.
> $$

> **Proposition (primitivation).** Si $f$ est dérivable sur $I$, $a \in I$, et si $f'(x) = \sum_{k=0}^{n} c_k (x - a)^k + o\big( (x - a)^n \big)$, alors
>
> $$
> f(x) = f(a) + \sum_{k=0}^{n} \frac{c_k}{k+1} (x - a)^{k+1} + o\big( (x - a)^{n+1} \big).
> $$

**On ne dérive pas un développement limité sans justification** : l'existence d'un $\mathrm{DL}_n(a)$ de $f$ ne donne aucun développement de $f'$. Si $f$ est dérivable sur $I$ et si $f'$ admet un $\mathrm{DL}_{n-1}(a)$ (c'est le cas si $f$ est de classe $\mathcal{C}^n$ sur $I$), alors, par primitivation et unicité, la partie régulière du $\mathrm{DL}_{n-1}(a)$ de $f'$ est la dérivée de celle du $\mathrm{DL}_n(a)$ de $f$.

Sommes, produits et composées de développements limités se calculent en tronquant au bon ordre ; pour une composée $g \circ f$, il faut $f(x) \to 0$ quand $x \to 0$ pour utiliser le $\mathrm{DL}(0)$ de $g$.

## Développements usuels en $0$

Pour tout $n \in \N$, quand $x \to 0$ :

$$
e^x = \sum_{k=0}^{n} \frac{x^k}{k!} + o(x^n), \qquad \frac{1}{1 - x} = \sum_{k=0}^{n} x^k + o(x^n), \qquad \ln(1 + x) = \sum_{k=1}^{n} \frac{(-1)^{k-1}}{k} x^k + o(x^n),
$$

$$
\cos x = \sum_{k=0}^{n} \frac{(-1)^k x^{2k}}{(2k)!} + o(x^{2n+1}), \qquad \sin x = \sum_{k=0}^{n} \frac{(-1)^k x^{2k+1}}{(2k+1)!} + o(x^{2n+2}),
$$

$$
\operatorname{ch} x = \sum_{k=0}^{n} \frac{x^{2k}}{(2k)!} + o(x^{2n+1}), \qquad \operatorname{sh} x = \sum_{k=0}^{n} \frac{x^{2k+1}}{(2k+1)!} + o(x^{2n+2}),
$$

$$
\arctan x = \sum_{k=0}^{n} \frac{(-1)^k x^{2k+1}}{2k+1} + o(x^{2n+2}), \qquad \tan x = x + \frac{x^3}{3} + \frac{2x^5}{15} + o(x^6),
$$

et, pour tout $\alpha \in \R$,

$$
(1 + x)^\alpha = 1 + \sum_{k=1}^{n} \frac{\alpha (\alpha - 1) \cdots (\alpha - k + 1)}{k!} x^k + o(x^n).
$$

## Applications

- **Équivalent :** si $f(x) = c_p (x - a)^p + o\big( (x - a)^p \big)$ avec $c_p \neq 0$, alors $f(x) \sim c_p (x - a)^p$.
- **Position relative d'une courbe et de sa tangente :** si $f(x) = c_0 + c_1 (x - a) + c_p (x - a)^p + o\big( (x - a)^p \big)$ avec $p \geq 2$ et $c_p \neq 0$, le signe de $c_p (x - a)^p$ donne la position locale du graphe par rapport à la tangente en $a$.
- **Asymptote en $+\infty$ :** on pose $x = \frac{1}{h}$ et on cherche $f(x) = \alpha x + \beta + \frac{\gamma}{x^p} + o\left( \frac{1}{x^p} \right)$ avec $\gamma \neq 0$.

## Pièges fréquents

- Additionner ou composer des équivalents.
- Tronquer trop tôt : dans un produit ou une composée, chaque facteur doit être développé à un ordre suffisant pour que les termes négligés soient bien des $o$ de l'ordre visé.
- Oublier que $o\big( (x - a)^n \big)$ désigne une fonction, et non un nombre : $o(x^2) - o(x^2)$ n'est pas nul, c'est un $o(x^2)$.
