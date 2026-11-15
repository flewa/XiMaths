---
titre: Théorème d'Abel radial
programmes: MP, MPI, L2
statut: preuve-hors-programme
ordre: 10
notion: series-entieres
---

## Énoncé

> **Théorème (Abel radial).** Soit $\sum a_n x^n$ une série entière de rayon de convergence $R \in \, ]0, +\infty[$, de somme $f$ sur $]{-}R, R[$. Si la série numérique $\sum a_n R^n$ converge, alors
>
> $$
> f(x) = \sum_{n=0}^{+\infty} a_n x^n \xrightarrow[x \to R^-]{} \sum_{n=0}^{+\infty} a_n R^n.
> $$

Au programme de MP, la démonstration est hors programme.

## Idée

On écrit $a_n$ comme différence de deux restes consécutifs de la série $\sum a_n R^n$ (transformation d'Abel, l'analogue discret d'une intégration par parties). La somme $f(x)$ s'exprime alors avec ces restes, qui tendent vers $0$, multipliés par le petit facteur $1 - x$.

## Démonstration

**Réduction à $R = 1$.** En posant $b_n = a_n R^n$, la série $\sum b_n y^n$ a pour rayon $1$, $\sum b_n$ converge, et $f(x) = \sum b_n \left( \frac{x}{R} \right)^n$. On suppose donc $R = 1$ et $\sum a_n$ convergente, de somme $S$.

**Transformation d'Abel.** Pour $n \geq 0$, soit $r_n = \sum_{k=n+1}^{+\infty} a_k$ le reste d'ordre $n$, et posons $r_{-1} = S$. Alors $a_n = r_{n-1} - r_n$ pour tout $n \geq 0$, et $r_n \to 0$. Pour $x \in [0, 1[$ et $N \in \N$ :

$$
\sum_{n=0}^{N} a_n x^n = \sum_{n=0}^{N} r_{n-1} x^n - \sum_{n=0}^{N} r_n x^n = S + \sum_{n=0}^{N-1} r_n x^{n+1} - \sum_{n=0}^{N} r_n x^n = S - (1 - x) \sum_{n=0}^{N-1} r_n x^n - r_N x^N,
$$

en décalant l'indice dans la première somme. La suite $(r_n)$ est bornée et $x \in [0, 1[$, donc $\sum r_n x^n$ converge et $r_N x^N \to 0$. En faisant tendre $N$ vers $+\infty$ :

$$
f(x) - S = -(1 - x) \sum_{n=0}^{+\infty} r_n x^n.
$$

**Estimation.** Soit $\varepsilon > 0$, et $N$ tel que $|r_n| \leq \varepsilon$ pour tout $n \geq N$. Pour $x \in [0, 1[$ :

$$
\lvert f(x) - S \rvert \leq (1 - x) \sum_{n=0}^{N-1} |r_n| + (1 - x) \sum_{n=N}^{+\infty} \varepsilon \, x^n \leq (1 - x) \sum_{n=0}^{N-1} |r_n| + \varepsilon,
$$

car $(1 - x) \sum_{n \geq N} x^n = x^N \leq 1$. Le premier terme est le produit de $1 - x$ par une constante : il est inférieur à $\varepsilon$ pour $x$ assez proche de $1$. Alors $|f(x) - S| \leq 2\varepsilon$. Donc $f(x) \to S$ quand $x \to 1^-$.

## Remarques

- **Applications.** La série $\sum \frac{(-1)^{n+1}}{n}$ converge (critère des séries alternées), et $\ln(1 + x) = \sum_{n \geq 1} \frac{(-1)^{n+1}}{n} x^n$ sur $]{-}1, 1[$ ; par le théorème, $\sum_{n=1}^{+\infty} \frac{(-1)^{n+1}}{n} = \ln 2$. De même, $\arctan x = \sum_{n \geq 0} \frac{(-1)^n}{2n+1} x^{2n+1}$ donne $\sum_{n=0}^{+\infty} \frac{(-1)^n}{2n+1} = \frac{\pi}{4}$.
- **La réciproque est fausse.** Pour $a_n = (-1)^n$, $f(x) = \frac{1}{1 + x} \to \frac{1}{2}$ quand $x \to 1^-$, alors que $\sum (-1)^n$ diverge. Il faut une hypothèse supplémentaire, par exemple $a_n = o\left( \frac{1}{n} \right)$ (théorème taubérien de Tauber).
