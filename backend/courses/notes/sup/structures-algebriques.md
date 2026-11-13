---
titre: Structures algébriques usuelles
programmes: MPSI, MP2I
ordre: 10
notion: groupes-anneaux
---

## Cadre et notations

Une **loi de composition interne** sur un ensemble $E$ est une application $E \times E \to E$, notée $(x, y) \mapsto x * y$. Elle est **associative** si $(x * y) * z = x * (y * z)$, **commutative** si $x * y = y * x$. Un élément $e$ est **neutre** si $e * x = x * e = x$ pour tout $x$ ; il est alors unique. Un élément $x$ est **inversible** s'il existe $y$ tel que $x * y = y * x = e$ ; pour une loi associative, cet inverse est unique, et si $x$ et $y$ sont inversibles, $x * y$ l'est, d'inverse $y^{-1} * x^{-1}$. Une partie $A$ est **stable** si $x * y \in A$ pour tous $x, y \in A$.

## Groupes

> **Définition.** Un **groupe** est un ensemble $G$ muni d'une loi associative, ayant un élément neutre, dans lequel tout élément est inversible. Il est **abélien** si sa loi est commutative.

En notation multiplicative, on écrit $x^n$ ($n \in \Z$) ; en notation additive, $nx$. Exemples : $(\Z, +)$, $(\Q, +)$, $(\R, +)$, $(\C, +)$ ; $(\Q^*, \times)$, $(\R^*, \times)$, $(\R_+^*, \times)$, $(\C^*, \times)$, $(\mathbb{U}, \times)$, $(\mathbb{U}_n, \times)$ ; le groupe $\mathfrak{S}_X$ des bijections d'un ensemble $X$, muni de la composition, qui n'est pas abélien dès que $X$ a au moins trois éléments. Le produit $G_1 \times G_2$ de deux groupes, muni de la loi composante par composante, est un groupe.

> **Proposition (caractérisation des sous-groupes).** Une partie $H$ d'un groupe $G$ est un **sous-groupe** (un groupe pour la loi induite) si et seulement si $H$ contient le neutre et si $x y^{-1} \in H$ pour tous $x, y \in H$.

Exemple : les sous-groupes de $(\Z, +)$ sont les $n\Z$, $n \in \N$.

> **Définition.** Soient $G$ et $G'$ deux groupes. Une application $f : G \to G'$ est un **morphisme** si $f(xy) = f(x) f(y)$ pour tous $x, y \in G$. On a alors $f(e) = e'$ et $f(x^{-1}) = f(x)^{-1}$. Un **isomorphisme** est un morphisme bijectif ; sa réciproque est un morphisme.

> **Proposition.** Soit $f : G \to G'$ un morphisme de groupes.
>
> 1. L'image directe d'un sous-groupe de $G$ et l'image réciproque d'un sous-groupe de $G'$ sont des sous-groupes.
> 2. Le **noyau** $\operatorname{Ker} f = \{ x \in G : f(x) = e' \}$ et l'**image** $\operatorname{Im} f = f(G)$ sont des sous-groupes de $G$ et de $G'$.
> 3. $f$ est injectif si et seulement si $\operatorname{Ker} f = \{ e \}$.

Exemples : $\exp : (\R, +) \to (\R_+^*, \times)$ est un isomorphisme ; $\theta \mapsto e^{i\theta}$ est un morphisme de $(\R, +)$ sur $(\mathbb{U}, \times)$, de noyau $2\pi\Z$.

## Anneaux et corps

> **Définition.** Un **anneau** est un ensemble $A$ muni de deux lois $+$ et $\times$ telles que $(A, +)$ soit un groupe abélien, $\times$ soit associative, distributive par rapport à $+$, et admette un élément neutre $1_A$. L'anneau est **commutatif** si $\times$ l'est.

Exemples : $\Z$, $\Q$, $\R$, $\C$, l'anneau $\K[X]$ des polynômes, l'anneau $\mathcal{M}_n(\K)$ des matrices carrées, qui n'est pas commutatif si $n \geq 2$. Dans un anneau, $0_A \times x = 0_A$ pour tout $x$.

> **Proposition.** Soient $A$ un anneau, $a, b \in A$ tels que $ab = ba$, et $n \in \N$. Alors
>
> $$
> (a + b)^n = \sum_{k=0}^{n} \binom{n}{k} a^k b^{n-k} \qquad \text{et} \qquad a^n - b^n = (a - b) \sum_{k=0}^{n-1} a^k b^{n-1-k}.
> $$

Les éléments inversibles pour $\times$ forment un groupe, le **groupe des inversibles** de $A$ : par exemple $\{ -1, 1 \}$ pour $\Z$, et $GL_n(\K)$ pour $\mathcal{M}_n(\K)$.

Un anneau commutatif $A$ est **intègre** s'il n'est pas réduit à $\{0\}$ et si $ab = 0 \implies a = 0$ ou $b = 0$. Un **corps** est un anneau commutatif, non réduit à $\{0\}$, dont tout élément non nul est inversible : $\Q$, $\R$, $\C$. Un corps est intègre.

Une partie $B$ d'un anneau $A$ est un **sous-anneau** si elle contient $1_A$ et si $x - y \in B$ et $xy \in B$ pour tous $x, y \in B$. Un **morphisme d'anneaux** $f : A \to A'$ vérifie $f(x + y) = f(x) + f(y)$, $f(xy) = f(x) f(y)$ et $f(1_A) = 1_{A'}$ ; un isomorphisme d'anneaux est un morphisme bijectif. Exemple : la conjugaison est un isomorphisme de l'anneau $\C$ sur lui-même.

## Pièges fréquents

- Oublier de vérifier qu'une partie contient le neutre avant de parler de sous-groupe.
- Développer $(a + b)^2$ en $a^2 + 2ab + b^2$ dans un anneau non commutatif sans savoir que $ab = ba$.
- Écrire « $ab = 0$ donc $a = 0$ ou $b = 0$ » dans $\mathcal{M}_n(\K)$, qui a des diviseurs de zéro.
- Croire qu'un morphisme de groupes $f$ vérifie $f(x + y) = f(x) + f(y)$ quand les lois sont multiplicatives : la relation suit les lois des deux groupes.
