---
titre: Fonctions usuelles
programmes: MPSI, MP2I
ordre: 4
notion: fonctions-usuelles
---

## Cadre et notations

Les fonctions sont définies sur une partie de $\R$. Une fonction $f$ est **bornée** si et seulement si $|f|$ est majorée. Le graphe de $x \mapsto f(x + a)$ se déduit de celui de $f$ par la translation de vecteur $(-a, 0)$ ; celui de $x \mapsto f(x) + b$ par la translation de vecteur $(0, b)$. Une fonction paire (resp. impaire) a un graphe symétrique par rapport à l'axe des ordonnées (resp. à l'origine) : on l'étudie sur $\R_+$.

## Logarithme, exponentielle, puissances

Le **logarithme népérien** $\ln$ est la primitive de $x \mapsto \frac{1}{x}$ sur $]0, +\infty[$ qui s'annule en $1$. Il est strictement croissant, $\ln(xy) = \ln x + \ln y$, et $\ln$ tend vers $-\infty$ en $0$ et vers $+\infty$ en $+\infty$. L'**exponentielle** $\exp : \R \to \, ]0, +\infty[$ est sa bijection réciproque : $\exp' = \exp$ et $e^{a + b} = e^a e^b$.

Pour $a > 0$ et $a \neq 1$, le logarithme en base $a$ est $\log_a x = \dfrac{\ln x}{\ln a}$ ; en particulier $\log_{10}$ (décimal) et $\log_2$.

**Puissances.** Pour $x > 0$ et $\alpha \in \R$, $x^\alpha = e^{\alpha \ln x}$. La fonction $x \mapsto x^\alpha$ est dérivable sur $]0, +\infty[$, de dérivée $x \mapsto \alpha x^{\alpha - 1}$ ; pour $\alpha > 0$, on la prolonge par continuité en $0$ par $0^\alpha = 0$. Seules les puissances entières sont aussi définies sur $]{-}\infty, 0[$. Pour $x, y > 0$ et $\alpha, \beta \in \R$ :

$$
(xy)^\alpha = x^\alpha y^\alpha, \qquad x^{\alpha + \beta} = x^\alpha x^\beta, \qquad (x^\alpha)^\beta = x^{\alpha\beta}.
$$

> **Théorème (croissances comparées).** Pour tous $\alpha, \beta, \gamma > 0$ :
>
> $$
> \frac{(\ln x)^\beta}{x^\alpha} \xrightarrow[x \to +\infty]{} 0, \qquad \frac{x^\alpha}{e^{\gamma x}} \xrightarrow[x \to +\infty]{} 0, \qquad x^\alpha |\ln x|^\beta \xrightarrow[x \to 0^+]{} 0.
> $$

> **Proposition (inégalités de convexité).** Pour tout $x \in \R$, $e^x \geq 1 + x$ ; pour tout $x > -1$, $\ln(1 + x) \leq x$. Les deux égalités n'ont lieu qu'en $x = 0$.

## Fonctions circulaires réciproques

> **Définition.**
>
> 1. La restriction de $\sin$ à $\left[ -\frac{\pi}{2}, \frac{\pi}{2} \right]$ est une bijection sur $[-1, 1]$ ; sa réciproque est $\arcsin : [-1, 1] \to \left[ -\frac{\pi}{2}, \frac{\pi}{2} \right]$.
> 2. La restriction de $\cos$ à $[0, \pi]$ est une bijection sur $[-1, 1]$ ; sa réciproque est $\arccos : [-1, 1] \to [0, \pi]$.
> 3. La restriction de $\tan$ à $\left] {-}\frac{\pi}{2}, \frac{\pi}{2} \right[$ est une bijection sur $\R$ ; sa réciproque est $\arctan : \R \to \left] {-}\frac{\pi}{2}, \frac{\pi}{2} \right[$.

> **Proposition.** $\arcsin$ est impaire et strictement croissante, $\arccos$ strictement décroissante, $\arctan$ impaire et strictement croissante, de limites $\pm \frac{\pi}{2}$ en $\pm\infty$. Elles sont dérivables, sauf $\arcsin$ et $\arccos$ en $\pm 1$ (tangentes verticales) :
>
> $$
> \arcsin' x = \frac{1}{\sqrt{1 - x^2}}, \qquad \arccos' x = -\frac{1}{\sqrt{1 - x^2}} \quad \text{sur } ]{-}1, 1[, \qquad \arctan' x = \frac{1}{1 + x^2} \quad \text{sur } \R.
> $$
>
> Pour tout $x \in [-1, 1]$, $\arcsin x + \arccos x = \frac{\pi}{2}$.

Ces dérivées viennent de la formule de la dérivée d'une réciproque : par exemple, pour $x \in \, ]{-}1, 1[$, $\arcsin' x = \dfrac{1}{\cos(\arcsin x)}$ et $\cos(\arcsin x) = \sqrt{1 - x^2}$ car ce cosinus est positif.

## Fonctions hyperboliques

Pour $x \in \R$ : $\operatorname{ch} x = \dfrac{e^x + e^{-x}}{2}$, $\operatorname{sh} x = \dfrac{e^x - e^{-x}}{2}$ et $\operatorname{th} x = \dfrac{\operatorname{sh} x}{\operatorname{ch} x}$.

> **Proposition.**
>
> 1. $\operatorname{ch}$ est paire, $\operatorname{sh}$ et $\operatorname{th}$ sont impaires ; $\operatorname{ch} x \geq 1$ pour tout $x$.
> 2. $\operatorname{ch}' = \operatorname{sh}$, $\operatorname{sh}' = \operatorname{ch}$ et $\operatorname{th}' = 1 - \operatorname{th}^2 = \dfrac{1}{\operatorname{ch}^2}$ ; $\operatorname{sh}$ et $\operatorname{th}$ sont strictement croissantes, et $\operatorname{th}$ réalise une bijection de $\R$ sur $]{-}1, 1[$.
> 3. Pour tout $x \in \R$ : $\operatorname{ch}^2 x - \operatorname{sh}^2 x = 1$.

Les fonctions hyperboliques réciproques ne sont pas au programme.

## Fonctions à valeurs complexes

Une fonction $f : I \to \C$ est dérivable si $\operatorname{Re} f$ et $\operatorname{Im} f$ le sont, et $f' = (\operatorname{Re} f)' + i (\operatorname{Im} f)'$. Sommes, produits et quotients se dérivent comme dans le cas réel. Si $\varphi : I \to \C$ est dérivable, alors $\exp \circ \varphi$ l'est et

$$
\big( e^{\varphi} \big)' = \varphi' \, e^{\varphi} ; \qquad \text{en particulier} \quad \frac{d}{dx} e^{\lambda x} = \lambda e^{\lambda x} \quad (\lambda \in \C).
$$

## Pièges fréquents

- Écrire $\arcsin(\sin x) = x$ pour tout $x$ : ce n'est vrai que pour $x \in \left[ -\frac{\pi}{2}, \frac{\pi}{2} \right]$ ; en revanche $\sin(\arcsin x) = x$ pour tout $x \in [-1, 1]$.
- Écrire $x^\alpha$ pour $x < 0$ et $\alpha$ non entier.
- Croire que $\arccos$ est impaire : $\arccos(-x) = \pi - \arccos x$.
- Écrire $\operatorname{ch}^2 - \operatorname{sh}^2 = -1$ ou confondre avec $\cos^2 + \sin^2 = 1$.
