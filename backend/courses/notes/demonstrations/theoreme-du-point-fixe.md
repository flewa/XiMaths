---
titre: Théorème du point fixe de Picard
programmes: MP, MPI, L2
statut: hors-programme
ordre: 17
notion: espaces-vectoriels-normes
---

## Énoncé

> **Théorème (point fixe de Picard).** Soient $E$ un espace vectoriel normé de dimension finie, $F$ une partie **fermée** non vide de $E$, et $f : F \to F$ une application **contractante** : il existe $k \in [0, 1[$ tel que $\|f(x) - f(y)\| \leq k \|x - y\|$ pour tous $x, y \in F$. Alors :
>
> 1. $f$ admet un unique point fixe $\ell \in F$ ;
> 2. pour tout $x_0 \in F$, la suite définie par $x_{n+1} = f(x_n)$ converge vers $\ell$, et
>
> $$
> \|x_n - \ell\| \leq \frac{k^n}{1 - k} \, \|x_1 - x_0\| \qquad \text{pour tout } n \in \N.
> $$

Le théorème reste vrai dans tout espace de Banach (espace normé complet), notion hors programme.

## Idée

Les pas $x_{n+1} - x_n$ décroissent au moins comme une suite géométrique de raison $k$. La série des pas converge donc absolument, ce qui donne la convergence de $(x_n)$ ; sa limite est un point fixe par continuité de $f$.

## Démonstration

**Existence.** Par récurrence, $\|x_{n+1} - x_n\| = \|f(x_n) - f(x_{n-1})\| \leq k \|x_n - x_{n-1}\|$, donc

$$
\|x_{n+1} - x_n\| \leq k^n \|x_1 - x_0\| \qquad \text{pour tout } n \in \N.
$$

La série $\sum (x_{n+1} - x_n)$ converge donc absolument (comparaison avec une série géométrique, $0 \leq k < 1$). Dans un espace de dimension finie, une série absolument convergente converge : la suite de ses sommes partielles, $x_n - x_0$, converge, donc $(x_n)$ converge vers un certain $\ell \in E$. Comme $F$ est fermé et que tous les $x_n$ sont dans $F$, on a $\ell \in F$. Enfin, $f$ est lipschitzienne donc continue, et en passant à la limite dans $x_{n+1} = f(x_n)$, on obtient $\ell = f(\ell)$.

**Unicité.** Si $\ell$ et $\ell'$ sont deux points fixes, $\|\ell - \ell'\| = \|f(\ell) - f(\ell')\| \leq k \|\ell - \ell'\|$, donc $(1 - k) \|\ell - \ell'\| \leq 0$, et $\ell = \ell'$ car $k < 1$.

**Vitesse.** Pour $n \in \N$, $\ell - x_n = \sum_{p=n}^{+\infty} (x_{p+1} - x_p)$, donc

$$
\|x_n - \ell\| \leq \sum_{p=n}^{+\infty} \|x_{p+1} - x_p\| \leq \|x_1 - x_0\| \sum_{p=n}^{+\infty} k^p = \frac{k^n}{1 - k} \, \|x_1 - x_0\|.
$$

## Remarques

- **Chaque hypothèse compte.**
  - $k < 1$ est indispensable, même avec une inégalité stricte : $f(x) = \sqrt{1 + x^2}$ vérifie $|f(x) - f(y)| < |x - y|$ pour $x \neq y$ (accroissements finis, $|f'| < 1$), mais n'a pas de point fixe sur $\R$ car $f(x) > |x| \geq x$.
  - $F$ fermé : $x \mapsto \frac{x}{2}$ est contractante de $]0, 1]$ dans $]0, 1]$, sans point fixe dans $]0, 1]$.
- **En pratique**, pour une fonction réelle dérivable sur un intervalle fermé stable $I$, on obtient $k$ en majorant $|f'|$ par une constante $k < 1$ sur $I$ (inégalité des accroissements finis). Exemple : $\cos$ envoie $[0, 1]$ dans $[\cos 1, 1] \subset [0, 1]$ et $|\cos'| = |\sin| \leq \sin 1 < 1$ sur $[0, 1]$ ; l'équation $\cos x = x$ a donc une unique solution dans $[0, 1]$, limite de toute suite $x_{n+1} = \cos x_n$ issue de $[0, 1]$.
- **Applications.** Le théorème de Cauchy-Lipschitz et le théorème d'inversion locale se démontrent avec ce théorème, dans un espace de fonctions de dimension infinie mais complet.
