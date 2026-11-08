---
titre: Convergence dominée et intégrales à paramètre
programmes: MP, PSI
ordre: 5
notion: integrales-a-parametre
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$ et $I$ est un intervalle de $\R$. Une fonction est **continue par morceaux sur $I$** si elle l'est sur tout segment inclus dans $I$, et **intégrable sur $I$** si l'intégrale de sa valeur absolue (ou de son module) sur $I$ converge.

## Convergence dominée

> **Théorème de convergence dominée.** Soit $(f_n)$ une suite de fonctions continues par morceaux de $I$ dans $\K$. On suppose :
>
> 1. $(f_n)$ converge simplement sur $I$ vers une fonction $f$ continue par morceaux sur $I$ ;
> 2. **(domination)** il existe $\varphi : I \to \R_+$ continue par morceaux et intégrable sur $I$ telle que $|f_n(t)| \leq \varphi(t)$ pour tout $n \in \N$ et tout $t \in I$.
>
> Alors les $f_n$ et $f$ sont intégrables sur $I$, et
>
> $$
> \int_I f_n \xrightarrow[n \to +\infty]{} \int_I f.
> $$

La fonction $\varphi$ ne dépend que de $t$ : on cherche une majoration de $|f_n(t)|$ valable **pour tous les $n$ à la fois**.

> **Théorème d'intégration terme à terme.** Soit $(f_n)$ une suite de fonctions continues par morceaux et intégrables sur $I$. On suppose que $\sum f_n$ converge simplement sur $I$ vers une fonction $S$ continue par morceaux sur $I$, et que la série numérique $\sum \int_I |f_n|$ converge. Alors $S$ est intégrable sur $I$ et
>
> $$
> \int_I \sum_{n=0}^{+\infty} f_n = \sum_{n=0}^{+\infty} \int_I f_n.
> $$

Si $\sum \int_I |f_n|$ diverge, on peut souvent appliquer la convergence dominée à la suite des sommes partielles.

## Continuité d'une intégrale à paramètre

Soient $A$ une partie de $\R$ (souvent un intervalle), $f : A \times I \to \K$, et $g(x) = \int_I f(x, t) \, dt$ quand cette intégrale converge.

> **Théorème (continuité).** On suppose :
>
> 1. pour tout $t \in I$, la fonction $x \mapsto f(x, t)$ est continue sur $A$ ;
> 2. pour tout $x \in A$, la fonction $t \mapsto f(x, t)$ est continue par morceaux sur $I$ ;
> 3. **(domination)** il existe $\varphi : I \to \R_+$ continue par morceaux et intégrable sur $I$ telle que $|f(x, t)| \leq \varphi(t)$ pour tout $(x, t) \in A \times I$.
>
> Alors $g$ est définie et continue sur $A$.

Si $A$ est un intervalle, il suffit que l'hypothèse de domination soit vérifiée sur tout segment $[c, d] \subset A$, avec une fonction $\varphi_{[c, d]}$ qui peut dépendre du segment : c'est la **domination locale**.

## Dérivation d'une intégrale à paramètre

Dans cette section, $J$ est un intervalle de $\R$ et $f : J \times I \to \K$.

> **Théorème (dérivation sous l'intégrale).** On suppose :
>
> 1. pour tout $x \in J$, la fonction $t \mapsto f(x, t)$ est continue par morceaux et intégrable sur $I$ ;
> 2. la dérivée partielle $\dfrac{\partial f}{\partial x}$ existe sur $J \times I$ ; pour tout $x \in J$, $t \mapsto \dfrac{\partial f}{\partial x}(x, t)$ est continue par morceaux sur $I$ ; pour tout $t \in I$, $x \mapsto \dfrac{\partial f}{\partial x}(x, t)$ est continue sur $J$ ;
> 3. **(domination)** il existe $\varphi : I \to \R_+$ continue par morceaux et intégrable sur $I$ telle que $\left| \dfrac{\partial f}{\partial x}(x, t) \right| \leq \varphi(t)$ pour tout $(x, t) \in J \times I$.
>
> Alors $g : x \mapsto \int_I f(x, t) \, dt$ est de classe $\mathcal{C}^1$ sur $J$ et, pour tout $x \in J$,
>
> $$
> g'(x) = \int_I \frac{\partial f}{\partial x}(x, t) \, dt.
> $$

La domination locale (sur tout segment de $J$) suffit encore.

**Classe $\mathcal{C}^k$** ($k \geq 1$). On suppose que, pour tout $j \in [\![0, k]\!]$, la dérivée partielle $\frac{\partial^j f}{\partial x^j}$ existe sur $J \times I$, est continue par rapport à $x$ et continue par morceaux par rapport à $t$ ; que $t \mapsto \frac{\partial^j f}{\partial x^j}(x, t)$ est intégrable sur $I$ pour tout $x \in J$ et tout $j \in [\![0, k-1]\!]$ ; et que $\frac{\partial^k f}{\partial x^k}$ vérifie l'hypothèse de domination, éventuellement locale. Alors $g$ est de classe $\mathcal{C}^k$ sur $J$ et $g^{(j)}(x) = \int_I \frac{\partial^j f}{\partial x^j}(x, t) \, dt$ pour $j \in [\![0, k]\!]$.

## Exemple : la fonction Gamma

Pour $x > 0$, l'intégrale $\Gamma(x) = \int_0^{+\infty} t^{x-1} e^{-t} \, dt$ converge. La fonction $\Gamma$ est de classe $\mathcal{C}^\infty$ sur $]0, +\infty[$ (domination sur chaque segment $[c, d] \subset \, ]0, +\infty[$), et

$$
\Gamma(x + 1) = x \, \Gamma(x) \quad \text{pour tout } x > 0, \qquad \Gamma(n + 1) = n! \quad \text{pour tout } n \in \N.
$$

## Pièges fréquents

- Majorer $|f(x, t)|$ par une fonction qui dépend encore de $x$ : ce n'est pas une domination.
- Dominer $f$ au lieu de $\frac{\partial f}{\partial x}$ pour dériver.
- Chercher une domination sur tout $J$ quand elle n'existe que sur les segments : la domination locale suffit, et c'est souvent la seule possible (par exemple pour $\Gamma$ près de $0$).
