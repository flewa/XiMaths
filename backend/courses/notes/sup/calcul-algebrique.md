---
titre: Sommes, inégalités et trigonométrie
programmes: MPSI, MP2I
ordre: 2
notion: sommes-recurrence
---

## Cadre et notations

Dans toute la fiche, $n \in \N$ et les $a_k$, $b_k$ sont des réels (ou des complexes pour les sommes). Pour un ensemble fini $I$, on note $\sum_{i \in I} a_i$ et $\prod_{i \in I} a_i$ ; une somme sur un ensemble vide vaut $0$, un produit sur un ensemble vide vaut $1$. On note $[\![p, q]\!]$ l'ensemble des entiers $k$ tels que $p \leq k \leq q$.

## Sommes et produits

**Télescopage.** $\sum_{k=0}^{n} (a_{k+1} - a_k) = a_{n+1} - a_0$ et, si les $a_k$ sont non nuls, $\prod_{k=0}^{n} \frac{a_{k+1}}{a_k} = \frac{a_{n+1}}{a_0}$.

**Changement d'indice.** $\sum_{k=1}^{n} a_k = \sum_{j=0}^{n-1} a_{j+1}$ (avec $j = k - 1$) et $\sum_{k=0}^{n} a_k = \sum_{j=0}^{n} a_{n-j}$ (avec $j = n - k$).

> **Proposition (sommes usuelles).** Pour $n \in \N^*$ et $x \in \C$ :
>
> $$
> \sum_{k=1}^{n} k = \frac{n(n+1)}{2}, \qquad \sum_{k=1}^{n} k^2 = \frac{n(n+1)(2n+1)}{6}, \qquad \sum_{k=0}^{n} x^k = \begin{cases} \dfrac{1 - x^{n+1}}{1 - x} & \text{si } x \neq 1, \\ n + 1 & \text{si } x = 1. \end{cases}
> $$
>
> Pour tous $a, b \in \C$ : $a^n - b^n = (a - b) \sum_{k=0}^{n-1} a^k b^{n-1-k}$.

**Sommes doubles.** Sur un rectangle, on peut intervertir : $\sum_{i=1}^{n} \sum_{j=1}^{p} a_{ij} = \sum_{j=1}^{p} \sum_{i=1}^{n} a_{ij}$, et $\left( \sum_{i=1}^{n} a_i \right) \left( \sum_{j=1}^{p} b_j \right) = \sum_{i=1}^{n} \sum_{j=1}^{p} a_i b_j$. Sur un triangle, on réécrit l'ensemble des indices :

$$
\sum_{i=1}^{n} \sum_{j=i}^{n} a_{ij} = \sum_{1 \leq i \leq j \leq n} a_{ij} = \sum_{j=1}^{n} \sum_{i=1}^{j} a_{ij}.
$$

## Coefficients binomiaux

Pour $0 \leq k \leq n$, on pose $\binom{n}{k} = \dfrac{n!}{k! \, (n - k)!}$, avec $0! = 1$ ; par convention $\binom{n}{k} = 0$ si $k < 0$ ou $k > n$.

> **Proposition.** Pour $n \in \N$ et $k \in \Z$ : $\binom{n}{k} = \binom{n}{n-k}$ et, pour $n \geq 1$, $\binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}$ (**formule de Pascal**). En particulier, $\binom{n}{k}$ est un entier.

> **Formule du binôme.** Pour tous $a, b \in \C$ et $n \in \N$ :
>
> $$
> (a + b)^n = \sum_{k=0}^{n} \binom{n}{k} a^k b^{n-k}.
> $$

Cas utiles : $\sum_{k=0}^{n} \binom{n}{k} = 2^n$ et, pour $n \geq 1$, $\sum_{k=0}^{n} (-1)^k \binom{n}{k} = 0$.

## Systèmes linéaires et pivot

On résout un système de deux ou trois équations à deux ou trois inconnues par des **opérations élémentaires** sur les lignes, qui donnent un système **équivalent** (mêmes solutions) :

- échange de deux lignes, noté $L_i \leftrightarrow L_j$ ;
- multiplication d'une ligne par un réel **non nul**, notée $L_i \leftarrow \lambda L_i$ ($\lambda \neq 0$) ;
- ajout à une ligne d'un multiple d'une **autre** ligne, noté $L_i \leftarrow L_i + \lambda L_j$ ($j \neq i$).

On se ramène ainsi à un système triangulaire, qu'on résout en remontant. Géométriquement, on cherche l'intersection de droites de $\R^2$ ou de plans de $\R^3$ : elle peut être vide, réduite à un point, ou infinie.

## Inégalités

L'ordre de $\R$ est compatible avec l'addition ($a \leq b \implies a + c \leq b + c$) et avec la multiplication par un réel **positif** ; multiplier par un réel négatif renverse les inégalités. Si $0 < a \leq b$, alors $\frac{1}{b} \leq \frac{1}{a}$.

**Valeur absolue.** $|x| = \max(x, -x)$. Pour $a \in \R$ et $b \geq 0$ : $|x - a| \leq b \iff a - b \leq x \leq a + b$, c'est-à-dire que $x$ est à distance au plus $b$ de $a$.

> **Inégalité triangulaire.** Pour tous $x, y \in \R$ : $\big| |x| - |y| \big| \leq |x + y| \leq |x| + |y|$.

Une partie $A$ de $\R$ est **majorée** s'il existe $M$ tel que $a \leq M$ pour tout $a \in A$ ; un **maximum** de $A$ est un majorant qui appartient à $A$. De même pour minorée et minimum ; bornée signifie majorée et minorée.

**Partie entière.** Pour $x \in \R$, $\lfloor x \rfloor$ est l'unique entier $n$ tel que $n \leq x < n + 1$. Ainsi $x - 1 < \lfloor x \rfloor \leq x$, et $\lfloor -2{,}5 \rfloor = -3$.

## Trigonométrie

On note $a \equiv b \ [2\pi]$ si $a - b \in 2\pi\Z$. Pour tout $x \in \R$, $\cos^2 x + \sin^2 x = 1$, et

$$
\cos(\pi - x) = -\cos x, \quad \sin(\pi - x) = \sin x, \quad \cos(\pi + x) = -\cos x, \quad \sin(\pi + x) = -\sin x,
$$

$$
\cos\left( \tfrac{\pi}{2} - x \right) = \sin x, \quad \sin\left( \tfrac{\pi}{2} - x \right) = \cos x, \quad \cos\left( \tfrac{\pi}{2} + x \right) = -\sin x, \quad \sin\left( \tfrac{\pi}{2} + x \right) = \cos x.
$$

Valeurs usuelles : $\cos \frac{\pi}{6} = \frac{\sqrt{3}}{2}$, $\sin \frac{\pi}{6} = \frac{1}{2}$ ; $\cos \frac{\pi}{4} = \sin \frac{\pi}{4} = \frac{\sqrt{2}}{2}$ ; $\cos \frac{\pi}{3} = \frac{1}{2}$, $\sin \frac{\pi}{3} = \frac{\sqrt{3}}{2}$.

> **Formules d'addition.** Pour tous $a, b \in \R$ :
>
> $$
> \cos(a \pm b) = \cos a \cos b \mp \sin a \sin b, \qquad \sin(a \pm b) = \sin a \cos b \pm \cos a \sin b.
> $$
>
> En particulier $\cos(2a) = \cos^2 a - \sin^2 a = 2\cos^2 a - 1 = 1 - 2\sin^2 a$ et $\sin(2a) = 2 \sin a \cos a$.

On en tire, en ajoutant ou retranchant deux formules d'addition :

$$
\cos a \cos b = \frac{\cos(a - b) + \cos(a + b)}{2}, \quad \sin a \sin b = \frac{\cos(a - b) - \cos(a + b)}{2}, \quad \sin a \cos b = \frac{\sin(a + b) + \sin(a - b)}{2}.
$$

**Tangente.** Sur $\R \setminus \left( \frac{\pi}{2} + \pi\Z \right)$, $\tan x = \frac{\sin x}{\cos x}$. Elle est impaire, $\pi$-périodique ($\tan(\pi + x) = \tan x$), dérivable, de dérivée $\tan' = 1 + \tan^2 = \frac{1}{\cos^2}$. Valeurs : $\tan \frac{\pi}{6} = \frac{1}{\sqrt{3}}$, $\tan \frac{\pi}{4} = 1$, $\tan \frac{\pi}{3} = \sqrt{3}$. Quand les tangentes sont définies :

$$
\tan(a \pm b) = \frac{\tan a \pm \tan b}{1 \mp \tan a \tan b}, \qquad \cos x = \frac{1 - t^2}{1 + t^2}, \quad \sin x = \frac{2t}{1 + t^2} \quad \text{avec } t = \tan \frac{x}{2}.
$$

> **Proposition (équations trigonométriques).** Pour tous $a, b \in \R$ :
>
> 1. $\cos a = \cos b \iff a \equiv b \ [2\pi]$ ou $a \equiv -b \ [2\pi]$ ;
> 2. $\sin a = \sin b \iff a \equiv b \ [2\pi]$ ou $a \equiv \pi - b \ [2\pi]$ ;
> 3. si $\tan a$ et $\tan b$ sont définies, $\tan a = \tan b \iff a - b \in \pi\Z$.

Pour tout $x \in \R$, $|\sin x| \leq |x|$.

## Pièges fréquents

- Oublier qu'une somme vide vaut $0$ et un produit vide $1$.
- Changer d'indice sans changer les bornes, ou intervertir une somme triangulaire comme si elle était rectangulaire.
- Multiplier une inégalité par un nombre dont on ne connaît pas le signe.
- Croire que $\lfloor -x \rfloor = -\lfloor x \rfloor$ : c'est faux dès que $x \notin \Z$.
- Écrire $\cos a = \cos b \implies a = b$ : on oublie les solutions $a \equiv -b \ [2\pi]$ et la période.
