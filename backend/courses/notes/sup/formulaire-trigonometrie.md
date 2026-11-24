---
titre: Formulaire de trigonométrie
programmes: MPSI, MP2I, PCSI, PTSI, BCPST1, L1
ordre: 22
notion: fonctions-usuelles
---

## Cadre et notations

Les angles sont en radians et $a, b, p, q, x$ désignent des réels. La tangente est définie en $x$ dès que $\cos x \neq 0$, c'est-à-dire pour $x \notin \frac{\pi}{2} + \pi\Z$. On note $x \equiv a \ [2\pi]$ lorsque $x - a \in 2\pi\Z$.

Les fonctions $\cos$ et $\sin$ sont $2\pi$-périodiques, $\tan$ est $\pi$-périodique ; $\cos$ est paire, $\sin$ et $\tan$ sont impaires.

Le cours, avec les démonstrations des formules : [Sommes, inégalités et trigonométrie](/rappels/calcul-algebrique), [Nombres complexes et trigonométrie](/rappels/nombres-complexes) et [Fonctions usuelles](/rappels/fonctions-usuelles).

## Valeurs remarquables

$$
\begin{array}{c|ccccc}
x & 0 & \dfrac{\pi}{6} & \dfrac{\pi}{4} & \dfrac{\pi}{3} & \dfrac{\pi}{2} \\[1.6ex] \hline
\cos x & 1 & \dfrac{\sqrt{3}}{2} & \dfrac{\sqrt{2}}{2} & \dfrac{1}{2} & 0 \\[1.6ex]
\sin x & 0 & \dfrac{1}{2} & \dfrac{\sqrt{2}}{2} & \dfrac{\sqrt{3}}{2} & 1 \\[1.6ex]
\tan x & 0 & \dfrac{\sqrt{3}}{3} & 1 & \sqrt{3} & \text{non définie}
\end{array}
$$

Les autres valeurs s'en déduisent par les symétries ci-dessous : par exemple $\cos \frac{2\pi}{3} = -\frac{1}{2}$ et $\sin \frac{5\pi}{6} = \frac{1}{2}$.

## Relations fondamentales et symétries

$$
\cos^2 x + \sin^2 x = 1, \qquad 1 + \tan^2 x = \frac{1}{\cos^2 x}.
$$

$$
\cos(\pi - x) = -\cos x, \qquad \sin(\pi - x) = \sin x, \qquad \cos(\pi + x) = -\cos x, \qquad \sin(\pi + x) = -\sin x,
$$

$$
\cos\left( \frac{\pi}{2} - x \right) = \sin x, \qquad \sin\left( \frac{\pi}{2} - x \right) = \cos x, \qquad \cos\left( \frac{\pi}{2} + x \right) = -\sin x, \qquad \sin\left( \frac{\pi}{2} + x \right) = \cos x.
$$

Pour la tangente, quand les deux membres sont définis : $\tan(\pi + x) = \tan x$ et $\tan\left( \frac{\pi}{2} - x \right) = \dfrac{1}{\tan x}$.

## Formules d'addition

$$
\cos(a + b) = \cos a \cos b - \sin a \sin b, \qquad \cos(a - b) = \cos a \cos b + \sin a \sin b,
$$

$$
\sin(a + b) = \sin a \cos b + \cos a \sin b, \qquad \sin(a - b) = \sin a \cos b - \cos a \sin b,
$$

$$
\tan(a + b) = \frac{\tan a + \tan b}{1 - \tan a \tan b}, \qquad \tan(a - b) = \frac{\tan a - \tan b}{1 + \tan a \tan b}.
$$

Les formules de la tangente valent quand $\tan a$, $\tan b$ et le membre de gauche sont définis.

## Duplication et linéarisation

$$
\cos 2a = \cos^2 a - \sin^2 a = 2\cos^2 a - 1 = 1 - 2\sin^2 a, \qquad \sin 2a = 2 \sin a \cos a, \qquad \tan 2a = \frac{2 \tan a}{1 - \tan^2 a}.
$$

$$
\cos 3a = 4\cos^3 a - 3\cos a, \qquad \sin 3a = 3\sin a - 4\sin^3 a.
$$

**Linéarisation** : on remplace un produit ou une puissance par une somme, pour intégrer ou dériver plus facilement.

$$
\cos^2 a = \frac{1 + \cos 2a}{2}, \qquad \sin^2 a = \frac{1 - \cos 2a}{2}, \qquad \sin a \cos a = \frac{\sin 2a}{2},
$$

$$
\cos a \cos b = \frac{\cos(a - b) + \cos(a + b)}{2}, \qquad \sin a \sin b = \frac{\cos(a - b) - \cos(a + b)}{2}, \qquad \sin a \cos b = \frac{\sin(a + b) + \sin(a - b)}{2}.
$$

Pour une puissance plus élevée, on passe par les formules d'Euler (voir plus bas).

## Sommes en produits

Les formules de Simpson factorisent une somme, pour résoudre une équation ou étudier un signe :

$$
\cos p + \cos q = 2 \cos \frac{p + q}{2} \cos \frac{p - q}{2}, \qquad \cos p - \cos q = -2 \sin \frac{p + q}{2} \sin \frac{p - q}{2},
$$

$$
\sin p + \sin q = 2 \sin \frac{p + q}{2} \cos \frac{p - q}{2}, \qquad \sin p - \sin q = 2 \cos \frac{p + q}{2} \sin \frac{p - q}{2}.
$$

## Tangente de l'angle moitié

Pour $x \notin \pi + 2\pi\Z$, on pose $t = \tan \frac{x}{2}$. Alors

$$
\cos x = \frac{1 - t^2}{1 + t^2}, \qquad \sin x = \frac{2t}{1 + t^2}, \qquad \tan x = \frac{2t}{1 - t^2} \quad (t^2 \neq 1).
$$

Ce changement de variable ramène l'intégrale d'une fraction rationnelle en $\cos x$ et $\sin x$ à celle d'une fraction rationnelle en $t$, avec $dx = \dfrac{2 \, dt}{1 + t^2}$.

## Écrire a cos x + b sin x

Pour $(a, b) \neq (0, 0)$, on pose $R = \sqrt{a^2 + b^2}$ et on choisit $\varphi$ tel que $\cos \varphi = \dfrac{a}{R}$ et $\sin \varphi = \dfrac{b}{R}$. Alors, pour tout $x$ :

$$
a \cos x + b \sin x = R \cos(x - \varphi).
$$

C'est ainsi qu'on résout $a \cos x + b \sin x = c$, ou qu'on trouve l'amplitude d'une somme d'oscillations.

## Équations trigonométriques

$$
\cos x = \cos a \iff x \equiv a \ [2\pi] \ \text{ ou } \ x \equiv -a \ [2\pi],
$$

$$
\sin x = \sin a \iff x \equiv a \ [2\pi] \ \text{ ou } \ x \equiv \pi - a \ [2\pi],
$$

$$
\tan x = \tan a \iff x \equiv a \ [\pi] \qquad \left( x, a \notin \frac{\pi}{2} + \pi\Z \right).
$$

## Lien avec l'exponentielle complexe

Les formules d'Euler et de Moivre retrouvent toutes les formules précédentes :

$$
\cos x = \frac{e^{ix} + e^{-ix}}{2}, \qquad \sin x = \frac{e^{ix} - e^{-ix}}{2i}, \qquad (\cos x + i \sin x)^n = \cos(nx) + i \sin(nx) \quad (n \in \Z).
$$

Par exemple, $\cos(a + b) + i \sin(a + b) = e^{i(a + b)} = e^{ia} e^{ib}$ donne les deux formules d'addition à la fois, en développant le produit et en identifiant parties réelle et imaginaire.

## Pièges fréquents

- Dans $\cos x = \cos a$, on oublie la seconde famille de solutions $x \equiv -a \ [2\pi]$ ; dans $\sin x = \sin a$, la famille $x \equiv \pi - a \ [2\pi]$.
- $\arcsin(\sin x) = x$ seulement pour $x \in \left[ -\frac{\pi}{2}, \frac{\pi}{2} \right]$ ; de même $\arccos(\cos x) = x$ seulement sur $[0, \pi]$.
- $\cos(a + b) \neq \cos a + \cos b$ : les formules d'addition ne sont pas linéaires.
- $\cos^2 x$ désigne $(\cos x)^2$, alors que $\cos(x^2)$ est une autre fonction.
