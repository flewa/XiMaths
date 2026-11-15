---
titre: Sous-groupes additifs de ℝ
programmes: MP, MPI, L2
statut: hors-programme
ordre: 18
notion: groupes-anneaux
---

## Énoncé

> **Théorème.** Soit $G$ un sous-groupe de $(\R, +)$. Alors, ou bien il existe un unique $a \geq 0$ tel que $G = a\Z$, ou bien $G$ est **dense** dans $\R$.
>
> **Corollaire.** Pour $\alpha \in \R$, le sous-groupe $\Z + \alpha\Z = \{ p + q\alpha : p, q \in \Z \}$ est dense dans $\R$ si et seulement si $\alpha$ est irrationnel.

## Idée

Tout se joue sur $a = \inf \left( G \cap \, ]0, +\infty[ \right)$. Si $a > 0$, c'est un élément de $G$ et tout élément de $G$ est un multiple de $a$, par une division euclidienne. Si $a = 0$, $G$ contient des éléments positifs aussi petits qu'on veut, et leurs multiples remplissent tous les intervalles.

## Démonstration

Si $G = \{0\}$, alors $G = 0\Z$. Supposons $G \neq \{0\}$ : si $x \in G$ est non nul, $x$ ou $-x$ est un élément strictement positif de $G$. L'ensemble $G_+ = G \cap \, ]0, +\infty[$ est donc non vide et minoré par $0$ ; soit $a = \inf G_+ \geq 0$.

**Cas $a > 0$.**

*$a$ appartient à $G$.* Sinon, par la caractérisation de la borne inférieure, il existe $x \in G_+$ tel que $a < x < 2a$ (puisque $x \neq a$), puis $y \in G_+$ tel que $a < y < x$. Alors $x - y \in G$ et $0 < x - y < 2a - a = a$ : c'est un élément de $G_+$ strictement inférieur à $a$, contradiction.

*$G = a\Z$.* Comme $a \in G$, tous ses multiples entiers sont dans $G$ : $a\Z \subset G$. Réciproquement, soit $g \in G$ et $n = \left\lfloor \frac{g}{a} \right\rfloor$. Alors $r = g - na \in G$ et $0 \leq r < a$. Si $r > 0$, $r$ serait un élément de $G_+$ inférieur à $a$ : donc $r = 0$ et $g = na \in a\Z$.

L'unicité de $a$ vient de ce que $a$ est alors le plus petit élément strictement positif de $G$.

**Cas $a = 0$.** Soit $]x, y[$ un intervalle avec $x < y$. Comme $\inf G_+ = 0 < y - x$, il existe $g \in G_+$ tel que $0 < g < y - x$. Posons $n = \left\lfloor \frac{x}{g} \right\rfloor + 1$ : alors $n - 1 \leq \frac{x}{g} < n$, donc

$$
x < ng \leq x + g < y.
$$

L'élément $ng$ de $G$ appartient à $]x, y[$ : $G$ rencontre tout intervalle ouvert non vide, il est dense dans $\R$.

**Corollaire.** Si $\alpha = \frac{p}{q}$ avec $p \in \Z$ et $q \in \N^*$, alors $\Z + \alpha\Z \subset \frac{1}{q}\Z$, qui ne rencontre pas l'intervalle $\left] 0, \frac{1}{q} \right[$ : il n'est pas dense. Si $\alpha$ est irrationnel et si $\Z + \alpha\Z = a\Z$ avec $a \geq 0$, alors $a > 0$ (car $1 \in a\Z$), $1 = ma$ et $\alpha = m'a$ pour des entiers $m \neq 0$, $m'$, donc $\alpha = \frac{m'}{m} \in \Q$ : contradiction. Par le théorème, $\Z + \alpha\Z$ est dense.

## Remarques

- **Application.** $\pi$ est irrationnel, donc $\Z + 2\pi\Z$ est dense dans $\R$. Pour tout $t \in \R$, il existe donc des entiers $p_k$, $q_k$ avec $p_k + 2\pi q_k \to t$, d'où $\cos p_k = \cos(p_k + 2\pi q_k) \to \cos t$ : l'ensemble $\{ \cos n : n \in \Z \}$ est dense dans $[-1, 1]$.
- **Sous-groupes de $\Z$.** La même démonstration, dans le cas $a > 0$, montre que les sous-groupes de $(\Z, +)$ sont les $n\Z$, $n \in \N$ : c'est le point de départ de l'arithmétique.
