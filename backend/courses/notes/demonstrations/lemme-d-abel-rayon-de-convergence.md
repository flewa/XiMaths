---
titre: Lemme d'Abel et rayon de convergence
programmes: MP, MPI, L2
statut: au-programme
ordre: 9
notion: series-entieres
---

## Énoncé

> **Lemme d'Abel.** Soient $(a_n)$ une suite complexe et $z_0 \in \C$ tels que la suite $(a_n z_0^n)$ soit bornée. Alors, pour tout $z \in \C$ tel que $|z| < |z_0|$, la série $\sum a_n z^n$ converge absolument.

> **Théorème (rayon de convergence).** Soit $R = \sup \{ r \geq 0 : (a_n r^n) \text{ est bornée} \} \in [0, +\infty]$. Alors :
>
> 1. si $|z| < R$, la série $\sum a_n z^n$ converge absolument ;
> 2. si $|z| > R$, elle diverge grossièrement ;
> 3. pour tout $r \in [0, R[$, elle converge normalement sur le disque fermé $\overline{D}(0, r)$.

## Idée

Si $(a_n z_0^n)$ est bornée par $M$, alors $|a_n z^n| \leq M q^n$ avec $q = \frac{|z|}{|z_0|} < 1$ : on compare à une série géométrique. Tout le reste découle de ce lemme et de la définition de $R$ comme borne supérieure.

## Démonstration

**Lemme d'Abel.** Si $z_0 = 0$, il n'y a aucun $z$ tel que $|z| < |z_0|$. Sinon, soit $M$ tel que $|a_n z_0^n| \leq M$ pour tout $n$, et $|z| < |z_0|$. Alors

$$
\lvert a_n z^n \rvert = |a_n z_0^n| \left| \frac{z}{z_0} \right|^n \leq M q^n, \qquad q = \frac{|z|}{|z_0|} \in [0, 1[.
$$

La série géométrique $\sum M q^n$ converge, donc $\sum |a_n z^n|$ converge par comparaison de séries à termes positifs.

L'ensemble $\{ r \geq 0 : (a_n r^n) \text{ bornée} \}$ contient $0$, donc $R$ est bien défini dans $[0, +\infty]$. C'est de plus un intervalle : si $(a_n r^n)$ est bornée et $0 \leq r' \leq r$, alors $|a_n r'^n| \leq |a_n r^n|$.

**Point 1.** Soit $|z| < R$. Par définition de la borne supérieure, il existe $r$ tel que $|z| < r$ et que $(a_n r^n)$ soit bornée. Le lemme d'Abel, appliqué avec $z_0 = r$, donne la convergence absolue de $\sum a_n z^n$.

**Point 2.** Soit $|z| > R$. Si la suite $(a_n z^n)$ tendait vers $0$, elle serait bornée, donc $(a_n |z|^n)$ aussi, et $|z|$ appartiendrait à l'ensemble dont $R$ est la borne supérieure : $|z| \leq R$, contradiction. Le terme général ne tend pas vers $0$ : la série diverge grossièrement.

**Point 3.** Soit $r \in [0, R[$. Choisissons $\rho$ tel que $r < \rho < R$ et que $(a_n \rho^n)$ soit bornée par $M$. Pour $|z| \leq r$ :

$$
\lvert a_n z^n \rvert \leq |a_n| r^n = |a_n \rho^n| \left( \frac{r}{\rho} \right)^n \leq M \left( \frac{r}{\rho} \right)^n.
$$

Le majorant ne dépend pas de $z$ et est le terme général d'une série géométrique convergente : la convergence est normale sur $\overline{D}(0, r)$.

## Remarques

- **Sur le cercle $|z| = R$, tout peut arriver.** $\sum z^n$ diverge en tout point du cercle unité ; $\sum \frac{z^n}{n^2}$ converge absolument en tout point ; $\sum \frac{z^n}{n}$ converge en tout point sauf $z = 1$.
- **La convergence n'est pas normale sur le disque ouvert en général** : pour $\sum z^n$, $\sup_{|z| < 1} |z^n| = 1$. C'est pourquoi on travaille sur les disques fermés $\overline{D}(0, r)$, $r < R$ ; la continuité de la somme sur le disque ouvert en découle, car tout point du disque ouvert est intérieur à l'un d'eux.
- **Calcul pratique :** si $\left| \frac{a_{n+1}}{a_n} \right| \to \ell \in [0, +\infty]$, alors $R = \frac{1}{\ell}$ (règle de d'Alembert), avec les conventions $\frac{1}{0} = +\infty$ et $\frac{1}{+\infty} = 0$.
