---
titre: Séries entières
programmes: MP, PSI
ordre: 3
notion: series-entieres
---

## Cadre et notations

Dans toute la fiche, $(a_n)_{n \in \N}$ et $(b_n)_{n \in \N}$ sont des suites de nombres complexes. On appelle **série entière** de coefficients $(a_n)$ la série de fonctions $\sum a_n z^n$, où la variable $z$ décrit $\C$. Pour $r > 0$, on note $D(0, r) = \{ z \in \C : |z| < r \}$ le disque ouvert de centre $0$ et de rayon $r$, et $\overline{D}(0, r) = \{ z \in \C : |z| \leq r \}$ le disque fermé ; on pose $D(0, +\infty) = \C$.

## Rayon de convergence

> **Lemme d'Abel.** Soit $z_0 \in \C$ tel que la suite $(a_n z_0^n)_{n \in \N}$ soit bornée. Alors, pour tout $z \in \C$ tel que $|z| < |z_0|$, la série $\sum a_n z^n$ converge absolument.

> **Définition (rayon de convergence).** Le rayon de convergence de la série entière $\sum a_n z^n$ est
>
> $$
> R = \sup \left\{ r \in \R_+ : \text{la suite } (a_n r^n)_{n \in \N} \text{ est bornée} \right\} \in [0, +\infty].
> $$
>
> L'ensemble considéré contient $0$, donc la borne supérieure existe dans $[0, +\infty]$.

> **Théorème.** Soit $R$ le rayon de convergence de $\sum a_n z^n$ et $z \in \C$.
>
> 1. Si $|z| < R$, la série $\sum a_n z^n$ converge absolument.
> 2. Si $|z| > R$, la suite $(a_n z^n)$ n'est pas bornée ; la série $\sum a_n z^n$ diverge grossièrement.

Le disque $D(0, R)$ s'appelle le **disque ouvert de convergence** ; pour une variable réelle, on parle de l'**intervalle ouvert de convergence** $]{-}R, R[$.

**Sur le cercle $|z| = R$, on ne peut rien affirmer en général.** Les trois séries suivantes ont pour rayon $1$ :

- $\sum z^n$ diverge grossièrement en tout point du cercle $|z| = 1$ ;
- $\sum \frac{z^n}{n^2}$ converge absolument en tout point du cercle $|z| = 1$ ;
- $\sum_{n \geq 1} \frac{z^n}{n}$ diverge en $z = 1$ et converge en $z = -1$.

## Déterminer un rayon de convergence

> **Proposition (règle de d'Alembert).** On suppose $a_n \neq 0$ à partir d'un certain rang et
>
> $$
> \frac{|a_{n+1}|}{|a_n|} \xrightarrow[n \to +\infty]{} \ell \in [0, +\infty].
> $$
>
> Alors $R = \frac{1}{\ell}$, avec les conventions $\frac{1}{0} = +\infty$ et $\frac{1}{+\infty} = 0$.

> **Proposition (comparaison).** Soient $R_a$ et $R_b$ les rayons de convergence de $\sum a_n z^n$ et $\sum b_n z^n$.
>
> 1. Si $a_n = O(b_n)$ quand $n \to +\infty$ (en particulier si $|a_n| \leq |b_n|$ à partir d'un certain rang), alors $R_a \geq R_b$.
> 2. Si $a_n \sim b_n$ quand $n \to +\infty$, alors $R_a = R_b$.

> **Proposition (un point bien choisi).** Soient $R$ le rayon de convergence de $\sum a_n z^n$ et $z_0 \in \C$.
>
> 1. Si la suite $(a_n z_0^n)$ est bornée (en particulier si $\sum a_n z_0^n$ converge), alors $R \geq |z_0|$.
> 2. Si la suite $(a_n z_0^n)$ n'est pas bornée, ou si la série $\sum a_n z_0^n$ diverge, alors $R \leq |z_0|$.
> 3. Si $\sum a_n z_0^n$ converge sans converger absolument, alors $R = |z_0|$.

**Méthode.** Pour une série « lacunaire » comme $\sum a_n z^{2n}$, les coefficients d'indice impair sont nuls : on n'applique pas la règle de d'Alembert aux coefficients, mais la règle de d'Alembert pour les séries numériques au terme général $u_n(z) = a_n z^{2n}$, à $z \neq 0$ fixé.

## Opérations

> **Proposition.** Soient $R_a$ et $R_b$ les rayons de convergence de $\sum a_n z^n$ et $\sum b_n z^n$.
>
> 1. **Somme.** Le rayon $R$ de $\sum (a_n + b_n) z^n$ vérifie $R \geq \min(R_a, R_b)$, avec égalité si $R_a \neq R_b$ ; et pour $|z| < \min(R_a, R_b)$, $\sum_{n=0}^{+\infty} (a_n + b_n) z^n = \sum_{n=0}^{+\infty} a_n z^n + \sum_{n=0}^{+\infty} b_n z^n$.
> 2. **Produit de Cauchy.** Posons $c_n = \sum_{k=0}^{n} a_k b_{n-k}$. Le rayon de $\sum c_n z^n$ est au moins $\min(R_a, R_b)$, et pour $|z| < \min(R_a, R_b)$ :
>
> $$
> \sum_{n=0}^{+\infty} c_n z^n = \left( \sum_{n=0}^{+\infty} a_n z^n \right) \left( \sum_{n=0}^{+\infty} b_n z^n \right).
> $$

> **Proposition.** Les séries entières $\sum a_n z^n$, $\sum_{n \geq 1} n a_n z^{n-1}$ et $\sum \frac{a_n}{n+1} z^{n+1}$ ont le même rayon de convergence.

## Régularité de la somme

> **Théorème (convergence normale).** Si $R > 0$, la série de fonctions $\sum a_n z^n$ converge normalement sur tout disque fermé $\overline{D}(0, r)$ avec $0 \leq r < R$. Sa somme est donc continue sur le disque ouvert $D(0, R)$.

Dans la suite de cette section, $R > 0$ et $f : \, ]{-}R, R[ \, \to \C$ est définie par $f(x) = \sum_{n=0}^{+\infty} a_n x^n$.

> **Théorème (dérivation terme à terme).** La fonction $f$ est de classe $\mathcal{C}^\infty$ sur $]{-}R, R[$ et, pour tout $k \in \N$ et tout $x \in \, ]{-}R, R[$,
>
> $$
> f^{(k)}(x) = \sum_{n=k}^{+\infty} \frac{n!}{(n-k)!} \, a_n x^{n-k}.
> $$
>
> En particulier, $a_n = \dfrac{f^{(n)}(0)}{n!}$ pour tout $n \in \N$.

> **Théorème (intégration terme à terme).** La fonction $F : x \mapsto \sum_{n=0}^{+\infty} \frac{a_n}{n+1} x^{n+1}$ est définie sur $]{-}R, R[$ ; c'est la primitive de $f$ sur $]{-}R, R[$ qui s'annule en $0$.

> **Corollaire (unicité des coefficients).** S'il existe $r > 0$ tel que les deux séries aient un rayon au moins égal à $r$ et que $\sum_{n=0}^{+\infty} a_n x^n = \sum_{n=0}^{+\infty} b_n x^n$ pour tout $x \in \, ]{-}r, r[$, alors $a_n = b_n$ pour tout $n \in \N$.

Conséquence : si $f$ est paire, ses coefficients d'indice impair sont nuls ; si elle est impaire, ses coefficients d'indice pair sont nuls.

## Fonctions développables en série entière

> **Définition.** Soit $r \in \, ]0, +\infty]$. Une fonction $f : \, ]{-}r, r[ \, \to \C$ est **développable en série entière sur $]{-}r, r[$** s'il existe une série entière $\sum a_n x^n$ de rayon au moins égal à $r$ telle que $f(x) = \sum_{n=0}^{+\infty} a_n x^n$ pour tout $x \in \, ]{-}r, r[$.

Une telle fonction est de classe $\mathcal{C}^\infty$ sur $]{-}r, r[$, et la série est nécessairement sa **série de Taylor** en $0$ : $a_n = \frac{f^{(n)}(0)}{n!}$.

**Attention : une fonction de classe $\mathcal{C}^\infty$ n'est pas toujours développable en série entière.** La fonction $f$ définie sur $\R$ par $f(x) = e^{-1/x^2}$ si $x \neq 0$ et $f(0) = 0$ est de classe $\mathcal{C}^\infty$ et vérifie $f^{(n)}(0) = 0$ pour tout $n$ ; sa série de Taylor en $0$ est nulle, alors que $f$ ne s'annule qu'en $0$. Elle n'est développable en série entière sur aucun intervalle $]{-}r, r[$ avec $r > 0$.

> **Proposition (critère par le reste de Taylor).** Soit $f$ de classe $\mathcal{C}^\infty$ sur $]{-}r, r[$. Alors $f$ est développable en série entière sur $]{-}r, r[$ si et seulement si, pour tout $x \in \, ]{-}r, r[$,
>
> $$
> f(x) - \sum_{k=0}^{n} \frac{f^{(k)}(0)}{k!} x^k \xrightarrow[n \to +\infty]{} 0.
> $$

## Développements usuels

Pour tout $z \in \C$ :

$$
e^z = \sum_{n=0}^{+\infty} \frac{z^n}{n!}.
$$

Pour tout $z \in \C$ tel que $|z| < 1$ :

$$
\frac{1}{1-z} = \sum_{n=0}^{+\infty} z^n.
$$

Pour tout $x \in \R$ :

$$
\cos x = \sum_{n=0}^{+\infty} \frac{(-1)^n x^{2n}}{(2n)!}, \qquad \sin x = \sum_{n=0}^{+\infty} \frac{(-1)^n x^{2n+1}}{(2n+1)!},
$$

$$
\operatorname{ch} x = \sum_{n=0}^{+\infty} \frac{x^{2n}}{(2n)!}, \qquad \operatorname{sh} x = \sum_{n=0}^{+\infty} \frac{x^{2n+1}}{(2n+1)!}.
$$

Pour tout $x \in \, ]{-}1, 1[$ :

$$
\ln(1+x) = \sum_{n=1}^{+\infty} \frac{(-1)^{n-1}}{n} x^n, \qquad \arctan x = \sum_{n=0}^{+\infty} \frac{(-1)^n}{2n+1} x^{2n+1}.
$$

Pour tout $\alpha \in \R$ et tout $x \in \, ]{-}1, 1[$ :

$$
(1+x)^\alpha = 1 + \sum_{n=1}^{+\infty} \frac{\alpha (\alpha - 1) \cdots (\alpha - n + 1)}{n!} x^n.
$$

Les rayons de convergence sont $+\infty$ pour les quatre premières lignes, et $1$ pour $\ln(1+x)$, $\arctan x$ et $\frac{1}{1-z}$. Pour $(1+x)^\alpha$, le rayon vaut $1$ si $\alpha \notin \N$, et $+\infty$ si $\alpha \in \N$ (la somme est alors un polynôme).

## Méthodes

- **Calculer une somme.** On se ramène à un développement usuel par dérivation ou intégration terme à terme (sur l'intervalle ouvert de convergence), décomposition en éléments simples, ou produit de Cauchy.
- **Montrer qu'une fonction est développable en série entière.** Soit on l'obtient par opérations sur les développements usuels, soit on cherche une équation différentielle linéaire qu'elle vérifie, on cherche les solutions développables en série entière (relation de récurrence sur les coefficients, calcul du rayon), puis on conclut par l'unicité de la solution d'un problème de Cauchy, sur l'intervalle où le théorème de Cauchy linéaire s'applique.
- **Les égalités ne valent a priori que sur l'intervalle ouvert de convergence.** Une égalité au bord ($x = \pm R$) demande un argument supplémentaire (par exemple la convergence uniforme sur $[0, R]$).

## Pièges fréquents

- Conclure sur la convergence en un point $z$ tel que $|z| = R$ sans l'étudier.
- Appliquer la règle de d'Alembert aux coefficients alors qu'une infinité d'entre eux sont nuls, ou alors que le rapport $\frac{|a_{n+1}|}{|a_n|}$ n'a pas de limite : la règle ne dit alors rien.
- Confondre « la série de Taylor de $f$ converge » et « $f$ est égale à la somme de sa série de Taylor ».
