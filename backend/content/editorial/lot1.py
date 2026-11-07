"""Premier lot : le stock de départ, quatre exercices par niveau environ."""

EXERCISES = [
    # ------------------------------------------------------------------ L1
    {
        "title": "Limite de sin(3x)/(2x) en 0",
        "former_titles": ["Une limite usuelle"],
        "statement": r"Déterminer $\displaystyle\lim_{x \to 0} \frac{\sin(3x)}{2x}$.",
        "hints": [
            r"Faire apparaître le quotient $\dfrac{\sin(3x)}{3x}$.",
            r"On rappelle que $\dfrac{\sin u}{u} \to 1$ quand $u \to 0$.",
        ],
        "final_answer": "3/2",
        "difficulty": 1,
        "primary_level": "L1",
        "levels": ["L1", "MPSI", "MP2I", "PCSI", "PTSI"],
        "topics": ["analyse", "limites-continuite"],
        "challenge": {
            "statement": r"Déterminer $\displaystyle\lim_{x \to 0} \frac{\sin({{a}}x)}{{{b}}x}$.",
            "parameters": {"a": [2, 3, 5, 7], "b": [2, 3, 4, 6]},
            "answer": "a/b",
        },
    },
    {
        "title": "Somme des cubes des n premiers entiers, par récurrence",
        "former_titles": ["Somme des cubes"],
        "statement": (
            r"Montrer que pour tout entier $n \geq 1$,"
            "\n\n"
            r"$$\sum_{k=1}^{n} k^3 = \left(\frac{n(n+1)}{2}\right)^2.$$"
        ),
        "hints": [
            "Raisonner par récurrence sur $n$.",
            r"Pour l'hérédité, développer $\left(\frac{(n+1)(n+2)}{2}\right)^2 - \left(\frac{n(n+1)}{2}\right)^2$.",
        ],
        "difficulty": 1,
        "primary_level": "L1",
        "levels": ["L1", "MPSI", "MP2I", "PCSI", "PTSI"],
        "topics": ["algebre", "sommes-recurrence"],
    },
    {
        "title": "Injectivité d'une composée g∘f",
        "former_titles": ["Composée injective"],
        "statement": (
            r"Soit $f : E \to F$ et $g : F \to G$ deux applications."
            "\n\n"
            r"1. Montrer que si $g \circ f$ est injective, alors $f$ est injective."
            "\n"
            r"2. Donner un exemple où $g \circ f$ est injective sans que $g$ le soit."
        ),
        "hints": [
            r"Pour 1, partir de $f(x) = f(x')$ et appliquer $g$.",
            r"Pour 2, prendre $E$ à un élément et $F$ à deux éléments.",
        ],
        "difficulty": 1,
        "primary_level": "L1",
        "levels": ["L1", "MPSI", "MP2I", "PCSI"],
        "topics": ["algebre", "ensembles-applications"],
    },
    {
        "title": "Équation fonctionnelle de Cauchy f(x + y) = f(x) + f(y) sur les rationnels",
        "former_titles": ["Fonctions additives sur les rationnels"],
        "statement": (
            r"Soit $f : \R \to \R$ telle que $f(x + y) = f(x) + f(y)$ pour tous réels $x$ et $y$."
            "\n\n"
            r"Montrer que $f(x) = f(1)\,x$ pour tout $x \in \Q$."
        ),
        "hints": [
            r"Calculer $f(0)$, puis $f(-x)$ en fonction de $f(x)$.",
            r"Montrer $f(nx) = n f(x)$ pour $n \in \N$, puis appliquer cette relation à $x = \frac{p}{q}$ avec $n = q$.",
        ],
        "difficulty": 2,
        "primary_level": "L1",
        "levels": ["L1", "MPSI", "MP2I"],
        "topics": ["analyse", "algebre", "nombres-reels"],
    },
    {
        "title": "Partie entière : ⌊2x⌋ = ⌊x⌋ + ⌊x + 1/2⌋",
        "former_titles": ["Partie entière du double"],
        "statement": (
            r"On note $\lfloor x \rfloor$ la partie entière du réel $x$. Montrer que pour tout réel $x$,"
            "\n\n"
            r"$$\lfloor 2x \rfloor = \lfloor x \rfloor + \left\lfloor x + \tfrac{1}{2} \right\rfloor.$$"
        ),
        "hints": [
            r"Écrire $x = n + r$ avec $n = \lfloor x \rfloor$ et $0 \leq r < 1$.",
            r"Distinguer les cas $r < \frac{1}{2}$ et $r \geq \frac{1}{2}$.",
        ],
        "difficulty": 2,
        "primary_level": "L1",
        "levels": ["L1", "MPSI", "MP2I", "PCSI", "PTSI"],
        "topics": ["analyse", "nombres-reels", "fonctions-usuelles"],
    },
    {
        "title": "Les sous-groupes de Z sont les nZ",
        "former_titles": ["Sous-groupes de Z"],
        "statement": (
            r"Montrer que tout sous-groupe $H$ du groupe $(\Z, +)$ est de la forme $n\Z$"
            r" pour un unique entier $n \geq 0$."
        ),
        "hints": [
            r"Si $H \neq \{0\}$, considérer le plus petit élément strictement positif $n$ de $H$.",
            r"Pour $h \in H$, effectuer la division euclidienne de $h$ par $n$.",
        ],
        "difficulty": 2,
        "primary_level": "L1",
        "levels": ["L1", "L2", "MPSI", "MP2I"],
        "topics": ["algebre", "arithmetique", "groupes-anneaux", "divisibilite-pgcd"],
    },
    # ------------------------------------------------------------------ L2
    {
        "title": "Somme de la série de terme général n/2ⁿ",
        "former_titles": ["Une série dérivée"],
        "statement": r"Justifier la convergence de la série $\displaystyle\sum_{n \geq 1} \frac{n}{2^n}$ et calculer sa somme.",
        "hints": [
            r"Pour $|x| < 1$, dériver terme à terme $\displaystyle\sum_{n \geq 0} x^n = \frac{1}{1-x}$.",
            r"En déduire $\displaystyle\sum_{n \geq 1} n x^n = \frac{x}{(1-x)^2}$, puis prendre $x = \frac{1}{2}$.",
        ],
        "final_answer": "2",
        "difficulty": 2,
        "primary_level": "L2",
        "levels": ["L2", "MP", "PSI", "PC", "PT"],
        "topics": ["analyse", "series-numeriques", "series-entieres"],
        "challenge": {
            "statement": r"Calculer la somme de la série $\displaystyle\sum_{n \geq 1} \frac{n}{{{b}}^n}$.",
            "parameters": {"b": [2, 3, 4, 5, 7]},
            "answer": "b/(b-1)^2",
        },
    },
    {
        "title": "Noyau, image et rang de la dérivation sur Rₙ[X]",
        "former_titles": ["La dérivation sur les polynômes"],
        "statement": (
            r"Soit $n \geq 1$ et $E = \R_n[X]$ l'espace des polynômes réels de degré au plus $n$."
            r" On note $D : E \to E$ l'application $P \mapsto P'$."
            "\n\n"
            r"Montrer que $D$ est linéaire, puis déterminer son noyau, son image et son rang."
        ),
        "hints": [
            "Le noyau est formé des polynômes de dérivée nulle.",
            "Appliquer le théorème du rang, puis identifier l'image par inclusion et égalité des dimensions.",
        ],
        "final_answer": "n",
        "difficulty": 2,
        "primary_level": "L2",
        "levels": ["L1", "L2", "MPSI", "MP2I", "PCSI"],
        "topics": ["algebre-lineaire", "applications-lineaires", "polynomes"],
    },
    {
        "title": "Convergence simple mais non uniforme de xⁿ sur [0, 1]",
        "former_titles": ["Convergence uniforme de x puissance n"],
        "statement": (
            r"Pour $n \in \N$ et $x \in [0, 1]$, on pose $f_n(x) = x^n$."
            "\n\n"
            r"1. Déterminer la limite simple $f$ de la suite $(f_n)$ sur $[0, 1]$."
            "\n"
            r"2. Montrer que la convergence n'est pas uniforme sur $[0, 1]$."
            "\n"
            r"3. Montrer qu'elle est uniforme sur $[0, a]$ pour tout $a \in [0, 1[$."
        ),
        "hints": [
            "Pour 2, une limite uniforme de fonctions continues est continue.",
            r"Pour 3, majorer $\sup_{[0, a]} |f_n - f|$ par $a^n$.",
        ],
        "difficulty": 2,
        "primary_level": "L2",
        "levels": ["L2", "MP", "PSI", "PC"],
        "topics": ["analyse", "suites-series-fonctions"],
    },
    {
        "title": "Puissances de la matrice I + J, J remplie de 1",
        "former_titles": ["Puissances d'une matrice de rang un augmentée"],
        "statement": (
            r"On pose $J$ la matrice de $\mathcal{M}_3(\R)$ dont tous les coefficients valent $1$,"
            r" et $A = I_3 + J$."
            "\n\n"
            r"1. Calculer $J^2$ en fonction de $J$."
            "\n"
            r"2. En déduire, pour tout $n \in \N$, une expression de $A^n$ sous la forme $I_3 + c_n J$."
            "\n"
            r"3. Déterminer les valeurs propres de $A$."
        ),
        "hints": [
            r"$J^2 = 3J$, donc $I_3$ et $J$ commutent et la formule du binôme s'applique.",
            r"Chercher $c_n$ par récurrence : $c_{n+1} = 1 + 4c_n$, ou utiliser le binôme.",
        ],
        "difficulty": 2,
        "primary_level": "L2",
        "levels": ["L1", "L2", "MPSI", "MP", "PSI"],
        "topics": ["algebre-lineaire", "calcul-matriciel"],
    },
    # ------------------------------------------------------------------ L3
    {
        "title": "Intégrale de e⁻²ˣ sin(3x) sur [0, +∞[ : transformée de Laplace",
        "former_titles": ["Transformée de Laplace d'un sinus"],
        "statement": (
            r"Justifier la convergence de l'intégrale $\displaystyle\int_0^{+\infty} e^{-2x} \sin(3x)\,dx$,"
            " puis calculer sa valeur."
        ),
        "hints": [
            r"Majorer $|e^{-2x} \sin(3x)|$ par $e^{-2x}$.",
            r"Écrire $\sin(3x) = \operatorname{Im}(e^{3ix})$ et intégrer $e^{(-2 + 3i)x}$.",
        ],
        "final_answer": "3/13",
        "difficulty": 2,
        "primary_level": "L3",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "integrales-generalisees"],
        "challenge": {
            "statement": r"Calculer $\displaystyle\int_0^{+\infty} e^{-{{a}}x} \sin({{b}}x)\,dx$.",
            "parameters": {"a": [1, 2, 3, 4], "b": [1, 2, 3, 5]},
            "answer": "b/(a^2 + b^2)",
        },
    },
    {
        "title": "La boule unité de ℓ² n'est pas compacte",
        "former_titles": ["La boule unité de l'espace des suites de carré sommable"],
        "statement": (
            r"On note $\ell^2$ l'espace des suites réelles $u = (u_n)_{n \in \N}$ telles que"
            r" $\sum u_n^2 < +\infty$, muni de la norme $\|u\|_2 = \left(\sum_{n} u_n^2\right)^{1/2}$."
            "\n\n"
            r"Montrer que la boule unité fermée de $\ell^2$ n'est pas compacte."
        ),
        "hints": [
            r"Considérer la suite $(e_k)_{k \in \N}$ où $e_k$ a pour seul coefficient non nul un $1$ en position $k$.",
            r"Calculer $\|e_k - e_l\|_2$ pour $k \neq l$.",
        ],
        "difficulty": 3,
        "primary_level": "L3",
        "levels": ["L3", "M1"],
        "topics": ["topologie", "espaces-vectoriels-normes"],
    },
    {
        "title": "Q n'est pas un G-delta de R (théorème de Baire)",
        "former_titles": ["Les rationnels ne sont pas un G-delta"],
        "statement": (
            r"Montrer que $\Q$ n'est pas une intersection dénombrable d'ouverts de $\R$."
        ),
        "hints": [
            r"Supposer $\Q = \bigcap_{n} U_n$ avec $U_n$ ouvert : chaque $U_n$ est dense.",
            r"Les ouverts denses $V_q = \R \setminus \{q\}$, $q \in \Q$, sont aussi en quantité dénombrable : appliquer le théorème de Baire à la famille des $U_n$ et des $V_q$.",
        ],
        "difficulty": 4,
        "primary_level": "L3",
        "levels": ["L3", "M1"],
        "topics": ["topologie", "espaces-metriques"],
    },
    {
        "title": "Ensemble triadique de Cantor : compact, de mesure nulle, non dénombrable",
        "former_titles": ["L'ensemble triadique de Cantor"],
        "statement": (
            r"On pose $K_0 = [0, 1]$ et, pour $n \in \N$, on obtient $K_{n+1}$ en retirant de chacun"
            r" des segments de $K_n$ son tiers central ouvert. On note $K = \bigcap_{n} K_n$."
            "\n\n"
            r"1. Montrer que $K$ est un compact non vide de mesure de Lebesgue nulle."
            "\n"
            r"2. Montrer que $K$ est l'ensemble des réels de $[0, 1]$ qui admettent un développement"
            r" en base $3$ sans chiffre $1$, et en déduire que $K$ n'est pas dénombrable."
        ),
        "hints": [
            r"$K_n$ est la réunion de $2^n$ segments de longueur $3^{-n}$.",
            r"Pour 2, construire une surjection de $K$ sur $[0, 1]$ en remplaçant les chiffres $2$ par des $1$ et en lisant le résultat en base $2$.",
        ],
        "difficulty": 3,
        "primary_level": "L3",
        "levels": ["L3", "M1"],
        "topics": ["topologie", "analyse", "espaces-metriques", "integration-lebesgue"],
    },
    # ------------------------------------------------------------------ M1
    {
        "title": "Intégrale de 1/(x² + 4)² par le théorème des résidus",
        "former_titles": ["Une intégrale par les résidus"],
        "statement": r"Calculer $\displaystyle\int_{-\infty}^{+\infty} \frac{dx}{(x^2 + 4)^2}$ à l'aide du théorème des résidus.",
        "hints": [
            r"Intégrer $f(z) = \dfrac{1}{(z^2 + 4)^2}$ sur le bord du demi-disque supérieur de rayon $R$, puis faire tendre $R$ vers $+\infty$.",
            r"Le seul pôle dans le demi-plan supérieur est $2i$, d'ordre $2$.",
        ],
        "final_answer": "pi/16",
        "difficulty": 3,
        "primary_level": "M1",
        "levels": ["L3", "M1"],
        "topics": ["analyse", "integrales-generalisees"],
        "challenge": {
            "statement": r"Calculer $\displaystyle\int_{-\infty}^{+\infty} \frac{dx}{(x^2 + {{a}}^2)^2}$.",
            "parameters": {"a": [1, 2, 3, 4, 5]},
            "answer": "pi/(2*a^3)",
        },
    },
    {
        "title": "Lemme de Riemann-Lebesgue pour une fonction intégrable",
        "former_titles": ["Lemme de Riemann-Lebesgue"],
        "statement": (
            r"Soit $f \in L^1(\R)$. Montrer que"
            "\n\n"
            r"$$\lim_{|\xi| \to +\infty} \int_{\R} f(x)\, e^{-i x \xi}\,dx = 0.$$"
        ),
        "hints": [
            "Traiter d'abord le cas d'une indicatrice de segment, par un calcul explicite.",
            r"Conclure par densité des fonctions en escalier dans $L^1(\R)$.",
        ],
        "difficulty": 3,
        "primary_level": "M1",
        "levels": ["L3", "M1"],
        "topics": ["analyse", "integration-lebesgue"],
    },
    {
        "title": "Idéaux premiers et maximaux de Z[X] : (X) et (2, X)",
        "former_titles": ["Un idéal maximal de Z[X]"],
        "statement": (
            r"Dans l'anneau $\Z[X]$ :"
            "\n\n"
            r"1. Montrer que l'idéal $(X)$ est premier mais pas maximal."
            "\n"
            r"2. Montrer que l'idéal $(2, X)$ est maximal."
        ),
        "hints": [
            r"Identifier les quotients $\Z[X]/(X)$ et $\Z[X]/(2, X)$ à l'aide du morphisme $P \mapsto P(0)$.",
            "Un idéal est premier si le quotient est intègre, maximal si le quotient est un corps.",
        ],
        "difficulty": 3,
        "primary_level": "M1",
        "levels": ["L3", "M1"],
        "topics": ["algebre", "groupes-anneaux", "polynomes"],
    },
    {
        "title": "Loi forte des grands nombres avec un moment d'ordre 4",
        "statement": (
            r"Soit $(X_n)_{n \geq 1}$ une suite de variables aléatoires réelles indépendantes, de même loi,"
            r" centrées et telles que $E[X_1^4] < +\infty$. On pose $S_n = X_1 + \dots + X_n$."
            "\n\n"
            r"1. Montrer que $E[S_n^4] = n\,E[X_1^4] + 3n(n-1)\,E[X_1^2]^2$."
            "\n"
            r"2. En déduire que $\dfrac{S_n}{n} \to 0$ presque sûrement."
        ),
        "hints": [
            r"En développant $S_n^4$, les termes contenant un $X_i$ à la puissance $1$ ont une espérance nulle.",
            r"Pour 2, montrer que $\sum_n E\left[(S_n/n)^4\right] < +\infty$, puis utiliser l'inégalité de Markov et le lemme de Borel-Cantelli.",
        ],
        "difficulty": 4,
        "primary_level": "M1",
        "levels": ["M1"],
        "topics": ["probabilites", "theoremes-limites"],
    },
    # ------------------------------------------------------------------ M2
    {
        "title": "Temps de sortie moyen d'une marche aléatoire simple",
        "former_titles": ["Temps de sortie d'une marche aléatoire"],
        "statement": (
            r"Soit $(S_n)_{n \geq 0}$ la marche aléatoire simple symétrique sur $\Z$ issue de $S_0 = 2$ :"
            r" ses pas valent $+1$ ou $-1$ avec probabilité $\frac{1}{2}$, indépendamment."
            r" On note $T = \inf\{n \geq 0 : S_n \in \{0, 5\}\}$."
            "\n\n"
            r"Montrer que $T$ est presque sûrement fini et calculer $E[T]$."
        ),
        "hints": [
            r"Montrer que $(S_n^2 - n)_{n \geq 0}$ est une martingale.",
            r"Appliquer le théorème d'arrêt à $T \wedge n$, puis faire tendre $n$ vers $+\infty$. La probabilité de sortir par $5$ vaut $\frac{2}{5}$.",
        ],
        "final_answer": "6",
        "difficulty": 4,
        "primary_level": "M2",
        "levels": ["M1", "M2"],
        "topics": ["probabilites", "marches-aleatoires"],
        "challenge": {
            "statement": (
                r"La marche aléatoire simple symétrique sur $\Z$ part de ${{a}}$. Calculer l'espérance du temps"
                r" qu'elle met à atteindre $0$ ou ${{b}}$."
            ),
            "parameters": {"a": [1, 2, 3], "b": [5, 6, 7, 8]},
            "answer": "a*(b - a)",
        },
    },
    {
        "title": "Injection de Sobolev en dimension 1 : H¹ et fonctions höldériennes",
        "former_titles": ["Injection de Sobolev en dimension un"],
        "statement": (
            r"Soit $u \in C^1([0, 1])$. Montrer que pour tous $x, y \in [0, 1]$,"
            "\n\n"
            r"$$|u(x) - u(y)| \leq |x - y|^{1/2} \, \|u'\|_{L^2(0, 1)}.$$"
            "\n\n"
            r"En déduire que toute fonction de $H^1(0, 1)$ admet un représentant continu,"
            r" et même höldérien d'exposant $\frac{1}{2}$."
        ),
        "hints": [
            r"Écrire $u(x) - u(y) = \int_y^x u'(t)\,dt$ et appliquer l'inégalité de Cauchy-Schwarz.",
            r"Pour la seconde partie, utiliser la densité de $C^1([0, 1])$ dans $H^1(0, 1)$.",
        ],
        "difficulty": 4,
        "primary_level": "M2",
        "levels": ["M1", "M2"],
        "topics": ["analyse", "analyse-fonctionnelle"],
    },
    {
        "title": "Problème de Dirichlet −u'' + u = f par le théorème de Lax-Milgram",
        "former_titles": ["Problème de Dirichlet par Lax-Milgram"],
        "statement": (
            r"Soit $f \in L^2(0, 1)$. On cherche $u \in H^1_0(0, 1)$ telle que $-u'' + u = f$ au sens faible :"
            "\n\n"
            r"$$\forall v \in H^1_0(0, 1), \quad \int_0^1 (u'v' + uv) = \int_0^1 f v.$$"
            "\n\n"
            r"Montrer qu'il existe une unique telle fonction $u$, et que $\|u\|_{H^1} \leq \|f\|_{L^2}$."
        ),
        "hints": [
            r"La forme bilinéaire $a(u, v) = \int_0^1 (u'v' + uv)$ est le produit scalaire de $H^1$ : elle est continue et coercive.",
            r"Pour l'estimation, prendre $v = u$ dans la formulation faible.",
        ],
        "difficulty": 4,
        "primary_level": "M2",
        "levels": ["M1", "M2"],
        "topics": ["analyse", "analyse-fonctionnelle"],
    },
    {
        "title": "Moment d'ordre 4 du mouvement brownien par la formule d'Itô",
        "former_titles": ["Moment d'ordre 4 du mouvement brownien"],
        "statement": (
            r"Soit $(B_t)_{t \geq 0}$ un mouvement brownien standard. À l'aide de la formule d'Itô appliquée"
            r" à $x \mapsto x^4$, calculer $E[B_t^4]$ pour $t \geq 0$."
        ),
        "hints": [
            r"La formule d'Itô donne $B_t^4 = 4\int_0^t B_s^3\,dB_s + 6\int_0^t B_s^2\,ds$.",
            r"L'intégrale stochastique est d'espérance nulle et $E[B_s^2] = s$.",
        ],
        "final_answer": "3*t^2",
        "difficulty": 3,
        "primary_level": "M2",
        "levels": ["M2"],
        "topics": ["probabilites", "marches-aleatoires"],
    },
    {
        "title": "Ruine du joueur : probabilité de ruine dans le cas équitable",
        "former_titles": ["Ruine du joueur, cas équitable"],
        "statement": (
            r"Un joueur possède $3$ euros. À chaque partie, il gagne ou perd $1$ euro avec probabilité"
            r" $\frac{1}{2}$, indépendamment des parties précédentes. Il s'arrête dès qu'il est ruiné"
            r" ou qu'il possède $10$ euros."
            "\n\n"
            r"Quelle est la probabilité qu'il atteigne $10$ euros ?"
        ),
        "hints": [
            r"Sa fortune $(X_n)$ arrêtée au temps de sortie $T$ est une martingale bornée.",
            r"Le théorème d'arrêt donne $E[X_T] = 3$, avec $X_T \in \{0, 10\}$.",
        ],
        "final_answer": "3/10",
        "difficulty": 3,
        "primary_level": "M2",
        "levels": ["L3", "M1", "M2"],
        "topics": ["probabilites", "marches-aleatoires", "probabilites-conditionnelles"],
    },
    # ------------------------------------------------------------------ MPSI
    {
        "title": "Formule du binôme : somme des k parmi 5 fois 2ᵏ",
        "former_titles": ["Somme binomiale"],
        "statement": r"Calculer $\displaystyle\sum_{k=0}^{5} \binom{5}{k}\, 2^k$.",
        "hints": [r"Reconnaître le développement de $(1 + x)^5$ par la formule du binôme."],
        "final_answer": "243",
        "difficulty": 1,
        "primary_level": "MPSI",
        "levels": ["L1", "MPSI", "MP2I", "PCSI", "PTSI"],
        "topics": ["algebre", "sommes-recurrence", "denombrement"],
        "challenge": {
            "statement": r"Calculer $\displaystyle\sum_{k=0}^{{{a}}} \binom{{{a}}}{k}\, {{b}}^k$.",
            "parameters": {"a": [3, 4, 5, 6], "b": [2, 3, 4]},
            "answer": "(b + 1)^a",
        },
    },
    {
        "title": "Racines n-ièmes de l'unité : somme, et produit des 1 − ωᵏ",
        "former_titles": ["Produit autour des racines de l'unité"],
        "statement": (
            r"Soit $n \geq 2$ et $\omega = e^{2i\pi/n}$."
            "\n\n"
            r"1. Montrer que $\displaystyle\sum_{k=0}^{n-1} \omega^k = 0$."
            "\n"
            r"2. Calculer $\displaystyle\prod_{k=1}^{n-1} (1 - \omega^k)$."
        ),
        "hints": [
            r"Pour 2, factoriser $X^n - 1 = \prod_{k=0}^{n-1} (X - \omega^k)$, diviser par $X - 1$ et évaluer en $1$.",
            r"$\dfrac{X^n - 1}{X - 1} = 1 + X + \dots + X^{n-1}$.",
        ],
        "final_answer": "n",
        "difficulty": 2,
        "primary_level": "MPSI",
        "levels": ["L1", "MPSI", "MP2I", "PCSI"],
        "topics": ["algebre", "nombres-complexes", "polynomes"],
    },
    {
        "title": "Suite récurrente u(n+1) = √(2 + u(n)) : convergence et limite",
        "former_titles": ["Racines carrées emboîtées"],
        "statement": (
            r"On définit la suite $(u_n)$ par $u_0 = 0$ et $u_{n+1} = \sqrt{2 + u_n}$ pour tout $n \in \N$."
            "\n\n"
            r"Montrer que $(u_n)$ converge et déterminer sa limite."
        ),
        "hints": [
            r"Montrer par récurrence que $0 \leq u_n \leq u_{n+1} \leq 2$.",
            r"La limite $\ell$ vérifie $\ell = \sqrt{2 + \ell}$ et $\ell \geq 0$.",
        ],
        "final_answer": "2",
        "difficulty": 1,
        "primary_level": "MPSI",
        "levels": ["L1", "MPSI", "MP2I", "PCSI", "PTSI"],
        "topics": ["analyse", "suites-numeriques"],
    },
    {
        "title": "Intégrales de Wallis : relation de récurrence et valeur de W4",
        "former_titles": ["Intégrales de Wallis"],
        "statement": (
            r"Pour $n \in \N$, on pose $W_n = \displaystyle\int_0^{\pi/2} \sin^n t\,dt$."
            "\n\n"
            r"1. Montrer que $(n + 2)\,W_{n+2} = (n + 1)\,W_n$ pour tout $n \in \N$."
            "\n"
            r"2. En déduire la valeur de $W_4$."
        ),
        "hints": [
            r"Écrire $\sin^{n+2} t = \sin^{n+1} t \cdot \sin t$ et intégrer par parties.",
            r"$W_0 = \frac{\pi}{2}$.",
        ],
        "final_answer": "3*pi/16",
        "difficulty": 2,
        "primary_level": "MPSI",
        "levels": ["L1", "MPSI", "PCSI", "PTSI"],
        "topics": ["analyse", "calcul-integral"],
    },
    # ------------------------------------------------------------------ MP2I
    {
        "title": "Nombre de diviseurs positifs de 144",
        "former_titles": ["Nombre de diviseurs"],
        "statement": r"Combien l'entier $144$ admet-il de diviseurs positifs ?",
        "hints": [
            r"$144 = 2^4 \times 3^2$.",
            r"Un diviseur positif s'écrit $2^i 3^j$ avec $0 \leq i \leq 4$ et $0 \leq j \leq 2$.",
        ],
        "final_answer": "15",
        "difficulty": 1,
        "primary_level": "MP2I",
        "levels": ["L1", "MPSI", "MP2I"],
        "topics": ["arithmetique", "divisibilite-pgcd"],
        "challenge": {
            "statement": r"Combien l'entier $2^{{{a}}} \times 3^{{{b}}}$ admet-il de diviseurs positifs ?",
            "parameters": {"a": [2, 3, 4, 5, 6], "b": [1, 2, 3, 4]},
            "answer": "(a + 1)*(b + 1)",
        },
    },
    {
        "title": "PGCD de 120 et 84 par l'algorithme d'Euclide, et relation de Bézout",
        "former_titles": ["Algorithme d'Euclide et relation de Bézout"],
        "statement": (
            r"1. Calculer $d = \operatorname{pgcd}(120, 84)$ par l'algorithme d'Euclide."
            "\n"
            r"2. En remontant les calculs, trouver des entiers $u$ et $v$ tels que $120u + 84v = d$."
        ),
        "hints": [r"$120 = 1 \times 84 + 36$, puis $84 = 2 \times 36 + 12$."],
        "final_answer": "12",
        "difficulty": 1,
        "primary_level": "MP2I",
        "levels": ["L1", "MPSI", "MP2I"],
        "topics": ["arithmetique", "divisibilite-pgcd"],
    },
    {
        "title": "Reste de 3¹⁰⁰ modulo 7",
        "former_titles": ["Une puissance modulo 7"],
        "statement": r"Déterminer le reste de la division euclidienne de $3^{100}$ par $7$.",
        "hints": [
            r"D'après le petit théorème de Fermat, $3^6 \equiv 1 \pmod 7$.",
            r"$100 = 6 \times 16 + 4$.",
        ],
        "final_answer": "4",
        "difficulty": 1,
        "primary_level": "MP2I",
        "levels": ["L1", "MPSI", "MP2I"],
        "topics": ["arithmetique", "congruences"],
    },
    {
        "title": "Nombre de surjections de {1, …, n} sur {1, 2}",
        "former_titles": ["Surjections vers un ensemble à deux éléments"],
        "statement": (
            r"Soit $n \geq 1$. Combien y a-t-il de surjections de $\{1, \dots, n\}$ sur $\{1, 2\}$ ?"
            r" Donner la valeur pour $n = 4$."
        ),
        "hints": [
            r"Une application vers $\{1, 2\}$ est surjective sauf si elle est constante.",
            r"Il y a $2^n$ applications de $\{1, \dots, n\}$ dans $\{1, 2\}$.",
        ],
        "final_answer": "14",
        "difficulty": 1,
        "primary_level": "MP2I",
        "levels": ["L1", "MPSI", "MP2I", "PCSI"],
        "topics": ["algebre", "denombrement", "ensembles-applications"],
    },
    # ------------------------------------------------------------------ PCSI
    {
        "title": "Module du nombre complexe (1 + i√3)⁵",
        "former_titles": ["Module d'une puissance"],
        "statement": r"Calculer le module du nombre complexe $(1 + i\sqrt{3})^5$.",
        "hints": [r"Le module d'un produit est le produit des modules : calculer $|1 + i\sqrt{3}|$."],
        "final_answer": "32",
        "difficulty": 1,
        "primary_level": "PCSI",
        "levels": ["L1", "MPSI", "PCSI", "PTSI"],
        "topics": ["algebre", "nombres-complexes"],
        "challenge": {
            "statement": r"Calculer le module du nombre complexe $(1 + i\sqrt{3})^{{{a}}}$.",
            "parameters": {"a": [3, 4, 5, 6, 7, 8]},
            "answer": "2^a",
        },
    },
    {
        "title": "Équation différentielle y'' − 3y' + 2y = 0 avec conditions initiales",
        "former_titles": ["Équation différentielle du second ordre"],
        "statement": (
            r"Déterminer la solution $y$ de l'équation $y'' - 3y' + 2y = 0$ vérifiant $y(0) = 1$ et $y'(0) = 0$,"
            r" puis calculer $y(1)$."
        ),
        "hints": [
            r"L'équation caractéristique $r^2 - 3r + 2 = 0$ a pour racines $1$ et $2$.",
            r"Chercher $y(x) = \alpha e^x + \beta e^{2x}$.",
        ],
        "final_answer": "2*e - e^2",
        "difficulty": 1,
        "primary_level": "PCSI",
        "levels": ["L1", "MPSI", "PCSI", "PTSI"],
        "topics": ["analyse", "equations-differentielles"],
    },
    {
        "title": "Développement limité de tan x à l'ordre 5",
        "former_titles": ["Développement limité de la tangente"],
        "statement": (
            r"Déterminer le développement limité à l'ordre $5$ en $0$ de la fonction tangente."
            r" Quel est le coefficient de $x^5$ ?"
        ),
        "hints": [
            r"La tangente est impaire : $\tan x = x + a x^3 + b x^5 + o(x^5)$.",
            r"Utiliser $\tan' = 1 + \tan^2$ et identifier les coefficients.",
        ],
        "final_answer": "2/15",
        "difficulty": 2,
        "primary_level": "PCSI",
        "levels": ["L1", "MPSI", "PCSI", "PTSI"],
        "topics": ["analyse", "developpements-limites"],
    },
    {
        "title": "Aire entre les courbes y = x² et y = √x",
        "former_titles": ["Aire entre deux courbes"],
        "statement": r"Calculer l'aire du domaine compris entre les courbes d'équations $y = x^2$ et $y = \sqrt{x}$.",
        "hints": [
            r"Les courbes se coupent en $x = 0$ et $x = 1$, et $\sqrt{x} \geq x^2$ sur $[0, 1]$.",
            r"L'aire vaut $\displaystyle\int_0^1 \left(\sqrt{x} - x^2\right) dx$.",
        ],
        "final_answer": "1/3",
        "difficulty": 1,
        "primary_level": "PCSI",
        "levels": ["L1", "PCSI", "PTSI"],
        "topics": ["analyse", "calcul-integral"],
    },
    # ------------------------------------------------------------------ PTSI
    {
        "title": "Distance du point A(1, 2) à la droite 3x + 4y = 0",
        "former_titles": ["Distance d'un point à une droite"],
        "statement": (
            r"Dans un repère orthonormé du plan, calculer la distance du point $A(1, 2)$ à la droite"
            r" d'équation $3x + 4y = 0$."
        ),
        "hints": [
            r"Un vecteur normal à la droite est $\vec n = (3, 4)$.",
            r"La distance vaut $\dfrac{|3x_A + 4y_A|}{\|\vec n\|}$.",
        ],
        "final_answer": "11/5",
        "difficulty": 1,
        "primary_level": "PTSI",
        "levels": ["L1", "MPSI", "PCSI", "PTSI"],
        "topics": ["geometrie", "geometrie-plan-espace"],
        "challenge": {
            "statement": (
                r"Dans un repère orthonormé du plan, calculer la distance du point $A({{a}}, {{b}})$ à la droite"
                r" d'équation $3x + 4y = 0$."
            ),
            "parameters": {"a": [1, 2, 3, 4], "b": [1, 2, 3, 5]},
            "answer": "(3*a + 4*b)/5",
        },
    },
    {
        "title": "Aire d'un triangle de l'espace par le produit vectoriel",
        "former_titles": ["Aire d'un triangle de l'espace"],
        "statement": (
            r"Dans un repère orthonormé de l'espace, on considère les points $A(1, 0, 0)$, $B(0, 2, 0)$"
            r" et $C(0, 0, 3)$. Calculer l'aire du triangle $ABC$."
        ),
        "hints": [r"L'aire vaut $\frac{1}{2}\left\|\overrightarrow{AB} \wedge \overrightarrow{AC}\right\|$."],
        "final_answer": "7/2",
        "difficulty": 1,
        "primary_level": "PTSI",
        "levels": ["L1", "MPSI", "PCSI", "PTSI"],
        "topics": ["geometrie", "geometrie-plan-espace"],
    },
    {
        "title": "Axe et angle d'une rotation de R³ donnée par sa matrice",
        "former_titles": ["Axe et angle d'une rotation"],
        "statement": (
            r"Soit $f$ l'endomorphisme de $\R^3$ canoniquement associé à la matrice"
            "\n\n"
            r"$$M = \begin{pmatrix} 0 & 0 & 1 \\ 1 & 0 & 0 \\ 0 & 1 & 0 \end{pmatrix}.$$"
            "\n\n"
            r"1. Montrer que $f$ est une rotation."
            "\n"
            r"2. Déterminer son axe et le cosinus de son angle."
        ),
        "hints": [
            r"Vérifier que $M^\top M = I_3$ et que $\det M = 1$.",
            r"L'axe est dirigé par un vecteur fixe ; la trace vaut $1 + 2\cos\theta$.",
        ],
        "final_answer": "-1/2",
        "difficulty": 2,
        "primary_level": "PTSI",
        "levels": ["L1", "L2", "MPSI", "PCSI", "PTSI"],
        "topics": ["algebre-lineaire", "geometrie", "geometrie-plan-espace", "espaces-euclidiens"],
    },
    {
        "title": "Longueur d'une arche de cycloïde",
        "statement": (
            r"Calculer la longueur de l'arc paramétré $t \mapsto (t - \sin t,\ 1 - \cos t)$ pour $t \in [0, 2\pi]$."
        ),
        "hints": [
            r"La vitesse a pour norme $\sqrt{2 - 2\cos t}$.",
            r"$2 - 2\cos t = 4\sin^2(t/2)$, et $\sin(t/2) \geq 0$ sur $[0, 2\pi]$.",
        ],
        "final_answer": "8",
        "difficulty": 2,
        "primary_level": "PTSI",
        "levels": ["MPSI", "PCSI", "PTSI", "PT"],
        "topics": ["geometrie", "analyse", "courbes-coniques"],
    },
    # ------------------------------------------------------------------ MP
    {
        "title": "Déterminant d'une matrice à diagonale constante",
        "former_titles": ["Déterminant à diagonale constante"],
        "statement": (
            r"Calculer le déterminant de la matrice de $\mathcal{M}_4(\R)$ dont les coefficients diagonaux"
            r" valent $3$ et tous les autres valent $1$."
        ),
        "hints": [
            r"La matrice s'écrit $2I_4 + J$, où $J$ est la matrice dont tous les coefficients valent $1$.",
            r"$J$ est de rang $1$ : ses valeurs propres sont $4$ et $0$ (triple).",
        ],
        "final_answer": "48",
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "MP", "PSI", "PC"],
        "topics": ["algebre-lineaire", "determinants"],
        "challenge": {
            "statement": (
                r"Calculer le déterminant de la matrice de $\mathcal{M}_{{{b}}}(\R)$ dont les coefficients diagonaux"
                r" valent ${{a}}$ et tous les autres valent $1$."
            ),
            "parameters": {"a": [2, 3, 4, 5], "b": [3, 4, 5]},
            "answer": "(a - 1)^(b - 1)*(a + b - 1)",
        },
    },
    {
        "title": "Inverse d'une matrice par un polynôme annulateur",
        "former_titles": ["Inverse par un polynôme annulateur"],
        "statement": (
            r"Soit $A \in \mathcal{M}_n(\R)$ telle que $A^2 - 3A + 2I_n = 0$."
            "\n\n"
            r"1. Montrer que $A$ est inversible et exprimer $A^{-1}$ en fonction de $A$ et $I_n$."
            "\n"
            r"2. Montrer que $A$ est diagonalisable et que ses valeurs propres sont parmi $1$ et $2$."
        ),
        "hints": [
            r"Pour 1, écrire $A(3I_n - A) = 2I_n$.",
            "Pour 2, le polynôme annulateur est scindé à racines simples.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "MP", "PSI", "PC"],
        "topics": ["algebre-lineaire", "calcul-matriciel", "reduction"],
    },
    {
        "title": "Rayon et somme de la série entière de terme général n² xⁿ",
        "former_titles": ["Une série entière à coefficients polynomiaux"],
        "statement": (
            r"1. Déterminer le rayon de convergence $R$ de la série entière $\displaystyle\sum_{n \geq 1} n^2 x^n$,"
            r" puis calculer sa somme sur $]-R, R[$."
            "\n"
            r"2. En déduire la valeur de $\displaystyle\sum_{n \geq 1} \frac{n^2}{2^n}$."
        ),
        "hints": [
            r"Appliquer deux fois $x \dfrac{d}{dx}$ à $\displaystyle\sum_{n \geq 0} x^n = \frac{1}{1 - x}$.",
            r"On trouve $\displaystyle\sum_{n \geq 1} n^2 x^n = \frac{x(1 + x)}{(1 - x)^3}$.",
        ],
        "final_answer": "6",
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "MP", "PSI", "PC"],
        "topics": ["analyse", "series-entieres"],
    },
    {
        "title": "Intégrale de Dirichlet : convergence et valeur de l'intégrale de sin x / x",
        "former_titles": ["Intégrale de Dirichlet"],
        "statement": (
            r"1. Montrer que l'intégrale $\displaystyle\int_0^{+\infty} \frac{\sin x}{x}\,dx$ converge,"
            " mais pas absolument."
            "\n"
            r"2. Pour $t > 0$, on pose $F(t) = \displaystyle\int_0^{+\infty} e^{-tx} \frac{\sin x}{x}\,dx$."
            r" Montrer que $F$ est dérivable sur $]0, +\infty[$ et calculer $F'(t)$."
            "\n"
            r"3. En admettant que $F$ est continue en $0$, calculer $\displaystyle\int_0^{+\infty} \frac{\sin x}{x}\,dx$."
        ),
        "hints": [
            r"Pour 1, intégrer par parties sur $[1, X]$ ; pour l'absence de convergence absolue, minorer $\int_{k\pi}^{(k+1)\pi} \frac{|\sin x|}{x}\,dx$.",
            r"$F'(t) = -\dfrac{1}{1 + t^2}$ et $F(t) \to 0$ quand $t \to +\infty$.",
        ],
        "final_answer": "pi/2",
        "difficulty": 4,
        "primary_level": "MP",
        "levels": ["L3", "MP"],
        "topics": ["analyse", "integrales-generalisees", "integrales-a-parametre"],
    },
    {
        "title": "Meilleure approximation affine de x² dans L², par projection orthogonale",
        "former_titles": ["Meilleure approximation affine dans L2"],
        "statement": (
            r"On munit $C([0, 1])$ du produit scalaire $\langle f, g \rangle = \displaystyle\int_0^1 f g$."
            "\n\n"
            r"Déterminer $\displaystyle\min_{(a, b) \in \R^2} \int_0^1 \left(x^2 - a x - b\right)^2 dx$."
        ),
        "hints": [
            r"Le minimum est atteint pour la projection orthogonale de $x \mapsto x^2$ sur $\operatorname{Vect}(1, x)$.",
            r"Écrire les conditions d'orthogonalité : $\langle x^2 - ax - b, 1 \rangle = \langle x^2 - ax - b, x \rangle = 0$.",
        ],
        "final_answer": "1/180",
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["algebre-lineaire", "espaces-euclidiens"],
    },
    # ------------------------------------------------------------------ PC
    {
        "title": "Équation différentielle y' + 2y = 0 avec condition initiale",
        "former_titles": ["Équation différentielle linéaire du premier ordre"],
        "statement": r"Déterminer la solution $y$ de $y' + 2y = 0$ telle que $y(0) = 3$, puis calculer $y(1)$.",
        "hints": [r"Les solutions sont les fonctions $x \mapsto C e^{-2x}$."],
        "final_answer": "3*exp(-2)",
        "difficulty": 1,
        "primary_level": "PC",
        "levels": ["L1", "PCSI", "PC", "PSI", "PT"],
        "topics": ["analyse", "equations-differentielles"],
        "challenge": {
            "statement": (
                r"Soit $y$ la solution de $y' + {{a}}\,y = 0$ telle que $y(0) = {{b}}$. Calculer $y(1)$."
            ),
            "parameters": {"a": [1, 2, 3, 4], "b": [2, 3, 5, 7]},
            "answer": "b*exp(-a)",
        },
    },
    {
        "title": "Diagonalisation d'une matrice symétrique et trace de A¹⁰",
        "former_titles": ["Trace d'une puissance d'une matrice symétrique"],
        "statement": (
            r"Soit $A = \begin{pmatrix} 1 & 2 \\ 2 & 1 \end{pmatrix}$."
            "\n\n"
            r"1. Diagonaliser $A$ dans une base orthonormée."
            "\n"
            r"2. Calculer la trace de $A^{10}$."
        ),
        "hints": [
            r"Les valeurs propres sont $3$ et $-1$.",
            r"La trace de $A^{10}$ est la somme des puissances dixièmes des valeurs propres.",
        ],
        "final_answer": "59050",
        "difficulty": 2,
        "primary_level": "PC",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["algebre-lineaire", "reduction", "espaces-euclidiens"],
    },
    {
        "title": "Intégrale double de exp(−x² − y²) sur le disque unité, en coordonnées polaires",
        "former_titles": ["Intégrale double en coordonnées polaires"],
        "statement": r"Calculer $\displaystyle\iint_{x^2 + y^2 \leq 1} e^{-(x^2 + y^2)}\,dx\,dy$.",
        "hints": [
            r"Passer en coordonnées polaires : $dx\,dy = r\,dr\,d\theta$.",
            r"Une primitive de $r e^{-r^2}$ est $-\frac{1}{2} e^{-r^2}$.",
        ],
        "final_answer": "pi*(1 - exp(-1))",
        "difficulty": 2,
        "primary_level": "PC",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["analyse", "fonctions-plusieurs-variables", "calcul-integral"],
    },
    {
        "title": "Minimum de f(x, y) = x² + xy + y² − 3x",
        "former_titles": ["Minimum d'une fonction de deux variables"],
        "statement": (
            r"Soit $f : \R^2 \to \R$ définie par $f(x, y) = x^2 + xy + y^2 - 3x$."
            "\n\n"
            r"Déterminer les points critiques de $f$, puis montrer que $f$ admet un minimum global et calculer sa valeur."
        ),
        "hints": [
            r"Résoudre $\partial_x f = 2x + y - 3 = 0$ et $\partial_y f = x + 2y = 0$.",
            r"Écrire $f(2 + h, -1 + k) - f(2, -1)$ comme une forme quadratique en $(h, k)$.",
        ],
        "final_answer": "-3",
        "difficulty": 2,
        "primary_level": "PC",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["analyse", "fonctions-plusieurs-variables"],
    },
    # ------------------------------------------------------------------ PSI
    {
        "title": "Moment d'ordre 2 d'une loi géométrique : calcul de E(X²)",
        "former_titles": ["Moment d'ordre 2 d'une loi géométrique"],
        "statement": (
            r"Soit $X$ une variable aléatoire suivant la loi géométrique de paramètre $p = \frac{1}{4}$ :"
            r" $P(X = k) = p(1 - p)^{k-1}$ pour $k \geq 1$. Calculer $E[X^2]$."
        ),
        "hints": [
            r"$E[X] = \dfrac{1}{p}$ et $V(X) = \dfrac{1 - p}{p^2}$.",
            r"$E[X^2] = V(X) + E[X]^2$.",
        ],
        "final_answer": "28",
        "difficulty": 2,
        "primary_level": "PSI",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["probabilites", "variables-aleatoires-discretes"],
        "challenge": {
            "statement": (
                r"Soit $X$ une variable aléatoire suivant la loi géométrique de paramètre $p = \frac{1}{{{a}}}$."
                r" Calculer $E[X^2]$."
            ),
            "parameters": {"a": [2, 3, 4, 5, 6]},
            "answer": "2*a^2 - a",
        },
    },
    {
        "title": "Somme de deux lois de Poisson indépendantes",
        "statement": (
            r"Soit $X$ et $Y$ deux variables aléatoires indépendantes, de lois de Poisson de paramètres"
            r" $\lambda > 0$ et $\mu > 0$. Montrer que $X + Y$ suit la loi de Poisson de paramètre $\lambda + \mu$."
        ),
        "hints": [
            r"Pour $n \in \N$, écrire $P(X + Y = n) = \sum_{k=0}^{n} P(X = k)\,P(Y = n - k)$.",
            "Reconnaître la formule du binôme. On peut aussi utiliser les fonctions génératrices.",
        ],
        "difficulty": 2,
        "primary_level": "PSI",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["probabilites", "variables-aleatoires-discretes"],
    },
    {
        "title": "Inégalité de Bienaymé-Tchebychev : combien de lancers pour estimer une proportion",
        "former_titles": ["Combien de lancers pour estimer une proportion"],
        "statement": (
            r"On lance $n$ fois une pièce équilibrée et on note $F_n$ la fréquence des piles obtenus."
            "\n\n"
            r"À l'aide de l'inégalité de Bienaymé-Tchebychev, déterminer le plus petit entier $n$ pour lequel"
            r" cette inégalité garantit $P\left(\left|F_n - \tfrac{1}{2}\right| \geq \tfrac{1}{10}\right) \leq \tfrac{1}{20}$."
        ),
        "hints": [
            r"$nF_n$ suit la loi binomiale $\mathcal{B}(n, \frac{1}{2})$, donc $V(F_n) = \dfrac{1}{4n}$.",
            r"Bienaymé-Tchebychev donne la majoration $\dfrac{V(F_n)}{(1/10)^2} = \dfrac{25}{n}$.",
        ],
        "final_answer": "500",
        "difficulty": 2,
        "primary_level": "PSI",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["probabilites", "theoremes-limites"],
    },
    {
        "title": "Commutant d'une matrice diagonale à coefficients distincts",
        "former_titles": ["Commutant d'une matrice diagonale"],
        "statement": (
            r"Soit $D = \operatorname{diag}(\lambda_1, \dots, \lambda_n)$ une matrice diagonale de $\mathcal{M}_n(\R)$"
            r" dont les coefficients diagonaux sont deux à deux distincts."
            "\n\n"
            r"Montrer que les matrices qui commutent avec $D$ sont exactement les matrices diagonales,"
            r" et donner la dimension de cet espace."
        ),
        "hints": [r"Comparer les coefficients d'indice $(i, j)$ de $MD$ et de $DM$ : $m_{ij}\lambda_j = \lambda_i m_{ij}$."],
        "final_answer": "n",
        "difficulty": 2,
        "primary_level": "PSI",
        "levels": ["L2", "MP", "PSI", "PC"],
        "topics": ["algebre-lineaire", "calcul-matriciel", "reduction"],
    },
    # ------------------------------------------------------------------ PT
    {
        "title": "Intégrale de x² ln x sur ]0, 1]",
        "former_titles": ["Une intégrale avec un logarithme"],
        "statement": (
            r"Justifier la convergence de l'intégrale $\displaystyle\int_0^1 x^2 \ln x\,dx$ et calculer sa valeur."
        ),
        "hints": [
            r"La fonction $x \mapsto x^2 \ln x$ se prolonge par continuité en $0$.",
            r"Intégrer par parties sur $[\varepsilon, 1]$ en dérivant $\ln x$.",
        ],
        "final_answer": "-1/9",
        "difficulty": 2,
        "primary_level": "PT",
        "levels": ["L2", "PC", "PSI", "PT"],
        "topics": ["analyse", "integrales-generalisees"],
        "challenge": {
            "statement": r"Calculer $\displaystyle\int_0^1 x^{{{a}}} \ln x\,dx$.",
            "parameters": {"a": [1, 2, 3, 4, 5]},
            "answer": "-1/(a + 1)^2",
        },
    },
    {
        "title": "Rayon de courbure au sommet d'une parabole",
        "statement": (
            r"Calculer le rayon de courbure de la parabole d'équation $y = x^2$ en son sommet $O(0, 0)$."
        ),
        "hints": [
            r"Pour une courbe $y = f(x)$, la courbure vaut $\gamma = \dfrac{|f''(x)|}{\left(1 + f'(x)^2\right)^{3/2}}$.",
            r"Le rayon de courbure est $R = \dfrac{1}{\gamma}$.",
        ],
        "final_answer": "1/2",
        "difficulty": 2,
        "primary_level": "PT",
        "levels": ["L2", "PTSI", "PT"],
        "topics": ["geometrie", "courbes-coniques"],
    },
    {
        "title": "Équation du plan tangent à une sphère en un point",
        "former_titles": ["Plan tangent à une sphère"],
        "statement": (
            r"Soit $S$ la sphère d'équation $x^2 + y^2 + z^2 = 9$ dans un repère orthonormé."
            "\n\n"
            r"Vérifier que $A(1, 2, 2)$ appartient à $S$ et déterminer une équation du plan tangent à $S$ en $A$."
        ),
        "hints": [
            r"Le gradient de $(x, y, z) \mapsto x^2 + y^2 + z^2$ en $A$ est normal au plan tangent.",
            r"Un vecteur normal est donc $\overrightarrow{OA} = (1, 2, 2)$.",
        ],
        "difficulty": 1,
        "primary_level": "PT",
        "levels": ["L2", "PTSI", "PC", "PT"],
        "topics": ["geometrie", "geometrie-plan-espace"],
    },
    {
        "title": "Équation différentielle y' + y = x e⁻ˣ",
        "former_titles": ["Équation différentielle avec second membre"],
        "statement": (
            r"Déterminer la solution $y$ de l'équation $y' + y = x e^{-x}$ telle que $y(0) = 1$, puis calculer $y(1)$."
        ),
        "hints": [
            r"Chercher une solution particulière par variation de la constante : $y(x) = C(x) e^{-x}$.",
            r"On obtient $C'(x) = x$.",
        ],
        "final_answer": "3*exp(-1)/2",
        "difficulty": 1,
        "primary_level": "PT",
        "levels": ["L1", "PCSI", "PTSI", "PC", "PT"],
        "topics": ["analyse", "equations-differentielles"],
    },
]
