---
titre: Dérivées et primitives usuelles
programmes: MPSI, MP2I, PCSI, PTSI, BCPST1, L1
ordre: 23
notion: derivation
---

## Cadre et notations

Chaque formule vaut sur tout **intervalle** où les expressions sont définies. Une primitive n'est donnée qu'à une constante près : sur un intervalle, deux primitives d'une même fonction diffèrent d'une constante ; sur une réunion d'intervalles disjoints, la constante peut changer d'un intervalle à l'autre. On note $\alpha$ un réel, $n$ un entier naturel non nul et $a$ un réel strictement positif.

Le cours : [Dérivation et convexité](/rappels/derivation), [Intégration sur un segment](/rappels/calcul-integral) et [Fonctions usuelles](/rappels/fonctions-usuelles).

## Dérivées des fonctions usuelles

$$
\begin{array}{lll}
f(x) & f'(x) & \text{domaine de dérivabilité} \\[2.4ex] \hline
x^n & n x^{n-1} & \R \\[2.4ex]
x^\alpha & \alpha x^{\alpha - 1} & ]0, +\infty[ \\[2.4ex]
\dfrac{1}{x} & -\dfrac{1}{x^2} & \R^* \\[2.4ex]
\sqrt{x} & \dfrac{1}{2\sqrt{x}} & ]0, +\infty[ \\[2.4ex]
e^x & e^x & \R \\[2.4ex]
a^x & a^x \ln a & \R \\[2.4ex]
\ln x & \dfrac{1}{x} & ]0, +\infty[ \\[2.4ex]
\ln \lvert x \rvert & \dfrac{1}{x} & \R^* \\[2.4ex]
\cos x & -\sin x & \R \\[2.4ex]
\sin x & \cos x & \R \\[2.4ex]
\tan x & 1 + \tan^2 x = \dfrac{1}{\cos^2 x} & x \notin \dfrac{\pi}{2} + \pi\Z \\[2.4ex]
\arcsin x & \dfrac{1}{\sqrt{1 - x^2}} & ]{-}1, 1[ \\[2.4ex]
\arccos x & -\dfrac{1}{\sqrt{1 - x^2}} & ]{-}1, 1[ \\[2.4ex]
\arctan x & \dfrac{1}{1 + x^2} & \R \\[2.4ex]
\operatorname{ch} x & \operatorname{sh} x & \R \\[2.4ex]
\operatorname{sh} x & \operatorname{ch} x & \R \\[2.4ex]
\operatorname{th} x & 1 - \operatorname{th}^2 x = \dfrac{1}{\operatorname{ch}^2 x} & \R
\end{array}
$$

## Opérations et composées

Si $u$ et $v$ sont dérivables et $\lambda$ est une constante :

$$
(u + v)' = u' + v', \qquad (\lambda u)' = \lambda u', \qquad (uv)' = u'v + uv', \qquad \left( \frac{u}{v} \right)' = \frac{u'v - uv'}{v^2} \quad (v \neq 0).
$$

**Composée.** $(v \circ u)' = u' \times (v' \circ u)$. D'où, pour $u$ dérivable :

$$
(u^n)' = n u' u^{n-1}, \qquad \left( \frac{1}{u} \right)' = -\frac{u'}{u^2}, \qquad (\sqrt{u})' = \frac{u'}{2\sqrt{u}} \quad (u > 0),
$$

$$
(e^u)' = u' e^u, \qquad (\ln \lvert u \rvert)' = \frac{u'}{u} \quad (u \neq 0), \qquad (\cos u)' = -u' \sin u, \qquad (\sin u)' = u' \cos u.
$$

**Réciproque.** Si $f$ est une bijection dérivable de $I$ sur $J$ et si $f'$ ne s'annule pas sur $I$, alors $f^{-1}$ est dérivable sur $J$ et $(f^{-1})' = \dfrac{1}{f' \circ f^{-1}}$.

## Primitives usuelles

$$
\begin{array}{lll}
f(x) & \text{une primitive } F(x) & \text{sur} \\[2.4ex] \hline
x^\alpha \ (\alpha \neq -1) & \dfrac{x^{\alpha + 1}}{\alpha + 1} & ]0, +\infty[ \ \text{(ou } \R \text{ si } \alpha \in \N) \\[2.4ex]
\dfrac{1}{x} & \ln \lvert x \rvert & ]{-}\infty, 0[ \ \text{ou} \ ]0, +\infty[ \\[2.4ex]
e^{\lambda x} \ (\lambda \in \C^*) & \dfrac{e^{\lambda x}}{\lambda} & \R \\[2.4ex]
\ln x & x \ln x - x & ]0, +\infty[ \\[2.4ex]
\cos x & \sin x & \R \\[2.4ex]
\sin x & -\cos x & \R \\[2.4ex]
\dfrac{1}{\cos^2 x} = 1 + \tan^2 x & \tan x & \left] {-}\dfrac{\pi}{2}, \dfrac{\pi}{2} \right[ \ \text{(modulo } \pi) \\[2.4ex]
\tan x & -\ln \lvert \cos x \rvert & \left] {-}\dfrac{\pi}{2}, \dfrac{\pi}{2} \right[ \ \text{(modulo } \pi) \\[2.4ex]
\operatorname{ch} x & \operatorname{sh} x & \R \\[2.4ex]
\operatorname{sh} x & \operatorname{ch} x & \R \\[2.4ex]
\dfrac{1}{1 + x^2} & \arctan x & \R \\[2.4ex]
\dfrac{1}{a^2 + x^2} & \dfrac{1}{a} \arctan \dfrac{x}{a} & \R \\[2.4ex]
\dfrac{1}{\sqrt{1 - x^2}} & \arcsin x & ]{-}1, 1[ \\[2.4ex]
\dfrac{1}{\sqrt{a^2 - x^2}} & \arcsin \dfrac{x}{a} & ]{-}a, a[ \\[2.4ex]
\dfrac{1}{x^2 - a^2} & \dfrac{1}{2a} \ln \left\lvert \dfrac{x - a}{x + a} \right\rvert & \text{chaque intervalle sans } \pm a \\[2.4ex]
\dfrac{1}{\sqrt{x^2 + 1}} & \ln\left( x + \sqrt{x^2 + 1} \right) & \R \\[2.4ex]
\dfrac{1}{\sqrt{x^2 - 1}} & \ln\left( x + \sqrt{x^2 - 1} \right) & ]1, +\infty[
\end{array}
$$

## Primitives de composées

On lit les formules de dérivation à l'envers. Pour $u$ de classe $\mathcal{C}^1$ :

$$
u' u^\alpha \longmapsto \frac{u^{\alpha + 1}}{\alpha + 1} \ (\alpha \neq -1), \qquad \frac{u'}{u} \longmapsto \ln \lvert u \rvert, \qquad \frac{u'}{\sqrt{u}} \longmapsto 2\sqrt{u}, \qquad u' e^u \longmapsto e^u,
$$

$$
u' \cos u \longmapsto \sin u, \qquad u' \sin u \longmapsto -\cos u, \qquad \frac{u'}{1 + u^2} \longmapsto \arctan u, \qquad \frac{u'}{\sqrt{1 - u^2}} \longmapsto \arcsin u.
$$

Exemple : $\dfrac{x}{1 + x^2} = \dfrac{1}{2} \cdot \dfrac{2x}{1 + x^2}$ a pour primitive $\dfrac{1}{2} \ln(1 + x^2)$.

## Méthodes

**Intégration par parties.** Pour $u, v$ de classe $\mathcal{C}^1$ sur $[a, b]$ :

$$
\int_a^b u'(t) v(t) \, dt = \big[ u(t) v(t) \big]_a^b - \int_a^b u(t) v'(t) \, dt.
$$

Elle sert pour $t^n e^t$, $t^n \cos t$, $\ln t$, $\arctan t$ : on dérive le facteur qui se simplifie.

**Changement de variable.** Si $\varphi$ est de classe $\mathcal{C}^1$ sur $[\alpha, \beta]$ et $f$ continue sur $\varphi([\alpha, \beta])$ :

$$
\int_{\varphi(\alpha)}^{\varphi(\beta)} f(x) \, dx = \int_\alpha^\beta f\big( \varphi(t) \big) \varphi'(t) \, dt.
$$

**Exponentielle et trigonométrie.** $e^{ax} \cos(bx)$ et $e^{ax} \sin(bx)$ sont les parties réelle et imaginaire de $e^{(a + ib)x}$, qui a pour primitive $\dfrac{e^{(a + ib)x}}{a + ib}$ quand $(a, b) \neq (0, 0)$.

**Puissances de cos et sin.** On linéarise (voir le formulaire de trigonométrie), ou, pour une puissance impaire, on pose $u = \sin x$ ou $u = \cos x$ : $\cos^3 x = (1 - \sin^2 x) \cos x$ a pour primitive $\sin x - \dfrac{\sin^3 x}{3}$.

## Pièges fréquents

- Une primitive de $\dfrac{1}{x^2}$ est $-\dfrac{1}{x}$, pas un logarithme : la formule en $\ln$ ne vaut que pour l'exposant $-1$.
- $\ln \lvert x \rvert$ est une primitive de $\dfrac{1}{x}$ sur chacun des deux intervalles $]{-}\infty, 0[$ et $]0, +\infty[$ séparément ; on n'intègre jamais $\dfrac{1}{x}$ à travers $0$.
- Le signe : une primitive de $\tan x$ est $-\ln \lvert \cos x \rvert$, et une primitive de $\sin x$ est $-\cos x$.
- Dans un changement de variable, on change aussi les bornes et l'élément $dx$.
