---
titre: Nombres complexes et trigonométrie
programmes: MPSI, PCSI
ordre: 1
notion: nombres-complexes
---

## Cadre et notations

Tout nombre complexe $z$ s'écrit de façon unique $z = a + ib$ avec $(a, b) \in \R^2$ : $a = \operatorname{Re} z$ est sa partie réelle, $b = \operatorname{Im} z$ sa partie imaginaire. Son **conjugué** est $\overline{z} = a - ib$ et son **module** est $|z| = \sqrt{a^2 + b^2}$. On note $\mathbb{U} = \{ z \in \C : |z| = 1 \}$.

## Conjugué et module

> **Proposition.** Pour tous $z, w \in \C$ :
>
> $$
> \overline{z + w} = \overline{z} + \overline{w}, \qquad \overline{z w} = \overline{z} \, \overline{w}, \qquad z \overline{z} = |z|^2, \qquad |z w| = |z| \, |w|,
> $$
>
> $$
> \operatorname{Re} z = \frac{z + \overline{z}}{2}, \qquad \operatorname{Im} z = \frac{z - \overline{z}}{2i}.
> $$
>
> Si $z \neq 0$, alors $\dfrac{1}{z} = \dfrac{\overline{z}}{|z|^2}$.

> **Théorème (inégalité triangulaire).** Pour tous $z, w \in \C$ :
>
> $$
> \big| |z| - |w| \big| \leq |z + w| \leq |z| + |w|.
> $$
>
> On a $|z + w| = |z| + |w|$ si et seulement si $w = 0$ ou s'il existe $\lambda \in \R_+$ tel que $z = \lambda w$.

## Exponentielle complexe

> **Définition.** Pour $\theta \in \R$, on pose $e^{i\theta} = \cos \theta + i \sin \theta$. Pour $z = a + ib$ avec $(a, b) \in \R^2$, on pose $e^z = e^a e^{ib}$.

> **Proposition.** Pour tous $\theta, \theta' \in \R$ et tous $z, w \in \C$ :
>
> 1. $e^{i\theta} \in \mathbb{U}$, et tout élément de $\mathbb{U}$ s'écrit $e^{i\theta}$ avec $\theta \in \R$ ;
> 2. $e^{i\theta} = e^{i\theta'}$ si et seulement si $\theta - \theta' \in 2\pi\Z$ ;
> 3. $e^{z + w} = e^z e^w$, $e^z \neq 0$ et $|e^z| = e^{\operatorname{Re} z}$ ;
> 4. $e^z = e^w$ si et seulement si $z - w \in 2i\pi\Z$.

> **Formules d'Euler et de Moivre.** Pour tout $\theta \in \R$ et tout $n \in \Z$ :
>
> $$
> \cos \theta = \frac{e^{i\theta} + e^{-i\theta}}{2}, \qquad \sin \theta = \frac{e^{i\theta} - e^{-i\theta}}{2i}, \qquad (\cos \theta + i \sin \theta)^n = \cos(n\theta) + i \sin(n\theta).
> $$

**Forme trigonométrique.** Tout $z \in \C^*$ s'écrit $z = r e^{i\theta}$ avec $r = |z| > 0$ et $\theta \in \R$ ; le réel $\theta$ est unique modulo $2\pi$ et s'appelle **un argument** de $z$. Le nombre $0$ n'a pas d'argument. Si $z, w \in \C^*$ ont pour arguments $\theta$ et $\theta'$, alors $\theta + \theta'$ est un argument de $zw$.

**Équation $e^z = w$.** Pour $w \in \C^*$ d'argument $\alpha$, les solutions de $e^z = w$ sont les $z = \ln|w| + i(\alpha + 2k\pi)$, $k \in \Z$. L'équation $e^z = 0$ n'a pas de solution.

## Technique de l'angle moitié

Pour tous $a, b \in \R$ :

$$
e^{ia} + e^{ib} = 2 \cos\left( \frac{a - b}{2} \right) e^{i\frac{a+b}{2}}, \qquad e^{ia} - e^{ib} = 2i \sin\left( \frac{a - b}{2} \right) e^{i\frac{a+b}{2}}.
$$

Application : pour $\theta \in \R \setminus 2\pi\Z$ et $n \in \N$,

$$
\sum_{k=0}^{n} e^{ik\theta} = \frac{e^{i(n+1)\theta} - 1}{e^{i\theta} - 1} = e^{i\frac{n\theta}{2}} \, \frac{\sin\left( \frac{(n+1)\theta}{2} \right)}{\sin\left( \frac{\theta}{2} \right)}.
$$

En prenant parties réelle et imaginaire, on obtient $\sum_{k=0}^{n} \cos(k\theta)$ et $\sum_{k=0}^{n} \sin(k\theta)$.

## Racines $n$-ièmes

Dans cette section, $n \in \N^*$.

> **Proposition (racines $n$-ièmes de l'unité).** L'ensemble $\mathbb{U}_n = \{ z \in \C : z^n = 1 \}$ a exactement $n$ éléments :
>
> $$
> \mathbb{U}_n = \left\{ e^{\frac{2ik\pi}{n}} : k \in [\![0, n-1]\!] \right\}.
> $$
>
> Si $n \geq 2$, la somme des éléments de $\mathbb{U}_n$ est nulle.

> **Proposition (racines $n$-ièmes d'un complexe non nul).** Soit $w = \rho e^{i\alpha}$ avec $\rho > 0$ et $\alpha \in \R$. L'équation $z^n = w$ a exactement $n$ solutions dans $\C$ :
>
> $$
> z_k = \rho^{1/n} \, e^{i\frac{\alpha + 2k\pi}{n}}, \qquad k \in [\![0, n-1]\!].
> $$

**Racines carrées sous forme algébrique.** Pour trouver les $z = x + iy$ ($x, y \in \R$) tels que $z^2 = a + ib$ ($a, b \in \R$), on résout le système $x^2 - y^2 = a$, $2xy = b$, $x^2 + y^2 = \sqrt{a^2 + b^2}$ ; la dernière équation vient de $|z|^2 = |z^2|$.

> **Théorème (équation du second degré).** Soient $a, b, c \in \C$ avec $a \neq 0$, $\Delta = b^2 - 4ac$, et $\delta \in \C$ tel que $\delta^2 = \Delta$. Les solutions de $a z^2 + b z + c = 0$ sont
>
> $$
> z_1 = \frac{-b + \delta}{2a} \qquad \text{et} \qquad z_2 = \frac{-b - \delta}{2a},
> $$
>
> confondues si et seulement si $\Delta = 0$. Elles vérifient $z_1 + z_2 = -\dfrac{b}{a}$ et $z_1 z_2 = \dfrac{c}{a}$.

Si $a, b, c$ sont réels et $\Delta < 0$, on peut prendre $\delta = i\sqrt{-\Delta}$ : les deux solutions sont complexes conjuguées.

## Géométrie

On identifie le plan à $\C$ : le point $M$ d'affixe $z$. Soient $A$, $B$, $C$ trois points d'affixes $a$, $b$, $c$, avec $A \neq B$ et $A \neq C$.

- Un argument de $\dfrac{c - a}{b - a}$ est une mesure de l'angle orienté $(\overrightarrow{AB}, \overrightarrow{AC})$.
- $A$, $B$, $C$ sont alignés si et seulement si $\dfrac{c - a}{b - a} \in \R$.
- $(AB) \perp (AC)$ si et seulement si $\dfrac{c - a}{b - a} \in i\R$.

> **Proposition (similitudes directes).** Soient $\alpha \in \C^*$, $\beta \in \C$ et $f : z \mapsto \alpha z + \beta$.
>
> 1. Si $\alpha = 1$, $f$ est la translation de vecteur d'affixe $\beta$.
> 2. Si $\alpha \neq 1$, $f$ a un unique point fixe $\omega = \dfrac{\beta}{1 - \alpha}$, et $f(z) - \omega = \alpha (z - \omega)$ pour tout $z \in \C$ : $f$ est la similitude directe de centre $\omega$, de rapport $|\alpha|$ et d'angle un argument de $\alpha$.

## Pièges fréquents

- Écrire $\sqrt{z}$ pour un complexe $z$ qui n'est pas un réel positif : cette notation n'est pas définie. Un complexe non nul a **deux** racines carrées, opposées.
- Confondre $|z|^2 = z \overline{z}$ et $z^2$ : ils ne sont égaux que si $z$ est réel.
- Parler de « l'argument » de $z$ : il n'est défini qu'à $2\pi$ près, et pas du tout pour $z = 0$.
- Conclure $z = w$ de $e^z = e^w$ : on sait seulement que $z - w \in 2i\pi\Z$.
