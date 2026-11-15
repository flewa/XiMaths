---
titre: Somme des inverses des carrés (problème de Bâle)
programmes: MP, MPI, L2
statut: hors-programme
ordre: 19
notion: series-numeriques
---

## Énoncé

> **Théorème (Euler).**
>
> $$
> \sum_{n=1}^{+\infty} \frac{1}{n^2} = \frac{\pi^2}{6}.
> $$

On donne ici une démonstration élémentaire, qui n'utilise que la formule de Moivre, les relations entre coefficients et racines et un encadrement trigonométrique.

## Idée

Les nombres $\cot^2\left( \frac{k\pi}{2m+1} \right)$, $1 \leq k \leq m$, sont les racines d'un polynôme explicite : leur somme se calcule exactement. Or $\cot^2 x$ et $\frac{1}{x^2}$ diffèrent de moins de $1$ sur $\left] 0, \frac{\pi}{2} \right[$ : on encadre la somme partielle de $\sum \frac{1}{k^2}$, et les deux bornes tendent vers $\frac{\pi^2}{6}$.

## Démonstration

**Étape 1 : un encadrement.** Pour $0 < x < \frac{\pi}{2}$, on a $0 < \sin x < x < \tan x$, donc $\frac{1}{\tan^2 x} < \frac{1}{x^2} < \frac{1}{\sin^2 x}$, c'est-à-dire, avec $\cot = \frac{\cos}{\sin}$ et $\frac{1}{\sin^2} = 1 + \cot^2$ :

$$
\cot^2 x < \frac{1}{x^2} < 1 + \cot^2 x. \qquad (1)
$$

**Étape 2 : un polynôme dont les racines sont les $\cot^2$.** Soient $m \geq 1$ et $\theta \in \R$ tel que $\sin \theta \neq 0$. La formule de Moivre et le binôme donnent

$$
\cos\big( (2m+1)\theta \big) + i \sin\big( (2m+1)\theta \big) = (\cos \theta + i \sin \theta)^{2m+1} = \sum_{p=0}^{2m+1} \binom{2m+1}{p} \cos^{2m+1-p} \theta \, (i \sin \theta)^p.
$$

Les termes imaginaires sont ceux d'indice $p = 2j + 1$ impair, avec $i^{2j+1} = (-1)^j i$. En prenant la partie imaginaire et en factorisant par $\sin^{2m+1} \theta$ :

$$
\sin\big( (2m+1)\theta \big) = \sum_{j=0}^{m} (-1)^j \binom{2m+1}{2j+1} \cos^{2m-2j} \theta \, \sin^{2j+1} \theta = \sin^{2m+1} \theta \; P\big( \cot^2 \theta \big),
$$

où $P = \sum_{j=0}^{m} (-1)^j \binom{2m+1}{2j+1} X^{m-j} = \binom{2m+1}{1} X^m - \binom{2m+1}{3} X^{m-1} + \cdots$, de degré $m$. Pour $\theta_k = \frac{k\pi}{2m+1}$ avec $k \in [\![1, m]\!]$, on a $\sin\big( (2m+1)\theta_k \big) = \sin(k\pi) = 0$ et $\sin \theta_k \neq 0$, donc $P(\cot^2 \theta_k) = 0$. Les $\theta_k$ sont distincts dans $\left] 0, \frac{\pi}{2} \right[$, où $\cot^2$ est strictement décroissante : les $m$ réels $\cot^2 \theta_k$ sont distincts. Ce sont donc **toutes** les racines de $P$, qui est de degré $m$. Par les relations entre coefficients et racines :

$$
\sum_{k=1}^{m} \cot^2 \theta_k = \frac{\binom{2m+1}{3}}{\binom{2m+1}{1}} = \frac{(2m+1)(2m)(2m-1)}{6(2m+1)} = \frac{m(2m-1)}{3}. \qquad (2)
$$

**Étape 3 : l'encadrement de la somme partielle.** On applique (1) en $x = \theta_k$ et on somme pour $k$ de $1$ à $m$, avec $\frac{1}{\theta_k^2} = \frac{(2m+1)^2}{\pi^2 k^2}$ et (2) :

$$
\frac{m(2m-1)}{3} < \frac{(2m+1)^2}{\pi^2} \sum_{k=1}^{m} \frac{1}{k^2} < m + \frac{m(2m-1)}{3} = \frac{2m(m+1)}{3}.
$$

En multipliant par $\frac{\pi^2}{(2m+1)^2}$ :

$$
\frac{\pi^2}{6} \cdot \frac{2m(2m-1)}{(2m+1)^2} < \sum_{k=1}^{m} \frac{1}{k^2} < \frac{\pi^2}{6} \cdot \frac{4m(m+1)}{(2m+1)^2}.
$$

Les deux fractions tendent vers $1$ quand $m \to +\infty$. Par encadrement, $\sum_{k=1}^{m} \frac{1}{k^2} \to \frac{\pi^2}{6}$.

## Remarques

- **Conséquences.** En séparant indices pairs et impairs, $\sum_{n \geq 0} \frac{1}{(2n+1)^2} = \frac{\pi^2}{6} - \frac{1}{4} \cdot \frac{\pi^2}{6} = \frac{\pi^2}{8}$, et $\sum_{n \geq 1} \frac{(-1)^{n+1}}{n^2} = \frac{\pi^2}{12}$.
- **Autres preuves.** Les séries de Fourier (égalité de Parseval appliquée à $x \mapsto x$ sur $[-\pi, \pi]$), une intégrale double sur $[0, 1]^2$, ou le produit infini de $\frac{\sin x}{x}$ proposé par Euler. Plus généralement, $\zeta(2p)$ est un multiple rationnel de $\pi^{2p}$ ; on ignore en revanche presque tout de $\zeta(3)$, dont on sait seulement depuis Apéry (1978) qu'il est irrationnel.
