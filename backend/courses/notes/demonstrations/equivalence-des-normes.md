---
titre: Équivalence des normes en dimension finie
programmes: MP, MPI, L2
statut: preuve-hors-programme
ordre: 5
notion: espaces-vectoriels-normes
---

## Énoncé

> **Théorème.** Sur un $\K$-espace vectoriel $E$ de dimension finie, toutes les normes sont équivalentes : si $N$ et $N'$ sont deux normes sur $E$, il existe $\alpha, \beta > 0$ tels que $\alpha N \leq N' \leq \beta N$.

Au programme de MP, la démonstration n'est pas exigible.

## Idée

On compare toute norme $N$ à la norme infinie dans une base. La majoration est un simple calcul. Pour la minoration, on montre que $N$ atteint un minimum strictement positif sur la sphère unité de la norme infinie, grâce au théorème de Bolzano-Weierstrass appliqué coordonnée par coordonnée.

## Démonstration

Si $E = \{0\}$, il n'y a rien à montrer. Sinon, soit $(e_1, \dots, e_n)$ une base de $E$. Pour $x = \sum_{i=1}^{n} x_i e_i$, on pose $N_\infty(x) = \max_i |x_i|$ : c'est une norme sur $E$. L'équivalence des normes étant une relation transitive et symétrique, il suffit de montrer que toute norme $N$ est équivalente à $N_\infty$.

**Majoration.** Par l'inégalité triangulaire,

$$
N(x) \leq \sum_{i=1}^{n} |x_i| \, N(e_i) \leq \beta \, N_\infty(x), \qquad \text{avec} \quad \beta = \sum_{i=1}^{n} N(e_i) > 0.
$$

En particulier, $|N(x) - N(y)| \leq N(x - y) \leq \beta N_\infty(x - y)$ : si $N_\infty(x_k - x) \to 0$, alors $N(x_k) \to N(x)$.

**Minoration.** Soit $S = \{ x \in E : N_\infty(x) = 1 \}$, non vide, et $\alpha = \inf_{x \in S} N(x) \geq 0$. Soit $(x_k)$ une suite d'éléments de $S$ telle que $N(x_k) \to \alpha$, et notons $x_{k,i}$ ses coordonnées : elles vérifient $|x_{k,i}| \leq 1$.

- Par le théorème de Bolzano-Weierstrass dans $\K$, on extrait de $(x_k)$ une sous-suite dont la première coordonnée converge ; de celle-ci, une sous-suite dont la deuxième coordonnée converge ; et ainsi de suite. Après $n$ extractions, on obtient une suite extraite $(x_{\varphi(k)})$ dont **toutes** les coordonnées convergent, vers $\ell_1, \dots, \ell_n$.
- Soit $\ell = \sum \ell_i e_i$. Alors $N_\infty(x_{\varphi(k)} - \ell) = \max_i |x_{\varphi(k), i} - \ell_i| \to 0$. Comme $|N_\infty(x_{\varphi(k)}) - N_\infty(\ell)| \leq N_\infty(x_{\varphi(k)} - \ell)$, on a $N_\infty(\ell) = 1$ : $\ell \in S$, et en particulier $\ell \neq 0$.
- Par la remarque qui suit la majoration, $N(x_{\varphi(k)}) \to N(\ell)$ ; donc $N(\ell) = \alpha$. Comme $\ell \neq 0$, $\alpha = N(\ell) > 0$.

Pour $x \neq 0$, le vecteur $\frac{x}{N_\infty(x)}$ appartient à $S$, donc $N\left( \frac{x}{N_\infty(x)} \right) \geq \alpha$, c'est-à-dire $N(x) \geq \alpha N_\infty(x)$ ; c'est encore vrai pour $x = 0$. Ainsi $\alpha N_\infty \leq N \leq \beta N_\infty$.

## Remarques

- **Conséquences.** En dimension finie, la convergence d'une suite, la continuité d'une fonction, le caractère ouvert, fermé, borné ou compact d'une partie ne dépendent pas de la norme. Une suite converge si et seulement si chacune de ses coordonnées dans une base converge ; toute application linéaire est continue.
- **Faux en dimension infinie.** Sur $\R[X]$, les normes $N_1\left( \sum a_k X^k \right) = \sum |a_k|$ et $N_\infty\left( \sum a_k X^k \right) = \max |a_k|$ ne sont pas équivalentes : pour $P_n = 1 + X + \dots + X^n$, $N_1(P_n) = n + 1$ tandis que $N_\infty(P_n) = 1$.
