---
titre: Formule de Stirling
programmes: MPSI, MP, L2
statut: preuve-hors-programme
ordre: 12
notion: developpements-limites
---

## Énoncé

> **Théorème (Stirling).** Quand $n \to +\infty$,
>
> $$
> n! \sim \sqrt{2\pi n} \left( \frac{n}{e} \right)^n.
> $$

Au programme de MPSI, la démonstration n'est pas exigible.

## Idée

On montre d'abord que $n! \sim C \sqrt{n} \left( \frac{n}{e} \right)^n$ pour une constante $C > 0$, en étudiant une série télescopique. On identifie ensuite $C = \sqrt{2\pi}$ grâce aux intégrales de Wallis, dont on connaît à la fois un équivalent et une expression avec des factorielles.

## Démonstration

**Étape 1 : existence de la constante.** Posons $u_n = \dfrac{n! \, e^n}{n^{n + 1/2}}$ pour $n \geq 1$. Alors

$$
\frac{u_{n+1}}{u_n} = e \left( \frac{n}{n+1} \right)^{n + 1/2}, \qquad \ln \frac{u_{n+1}}{u_n} = 1 - \left( n + \frac{1}{2} \right) \ln\left( 1 + \frac{1}{n} \right).
$$

Avec $\ln(1 + h) = h - \frac{h^2}{2} + \frac{h^3}{3} + O(h^4)$ pour $h = \frac{1}{n}$ :

$$
\left( n + \frac{1}{2} \right) \left( \frac{1}{n} - \frac{1}{2n^2} + \frac{1}{3n^3} + O\left( \frac{1}{n^4} \right) \right) = 1 + \left( \frac{1}{3} - \frac{1}{4} \right) \frac{1}{n^2} + O\left( \frac{1}{n^3} \right) = 1 + \frac{1}{12 n^2} + O\left( \frac{1}{n^3} \right).
$$

Donc $\ln u_{n+1} - \ln u_n = -\frac{1}{12n^2} + O\left( \frac{1}{n^3} \right) = O\left( \frac{1}{n^2} \right)$ : la série télescopique $\sum (\ln u_{n+1} - \ln u_n)$ converge absolument, donc $(\ln u_n)$ converge vers un réel $L$, et $u_n \to C = e^L > 0$. Autrement dit :

$$
n! \sim C \sqrt{n} \left( \frac{n}{e} \right)^n.
$$

**Étape 2 : intégrales de Wallis.** Soit $W_n = \int_0^{\pi/2} \sin^n t \, dt$. On a $W_0 = \frac{\pi}{2}$, $W_1 = 1$, et $W_n > 0$. Une intégration par parties ($u = \sin^{n+1} t$, $v' = \sin t$) donne, pour $n \geq 0$, $W_{n+2} = (n+1)(W_n - W_{n+2})$, soit

$$
W_{n+2} = \frac{n+1}{n+2} W_n.
$$

*Équivalent.* Comme $0 \leq \sin t \leq 1$ sur $\left[ 0, \frac{\pi}{2} \right]$, la suite $(W_n)$ est décroissante ; donc $\frac{n+1}{n+2} = \frac{W_{n+2}}{W_n} \leq \frac{W_{n+1}}{W_n} \leq 1$, et $W_{n+1} \sim W_n$. Par ailleurs la suite $(n+1) W_{n+1} W_n$ est constante (par la relation de récurrence), égale à $W_1 W_0 = \frac{\pi}{2}$. Donc $n W_n^2 \sim (n+1) W_{n+1} W_n = \frac{\pi}{2}$, et

$$
W_n \sim \sqrt{\frac{\pi}{2n}}.
$$

*Expression exacte.* En itérant la relation de récurrence depuis $W_0$ :

$$
W_{2p} = \frac{2p - 1}{2p} \cdot \frac{2p - 3}{2p - 2} \cdots \frac{1}{2} \cdot \frac{\pi}{2} = \frac{(2p)!}{2^{2p} (p!)^2} \cdot \frac{\pi}{2},
$$

en multipliant numérateur et dénominateur par $(2p)(2p - 2) \cdots 2 = 2^p p!$.

**Étape 3 : identification de $C$.** Par l'étape 1, $(2p)! \sim C \sqrt{2p} \left( \frac{2p}{e} \right)^{2p}$ et $(p!)^2 \sim C^2 p \left( \frac{p}{e} \right)^{2p}$. Donc

$$
W_{2p} \sim \frac{\pi}{2} \cdot \frac{C \sqrt{2p} \, 2^{2p} p^{2p} e^{-2p}}{2^{2p} \, C^2 p \, p^{2p} e^{-2p}} = \frac{\pi \sqrt{2}}{2 C \sqrt{p}}.
$$

L'étape 2 donne aussi $W_{2p} \sim \sqrt{\frac{\pi}{4p}} = \frac{\sqrt{\pi}}{2\sqrt{p}}$. Par unicité de la limite de $\sqrt{p} \, W_{2p}$, on obtient $\frac{\pi\sqrt{2}}{2C} = \frac{\sqrt{\pi}}{2}$, soit $C = \sqrt{2\pi}$.

## Remarques

- Le calcul de l'étape 1 donne plus : $\ln u_n = L + \sum_{k \geq n} \left( \frac{1}{12k^2} + O\left( \frac{1}{k^3} \right) \right) = L + \frac{1}{12n} + O\left( \frac{1}{n^2} \right)$, d'où le développement $n! = \sqrt{2\pi n} \left( \frac{n}{e} \right)^n \left( 1 + \frac{1}{12n} + O\left( \frac{1}{n^2} \right) \right)$.
- **Applications.** $\binom{2n}{n} \sim \frac{4^n}{\sqrt{\pi n}}$ ; la probabilité qu'une marche aléatoire simple revienne en $0$ au temps $2n$ est $\binom{2n}{n} 4^{-n} \sim \frac{1}{\sqrt{\pi n}}$, terme général d'une série divergente.
