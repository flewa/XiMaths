"""Troisième lot : les chapitres restés minces (topologie, arithmétique, géométrie) et des
énoncés plus difficiles (4 et 5), dont le catalogue manquait.

Des résultats classiques, découpés en questions qui guident la preuve. Pas de corrigé : les
solutions viennent des membres. Les réponses finales données ont été recalculées à part.
"""

PREMIERE_ANNEE = ["L1", "MPSI", "MP2I", "PCSI", "PTSI"]

EXERCISES = [
    # ------------------------------------------------------------------ Topologie
    {
        "title": "L'adhérence d'un sous-espace vectoriel ; un hyperplan est fermé ou dense",
        "statement": (
            r"Soit $E$ un espace vectoriel normé et $F$ un sous-espace vectoriel de $E$."
            "\n\n"
            r"1. Montrer que l'adhérence $\overline{F}$ est un sous-espace vectoriel de $E$."
            "\n"
            r"2. On suppose que $F$ est un hyperplan de $E$. Montrer que $F$ est fermé, ou dense dans $E$."
            "\n"
            r"3. Donner un exemple d'hyperplan dense dans un espace vectoriel normé."
        ),
        "hints": [
            r"Pour 1, écrire deux éléments de $\overline{F}$ comme limites de suites d'éléments de $F$.",
            r"Pour 2, $\overline{F}$ est un sous-espace vectoriel qui contient l'hyperplan $F$ : il n'y a que deux possibilités.",
            r"Pour 3, dans $\R[X]$ muni de la norme $\|P\| = \sup_{[0, 1]} |P|$, regarder le noyau de $P \mapsto P(2)$.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L3", "MP"],
        "topics": ["topologie", "espaces-vectoriels-normes"],
    },
    {
        "title": "Une forme linéaire est continue si et seulement si son noyau est fermé",
        "statement": (
            r"Soit $E$ un espace vectoriel normé et $\varphi$ une forme linéaire non nulle sur $E$. "
            r"Montrer que $\varphi$ est continue si et seulement si son noyau $\ker \varphi$ est fermé."
        ),
        "hints": [
            r"Sens direct : $\ker \varphi$ est l'image réciproque du fermé $\{0\}$ par $\varphi$.",
            r"Réciproque, par contraposée : si $\varphi$ n'est pas continue, il existe une suite $(x_n)$ de vecteurs de norme $1$ telle que $|\varphi(x_n)| \to +\infty$.",
            r"Fixer $a$ tel que $\varphi(a) = 1$ : la suite $a - \dfrac{x_n}{\varphi(x_n)}$ est dans le noyau et tend vers $a$.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L3", "MP"],
        "topics": ["topologie", "espaces-vectoriels-normes"],
    },
    {
        "title": "Théorème de Heine : continue sur un compact, donc uniformément continue",
        "statement": (
            r"Soit $(K, d)$ un espace métrique compact, $(Y, \delta)$ un espace métrique et $f : K \to Y$ une application continue."
            "\n\n"
            r"1. Montrer que $f$ est uniformément continue."
            "\n"
            r"2. Donner un exemple de fonction continue et bornée sur $\R$ qui n'est pas uniformément continue."
        ),
        "hints": [
            r"Raisonner par l'absurde : il existe $\varepsilon > 0$ et deux suites $(x_n)$, $(y_n)$ de $K$ telles que $d(x_n, y_n) \to 0$ et $\delta(f(x_n), f(y_n)) \geq \varepsilon$.",
            r"Extraire de $(x_n)$ une sous-suite convergente : la sous-suite correspondante de $(y_n)$ a la même limite.",
            r"Pour 2, penser à $x \mapsto \sin(x^2)$.",
        ],
        "difficulty": 3,
        "primary_level": "L3",
        "levels": ["L2", "L3", "MP"],
        "topics": ["topologie", "espaces-metriques"],
    },
    {
        "title": r"Point fixe sur un compact : $d(f(x), f(y)) < d(x, y)$ suffit",
        "statement": (
            r"Soit $(K, d)$ un espace métrique compact non vide et $f : K \to K$ une application telle que, "
            r"pour tous $x \neq y$ dans $K$, $d(f(x), f(y)) < d(x, y)$."
            "\n\n"
            r"1. Montrer que $f$ admet un unique point fixe $a$."
            "\n"
            r"2. Soit $x_0 \in K$ et, pour tout $n$, $x_{n+1} = f(x_n)$. Montrer que la suite $(x_n)$ converge vers $a$."
            "\n"
            r"3. Montrer par un exemple que la question 1 tombe en défaut si l'on suppose seulement $K$ complet."
        ),
        "hints": [
            r"Pour 1, la fonction $x \mapsto d(x, f(x))$ est continue sur le compact $K$ : elle atteint son minimum.",
            r"Pour 2, la suite $d(x_n, a)$ décroît, donc converge vers un réel $\ell \geq 0$. Si $\ell > 0$, considérer une valeur d'adhérence $b$ de $(x_n)$ et comparer $d(b, a)$ et $d(f(b), a)$.",
            r"Pour 3, essayer $f(x) = \sqrt{1 + x^2}$ sur $\R$.",
        ],
        "difficulty": 4,
        "primary_level": "L3",
        "levels": ["L3", "M1", "MP"],
        "topics": ["topologie", "espaces-metriques"],
    },
    {
        "title": r"$\R$ et $\R^2$ ne sont pas homéomorphes",
        "statement": (
            r"1. Montrer que $\R^2$ privé d'un point est connexe par arcs."
            "\n"
            r"2. En déduire qu'il n'existe pas d'homéomorphisme de $\R$ sur $\R^2$."
            "\n"
            r"3. Le segment $[0, 1]$ et le cercle unité de $\R^2$ sont-ils homéomorphes ?"
        ),
        "hints": [
            "Pour 1, relier deux points par un segment, ou par deux segments si le premier passe par le point retiré.",
            r"Pour 2, un homéomorphisme $h : \R \to \R^2$ induirait un homéomorphisme de $\R \setminus \{0\}$ sur $\R^2 \setminus \{h(0)\}$.",
            "Pour 3, retirer du segment un point bien choisi.",
        ],
        "difficulty": 3,
        "primary_level": "L3",
        "levels": ["L3", "MP"],
        "topics": ["topologie", "espaces-metriques"],
    },
    {
        "title": r"$\mathrm{GL}_n(\R)$ est un ouvert dense de $\mathcal{M}_n(\R)$",
        "statement": (
            r"1. Montrer que $\mathrm{GL}_n(\R)$ est un ouvert de $\mathcal{M}_n(\R)$."
            "\n"
            r"2. Montrer que $\mathrm{GL}_n(\R)$ est dense dans $\mathcal{M}_n(\R)$."
            "\n"
            r"3. Application : montrer que, pour toutes matrices $A$ et $B$ de $\mathcal{M}_n(\R)$, "
            r"les matrices $AB$ et $BA$ ont le même polynôme caractéristique."
        ),
        "hints": [
            "Pour 1, le déterminant est une fonction continue des coefficients.",
            r"Pour 2, $A$ étant fixée, la matrice $A - \lambda I_n$ n'est non inversible que pour un nombre fini de réels $\lambda$.",
            r"Pour 3, traiter d'abord le cas où $A$ est inversible : $BA = A^{-1}(AB)A$. Conclure par densité, les coefficients du polynôme caractéristique étant des fonctions continues de la matrice.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L3", "MP"],
        "topics": ["topologie", "espaces-vectoriels-normes", "algebre-lineaire", "reduction"],
    },
    {
        "title": "Théorème de Riesz : la boule unité n'est compacte qu'en dimension finie",
        "statement": (
            r"Soit $E$ un espace vectoriel normé."
            "\n\n"
            r"1. (Lemme de Riesz.) Soit $F$ un sous-espace vectoriel fermé de $E$, distinct de $E$. "
            r"Montrer qu'il existe $u \in E$ tel que $\|u\| = 1$ et $d(u, F) \geq \dfrac{1}{2}$."
            "\n"
            r"2. On suppose $E$ de dimension infinie. Construire une suite $(u_n)$ de vecteurs de norme $1$ "
            r"telle que $\|u_n - u_m\| \geq \dfrac{1}{2}$ pour tous $n \neq m$."
            "\n"
            r"3. En déduire que la boule unité fermée de $E$ est compacte si et seulement si $E$ est de dimension finie."
        ),
        "hints": [
            r"Pour 1, prendre $x \notin F$, puis $y \in F$ tel que $\|x - y\| \leq 2\, d(x, F)$, et normaliser $x - y$.",
            r"Pour 2, un sous-espace de dimension finie est fermé : appliquer le lemme à $F_n = \mathrm{Vect}(u_1, \dots, u_n)$.",
            r"Pour 3, une suite dont les termes sont deux à deux distants d'au moins $\dfrac{1}{2}$ n'a aucune sous-suite convergente.",
        ],
        "difficulty": 4,
        "primary_level": "L3",
        "levels": ["L3", "M1", "MP"],
        "topics": ["topologie", "espaces-vectoriels-normes"],
    },
    {
        "title": "Théorème de Banach-Steinhaus par le théorème de Baire",
        "statement": (
            r"Soit $E$ un espace de Banach, $F$ un espace vectoriel normé et $(T_i)_{i \in I}$ une famille "
            r"d'applications linéaires continues de $E$ dans $F$. On suppose que, pour tout $x \in E$, "
            r"$\sup_{i \in I} \|T_i(x)\| < +\infty$."
            "\n\n"
            r"1. Pour $n \in \N$, on pose $A_n = \{x \in E : \forall i \in I,\ \|T_i(x)\| \leq n\}$. "
            r"Montrer que chaque $A_n$ est fermé, et que l'un d'eux est d'intérieur non vide."
            "\n"
            r"2. En déduire que $\sup_{i \in I} \|T_i\| < +\infty$."
            "\n"
            r"3. Application. Soit $(T_n)$ une suite d'applications linéaires continues de $E$ dans $F$ "
            r"qui converge simplement vers une application $T$. Montrer que $T$ est linéaire et continue."
        ),
        "hints": [
            r"Pour 1, $E$ est la réunion des $A_n$ : appliquer le théorème de Baire dans l'espace complet $E$.",
            r"Pour 2, si $A_n$ contient la boule fermée de centre $a$ et de rayon $r > 0$, écrire, pour $\|x\| \leq 1$, $x = \dfrac{1}{r}\big((a + r x) - a\big)$ : on obtient $\|T_i\| \leq \dfrac{2n}{r}$.",
            r"Pour 3, pour chaque $x$ la suite $(T_n(x))$ converge, donc est bornée : la question 2 donne $M$ tel que $\|T_n(x)\| \leq M \|x\|$ pour tout $n$, et l'on passe à la limite.",
        ],
        "difficulty": 5,
        "primary_level": "M1",
        "levels": ["L3", "M1", "M2"],
        "topics": ["topologie", "espaces-metriques", "analyse", "analyse-fonctionnelle"],
    },
    # ------------------------------------------------------------------ Arithmétique
    {
        "title": "Une infinité de nombres premiers congrus à 3 modulo 4",
        "statement": (
            r"1. Montrer que tout entier $n \geq 2$ congru à $3$ modulo $4$ admet un diviseur premier congru à $3$ modulo $4$."
            "\n"
            r"2. En déduire qu'il existe une infinité de nombres premiers congrus à $3$ modulo $4$."
        ),
        "hints": [
            r"Pour 1, $n$ est impair, et un produit d'entiers congrus à $1$ modulo $4$ est congru à $1$ modulo $4$.",
            r"Pour 2, s'il n'y en avait qu'un nombre fini $p_1, \dots, p_r$, considérer $N = 4\, p_1 \cdots p_r - 1$.",
        ],
        "difficulty": 2,
        "primary_level": "MPSI",
        "levels": ["L1", "L2", "MPSI", "MP2I"],
        "topics": ["arithmetique", "congruences"],
    },
    {
        "title": r"Théorème de Wilson : $(p-1)! \equiv -1$ modulo $p$",
        "statement": (
            r"Soit $p$ un nombre premier."
            "\n\n"
            r"1. Déterminer les entiers $x$ compris entre $1$ et $p - 1$ tels que $x^2 \equiv 1$ modulo $p$."
            "\n"
            r"2. En déduire que $(p-1)! \equiv -1$ modulo $p$."
            "\n"
            r"3. Réciproquement, soit $n \geq 2$ un entier tel que $(n-1)! \equiv -1$ modulo $n$. Montrer que $n$ est premier."
        ),
        "hints": [
            r"Pour 1, $p$ divise $(x - 1)(x + 1)$ et $p$ est premier.",
            r"Pour 2, tout entier de $1$ à $p - 1$ a un inverse modulo $p$ dans le même intervalle : dans le produit, regrouper chaque entier avec son inverse.",
            r"Pour 3, un diviseur $d$ de $n$ tel que $1 < d < n$ diviserait à la fois $(n-1)!$ et $(n-1)! + 1$.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP"],
        "topics": ["arithmetique", "congruences"],
    },
    {
        "title": "Théorème chinois : un système de trois congruences",
        "statement": (
            r"Déterminer le plus petit entier naturel $x$ tel que"
            "\n\n"
            r"$$x \equiv 2 \ [5], \qquad x \equiv 3 \ [7], \qquad x \equiv 4 \ [9].$$"
            "\n\n"
            "Décrire ensuite l'ensemble de toutes les solutions entières du système."
        ),
        "hints": [
            r"Résoudre d'abord les deux premières congruences : leurs solutions sont les entiers $x \equiv 17 \ [35]$.",
            r"Chercher ensuite $k$ tel que $17 + 35k \equiv 4 \ [9]$.",
            r"Les modules $5$, $7$ et $9$ sont premiers entre eux deux à deux : les solutions forment une classe modulo $315$.",
        ],
        "final_answer": "157",
        "difficulty": 2,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE + ["L2"],
        "topics": ["arithmetique", "congruences"],
    },
    {
        "title": r"$n^{13} - n$ est divisible par 2730",
        "statement": r"Montrer que, pour tout entier $n$, l'entier $n^{13} - n$ est divisible par $2730$.",
        "hints": [
            r"$2730 = 2 \times 3 \times 5 \times 7 \times 13$.",
            r"Pour $p$ premier et $n$ non divisible par $p$, le petit théorème de Fermat donne $n^{p-1} \equiv 1$ modulo $p$.",
            r"Pour chacun des cinq facteurs premiers $p$, l'entier $p - 1$ divise $12$.",
        ],
        "difficulty": 2,
        "primary_level": "MPSI",
        "levels": ["L1", "L2", "MPSI", "MP2I", "MP"],
        "topics": ["arithmetique", "congruences"],
    },
    {
        "title": "Les nombres de Fermat sont premiers entre eux deux à deux",
        "statement": (
            r"Pour $n \in \N$, on pose $F_n = 2^{2^n} + 1$."
            "\n\n"
            r"1. Montrer que, pour tout $n \geq 1$, $F_n - 2 = F_0 F_1 \cdots F_{n-1}$."
            "\n"
            r"2. En déduire que, pour $m \neq n$, les entiers $F_m$ et $F_n$ sont premiers entre eux."
            "\n"
            r"3. Retrouver ainsi qu'il existe une infinité de nombres premiers."
        ),
        "hints": [
            r"Pour 1, raisonner par récurrence à l'aide de $F_n - 2 = (F_{n-1} - 2)\, F_{n-1}$.",
            r"Pour 2, un diviseur commun de $F_m$ et $F_n$, avec $m < n$, divise $2$ ; or les $F_n$ sont impairs.",
            r"Pour 3, choisir un diviseur premier de chaque $F_n$.",
        ],
        "difficulty": 2,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["arithmetique", "divisibilite-pgcd"],
    },
    {
        "title": r"Nombre de zéros à la fin de $100!$ (formule de Legendre)",
        "statement": (
            r"1. Soit $p$ un nombre premier et $n \geq 1$ un entier. Montrer que l'exposant de $p$ dans la "
            r"décomposition de $n!$ en facteurs premiers est $\displaystyle\sum_{k \geq 1} \left\lfloor \dfrac{n}{p^k} \right\rfloor$."
            "\n"
            r"2. Par combien de zéros se termine l'écriture décimale de $100!$ ?"
        ),
        "hints": [
            r"Pour 1, compter, pour chaque $k \geq 1$, les entiers de $1$ à $n$ divisibles par $p^k$.",
            r"Pour 2, le nombre de zéros est le plus grand $m$ tel que $10^m$ divise $100!$ : c'est le plus petit des exposants de $2$ et de $5$.",
            r"L'exposant de $5$ est le plus petit des deux.",
        ],
        "final_answer": "24",
        "difficulty": 2,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["arithmetique", "divisibilite-pgcd"],
    },
    {
        "title": "Un nombre premier congru à 1 modulo 4 est somme de deux carrés",
        "statement": (
            r"Soit $p$ un nombre premier congru à $1$ modulo $4$. On admet le théorème de Wilson : $(p-1)! \equiv -1$ modulo $p$."
            "\n\n"
            r"1. Montrer que l'entier $a = \left(\dfrac{p-1}{2}\right)!$ vérifie $a^2 \equiv -1$ modulo $p$."
            "\n"
            r"2. On considère les entiers $x - a y$, où $x$ et $y$ parcourent les entiers de $0$ à $\lfloor \sqrt{p} \rfloor$. "
            r"Montrer que deux d'entre eux, associés à des couples $(x, y)$ distincts, sont congrus modulo $p$."
            "\n"
            r"3. En déduire qu'il existe des entiers $u$ et $v$ tels que $p = u^2 + v^2$."
            "\n"
            r"4. Un nombre premier congru à $3$ modulo $4$ peut-il être somme de deux carrés ?"
        ),
        "hints": [
            r"Pour 1, dans $(p-1)!$, remplacer chaque facteur $k > \dfrac{p-1}{2}$ par $-(p - k)$ modulo $p$ ; $\dfrac{p-1}{2}$ est pair.",
            r"Pour 2, il y a $(\lfloor \sqrt{p} \rfloor + 1)^2 > p$ couples.",
            r"Pour 3, avec $u = x - x'$ et $v = y - y'$ : $u \equiv a v$ modulo $p$, donc $p$ divise $u^2 + v^2$, et $0 < u^2 + v^2 < 2p$.",
            r"Pour 4, un carré est congru à $0$ ou à $1$ modulo $4$.",
        ],
        "difficulty": 4,
        "primary_level": "L3",
        "levels": ["L3", "MP"],
        "topics": ["arithmetique", "congruences"],
    },
    # ------------------------------------------------------------------ Géométrie
    {
        "title": "Distance entre deux droites non coplanaires de l'espace",
        "statement": (
            r"Dans l'espace muni d'un repère orthonormé, on considère la droite $D_1$ passant par $A(1, 0, 0)$ "
            r"et dirigée par $\vec{u} = (1, 1, 0)$, et la droite $D_2$ passant par $B(0, 1, 1)$ et dirigée par $\vec{v} = (0, 1, 1)$."
            "\n\n"
            r"1. Montrer que $D_1$ et $D_2$ ne sont pas coplanaires."
            "\n"
            r"2. Déterminer les points $H_1 \in D_1$ et $H_2 \in D_2$ tels que la droite $(H_1 H_2)$ soit perpendiculaire à $D_1$ et à $D_2$."
            "\n"
            r"3. En déduire la distance entre $D_1$ et $D_2$."
        ),
        "hints": [
            r"Pour 1, calculer le déterminant de $(\overrightarrow{AB}, \vec{u}, \vec{v})$.",
            r"Pour 2, écrire $H_1 = A + s\vec{u}$ et $H_2 = B + t\vec{v}$, puis traduire les deux orthogonalités : on obtient un système en $s$ et $t$.",
            r"Pour 3, la distance entre les deux droites est la longueur $H_1 H_2$ ; on peut la contrôler avec $\dfrac{|\det(\overrightarrow{AB}, \vec{u}, \vec{v})|}{\|\vec{u} \wedge \vec{v}\|}$.",
        ],
        "final_answer": "sqrt(3)/3",
        "difficulty": 2,
        "primary_level": "PTSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["geometrie", "geometrie-plan-espace"],
    },
    {
        "title": "Projeté orthogonal et symétrique d'un point par rapport à un plan",
        "statement": (
            r"Dans l'espace muni d'un repère orthonormé, soit $P$ le plan d'équation $x + 2y - 2z = 3$ "
            r"et $A$ le point de coordonnées $(2, 3, -2)$."
            "\n\n"
            r"1. Déterminer le projeté orthogonal $H$ de $A$ sur $P$."
            "\n"
            r"2. En déduire le symétrique $A'$ de $A$ par rapport à $P$."
            "\n"
            r"3. Calculer la distance de $A$ à $P$."
        ),
        "hints": [
            r"Le vecteur $\vec{n} = (1, 2, -2)$ est normal à $P$ : chercher $H$ sous la forme $A + t\vec{n}$.",
            r"$A'$ est le point tel que $H$ soit le milieu de $[AA']$.",
            r"La distance de $A$ à $P$ est la longueur $AH$.",
        ],
        "final_answer": "3",
        "difficulty": 1,
        "primary_level": "PTSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["geometrie", "geometrie-plan-espace"],
    },
    {
        "title": r"Similitude directe $z \mapsto (1+i)z + 2 - i$ : centre, rapport, angle",
        "statement": (
            r"Dans le plan complexe, on considère la transformation $f : z \mapsto (1 + i)z + 2 - i$."
            "\n\n"
            r"1. Montrer que $f$ admet un unique point fixe $\omega$, et le déterminer."
            "\n"
            r"2. Exprimer $f(z) - \omega$ en fonction de $z - \omega$. En déduire la nature de $f$, son rapport et son angle."
            "\n"
            r"3. Quelle est l'image par $f$ du cercle de centre $0$ et de rayon $1$ ?"
        ),
        "hints": [
            r"Pour 1, résoudre $f(z) = z$.",
            r"Pour 2, $1 + i = \sqrt{2}\, e^{i\pi/4}$.",
            r"Pour 3, une similitude de rapport $k$ transforme un cercle de rayon $r$ en un cercle de rayon $kr$, dont le centre est l'image du centre.",
        ],
        "difficulty": 2,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["geometrie", "geometrie-plan-espace", "algebre", "nombres-complexes"],
    },
    {
        "title": r"Longueur et aire de la cardioïde $\rho = 1 + \cos\theta$",
        "statement": (
            r"On considère la courbe d'équation polaire $\rho(\theta) = 1 + \cos\theta$, pour $\theta \in [-\pi, \pi]$."
            "\n\n"
            r"1. Étudier les symétries de la courbe et la tracer."
            "\n"
            r"2. Calculer l'aire du domaine qu'elle délimite."
            "\n"
            r"3. Calculer sa longueur."
        ),
        "hints": [
            r"$\rho$ est paire : la courbe est symétrique par rapport à l'axe des abscisses.",
            r"L'aire vaut $\dfrac{1}{2}\displaystyle\int_{-\pi}^{\pi} \rho(\theta)^2 \,\mathrm{d}\theta$.",
            r"L'élément de longueur est $\sqrt{\rho^2 + \rho'^2}\,\mathrm{d}\theta$, et $1 + \cos\theta = 2\cos^2\dfrac{\theta}{2}$.",
        ],
        "final_answer": "8",
        "difficulty": 2,
        "primary_level": "PT",
        "levels": ["L2", "PT", "PTSI"],
        "topics": ["geometrie", "courbes-coniques"],
    },
    {
        "title": "Cercle orthoptique d'une ellipse",
        "statement": (
            r"Soit $a > b > 0$ et $\mathcal{E}$ l'ellipse d'équation $\dfrac{x^2}{a^2} + \dfrac{y^2}{b^2} = 1$."
            "\n\n"
            r"1. Montrer que la droite d'équation $y = mx + p$ est tangente à $\mathcal{E}$ si et seulement si $p^2 = a^2 m^2 + b^2$."
            "\n"
            r"2. Soit $M(x_0, y_0)$ un point du plan tel que $x_0^2 \neq a^2$. Montrer que les pentes des tangentes à "
            r"$\mathcal{E}$ issues de $M$ sont les racines réelles de l'équation "
            r"$(x_0^2 - a^2)\, m^2 - 2 x_0 y_0\, m + y_0^2 - b^2 = 0$."
            "\n"
            r"3. En déduire que l'ensemble des points d'où l'on peut mener à $\mathcal{E}$ deux tangentes "
            r"perpendiculaires est le cercle d'équation $x^2 + y^2 = a^2 + b^2$."
        ),
        "hints": [
            r"Pour 1, reporter $y = mx + p$ dans l'équation de l'ellipse : la droite est tangente quand l'équation du second degré obtenue a une racine double.",
            r"Pour 3, deux droites de pentes $m_1$ et $m_2$ sont perpendiculaires si et seulement si $m_1 m_2 = -1$ : utiliser le produit des racines.",
            r"Traiter à part les points tels que $x_0^2 = a^2$, pour lesquels une des tangentes est verticale.",
        ],
        "difficulty": 4,
        "primary_level": "PT",
        "levels": ["L2", "PT"],
        "topics": ["geometrie", "courbes-coniques"],
    },
    {
        "title": "Hélice circulaire : longueur, courbure et torsion",
        "statement": (
            r"Soit $a > 0$ et $b > 0$. On considère l'hélice paramétrée par $M(t) = (a\cos t,\ a\sin t,\ bt)$, $t \in \R$."
            "\n\n"
            r"1. Calculer la longueur de l'arc d'hélice correspondant à $t \in [0, 2\pi]$."
            "\n"
            r"2. Déterminer le repère de Frenet $(\vec{T}, \vec{N}, \vec{B})$ en tout point."
            "\n"
            r"3. En déduire que la courbure et la torsion sont constantes, et les calculer."
        ),
        "hints": [
            r"La vitesse est de norme constante $\sqrt{a^2 + b^2}$ : l'abscisse curviligne est $s = t\sqrt{a^2 + b^2}$.",
            r"$\vec{N}$ est le vecteur unitaire qui dirige $\dfrac{\mathrm{d}\vec{T}}{\mathrm{d}s}$, et $\vec{B} = \vec{T} \wedge \vec{N}$.",
            r"Les formules de Frenet s'écrivent $\dfrac{\mathrm{d}\vec{T}}{\mathrm{d}s} = \kappa \vec{N}$ et $\dfrac{\mathrm{d}\vec{B}}{\mathrm{d}s} = -\tau \vec{N}$.",
        ],
        "difficulty": 3,
        "primary_level": "L2",
        "levels": ["L2", "L3"],
        "topics": ["geometrie", "courbes-coniques"],
    },
    # ------------------------------------------------------------------ Plus difficiles
    {
        "title": "Théorème de Cayley-Hamilton par densité des matrices diagonalisables",
        "statement": (
            r"On note $\chi_A$ le polynôme caractéristique d'une matrice carrée $A$."
            "\n\n"
            r"1. Montrer que $\chi_A(A) = 0$ lorsque $A \in \mathcal{M}_n(\C)$ est diagonalisable."
            "\n"
            r"2. Montrer que l'ensemble des matrices diagonalisables est dense dans $\mathcal{M}_n(\C)$."
            "\n"
            r"3. En déduire que $\chi_A(A) = 0$ pour toute matrice $A$ de $\mathcal{M}_n(\C)$, puis de $\mathcal{M}_n(\R)$."
        ),
        "hints": [
            r"Pour 2, trigonaliser $A$, puis modifier légèrement les coefficients diagonaux pour les rendre deux à deux distincts.",
            r"Pour 3, l'application $A \mapsto \chi_A(A)$ est continue : ses coefficients sont des polynômes en ceux de $A$.",
        ],
        "difficulty": 4,
        "primary_level": "MP",
        "levels": ["L3", "MP"],
        "topics": ["algebre-lineaire", "reduction", "topologie", "espaces-vectoriels-normes"],
    },
    {
        "title": "Théorème de Weierstrass par les polynômes de Bernstein",
        "statement": (
            r"Soit $f : [0, 1] \to \R$ une fonction continue. Pour $n \geq 1$ et $x \in [0, 1]$, on pose"
            "\n\n"
            r"$$B_n(f)(x) = \sum_{k=0}^{n} \binom{n}{k} f\left(\dfrac{k}{n}\right) x^k (1-x)^{n-k}.$$"
            "\n\n"
            r"1. Montrer que, pour tout $x \in [0, 1]$, "
            r"$\displaystyle\sum_{k=0}^{n} \binom{n}{k} \left(\dfrac{k}{n} - x\right)^2 x^k (1-x)^{n-k} = \dfrac{x(1-x)}{n}$."
            "\n"
            r"2. Soit $\varepsilon > 0$, et $\delta > 0$ tel que $|f(x) - f(y)| \leq \varepsilon$ dès que $|x - y| \leq \delta$. "
            r"Montrer que, pour tout $x \in [0, 1]$, $|B_n(f)(x) - f(x)| \leq \varepsilon + \dfrac{\|f\|_\infty}{2 n \delta^2}$."
            "\n"
            r"3. En déduire que toute fonction continue sur $[0, 1]$ est limite uniforme d'une suite de fonctions polynomiales."
        ),
        "hints": [
            r"Pour 1, reconnaître la variance de $\dfrac{S}{n}$, où $S$ suit la loi binomiale de paramètres $n$ et $x$.",
            r"Pour 2, séparer les indices $k$ tels que $\left|\dfrac{k}{n} - x\right| \leq \delta$ des autres ; pour ces derniers, $1 \leq \dfrac{1}{\delta^2}\left(\dfrac{k}{n} - x\right)^2$.",
            r"$x(1-x) \leq \dfrac{1}{4}$ sur $[0, 1]$, et un tel $\delta$ existe pour tout $\varepsilon$ d'après le théorème de Heine.",
        ],
        "difficulty": 4,
        "primary_level": "MP",
        "levels": ["L3", "MP"],
        "topics": ["analyse", "suites-series-fonctions"],
    },
    {
        "title": "Décomposition de Dunford : existence et unicité",
        "statement": (
            r"Soit $E$ un $\C$-espace vectoriel de dimension finie et $u$ un endomorphisme de $E$."
            "\n\n"
            r"1. Montrer qu'il existe un endomorphisme diagonalisable $d$ et un endomorphisme nilpotent $n$ "
            r"tels que $u = d + n$ et $d \circ n = n \circ d$."
            "\n"
            r"2. Montrer que l'on peut choisir $d$ et $n$ polynômes en $u$."
            "\n"
            r"3. Montrer que le couple $(d, n)$ est unique."
        ),
        "hints": [
            r"Pour 1, décomposer $E$ en somme directe des sous-espaces caractéristiques $\ker (u - \lambda\, \mathrm{id})^{m_\lambda}$, et prendre pour $d$ l'endomorphisme qui vaut $\lambda\, \mathrm{id}$ sur chacun d'eux.",
            r"Pour 2, les projecteurs sur les sous-espaces caractéristiques sont des polynômes en $u$ : lemme des noyaux et relation de Bézout.",
            r"Pour 3, si $u = d' + n'$ est une autre décomposition, $d'$ et $n'$ commutent avec $u$, donc avec $d$ et $n$ : $d - d' = n' - n$ est à la fois diagonalisable et nilpotent.",
        ],
        "difficulty": 5,
        "primary_level": "MP",
        "levels": ["L3", "MP"],
        "topics": ["algebre-lineaire", "reduction"],
    },
    {
        "title": r"Irrationalité de $\pi$ (preuve de Niven)",
        "statement": (
            r"On suppose par l'absurde que $\pi = \dfrac{a}{b}$, avec $a$ et $b$ entiers strictement positifs. "
            r"Pour $n \geq 1$, on pose $P_n(x) = \dfrac{x^n (a - bx)^n}{n!}$ et "
            r"$I_n = \displaystyle\int_0^{\pi} P_n(x) \sin x \,\mathrm{d}x$."
            "\n\n"
            r"1. Montrer que $I_n > 0$ et que $I_n \to 0$ quand $n \to +\infty$."
            "\n"
            r"2. Montrer que, pour tout entier $k \geq 0$, les nombres $P_n^{(k)}(0)$ et $P_n^{(k)}(\pi)$ sont des entiers."
            "\n"
            r"3. En intégrant par parties, montrer que $I_n$ est un entier. Conclure."
        ),
        "hints": [
            r"Pour 1, sur $]0, \pi[$ on a $0 < x(a - bx) \leq \pi a$.",
            r"Pour 2, $P_n$ est $\dfrac{1}{n!}$ fois un polynôme à coefficients entiers dont tous les termes sont de degré au moins $n$. Remarquer aussi que $P_n(\pi - x) = P_n(x)$.",
            r"Pour 3, des intégrations par parties successives expriment $I_n$ à l'aide des $P_n^{(2j)}(0)$ et des $P_n^{(2j)}(\pi)$. Une suite d'entiers strictement positifs ne peut pas tendre vers $0$.",
        ],
        "difficulty": 5,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP"],
        "topics": ["analyse", "calcul-integral"],
    },
]
