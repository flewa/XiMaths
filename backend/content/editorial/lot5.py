"""Cinquième lot : les démonstrations classiques de MP, en énoncés seuls.

Tirés d'un recueil de démonstrations classiques de MP, sans les démonstrations : les
solutions viennent des membres. Les énoncés ont été corrigés au passage, quand une
hypothèse manquait ou qu'une conclusion était fausse :

- Dini : les fonctions $f_n$ doivent être continues ;
- hyperplan de $\\mathcal{M}_n(\\K)$ : faux pour $n = 1$, il faut $n \\geq 2$ ;
- matrice de rang 1 : « $A = 0$ ou $\\operatorname{tr} A \\neq 0$ » contredisait le rang 1 ;
- codiagonalisation : la dimension finie manquait, la clôture algébrique ne sert pas ;
- formule de Cauchy : $f$ est la somme de la série sur un disque de $\\C$, pas sur $]-R, R[$ ;
- Borel-Cantelli : la conclusion manquait ;
- inégalité de Chernoff : $e^{\\lambda X}$ doit avoir une espérance finie.

Ne sont pas repris ici les classiques déjà publiés : forme linéaire continue et noyau fermé,
point fixe sur un compact, densité de $\\mathrm{GL}_n$, décomposition de Dunford, et densité
des matrices diagonalisables (une question de l'exercice sur Cayley-Hamilton).
"""

FIRST_YEAR = ["L1", "L2", "MPSI", "MP2I", "MP"]
SECOND_YEAR = ["L2", "L3", "MP"]

EXERCISES = [
    # ------------------------------------------------------------------ inégalités
    {
        "title": "Inégalité de Cauchy-Schwarz dans un espace préhilbertien réel",
        "statement": (
            r"Soit $E$ un espace préhilbertien réel, de produit scalaire $\langle \cdot, \cdot \rangle$ et de norme"
            r" associée $\|\cdot\|$."
            "\n\n"
            r"1. Montrer que, pour tous $x, y \in E$, $|\langle x, y \rangle| \leq \|x\|\,\|y\|$."
            "\n"
            r"2. Montrer qu'il y a égalité si et seulement si $x$ et $y$ sont colinéaires."
        ),
        "hints": [
            r"Pour $y \neq 0$, le trinôme $\lambda \mapsto \|x + \lambda y\|^2$ est positif sur $\R$ : son discriminant est négatif ou nul.",
            r"Pour l'égalité, le discriminant est nul : le trinôme a une racine $\lambda_0$, et $x + \lambda_0 y = 0$.",
        ],
        "difficulty": 1,
        "primary_level": "MPSI",
        "levels": FIRST_YEAR + ["PCSI", "PTSI", "PSI"],
        "topics": ["algebre-lineaire", "espaces-euclidiens"],
    },
    {
        "title": "Cas d'égalité dans l'inégalité triangulaire pour des nombres complexes",
        "statement": (
            r"Soit $n \geq 2$ et $z_1, \dots, z_n$ des nombres complexes non nuls. Montrer que"
            "\n\n"
            r"$$\left|\sum_{k=1}^{n} z_k\right| = \sum_{k=1}^{n} |z_k|$$"
            "\n\n"
            r"si et seulement s'il existe des réels $\lambda_2, \dots, \lambda_n$ strictement positifs tels que"
            r" $z_k = \lambda_k z_1$ pour tout $k \in [\![2, n]\!]$."
        ),
        "hints": [
            r"Pour $n = 2$ : développer $|z_1 + z_2|^2 = (|z_1| + |z_2|)^2$, et en déduire que $z_1 \overline{z_2}$ est un réel strictement positif.",
            r"Pour passer de $n$ à $n + 1$ : $\left|\sum_{k=1}^{n+1} z_k\right| \leq \left|\sum_{k=1}^{n} z_k\right| + |z_{n+1}| \leq \sum_{k=1}^{n+1} |z_k|$, et l'égalité force l'égalité à chaque étape.",
        ],
        "difficulty": 2,
        "primary_level": "MPSI",
        "levels": ["L1", "MPSI", "MP2I", "PCSI", "PTSI", "MP"],
        "topics": ["algebre", "nombres-complexes"],
    },
    {
        "title": "Inégalité de Hölder pour des sommes finies",
        "statement": (
            r"Soit $p$ et $q$ deux réels de $]1, +\infty[$ tels que $\dfrac{1}{p} + \dfrac{1}{q} = 1$, et"
            r" $(x_1, \dots, x_n)$, $(y_1, \dots, y_n)$ deux familles de réels. Montrer que"
            "\n\n"
            r"$$\left|\sum_{k=1}^{n} x_k y_k\right| \leq \left(\sum_{k=1}^{n} |x_k|^p\right)^{1/p} \left(\sum_{k=1}^{n} |y_k|^q\right)^{1/q}.$$"
        ),
        "hints": [
            r"Par concavité du logarithme, $ab \leq \dfrac{a^p}{p} + \dfrac{b^q}{q}$ pour tous réels $a, b > 0$ (inégalité de Young).",
            r"Se ramener au cas où les deux membres de droite valent $1$ en divisant chaque famille par sa « norme », puis sommer l'inégalité de Young.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": SECOND_YEAR + ["MPSI", "MP2I"],
        "topics": ["analyse", "espaces-vectoriels-normes"],
    },
    {
        "title": "Inégalité de Minkowski : $\\|\\cdot\\|_p$ est une norme sur $\\R^n$",
        "statement": (
            r"Soit $p \in [1, +\infty[$. Pour $x = (x_1, \dots, x_n) \in \R^n$, on pose"
            r" $\|x\|_p = \left(\sum_{k=1}^{n} |x_k|^p\right)^{1/p}$."
            "\n\n"
            r"1. Montrer que, pour tous $x, y \in \R^n$, $\|x + y\|_p \leq \|x\|_p + \|y\|_p$."
            "\n"
            r"2. En déduire que $\|\cdot\|_p$ est une norme sur $\R^n$."
        ),
        "hints": [
            r"Le cas $p = 1$ est immédiat. Pour $p > 1$, écrire $|x_k + y_k|^p \leq |x_k + y_k|^{p-1} |x_k| + |x_k + y_k|^{p-1} |y_k|$.",
            r"Appliquer l'inégalité de Hölder à chacune des deux sommes, avec l'exposant conjugué $q = \dfrac{p}{p - 1}$, puis diviser par $\|x + y\|_p^{p-1}$ quand il n'est pas nul.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": SECOND_YEAR,
        "topics": ["topologie", "espaces-vectoriels-normes"],
    },
    # ------------------------------------------------------------------ intégrales généralisées
    {
        "title": "Une fonction décroissante intégrable est négligeable devant $1/x$",
        "statement": (
            r"Soit $f : [0, +\infty[ \to \R$ continue par morceaux, positive et décroissante, telle que"
            r" $\displaystyle\int_0^{+\infty} f(t)\,\mathrm{d}t$ converge."
            "\n\n"
            r"Montrer que $f(x) = o\left(\dfrac{1}{x}\right)$ quand $x \to +\infty$."
        ),
        "hints": [
            r"Par décroissance, $0 \leq \dfrac{x}{2} f(x) \leq \displaystyle\int_{x/2}^{x} f(t)\,\mathrm{d}t$ pour tout $x > 0$.",
            r"Le membre de droite tend vers $0$ : c'est une différence de deux restes d'une intégrale convergente.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "MP", "PSI", "PC", "PT"],
        "topics": ["analyse", "integrales-generalisees"],
    },
    {
        "title": "Intégrale convergente et continuité uniforme : la fonction tend vers 0",
        "statement": (
            r"Soit $f : [0, +\infty[ \to \R$ uniformément continue, telle que $\displaystyle\int_0^{+\infty} f(t)\,\mathrm{d}t$"
            r" converge. Montrer que $f(x) \to 0$ quand $x \to +\infty$."
        ),
        "hints": [
            r"Raisonner par l'absurde : il existe $\varepsilon > 0$ et une suite $x_n \to +\infty$ telle que $|f(x_n)| \geq \varepsilon$.",
            r"La continuité uniforme donne $\delta > 0$ tel que $f$ garde le signe de $f(x_n)$ et $|f| \geq \dfrac{\varepsilon}{2}$ sur $[x_n - \delta, x_n + \delta]$ : comparer $\displaystyle\int_{x_n - \delta}^{x_n + \delta} f$ au critère de Cauchy.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "integrales-generalisees"],
    },
    {
        "title": "Moyenne d'une fonction de carré intégrable : $\\frac{1}{\\sqrt{x}} \\int_0^x f \\to 0$",
        "statement": (
            r"Soit $f : [0, +\infty[ \to \C$ continue, telle que $\displaystyle\int_0^{+\infty} |f(t)|^2\,\mathrm{d}t$ converge."
            r" Montrer que"
            "\n\n"
            r"$$\frac{1}{\sqrt{x}} \int_0^{x} f(t)\,\mathrm{d}t \xrightarrow[x \to +\infty]{} 0.$$"
        ),
        "hints": [
            r"Soit $\varepsilon > 0$ et $x_0$ tel que $\displaystyle\int_{x_0}^{+\infty} |f|^2 \leq \varepsilon^2$. Couper l'intégrale en $x_0$.",
            r"Sur $[x_0, x]$, l'inégalité de Cauchy-Schwarz donne $\displaystyle\int_{x_0}^{x} |f| \leq \sqrt{x - x_0}\,\sqrt{\int_{x_0}^{x} |f|^2}$.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "integrales-generalisees"],
    },
    # ------------------------------------------------------------------ suites et séries
    {
        "title": "Lemme de la puce : les valeurs d'adhérence forment un intervalle",
        "statement": (
            r"Soit $(u_n)_{n \in \N}$ une suite réelle telle que $u_{n+1} - u_n \to 0$."
            "\n\n"
            r"Montrer que l'ensemble des valeurs d'adhérence de $(u_n)$ est un intervalle de $\R$ (éventuellement vide ou"
            r" réduit à un point)."
        ),
        "hints": [
            r"Soit $a < b$ deux valeurs d'adhérence et $c \in \left]a, b\right[$. Il s'agit de montrer que, pour tout $\eta > 0$, la suite passe une infinité de fois dans $]c - \eta, c + \eta[$.",
            r"À partir d'un certain rang, les pas $|u_{n+1} - u_n|$ sont inférieurs à $\eta$ : une suite qui passe près de $a$ puis près de $b$ ne peut pas « sauter » l'intervalle $]c - \eta, c + \eta[$.",
        ],
        "difficulty": 4,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MPSI", "MP2I", "MP"],
        "topics": ["analyse", "suites-numeriques"],
    },
    {
        "title": "Comparaison série-intégrale à l'aide de la dérivée",
        "statement": (
            r"Soit $f : [0, +\infty[ \to \C$ de classe $C^1$, telle que $\displaystyle\int_0^{+\infty} |f'(t)|\,\mathrm{d}t$"
            r" converge. Montrer que la série $\displaystyle\sum_{n \geq 0} f(n)$ converge si et seulement si la suite"
            r" $\left(\displaystyle\int_0^{n} f(t)\,\mathrm{d}t\right)_{n \in \N}$ converge."
        ),
        "hints": [
            r"Pour $n \geq 1$, poser $u_n = \displaystyle\int_{n-1}^{n} f(t)\,\mathrm{d}t - f(n)$ et intégrer par parties $\displaystyle\int_{n-1}^{n} \big(f(t) - f(n)\big)\,\mathrm{d}t$ avec la primitive $t - (n - 1)$ de $1$.",
            r"On obtient $|u_n| \leq \displaystyle\int_{n-1}^{n} |f'(t)|\,\mathrm{d}t$ : la série $\sum u_n$ converge absolument.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "series-numeriques", "integrales-generalisees"],
    },
    {
        "title": "Transformation d'Abel : convergence de $\\sum u_n v_n$",
        "statement": (
            r"Soit $(u_n)_{n \in \N}$ une suite réelle décroissante de limite nulle, et $(v_n)_{n \in \N}$ une suite complexe"
            r" dont les sommes partielles $S_n = \displaystyle\sum_{k=0}^{n} v_k$ forment une suite bornée."
            "\n\n"
            r"Montrer que la série $\displaystyle\sum_{n \geq 0} u_n v_n$ converge."
        ),
        "hints": [
            r"Avec $S_{-1} = 0$, écrire $v_n = S_n - S_{n-1}$ et réorganiser : $\displaystyle\sum_{n=0}^{N} u_n v_n = u_N S_N + \sum_{n=0}^{N-1} (u_n - u_{n+1}) S_n$.",
            r"Si $|S_n| \leq M$, alors $|(u_n - u_{n+1}) S_n| \leq M (u_n - u_{n+1})$, terme général d'une série télescopique convergente.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "series-numeriques"],
    },
    {
        "title": "Lemme de Fekete pour une suite sous-additive",
        "statement": (
            r"Soit $(a_n)_{n \geq 1}$ une suite réelle sous-additive : $a_{m+n} \leq a_m + a_n$ pour tous $m, n \geq 1$."
            "\n\n"
            r"Montrer que la suite $\left(\dfrac{a_n}{n}\right)_{n \geq 1}$ tend vers $\displaystyle\inf_{n \geq 1} \frac{a_n}{n}$,"
            r" cette borne inférieure étant un réel ou $-\infty$."
        ),
        "hints": [
            r"Fixer $m \geq 1$ et écrire la division euclidienne $n = qm + r$ avec $0 \leq r < m$ : la sous-additivité donne $a_n \leq q\,a_m + a_r$ (avec la convention $a_0 = 0$).",
            r"En déduire $\displaystyle\limsup_{n \to +\infty} \frac{a_n}{n} \leq \frac{a_m}{m}$ pour tout $m$.",
        ],
        "difficulty": 4,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP"],
        "topics": ["analyse", "suites-numeriques"],
    },
    {
        "title": "Formule de Cauchy pour les coefficients d'une série entière",
        "statement": (
            r"Soit $\sum a_n z^n$ une série entière complexe de rayon de convergence $R > 0$, et $f(z) = \displaystyle\sum_{n=0}^{+\infty} a_n z^n$"
            r" sa somme sur le disque ouvert $|z| < R$."
            "\n\n"
            r"Montrer que, pour tout $r \in \left]0, R\right[$ et tout $n \in \N$,"
            "\n\n"
            r"$$a_n = \frac{1}{2\pi r^n} \int_0^{2\pi} f\left(r e^{it}\right) e^{-int}\,\mathrm{d}t.$$"
        ),
        "hints": [
            r"Écrire $f(re^{it}) e^{-int} = \displaystyle\sum_{k=0}^{+\infty} a_k r^k e^{i(k - n)t}$ : la série converge normalement sur $[0, 2\pi]$, car $\sum |a_k| r^k$ converge.",
            r"Intégrer terme à terme sur le segment $[0, 2\pi]$, avec $\displaystyle\int_0^{2\pi} e^{ipt}\,\mathrm{d}t = 0$ pour $p \in \Z^*$.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "series-entieres"],
    },
    {
        "title": "La fonction cosinus hyperbolique est majorée par $e^{t^2/2}$",
        "statement": r"Montrer que, pour tout réel $t$, $\operatorname{ch} t \leq e^{t^2/2}$.",
        "hints": [
            r"Développer les deux membres en série entière : $\operatorname{ch} t = \displaystyle\sum_{k \geq 0} \frac{t^{2k}}{(2k)!}$ et $e^{t^2/2} = \displaystyle\sum_{k \geq 0} \frac{t^{2k}}{2^k\,k!}$.",
            r"Comparer terme à terme : $(2k)! \geq 2^k\,k!$.",
        ],
        "difficulty": 1,
        "primary_level": "MP",
        "levels": ["L2", "MP", "PSI", "PC", "PT"],
        "topics": ["analyse", "series-entieres", "fonctions-usuelles"],
    },
    # ------------------------------------------------------------------ dénombrabilité, topologie
    {
        "title": "L'ensemble des nombres algébriques est dénombrable",
        "statement": (
            r"Un nombre complexe est dit algébrique s'il est racine d'un polynôme non nul à coefficients rationnels."
            r" Montrer que l'ensemble des nombres algébriques est dénombrable."
        ),
        "hints": [
            r"$\Q_n[X]$ est en bijection avec $\Q^{n+1}$, donc dénombrable ; $\Q[X]$ est une réunion dénombrable d'ensembles dénombrables.",
            r"Chaque polynôme non nul n'a qu'un nombre fini de racines ; tout rationnel $q$ est racine de $X - q$, donc l'ensemble est infini.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP"],
        "topics": ["algebre", "ensembles-applications", "polynomes"],
    },
    {
        "title": "Dans un compact, une suite converge si et seulement si elle a une seule valeur d'adhérence",
        "statement": (
            r"Soit $E$ un espace vectoriel normé, $K$ une partie compacte de $E$ et $(u_n)$ une suite d'éléments de $K$."
            "\n\n"
            r"Montrer que $(u_n)$ converge si et seulement si elle admet une unique valeur d'adhérence."
        ),
        "hints": [
            r"Si $(u_n)$ ne converge pas vers sa valeur d'adhérence $\ell$, il existe $\varepsilon > 0$ et une suite extraite $(u_{\varphi(n)})$ telle que $\|u_{\varphi(n)} - \ell\| \geq \varepsilon$ pour tout $n$.",
            r"Cette suite extraite reste dans le compact $K$ : elle a elle-même une valeur d'adhérence, distincte de $\ell$.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["topologie", "espaces-vectoriels-normes"],
    },
    {
        "title": "Un compact est recouvert par un nombre fini de boules de rayon donné",
        "statement": (
            r"Soit $E$ un espace vectoriel normé et $K$ une partie compacte non vide de $E$. Montrer que, pour tout"
            r" $\varepsilon > 0$, il existe un entier $p \geq 1$ et des points $x_1, \dots, x_p$ de $K$ tels que"
            "\n\n"
            r"$$K \subset \bigcup_{k=1}^{p} B(x_k, \varepsilon).$$"
        ),
        "hints": [
            r"Raisonner par l'absurde, et construire par récurrence une suite $(x_n)$ de $K$ telle que $x_{n+1} \notin \bigcup_{k \leq n} B(x_k, \varepsilon)$.",
            r"Deux termes distincts de cette suite sont à distance au moins $\varepsilon$ : aucune suite extraite ne peut converger.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["topologie", "espaces-vectoriels-normes"],
    },
    # ------------------------------------------------------------------ suites et séries de fonctions
    {
        "title": "Théorème de Dini : convergence monotone vers une fonction continue",
        "statement": (
            r"Soit $(f_n)$ une suite de fonctions continues de $[a, b]$ dans $\R$, croissante (pour tout $x$, la suite"
            r" $(f_n(x))$ est croissante), qui converge simplement sur $[a, b]$ vers une fonction $f$ continue."
            "\n\n"
            r"Montrer que la convergence est uniforme sur $[a, b]$."
        ),
        "hints": [
            r"Raisonner par l'absurde : il existe $\varepsilon > 0$, une extraction $\varphi$ et des points $x_n$ tels que $f(x_n) - f_{\varphi(n)}(x_n) \geq \varepsilon$.",
            r"Extraire de $(x_n)$ une suite convergente, de limite $x$. Pour $N$ fixé et $\varphi(n) \geq N$, la croissance donne $f(x_n) - f_N(x_n) \geq \varepsilon$ : passer à la limite, $f$ et $f_N$ étant continues.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "suites-series-fonctions"],
    },
    {
        "title": "Convergence uniforme d'une suite de fonctions et de la série des différences",
        "statement": (
            r"Soit $A$ un ensemble et $(f_n)_{n \in \N}$ une suite de fonctions de $A$ dans $\C$."
            "\n\n"
            r"Montrer que la suite $(f_n)$ converge uniformément sur $A$ si et seulement si la série de fonctions"
            r" $\displaystyle\sum_{n \geq 0} (f_{n+1} - f_n)$ converge uniformément sur $A$, et que, dans ce cas,"
            r" sa somme est $f - f_0$, où $f$ est la limite de $(f_n)$."
        ),
        "hints": [
            r"La somme partielle de rang $n - 1$ de la série vaut $\displaystyle\sum_{k=0}^{n-1} (f_{k+1} - f_k) = f_n - f_0$.",
            r"Le reste de la série est alors $(f - f_0) - (f_n - f_0) = f - f_n$.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "suites-series-fonctions"],
    },
    {
        "title": "Lemme de Riemann-Lebesgue pour une fonction continue par morceaux sur un segment",
        "statement": (
            r"Soit $f : [a, b] \to \C$ continue par morceaux. Montrer que"
            "\n\n"
            r"$$\int_a^b f(t)\, e^{i\lambda t}\,\mathrm{d}t \xrightarrow[\lambda \to +\infty]{} 0.$$"
        ),
        "hints": [
            r"Traiter d'abord le cas d'une fonction en escalier, par un calcul explicite sur chaque palier : $\left|\displaystyle\int_\alpha^\beta e^{i\lambda t}\,\mathrm{d}t\right| \leq \dfrac{2}{\lambda}$.",
            r"Une fonction continue par morceaux est limite uniforme de fonctions en escalier : conclure avec une approximation à $\varepsilon$ près.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "calcul-integral"],
    },
    # ------------------------------------------------------------------ groupes
    {
        "title": "Sous-groupes de $(\\R, +)$ : monogènes ou denses",
        "statement": (
            r"Soit $G$ un sous-groupe du groupe additif $(\R, +)$, non réduit à $\{0\}$. On pose $a = \inf\left(G \cap \left]0, +\infty\right[\right)$."
            "\n\n"
            r"1. Montrer que si $a > 0$, alors $a \in G$ et $G = a\Z$."
            "\n"
            r"2. Montrer que si $a = 0$, alors $G$ est dense dans $\R$."
        ),
        "hints": [
            r"Pour 1, si $a \notin G$, on trouve deux éléments de $G$ dans $\left]a, 2a\right[$ : leur différence est un élément de $G \cap \left]0, a\right[$. Puis, pour $x \in G$, regarder $x - \left\lfloor \frac{x}{a} \right\rfloor a$.",
            r"Pour 2, pour $\varepsilon > 0$ prendre $g \in G \cap \left]0, \varepsilon\right[$ : les multiples entiers de $g$ sont dans $G$ et forment une grille de pas inférieur à $\varepsilon$.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": FIRST_YEAR + ["L3"],
        "topics": ["algebre", "groupes-anneaux", "nombres-reels"],
    },
    # ------------------------------------------------------------------ algèbre linéaire
    {
        "title": "Tout hyperplan de $\\mathcal{M}_n(\\K)$ contient une matrice inversible",
        "statement": (
            r"Soit $\K = \R$ ou $\C$ et $n \geq 2$."
            "\n\n"
            r"1. Montrer que tout hyperplan de $\mathcal{M}_n(\K)$ contient une matrice inversible."
            "\n"
            r"2. Pourquoi faut-il supposer $n \geq 2$ ?"
        ),
        "hints": [
            r"Un hyperplan est le noyau d'une forme linéaire non nulle $\varphi$. Si $\varphi(E_{ij}) \neq 0$ pour un couple $i \neq j$, chercher une matrice inversible de la forme $I_n + \alpha E_{ij}$.",
            r"Sinon, $\varphi$ est nulle sur toutes les $E_{ij}$ avec $i \neq j$ : chercher une matrice de permutation sans coefficient diagonal non nul, par exemple celle d'un cycle de longueur $n$.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP"],
        "topics": ["algebre-lineaire", "calcul-matriciel", "applications-lineaires"],
    },
    {
        "title": "Deux matrices réelles semblables sur $\\C$ le sont sur $\\R$",
        "statement": (
            r"Soit $A$ et $B$ deux matrices de $\mathcal{M}_n(\R)$. On suppose qu'il existe $P \in \mathrm{GL}_n(\C)$ telle"
            r" que $B = P^{-1} A P$."
            "\n\n"
            r"Montrer qu'il existe $Q \in \mathrm{GL}_n(\R)$ telle que $B = Q^{-1} A Q$."
        ),
        "hints": [
            r"Écrire $P = X + iY$ avec $X, Y \in \mathcal{M}_n(\R)$ : l'égalité $AP = PB$ donne $AX = XB$ et $AY = YB$, donc $A(X + tY) = (X + tY)B$ pour tout réel $t$.",
            r"$t \mapsto \det(X + tY)$ est un polynôme, non nul car il ne s'annule pas en $t = i$ : il a un nombre fini de racines, et l'on choisit un réel $t$ qui n'en est pas une.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP"],
        "topics": ["algebre-lineaire", "calcul-matriciel", "determinants"],
    },
    {
        "title": "Commutant d'un endomorphisme à $n$ valeurs propres distinctes",
        "statement": (
            r"Soit $E$ un $\K$-espace vectoriel de dimension $n \geq 1$ et $u \in \mathcal{L}(E)$ admettant $n$ valeurs"
            r" propres distinctes."
            "\n\n"
            r"Montrer que l'ensemble des endomorphismes qui commutent avec $u$ est $\mathrm{Vect}(\mathrm{Id}_E, u, \dots, u^{n-1})$."
        ),
        "hints": [
            r"Dans une base de vecteurs propres de $u$, sa matrice est diagonale à coefficients distincts : les matrices qui commutent avec elle sont les matrices diagonales, qui forment un espace de dimension $n$.",
            r"$\mathrm{Id}_E, u, \dots, u^{n-1}$ commutent avec $u$ et sont libres, sinon $u$ aurait un polynôme annulateur non nul de degré au plus $n - 1$, qui s'annulerait en ses $n$ valeurs propres.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["algebre-lineaire", "reduction"],
    },
    {
        "title": "Diagonalisation simultanée de deux endomorphismes qui commutent",
        "statement": (
            r"Soit $E$ un $\K$-espace vectoriel de dimension finie, et $u, v$ deux endomorphismes diagonalisables de $E$"
            r" tels que $u \circ v = v \circ u$."
            "\n\n"
            r"Montrer qu'il existe une base de $E$ formée de vecteurs propres communs à $u$ et à $v$."
        ),
        "hints": [
            r"Les sous-espaces propres de $u$ sont stables par $v$, puisque $u$ et $v$ commutent.",
            r"La restriction de $v$ à un sous-espace stable est diagonalisable : elle a pour polynôme annulateur un polynôme annulateur de $v$, scindé à racines simples. Réunir des bases adaptées.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["algebre-lineaire", "reduction"],
    },
    {
        "title": "Une matrice de rang 1 est diagonalisable si et seulement si sa trace est non nulle",
        "statement": (
            r"Soit $\K = \R$ ou $\C$ et $A \in \mathcal{M}_n(\K)$ de rang $1$."
            "\n\n"
            r"1. Montrer que $A^2 = \operatorname{tr}(A)\, A$."
            "\n"
            r"2. En déduire que $A$ est diagonalisable si et seulement si $\operatorname{tr}(A) \neq 0$."
        ),
        "hints": [
            r"Une matrice de rang $1$ s'écrit $A = C L$, avec $C$ une colonne et $L$ une ligne non nulles, et $LC$ est un scalaire égal à $\operatorname{tr}(A)$.",
            r"Si $\operatorname{tr}(A) \neq 0$, le polynôme $X(X - \operatorname{tr}(A))$ annule $A$ et est scindé à racines simples. Sinon, $A$ est nilpotente et non nulle.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "MP", "PSI", "PC"],
        "topics": ["algebre-lineaire", "reduction"],
    },
    {
        "title": "Racine carrée d'une matrice symétrique positive",
        "statement": (
            r"On note $\mathcal{S}_n^+(\R)$ l'ensemble des matrices symétriques réelles positives, c'est-à-dire dont les"
            r" valeurs propres sont positives."
            "\n\n"
            r"Soit $A \in \mathcal{S}_n^+(\R)$. Montrer qu'il existe une unique matrice $R \in \mathcal{S}_n^+(\R)$ telle que $R^2 = A$."
        ),
        "hints": [
            r"Existence : par le théorème spectral, $A = P\,\mathrm{diag}(\lambda_1, \dots, \lambda_n)\,P^\top$ avec $P$ orthogonale ; prendre les racines carrées des $\lambda_i$.",
            r"Unicité : si $R^2 = A$, $R$ commute avec $A$, donc laisse stable chaque sous-espace propre $E_\lambda(A)$, où sa restriction est symétrique positive de carré $\lambda\,\mathrm{Id}$ : c'est $\sqrt{\lambda}\,\mathrm{Id}$.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["algebre-lineaire", "espaces-euclidiens", "reduction"],
    },
    {
        "title": "Décomposition polaire d'une matrice inversible",
        "statement": (
            r"On note $\mathcal{S}_n^{++}(\R)$ l'ensemble des matrices symétriques réelles dont les valeurs propres sont"
            r" strictement positives, et $\mathrm{O}_n(\R)$ le groupe orthogonal."
            "\n\n"
            r"Soit $A \in \mathrm{GL}_n(\R)$. Montrer qu'il existe un unique couple $(O, S) \in \mathrm{O}_n(\R) \times \mathcal{S}_n^{++}(\R)$"
            r" tel que $A = OS$."
        ),
        "hints": [
            r"Analyse : si $A = OS$, alors $A^\top A = S^2$, et $A^\top A$ est symétrique à valeurs propres strictement positives. Utiliser l'unicité de la racine carrée d'une matrice symétrique positive.",
            r"Synthèse : prendre pour $S$ la racine carrée de $A^\top A$, puis $O = A S^{-1}$, et vérifier que $O^\top O = I_n$.",
        ],
        "difficulty": 4,
        "primary_level": "MP",
        "levels": ["L3", "MP", "M1"],
        "topics": ["algebre-lineaire", "espaces-euclidiens", "reduction"],
    },
    {
        "title": "Norme subordonnée euclidienne et valeurs propres de $A^\\top A$",
        "statement": (
            r"On munit $\R^n$ de sa norme euclidienne $\|\cdot\|$ et, pour $A \in \mathcal{M}_n(\R)$, on note"
            r" $|||A||| = \displaystyle\sup_{\|X\| = 1} \|AX\|$ la norme subordonnée. Soit $A \in \mathcal{M}_n(\R)$ et $S = A^\top A$."
            "\n\n"
            r"1. Montrer que $S$ est symétrique positive."
            "\n"
            r"2. Montrer que $\operatorname{rg}(S) = \operatorname{rg}(A)$."
            "\n"
            r"3. Montrer que $|||A||| = \displaystyle\max_{\lambda \in \operatorname{Sp}(S)} \sqrt{\lambda}$."
        ),
        "hints": [
            r"Pour 1 et 2 : $X^\top S X = \|AX\|^2$, donc $SX = 0$ entraîne $AX = 0$ : $\ker S = \ker A$.",
            r"Pour 3 : $\|AX\|^2 = X^\top S X$. Décomposer $X$ dans une base orthonormée de vecteurs propres de $S$, puis tester un vecteur propre unitaire associé à la plus grande valeur propre.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["algebre-lineaire", "espaces-euclidiens", "espaces-vectoriels-normes"],
    },
    # ------------------------------------------------------------------ probabilités
    {
        "title": "Inégalité de Chernoff",
        "statement": (
            r"Soit $X$ une variable aléatoire réelle et $\lambda > 0$ tel que $e^{\lambda X}$ admette une espérance finie."
            "\n\n"
            r"Montrer que, pour tout réel $t$, $P(X \geq t) \leq e^{-\lambda t}\, E\left(e^{\lambda X}\right)$."
        ),
        "hints": [
            r"Par croissance de l'exponentielle, $\{X \geq t\} = \{e^{\lambda X} \geq e^{\lambda t}\}$.",
            r"Appliquer l'inégalité de Markov à la variable aléatoire positive $e^{\lambda X}$.",
        ],
        "difficulty": 1,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI", "PC", "PT"],
        "topics": ["probabilites", "theoremes-limites"],
    },
    {
        "title": "Somme de variables de Rademacher : une inégalité de concentration",
        "statement": (
            r"Soit $X_1, \dots, X_n$ des variables aléatoires indépendantes telles que $P(X_k = 1) = P(X_k = -1) = \dfrac{1}{2}$,"
            r" et $S_n = X_1 + \dots + X_n$."
            "\n\n"
            r"1. Montrer que, pour tout réel $t$, $E\left(e^{t S_n}\right) \leq e^{n t^2/2}$."
            "\n"
            r"2. En déduire que, pour tout $\lambda > 0$, $P(S_n \geq n\lambda) \leq e^{-n\lambda^2/2}$."
        ),
        "hints": [
            r"Pour 1, par indépendance, $E\left(e^{t S_n}\right) = \left(\operatorname{ch} t\right)^n$, et l'on admet (ou l'on montre) que $\operatorname{ch} t \leq e^{t^2/2}$.",
            r"Pour 2, appliquer l'inégalité de Markov à $e^{t S_n}$ avec $t > 0$, puis choisir $t = \lambda$.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["probabilites", "variables-aleatoires-discretes", "theoremes-limites"],
    },
    {
        "title": "Premier lemme de Borel-Cantelli",
        "statement": (
            r"Soit $(A_n)_{n \geq 1}$ une suite d'événements telle que la série $\displaystyle\sum_{n \geq 1} P(A_n)$ converge."
            r" On note $\displaystyle\limsup_{n} A_n = \bigcap_{n \geq 1} \bigcup_{k \geq n} A_k$ l'événement « une infinité"
            r" des $A_n$ sont réalisés »."
            "\n\n"
            r"Montrer que $P\left(\limsup_{n} A_n\right) = 0$ : presque sûrement, seul un nombre fini des événements $A_n$"
            r" est réalisé."
        ),
        "hints": [
            r"Pour tout $n$, $\limsup_n A_n \subset \bigcup_{k \geq n} A_k$, donc $P\left(\limsup_n A_n\right) \leq \displaystyle\sum_{k \geq n} P(A_k)$ par sous-additivité.",
            r"Ce majorant est le reste d'une série convergente.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI", "M1"],
        "topics": ["probabilites", "theoremes-limites"],
    },
]
