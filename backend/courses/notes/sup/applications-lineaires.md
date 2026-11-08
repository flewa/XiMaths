---
titre: Espaces vectoriels et applications linéaires
programmes: MPSI, PCSI
ordre: 9
notion: applications-lineaires
---

## Cadre et notations

Dans toute la fiche, $\K = \R$ ou $\C$, et $E$, $F$ sont des $\K$-espaces vectoriels. On note $\mathcal{L}(E, F)$ l'ensemble des applications linéaires de $E$ dans $F$, et $\mathcal{L}(E) = \mathcal{L}(E, E)$.

## Sous-espaces vectoriels

> **Définition.** Une partie $G$ de $E$ est un **sous-espace vectoriel** de $E$ si $0_E \in G$ et si $\lambda x + \mu y \in G$ pour tous $x, y \in G$ et $\lambda, \mu \in \K$.

L'intersection de deux sous-espaces est un sous-espace ; leur réunion, en général, non.

> **Définition.** Soient $G$ et $H$ deux sous-espaces de $E$. Leur **somme** est $G + H = \{ x + y : x \in G, \ y \in H \}$. Elle est **directe**, notée $G \oplus H$, si tout vecteur de $G + H$ s'écrit de façon unique $x + y$ avec $x \in G$ et $y \in H$ ; c'est le cas si et seulement si $G \cap H = \{0_E\}$. Les sous-espaces $G$ et $H$ sont **supplémentaires** dans $E$ si $E = G \oplus H$.

## Familles de vecteurs

Une famille $(x_1, \dots, x_p)$ de vecteurs de $E$ est **libre** si $\sum_{i=1}^{p} \lambda_i x_i = 0$ entraîne $\lambda_1 = \dots = \lambda_p = 0$ ; **génératrice** si tout vecteur de $E$ est combinaison linéaire des $x_i$ ; c'est une **base** si elle est libre et génératrice, c'est-à-dire si tout vecteur de $E$ s'écrit de façon unique comme combinaison linéaire des $x_i$.

## Dimension finie

Un espace $E$ est de **dimension finie** s'il admet une famille génératrice finie.

> **Théorème (base incomplète).** Soit $E$ de dimension finie. Toute famille libre de $E$ peut être complétée en une base de $E$ par des vecteurs pris dans une famille génératrice donnée. En particulier, $E$ admet une base, et toutes ses bases ont le même nombre d'éléments : la **dimension** de $E$, notée $\dim E$.

> **Proposition.** Soit $E$ de dimension $n$.
>
> 1. Une famille libre de $E$ a au plus $n$ éléments ; une famille génératrice en a au moins $n$.
> 2. Une famille de $n$ vecteurs est une base si et seulement si elle est libre, si et seulement si elle est génératrice.
> 3. Tout sous-espace $G$ de $E$ est de dimension finie, $\dim G \leq n$, et $\dim G = n$ si et seulement si $G = E$.

> **Formule de Grassmann.** Si $G$ et $H$ sont deux sous-espaces de dimension finie de $E$ :
>
> $$
> \dim(G + H) = \dim G + \dim H - \dim(G \cap H).
> $$
>
> Si $E$ est de dimension finie : $E = G \oplus H$ si et seulement si $G \cap H = \{0_E\}$ et $\dim G + \dim H = \dim E$.

## Applications linéaires

> **Définition.** Une application $u : E \to F$ est **linéaire** si $u(\lambda x + \mu y) = \lambda u(x) + \mu u(y)$ pour tous $x, y \in E$ et $\lambda, \mu \in \K$. Son **noyau** est $\operatorname{Ker} u = \{ x \in E : u(x) = 0_F \}$ et son **image** est $\operatorname{Im} u = u(E)$ ; ce sont des sous-espaces de $E$ et de $F$.

> **Proposition.** Soit $u \in \mathcal{L}(E, F)$.
>
> 1. $u$ est injective si et seulement si $\operatorname{Ker} u = \{0_E\}$.
> 2. Si $(e_1, \dots, e_n)$ engendre $E$, alors $\big( u(e_1), \dots, u(e_n) \big)$ engendre $\operatorname{Im} u$.
> 3. Si $(e_1, \dots, e_n)$ est une base de $E$, une application linéaire de $E$ dans $F$ est entièrement déterminée par les images des $e_i$, qui peuvent être choisies arbitrairement dans $F$.

Lorsque $\operatorname{Im} u$ est de dimension finie, le **rang** de $u$ est $\operatorname{rg} u = \dim \operatorname{Im} u$.

> **Théorème du rang.** Si $E$ est de dimension finie et $u \in \mathcal{L}(E, F)$, alors $\operatorname{Im} u$ est de dimension finie et
>
> $$
> \dim E = \dim \operatorname{Ker} u + \operatorname{rg} u.
> $$

> **Corollaire.** Si $E$ et $F$ sont de même dimension finie et $u \in \mathcal{L}(E, F)$, alors $u$ est injective si et seulement si $u$ est surjective, si et seulement si $u$ est bijective. C'est le cas en particulier pour $u \in \mathcal{L}(E)$ avec $E$ de dimension finie.

En dimension infinie, c'est faux : sur $\K[X]$, la dérivation $P \mapsto P'$ est surjective et n'est pas injective.

## Projecteurs et symétries

> **Proposition.** Soit $p \in \mathcal{L}(E)$ tel que $p \circ p = p$ (un **projecteur**). Alors $E = \operatorname{Ker} p \oplus \operatorname{Im} p$, et $p$ est la projection sur $\operatorname{Im} p$ parallèlement à $\operatorname{Ker} p$ ; de plus $\operatorname{Im} p = \operatorname{Ker}(p - \mathrm{id}_E)$.
>
> Soit $s \in \mathcal{L}(E)$ tel que $s \circ s = \mathrm{id}_E$ (une **symétrie**). Alors $E = \operatorname{Ker}(s - \mathrm{id}_E) \oplus \operatorname{Ker}(s + \mathrm{id}_E)$, et $s$ est la symétrie par rapport au premier parallèlement au second.

## Formes linéaires et hyperplans

Une **forme linéaire** sur $E$ est un élément de $\mathcal{L}(E, \K)$. Un **hyperplan** de $E$ est le noyau d'une forme linéaire non nulle. Si $E$ est de dimension finie $n \geq 1$, les hyperplans sont exactement les sous-espaces de dimension $n - 1$.

## Pièges fréquents

- Confondre « supplémentaire » et « complémentaire » : un supplémentaire est un sous-espace, et il n'est pas unique.
- Déduire $E = \operatorname{Ker} u \oplus \operatorname{Im} u$ du théorème du rang : c'est faux en général (pour $u : (x, y) \mapsto (y, 0)$ sur $\K^2$, $\operatorname{Ker} u = \operatorname{Im} u$).
- Utiliser « injective $\iff$ surjective » hors de la dimension finie, ou entre deux espaces de dimensions différentes.
