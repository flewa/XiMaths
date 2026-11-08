---
titre: Suites et séries de fonctions
programmes: MP, PSI
ordre: 2
notion: suites-series-fonctions
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$, $A$ est une partie de $\K$ (le plus souvent un intervalle $I$ de $\R$), et $f_n, f : A \to \K$. Pour une fonction bornée $g : A \to \K$, on note $\|g\|_\infty = \sup_{x \in A} |g(x)|$.

## Modes de convergence des suites de fonctions

> **Définition.**
>
> 1. $(f_n)$ **converge simplement** vers $f$ sur $A$ si, pour tout $x \in A$, $f_n(x) \to f(x)$.
> 2. $(f_n)$ **converge uniformément** vers $f$ sur $A$ si $f_n - f$ est bornée sur $A$ à partir d'un certain rang et si $\|f_n - f\|_\infty \to 0$.

La convergence uniforme entraîne la convergence simple ; la limite uniforme est donc nécessairement la limite simple.

**Méthode.** On calcule d'abord la limite simple $f$. Pour prouver la convergence uniforme, on majore $|f_n(x) - f(x)|$ par un réel $\varepsilon_n$ **indépendant de $x$** tel que $\varepsilon_n \to 0$. Pour la réfuter, on exhibe une suite $(x_n)$ de points de $A$ telle que $f_n(x_n) - f(x_n)$ ne tende pas vers $0$.

## Propriétés de la limite uniforme

> **Théorème (continuité).** Si chaque $f_n$ est continue sur $A$ et si $(f_n)$ converge uniformément vers $f$ sur $A$, alors $f$ est continue sur $A$. Sur un intervalle $I$, il suffit que la convergence soit uniforme sur tout segment inclus dans $I$.

Exemple : sur $[0, 1]$, $f_n : x \mapsto x^n$ converge simplement vers la fonction nulle sur $[0, 1[$ et égale à $1$ en $1$ ; cette limite n'est pas continue, donc la convergence n'est pas uniforme sur $[0, 1]$.

> **Théorème (double limite).** Soit $a$ un point adhérent à $A$ (éventuellement $\pm\infty$ si $A \subset \R$). Si $(f_n)$ converge uniformément vers $f$ sur $A$ et si, pour tout $n$, $f_n(x) \to \ell_n \in \K$ quand $x \to a$, alors la suite $(\ell_n)$ converge vers un $\ell \in \K$ et $f(x) \to \ell$ quand $x \to a$.

> **Théorème (intégration sur un segment).** Si chaque $f_n$ est continue sur $[a, b]$ et si $(f_n)$ converge uniformément vers $f$ sur $[a, b]$, alors $\int_a^b f_n \to \int_a^b f$.

> **Théorème (dérivation).** Soit $I$ un intervalle. Si chaque $f_n$ est de classe $\mathcal{C}^1$ sur $I$, si $(f_n)$ converge simplement vers $f$ sur $I$ et si $(f_n')$ converge uniformément sur tout segment de $I$ vers une fonction $g$, alors $f$ est de classe $\mathcal{C}^1$ sur $I$ et $f' = g$.

## Séries de fonctions

On considère la série de fonctions $\sum f_n$, de sommes partielles $S_n = \sum_{k=0}^{n} f_k$.

> **Définition.**
>
> 1. $\sum f_n$ **converge simplement** sur $A$ si, pour tout $x \in A$, la série numérique $\sum f_n(x)$ converge.
> 2. $\sum f_n$ **converge uniformément** sur $A$ si la suite $(S_n)$ converge uniformément sur $A$ ; de façon équivalente, si elle converge simplement et si la suite des restes $R_n = \sum_{k=n+1}^{+\infty} f_k$ converge uniformément vers $0$ sur $A$.
> 3. $\sum f_n$ **converge normalement** sur $A$ si chaque $f_n$ est bornée sur $A$ et si la série numérique $\sum \|f_n\|_\infty$ converge.

Convergence normale $\implies$ convergence uniforme $\implies$ convergence simple ; la convergence normale entraîne aussi la convergence absolue en tout point. Pour prouver la convergence normale, il suffit de trouver une suite $(\alpha_n)$ telle que $|f_n(x)| \leq \alpha_n$ pour tous $n$ et $x \in A$, et $\sum \alpha_n$ convergente.

> **Théorème.** Soit $I$ un intervalle.
>
> 1. **Continuité :** si chaque $f_n$ est continue sur $A$ et si $\sum f_n$ converge uniformément sur $A$ (ou, sur un intervalle, sur tout segment de $I$), alors sa somme est continue.
> 2. **Double limite :** si $\sum f_n$ converge uniformément sur $A$ et si $f_n(x) \to \ell_n$ quand $x \to a$ pour tout $n$, alors $\sum \ell_n$ converge et $\sum_{n=0}^{+\infty} f_n(x) \to \sum_{n=0}^{+\infty} \ell_n$ quand $x \to a$.
> 3. **Intégration sur un segment :** si chaque $f_n$ est continue sur $[a, b]$ et si $\sum f_n$ converge uniformément sur $[a, b]$, alors $\int_a^b \sum_{n=0}^{+\infty} f_n = \sum_{n=0}^{+\infty} \int_a^b f_n$.
> 4. **Dérivation :** si chaque $f_n$ est de classe $\mathcal{C}^1$ sur $I$, si $\sum f_n$ converge simplement sur $I$ et si $\sum f_n'$ converge uniformément sur tout segment de $I$, alors $\sum_{n=0}^{+\infty} f_n$ est de classe $\mathcal{C}^1$ sur $I$ et sa dérivée est $\sum_{n=0}^{+\infty} f_n'$.

Plus généralement, pour $k \in \N^*$ : si chaque $f_n$ est de classe $\mathcal{C}^k$ sur $I$, si les séries $\sum f_n^{(j)}$ convergent simplement sur $I$ pour $0 \leq j \leq k - 1$ et si $\sum f_n^{(k)}$ converge uniformément sur tout segment de $I$, alors la somme est de classe $\mathcal{C}^k$ et se dérive $k$ fois terme à terme.

## Approximation

> **Théorème (Weierstrass).** Toute fonction continue sur un segment $[a, b]$, à valeurs dans $\K$, est limite uniforme sur $[a, b]$ d'une suite de fonctions polynomiales.

## Pièges fréquents

- Majorer $|f_n(x) - f(x)|$ par une quantité qui dépend encore de $x$, et conclure à la convergence uniforme.
- Conclure à la convergence uniforme sur $I$ entier alors qu'on l'a prouvée sur chaque segment $[a, b] \subset I$ : ce n'est pas la même chose, mais cela suffit pour la continuité et la dérivation.
- Dériver terme à terme en vérifiant la convergence uniforme de $\sum f_n$ au lieu de celle de $\sum f_n'$.
