---
titre: Raisonnement et vocabulaire ensembliste
programmes: MPSI, MP2I
ordre: 1
notion: ensembles-applications
---

## Cadre et notations

Une **proposition** est un énoncé vrai ou faux. On note $\forall$ (« pour tout ») et $\exists$ (« il existe ») les quantificateurs ; ils servent à écrire des énoncés précis, pas à abréger une phrase. Dans toute la fiche, $E$, $F$, $G$ sont des ensembles.

## Logique

**Négation.** La négation de « $\forall x \in E, \ P(x)$ » est « $\exists x \in E, \ \text{non } P(x)$ », et celle de « $\exists x \in E, \ P(x)$ » est « $\forall x \in E, \ \text{non } P(x)$ ». La négation de « $P$ et $Q$ » est « non $P$ ou non $Q$ » ; celle de « $P$ ou $Q$ » est « non $P$ et non $Q$ ».

Exemple : $f$ ne tend pas vers $\ell$ en $a$ s'écrit

$$
\exists \varepsilon > 0, \ \forall \delta > 0, \ \exists x \in I, \ |x - a| \leq \delta \ \text{et} \ |f(x) - \ell| > \varepsilon.
$$

**Implication.** « $P \implies Q$ » est fausse seulement quand $P$ est vraie et $Q$ fausse. Sa **contraposée** « non $Q \implies$ non $P$ » lui est équivalente ; sa **réciproque** « $Q \implies P$ » ne l'est pas. La négation de « $P \implies Q$ » est « $P$ et non $Q$ ». Si $P \implies Q$, on dit que $Q$ est une **condition nécessaire** de $P$ et que $P$ est une **condition suffisante** de $Q$ ; « $P \iff Q$ » signifie que $P \implies Q$ et $Q \implies P$.

## Modes de raisonnement

- **Disjonction des cas :** on démontre le résultat dans chacun des cas d'une liste qui les couvre tous (par exemple $n$ pair, $n$ impair).
- **Contraposition :** pour montrer $P \implies Q$, on montre non $Q \implies$ non $P$.
- **Absurde :** on suppose la négation du résultat et on aboutit à une contradiction.
- **Analyse-synthèse :** pour déterminer les objets qui vérifient une propriété, l'**analyse** suppose qu'un tel objet existe et en déduit sa forme (conditions nécessaires) ; la **synthèse** vérifie que les objets de cette forme conviennent (conditions suffisantes). Exemple : toute fonction $f : \R \to \R$ s'écrit de façon unique comme somme d'une fonction paire et d'une fonction impaire, $f(x) = \frac{f(x) + f(-x)}{2} + \frac{f(x) - f(-x)}{2}$.

> **Théorème (récurrence).** Soient $n_0 \in \N$ et $P(n)$ une proposition définie pour $n \geq n_0$.
>
> 1. **Simple :** si $P(n_0)$ est vraie et si $P(n) \implies P(n + 1)$ pour tout $n \geq n_0$, alors $P(n)$ est vraie pour tout $n \geq n_0$.
> 2. **Double :** si $P(n_0)$ et $P(n_0 + 1)$ sont vraies et si $\big( P(n) \text{ et } P(n + 1) \big) \implies P(n + 2)$ pour tout $n \geq n_0$, alors $P(n)$ est vraie pour tout $n \geq n_0$.
> 3. **Forte :** si $P(n_0)$ est vraie et si, pour tout $n \geq n_0$, $\big( P(n_0), \dots, P(n) \big) \implies P(n + 1)$, alors $P(n)$ est vraie pour tout $n \geq n_0$.

Ces principes reposent sur le fait que toute partie non vide de $\N$ possède un plus petit élément.

## Ensembles

On note $A \subset E$ si tout élément de $A$ appartient à $E$ ; $A = B$ si et seulement si $A \subset B$ et $B \subset A$. Pour $A, B \subset E$ : $A \cup B$, $A \cap B$, $A \setminus B = \{ x \in A : x \notin B \}$, et le **complémentaire** $\overline{A} = E \setminus A$.

> **Proposition (lois de De Morgan).** Pour $A, B \subset E$ : $\overline{A \cup B} = \overline{A} \cap \overline{B}$ et $\overline{A \cap B} = \overline{A} \cup \overline{B}$.

Le **produit cartésien** $E_1 \times \dots \times E_n$ est l'ensemble des $n$-uplets $(x_1, \dots, x_n)$ avec $x_i \in E_i$. L'ensemble des parties de $E$ est noté $\mathcal{P}(E)$. Une **partition** de $E$ est une famille de parties non vides, deux à deux disjointes, dont la réunion est $E$.

## Applications

Une **application** $f : E \to F$ associe à chaque élément de $E$ un unique élément de $F$. On note $\mathcal{F}(E, F)$ ou $F^E$ l'ensemble de ces applications. La **fonction indicatrice** de $A \subset E$ est $\mathbf{1}_A : E \to \{0, 1\}$, qui vaut $1$ sur $A$ et $0$ ailleurs.

Pour $A \subset E$ et $B \subset F$, l'**image directe** est $f(A) = \{ f(x) : x \in A \}$ et l'**image réciproque** est $f^{-1}(B) = \{ x \in E : f(x) \in B \}$. L'image réciproque existe toujours, même si $f$ n'est pas bijective.

> **Définition.** L'application $f : E \to F$ est
>
> 1. **injective** si, pour tous $x, x' \in E$, $f(x) = f(x') \implies x = x'$ ;
> 2. **surjective** si tout $y \in F$ a au moins un antécédent : $f(E) = F$ ;
> 3. **bijective** si elle est injective et surjective : tout $y \in F$ a un unique antécédent, noté $f^{-1}(y)$.

> **Proposition.** Soient $f : E \to F$ et $g : F \to G$.
>
> 1. Si $f$ et $g$ sont injectives (resp. surjectives, bijectives), $g \circ f$ l'est aussi.
> 2. Si $f$ et $g$ sont bijectives, $(g \circ f)^{-1} = f^{-1} \circ g^{-1}$.
> 3. $f$ est bijective si et seulement s'il existe $h : F \to E$ telle que $h \circ f = \mathrm{id}_E$ et $f \circ h = \mathrm{id}_F$ ; alors $h = f^{-1}$.

La **restriction** de $f$ à $A \subset E$ est $f_{|A} : A \to F$, $x \mapsto f(x)$.

## Relations

Une relation binaire $\mathcal{R}$ sur $E$ est une **relation d'équivalence** si elle est réflexive ($x \mathcal{R} x$), symétrique ($x \mathcal{R} y \implies y \mathcal{R} x$) et transitive ($x \mathcal{R} y$ et $y \mathcal{R} z \implies x \mathcal{R} z$). Les **classes d'équivalence** $\{ y \in E : x \mathcal{R} y \}$ forment une partition de $E$. Exemples : la congruence modulo $n$ sur $\Z$, la congruence modulo $2\pi$ sur $\R$, notées $a \equiv b \ [n]$ et $a \equiv b \ [2\pi]$.

C'est une **relation d'ordre** si elle est réflexive, antisymétrique ($x \mathcal{R} y$ et $y \mathcal{R} x \implies x = y$) et transitive. L'ordre est **total** si deux éléments sont toujours comparables, **partiel** sinon : $\leq$ sur $\R$ est total, l'inclusion sur $\mathcal{P}(E)$ et la divisibilité sur $\N$ sont partielles.

## Pièges fréquents

- Nier « $\forall \varepsilon > 0, \exists N$… » sans échanger chaque quantificateur : la négation commence par $\exists \varepsilon > 0$.
- Confondre la réciproque d'une implication et sa contraposée.
- Oublier la synthèse dans une analyse-synthèse : l'analyse ne donne que des conditions nécessaires.
- Croire que la notation $f^{-1}(B)$ suppose $f$ bijective : l'image réciproque est toujours définie.
- Initialiser une récurrence double avec un seul rang.
