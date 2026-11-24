---
titre: Limites et équivalents usuels
programmes: MPSI, MP2I, PCSI, PTSI, BCPST1, L1
ordre: 25
notion: limites-continuite
---

## Cadre et notations

Soient $f$ et $g$ définies au voisinage de $a \in \overline{\R}$. On dit que $f$ est **équivalente** à $g$ en $a$, et on note $f \underset{a}{\sim} g$, s'il existe une fonction $\varepsilon$ de limite nulle en $a$ telle que $f = g(1 + \varepsilon)$ au voisinage de $a$. Quand $g$ ne s'annule pas au voisinage de $a$ (sauf peut-être en $a$), cela revient à $\dfrac{f(x)}{g(x)} \xrightarrow[x \to a]{} 1$. Les mêmes définitions valent pour les suites, en $+\infty$.

Le cours : [Limites et continuité](/rappels/limites-continuite) et [Analyse asymptotique](/rappels/developpements-limites), qui donne les développements limités usuels.

## Croissances comparées

Pour tous $\alpha, \beta, \gamma > 0$ :

$$
\frac{(\ln x)^\beta}{x^\alpha} \xrightarrow[x \to +\infty]{} 0, \qquad \frac{x^\alpha}{e^{\gamma x}} \xrightarrow[x \to +\infty]{} 0, \qquad x^\alpha \lvert \ln x \rvert^\beta \xrightarrow[x \to 0^+]{} 0.
$$

Pour les suites, avec $\alpha > 0$ et $q > 1$ :

$$
\frac{(\ln n)^\beta}{n^\alpha} \longrightarrow 0, \qquad \frac{n^\alpha}{q^n} \longrightarrow 0, \qquad \frac{q^n}{n!} \longrightarrow 0, \qquad \frac{n!}{n^n} \longrightarrow 0.
$$

## Limites usuelles en 0

$$
\frac{\sin x}{x} \xrightarrow[x \to 0]{} 1, \qquad \frac{\tan x}{x} \xrightarrow[x \to 0]{} 1, \qquad \frac{1 - \cos x}{x^2} \xrightarrow[x \to 0]{} \frac{1}{2},
$$

$$
\frac{\ln(1 + x)}{x} \xrightarrow[x \to 0]{} 1, \qquad \frac{e^x - 1}{x} \xrightarrow[x \to 0]{} 1, \qquad \frac{(1 + x)^\alpha - 1}{x} \xrightarrow[x \to 0]{} \alpha \quad (\alpha \in \R).
$$

Ce sont des taux d'accroissement : chaque limite est la dérivée en $0$ de la fonction du numérateur.

## Limites usuelles à l'infini

$$
\left( 1 + \frac{a}{x} \right)^x \xrightarrow[x \to +\infty]{} e^a \quad (a \in \R), \qquad \left( 1 + \frac{1}{n} \right)^n \longrightarrow e, \qquad x^{1/x} \xrightarrow[x \to +\infty]{} 1, \qquad x \sin\frac{1}{x} \xrightarrow[x \to +\infty]{} 1.
$$

Pour la première, on écrit $\left( 1 + \frac{a}{x} \right)^x = \exp\left( x \ln\left( 1 + \frac{a}{x} \right) \right)$ et on utilise $\ln(1 + u) \sim u$ en $0$.

## Équivalents usuels en 0

$$
\sin x \sim x, \qquad \tan x \sim x, \qquad 1 - \cos x \sim \frac{x^2}{2}, \qquad \arcsin x \sim x, \qquad \arctan x \sim x,
$$

$$
\ln(1 + x) \sim x, \qquad e^x - 1 \sim x, \qquad (1 + x)^\alpha - 1 \sim \alpha x \quad (\alpha \neq 0),
$$

$$
\operatorname{sh} x \sim x, \qquad \operatorname{ch} x - 1 \sim \frac{x^2}{2}, \qquad \operatorname{th} x \sim x.
$$

Tous se lisent sur les développements limités usuels, au premier terme non nul.

## Équivalents de suites et de fonctions classiques

- **Polynôme.** Si $a_p \neq 0$, $a_p x^p + \dots + a_1 x + a_0 \underset{+\infty}{\sim} a_p x^p$ et $\underset{0}{\sim}$ son terme non nul de plus bas degré.
- **Stirling.** $n! \sim \sqrt{2\pi n} \left( \dfrac{n}{e} \right)^n$.
- **Série harmonique.** $\sum_{k=1}^{n} \dfrac{1}{k} \sim \ln n$ ; plus précisément, $\sum_{k=1}^{n} \dfrac{1}{k} = \ln n + \gamma + o(1)$, où $\gamma \approx 0{,}577$ est la constante d'Euler.
- **Logarithme.** $\ln(n + 1) \sim \ln n$, et $\ln(1 + x) \underset{+\infty}{\sim} \ln x$.

## Règles de calcul

- Les équivalents se **multiplient**, se **divisent** et s'élèvent à une **puissance fixe** : si $f \sim g$ et $u \sim v$ en $a$, alors $fu \sim gv$, $\dfrac{f}{u} \sim \dfrac{g}{v}$ et $f^\alpha \sim g^\alpha$ (pour $f, g > 0$).
- Si $f \sim g$ en $a$ et $g(x) \to \ell$, alors $f(x) \to \ell$ : un équivalent donne la limite et le signe au voisinage de $a$.
- **Logarithme.** Si $f \sim g$ en $a$, avec $g > 0$ et $g(x) \to \ell \in [0, +\infty] \setminus \{1\}$, alors $\ln f \sim \ln g$.
- On **compose à droite** par une fonction qui tend vers $a$ : si $f \underset{0}{\sim} g$ et $u(x) \to 0$, alors $f \circ u \sim g \circ u$. Ainsi $\sin\frac{1}{n} \sim \frac{1}{n}$.

## Pièges fréquents

- On n'**additionne** pas des équivalents : $x + x^2 \underset{0}{\sim} x$ et $-x \underset{0}{\sim} -x + x^3$, mais $x^2 \not\sim x^3$. On passe alors par les développements limités.
- On ne **compose pas à gauche** : $x + 1 \underset{+\infty}{\sim} x$, mais $e^{x + 1} = e \cdot e^x$ n'est pas équivalent à $e^x$. Pour l'exponentielle, $e^f \sim e^g$ si et seulement si $f - g \to 0$.
- « $f \sim 0$ » n'a de sens que si $f$ est nulle au voisinage de $a$ : on écrit plutôt $f = o(1)$ ou $f \to 0$.
- Un équivalent dépend du point : $\sin x \underset{0}{\sim} x$, mais $\sin x$ n'est équivalent à rien de simple en $+\infty$.
