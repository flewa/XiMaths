"""Quatrième lot : des exercices écrits pour les prépas BCPST, ECG et B/L.

Leurs programmes modélisent : dynamique des populations, génétique, économie, statistiques.
Les énoncés partent de ces situations, avec les outils de ces filières seulement (pas de
nombres complexes ni d'équations différentielles hors BCPST). Pas de corrigé : les solutions
viennent des membres. Les réponses finales données ont été recalculées à part.
"""

EXERCISES = [
    # ------------------------------------------------------------------ BCPST
    {
        "title": "Population de truites : une suite arithmético-géométrique",
        "statement": (
            r"Un étang contient $200$ truites. Chaque année, $20\,\%$ des truites disparaissent, puis on en "
            r"réintroduit $60$. On note $u_n$ le nombre de truites après $n$ années, de sorte que $u_0 = 200$ et "
            r"$u_{n+1} = 0{,}8\,u_n + 60$."
            "\n\n"
            r"1. Déterminer le réel $\ell$ tel que $\ell = 0{,}8\,\ell + 60$."
            "\n"
            r"2. Montrer que la suite $(u_n - \ell)$ est géométrique, et en déduire $u_n$ en fonction de $n$."
            "\n"
            r"3. Vers quelle valeur la population se stabilise-t-elle ?"
        ),
        "hints": [
            r"Soustraire les égalités $u_{n+1} = 0{,}8\,u_n + 60$ et $\ell = 0{,}8\,\ell + 60$.",
            r"Une suite géométrique de raison $0{,}8$ tend vers $0$.",
        ],
        "final_answer": "300",
        "difficulty": 1,
        "primary_level": "BCPST1",
        "levels": ["BCPST1", "ECG1", "BL1", "L1"],
        "topics": ["analyse", "suites-numeriques"],
    },
    {
        "title": "Croissance logistique d'une population",
        "statement": (
            r"L'effectif $N(t)$ d'une population de bactéries vérifie l'équation logistique "
            r"$$N'(t) = N(t)\left(1 - \frac{N(t)}{1000}\right), \qquad N(0) = 100,$$ "
            r"et l'on admet que $N$ ne s'annule pas."
            "\n\n"
            r"1. On pose $z = \dfrac{1}{N}$. Montrer que $z$ vérifie une équation différentielle linéaire du premier ordre."
            "\n"
            r"2. En déduire $N(t)$ pour tout $t \geq 0$, et sa limite quand $t \to +\infty$."
            "\n"
            r"3. À quel instant la population atteint-elle $500$ individus ?"
        ),
        "hints": [
            r"$z' = -\dfrac{N'}{N^2}$ : diviser l'équation par $N^2$.",
            r"On trouve $z' = -z + \dfrac{1}{1000}$, puis $N(t) = \dfrac{1000}{1 + 9e^{-t}}$.",
        ],
        "final_answer": "2*ln(3)",
        "difficulty": 2,
        "primary_level": "BCPST1",
        "levels": ["BCPST1", "L1", "PCSI"],
        "topics": ["analyse", "equations-differentielles"],
    },
    {
        "title": "Équilibre de Hardy-Weinberg",
        "statement": (
            r"Un gène possède deux allèles, $A$ et $a$, de fréquences $p$ et $q = 1 - p$ dans une population. "
            r"Chaque individu de la génération suivante reçoit deux allèles tirés indépendamment au hasard dans la population."
            "\n\n"
            r"1. Donner les probabilités des génotypes $AA$, $Aa$ et $aa$."
            "\n"
            r"2. Montrer que la fréquence de l'allèle $A$ à la génération suivante est encore $p$."
            "\n"
            r"3. Pour quelle valeur de $p$ la proportion d'hétérozygotes $Aa$ est-elle maximale, et que vaut alors cette proportion ?"
        ),
        "hints": [
            r"Un hétérozygote s'obtient de deux façons : $A$ puis $a$, ou $a$ puis $A$.",
            r"Un individu $AA$ porte deux allèles $A$, un individu $Aa$ un seul : la fréquence de $A$ vaut $p^2 + \tfrac{1}{2} \cdot 2pq$.",
            r"Étudier $p \mapsto 2p(1 - p)$ sur $[0, 1]$.",
        ],
        "final_answer": "1/2",
        "difficulty": 1,
        "primary_level": "BCPST1",
        "levels": ["BCPST1", "L1"],
        "topics": ["probabilites", "probabilites-conditionnelles"],
    },
    {
        "title": "Germination de cinq graines : une loi binomiale",
        "statement": (
            r"Une graine germe avec la probabilité $0{,}8$. On sème $5$ graines, qui germent indépendamment les unes des autres, "
            r"et on note $X$ le nombre de graines qui germent."
            "\n\n"
            r"1. Quelle est la loi de $X$ ? Donner son espérance et sa variance."
            "\n"
            r"2. Calculer la probabilité qu'au moins $4$ graines germent."
        ),
        "hints": [
            r"$X$ compte les succès de $5$ épreuves indépendantes de même probabilité de succès.",
            r"$P(X \geq 4) = P(X = 4) + P(X = 5)$.",
        ],
        "final_answer": "2304/3125",
        "difficulty": 1,
        "primary_level": "BCPST1",
        "levels": ["BCPST1", "ECG1", "BL1", "L1"],
        "topics": ["probabilites", "variables-aleatoires-discretes"],
    },
    {
        "title": "Modèle de Leslie à deux classes d'âge",
        "statement": (
            r"Une population est formée de juvéniles et d'adultes, d'effectifs $j_n$ et $a_n$ l'année $n$. D'une année à la suivante, "
            r"$$\begin{pmatrix} j_{n+1} \\ a_{n+1} \end{pmatrix} = A \begin{pmatrix} j_n \\ a_n \end{pmatrix}, "
            r"\qquad A = \begin{pmatrix} 1 & 4 \\ \tfrac{1}{2} & 0 \end{pmatrix},$$ "
            r"et l'on part de $j_0 = a_0 = 10$."
            "\n\n"
            r"1. Déterminer les valeurs propres de $A$ et un vecteur propre pour chacune."
            "\n"
            r"2. En déduire $j_n$ et $a_n$ en fonction de $n$."
            "\n"
            r"3. Déterminer la limite du rapport $\dfrac{j_n}{a_n}$ : c'est la structure d'âge vers laquelle tend la population."
        ),
        "hints": [
            r"Le polynôme caractéristique est $\lambda^2 - \lambda - 2$.",
            r"Décomposer le vecteur $(10, 10)$ dans la base de vecteurs propres : chaque composante est multipliée par sa valeur propre à chaque année.",
            r"Le terme en $2^n$ l'emporte sur le terme en $(-1)^n$.",
        ],
        "final_answer": "4",
        "difficulty": 2,
        "primary_level": "BCPST2",
        "levels": ["BCPST2", "ECG2", "BL2", "L2"],
        "topics": ["algebre-lineaire", "reduction"],
    },
    {
        "title": "Durée de vie exponentielle : médiane et absence de mémoire",
        "statement": (
            r"La durée de vie $T$ d'un individu, en années, suit la loi exponentielle de paramètre $\lambda > 0$ : "
            r"sa densité est $t \mapsto \lambda e^{-\lambda t}$ sur $[0, +\infty[$."
            "\n\n"
            r"1. Calculer $P(T > t)$ pour $t \geq 0$, puis l'espérance de $T$."
            "\n"
            r"2. Montrer que $P(T > s + t \mid T > s) = P(T > t)$ pour tous $s, t \geq 0$."
            "\n"
            r"3. La durée de vie moyenne est de $10$ ans. Quelle est la durée de vie médiane, c'est-à-dire le réel $m$ tel que $P(T \leq m) = \tfrac{1}{2}$ ?"
        ),
        "hints": [
            r"$P(T > t) = \displaystyle\int_t^{+\infty} \lambda e^{-\lambda u}\,\mathrm{d}u = e^{-\lambda t}$ ; l'espérance se calcule par une intégration par parties.",
            r"L'espérance vaut $\dfrac{1}{\lambda}$, donc $\lambda = \dfrac{1}{10}$ ; résoudre $e^{-\lambda m} = \tfrac{1}{2}$.",
        ],
        "final_answer": "10*ln(2)",
        "difficulty": 2,
        "primary_level": "BCPST2",
        "levels": ["BCPST2", "ECG2", "BL2", "L2"],
        "topics": ["probabilites", "variables-a-densite"],
    },
    {
        "title": "Droite des moindres carrés pour trois points",
        "statement": (
            r"On a mesuré trois couples $(x_i, y_i)$ : $(0, 1)$, $(1, 3)$ et $(2, 4)$. On cherche la droite $y = ax + b$ "
            r"qui rend minimale la somme $$S(a, b) = \sum_{i=1}^{3} (y_i - a x_i - b)^2.$$"
            "\n\n"
            r"1. Développer $S(a, b)$ et calculer ses dérivées partielles."
            "\n"
            r"2. Déterminer l'unique point critique de $S$."
            "\n"
            r"3. Justifier que $S$ y atteint son minimum, et donner la pente de la droite obtenue."
        ),
        "hints": [
            r"Les deux équations $\dfrac{\partial S}{\partial a} = 0$ et $\dfrac{\partial S}{\partial b} = 0$ forment un système linéaire : $5a + 3b = 11$ et $3a + 3b = 8$.",
            r"Pour le minimum : $S$ est une somme de carrés, et l'on peut l'écrire comme sa valeur au point critique plus une quantité positive.",
        ],
        "final_answer": "3/2",
        "difficulty": 2,
        "primary_level": "BCPST2",
        "levels": ["BCPST2", "ECG2", "BL2", "L2"],
        "topics": ["analyse", "fonctions-plusieurs-variables"],
    },
    # ------------------------------------------------------------------ ECG
    {
        "title": "Somme de la série de terme général $n^2/3^n$",
        "statement": (
            r"1. Justifier la convergence de la série $\displaystyle\sum_{n \geq 0} \frac{n^2}{3^n}$."
            "\n"
            r"2. Écrire $n^2 = n(n - 1) + n$, et calculer sa somme à l'aide des séries géométriques dérivées."
        ),
        "hints": [
            r"Pour $|x| < 1$ : $\displaystyle\sum_{n \geq 1} n x^{n-1} = \frac{1}{(1 - x)^2}$ et $\displaystyle\sum_{n \geq 2} n(n - 1) x^{n-2} = \frac{2}{(1 - x)^3}$.",
            r"Avec $x = \tfrac{1}{3}$ : $\displaystyle\sum n x^n = \frac{3}{4}$ et $\displaystyle\sum n(n - 1) x^n = \frac{3}{4}$.",
        ],
        "final_answer": "3/2",
        "difficulty": 2,
        "primary_level": "ECG1",
        "levels": ["ECG1", "BCPST2", "BL2", "L2"],
        "topics": ["analyse", "series-numeriques"],
    },
    {
        "title": "Suite récurrente linéaire d'ordre 2 : $u_{n+2} = 5u_{n+1} - 6u_n$",
        "statement": (
            r"On définit la suite $(u_n)$ par $u_0 = 1$, $u_1 = 4$ et $u_{n+2} = 5u_{n+1} - 6u_n$ pour tout $n \in \N$."
            "\n\n"
            r"1. Exprimer $u_n$ en fonction de $n$."
            "\n"
            r"2. Calculer $u_5$, puis la limite de $\dfrac{u_{n+1}}{u_n}$."
        ),
        "hints": [
            r"L'équation caractéristique $r^2 - 5r + 6 = 0$ a pour racines $2$ et $3$ : chercher $u_n = \alpha\,2^n + \beta\,3^n$.",
            r"Les conditions $u_0 = 1$ et $u_1 = 4$ donnent $\alpha$ et $\beta$.",
        ],
        "final_answer": "454",
        "difficulty": 1,
        "primary_level": "ECG1",
        "levels": ["ECG1", "BCPST1", "BL1", "L1"],
        "topics": ["analyse", "suites-numeriques"],
    },
    {
        "title": "Attendre la première boule rouge : rang pair ou impair",
        "statement": (
            r"Une urne contient $2$ boules rouges et $3$ boules blanches. On tire une boule, on la remet, et l'on recommence "
            r"jusqu'à obtenir une boule rouge. On note $X$ le nombre de tirages effectués."
            "\n\n"
            r"1. Donner la loi de $X$ et son espérance."
            "\n"
            r"2. Calculer la probabilité que $X$ soit pair."
        ),
        "hints": [
            r"$X$ suit la loi géométrique de paramètre $p = \tfrac{2}{5}$ : $P(X = k) = p\,(1 - p)^{k-1}$.",
            r"$P(X \text{ pair}) = \displaystyle\sum_{k \geq 1} P(X = 2k)$ est la somme d'une série géométrique.",
        ],
        "final_answer": "3/8",
        "difficulty": 2,
        "primary_level": "ECG1",
        "levels": ["ECG1", "BCPST2", "BL2", "L2"],
        "topics": ["probabilites", "variables-aleatoires-discretes"],
    },
    {
        "title": "Fidélité à une marque : une chaîne de Markov à deux états",
        "statement": (
            r"Chaque semaine, un consommateur achète la marque $A$ ou la marque $B$. S'il a acheté $A$, il rachète $A$ la semaine "
            r"suivante avec la probabilité $0{,}8$ ; s'il a acheté $B$, il passe à $A$ avec la probabilité $0{,}3$. "
            r"Il achète $A$ la semaine $0$, et l'on note $a_n$ la probabilité qu'il achète $A$ la semaine $n$."
            "\n\n"
            r"1. Montrer que $a_{n+1} = 0{,}5\,a_n + 0{,}3$ pour tout $n \in \N$."
            "\n"
            r"2. En déduire $a_n$ en fonction de $n$."
            "\n"
            r"3. Quelle est la limite de $(a_n)$ ? Dépend-elle de l'achat de la semaine $0$ ?"
        ),
        "hints": [
            r"Formule des probabilités totales, avec le système complet « il achète $A$ la semaine $n$ », « il achète $B$ la semaine $n$ ».",
            r"La suite est arithmético-géométrique : retrancher le point fixe de $x \mapsto 0{,}5\,x + 0{,}3$.",
        ],
        "final_answer": "3/5",
        "difficulty": 2,
        "primary_level": "ECG1",
        "levels": ["ECG1", "ECG2", "BCPST2", "BL2", "L2"],
        "topics": ["probabilites", "probabilites-conditionnelles"],
    },
    {
        "title": "Maximiser une utilité sous contrainte de budget",
        "statement": (
            r"Un consommateur achète des quantités $x > 0$ et $y > 0$ de deux biens, de prix unitaires $2$ et $3$, "
            r"avec un budget de $12$ qu'il dépense entièrement : $2x + 3y = 12$. Son utilité est $U(x, y) = xy$."
            "\n\n"
            r"1. Exprimer $y$ en fonction de $x$, et l'utilité comme une fonction $u$ de la seule variable $x$. Sur quel intervalle ?"
            "\n"
            r"2. Déterminer le panier $(x, y)$ qui maximise l'utilité, et la valeur de ce maximum."
            "\n"
            r"3. Vérifier qu'en ce point le rapport $\dfrac{\partial U / \partial x}{\partial U / \partial y}$ est égal au rapport des prix."
        ),
        "hints": [
            r"$y = \dfrac{12 - 2x}{3}$ avec $0 < x < 6$, et $u(x) = \dfrac{x(12 - 2x)}{3}$.",
            r"$u$ est un trinôme du second degré : son maximum est au milieu de ses racines.",
        ],
        "final_answer": "6",
        "difficulty": 1,
        "primary_level": "ECG2",
        "levels": ["ECG2", "BL2", "L2"],
        "topics": ["analyse", "fonctions-plusieurs-variables"],
    },
    {
        "title": "Densité $c\\,x(1 - x)$ sur $[0, 1]$ : constante, espérance, variance",
        "statement": (
            r"Soit $f$ la fonction définie par $f(x) = c\,x(1 - x)$ si $x \in [0, 1]$ et $f(x) = 0$ sinon."
            "\n\n"
            r"1. Déterminer le réel $c$ pour que $f$ soit une densité de probabilité."
            "\n"
            r"2. Soit $X$ une variable aléatoire de densité $f$. Calculer $E(X)$, puis $V(X)$."
        ),
        "hints": [
            r"Une densité est positive et d'intégrale $1$ : calculer $\displaystyle\int_0^1 x(1 - x)\,\mathrm{d}x$.",
            r"$V(X) = E(X^2) - E(X)^2$, avec $E(X^2) = \displaystyle\int_0^1 x^2 f(x)\,\mathrm{d}x$.",
        ],
        "final_answer": "1/20",
        "difficulty": 1,
        "primary_level": "ECG2",
        "levels": ["ECG2", "BCPST2", "BL2", "L2"],
        "topics": ["probabilites", "variables-a-densite"],
    },
    {
        "title": "Estimer le paramètre d'une loi uniforme par le maximum de l'échantillon",
        "statement": (
            r"Soit $\theta > 0$ inconnu, et $X_1, \dots, X_n$ des variables aléatoires indépendantes de loi uniforme sur $[0, \theta]$. "
            r"On pose $M_n = \max(X_1, \dots, X_n)$."
            "\n\n"
            r"1. Déterminer la fonction de répartition de $M_n$, puis une densité de $M_n$."
            "\n"
            r"2. Calculer $E(M_n)$, et en déduire un estimateur sans biais $T_n$ de $\theta$ de la forme $c_n M_n$."
            "\n"
            r"3. Calculer la variance de $T_n$, et la comparer à celle de l'estimateur sans biais $2\,\overline{X}_n$, "
            r"où $\overline{X}_n$ est la moyenne de l'échantillon. Lequel préférer ?"
        ),
        "hints": [
            r"$M_n \leq x$ si et seulement si tous les $X_i$ sont inférieurs à $x$ : $P(M_n \leq x) = \left(\dfrac{x}{\theta}\right)^n$ pour $x \in [0, \theta]$.",
            r"$E(M_n) = \dfrac{n\theta}{n + 1}$ et $E(M_n^2) = \dfrac{n\theta^2}{n + 2}$.",
            r"$V(T_n) = \dfrac{\theta^2}{n(n + 2)}$, à comparer à $V(2\,\overline{X}_n) = \dfrac{\theta^2}{3n}$.",
        ],
        "difficulty": 3,
        "primary_level": "ECG2",
        "levels": ["ECG2", "L3"],
        "topics": ["probabilites", "variables-a-densite"],
    },
    # ------------------------------------------------------------------ B/L
    {
        "title": "Bureaux d'association comptant au moins une femme",
        "statement": (
            r"Une association de $12$ membres, dont $5$ femmes et $7$ hommes, élit un bureau : un président, un trésorier et un "
            r"secrétaire, trois personnes différentes."
            "\n\n"
            r"1. Combien de bureaux différents peut-on former ?"
            "\n"
            r"2. Combien de bureaux comptent au moins une femme ?"
        ),
        "hints": [
            r"Les trois postes sont distincts : on choisit le président, puis le trésorier parmi les autres, puis le secrétaire.",
            r"Passer au complémentaire : compter les bureaux sans aucune femme.",
        ],
        "final_answer": "1110",
        "difficulty": 1,
        "primary_level": "BL1",
        "levels": ["BL1", "ECG1", "BCPST1", "L1"],
        "topics": ["algebre", "denombrement"],
    },
    {
        "title": "Courbe de Lorenz et indice de Gini",
        "statement": (
            r"Dans une population, la part du revenu total que détient la fraction $x \in [0, 1]$ des ménages les plus modestes "
            r"est $L(x) = \dfrac{x^2 + x^3}{2}$."
            "\n\n"
            r"1. Vérifier que $L(0) = 0$, $L(1) = 1$, que $L$ est croissante et convexe, et que $L(x) \leq x$ sur $[0, 1]$."
            "\n"
            r"2. Quelle part du revenu total détient la moitié la plus modeste de la population ?"
            "\n"
            r"3. L'indice de Gini est $G = 2\displaystyle\int_0^1 \big(x - L(x)\big)\,\mathrm{d}x$ : il vaut $0$ quand tous les revenus "
            r"sont égaux. Calculer $G$."
        ),
        "hints": [
            r"Pour $L(x) \leq x$ : $x - L(x) = \dfrac{x(1 - x)(2 + x)}{2}$.",
            r"$\displaystyle\int_0^1 L(x)\,\mathrm{d}x = \frac{1}{2}\left(\frac{1}{3} + \frac{1}{4}\right)$.",
        ],
        "final_answer": "5/12",
        "difficulty": 1,
        "primary_level": "BL1",
        "levels": ["BL1", "ECG1", "L1"],
        "topics": ["analyse", "calcul-integral"],
    },
    {
        "title": "Modèle de Leontief à deux secteurs",
        "statement": (
            r"Une économie compte deux secteurs. Pour produire une unité, le secteur 1 consomme $0{,}2$ unité de sa propre production "
            r"et $0{,}4$ unité de celle du secteur 2 ; le secteur 2 consomme $0{,}3$ unité de la production du secteur 1 et $0{,}1$ unité de la sienne. "
            r"La demande des ménages est de $30$ unités pour le secteur 1 et de $60$ pour le secteur 2. "
            r"On note $x_1$ et $x_2$ les productions qui satisfont exactement toutes les demandes."
            "\n\n"
            r"1. Écrire le système vérifié par $(x_1, x_2)$ sous la forme $(I_2 - A)X = D$, en précisant les matrices $A$ et $D$."
            "\n"
            r"2. Montrer que $I_2 - A$ est inversible et calculer son inverse."
            "\n"
            r"3. En déduire $x_1$ et $x_2$, puis la production totale $x_1 + x_2$."
        ),
        "hints": [
            r"La production du secteur 1 sert aux deux secteurs et aux ménages : $x_1 = 0{,}2\,x_1 + 0{,}3\,x_2 + 30$.",
            r"$I_2 - A = \begin{pmatrix} 0{,}8 & -0{,}3 \\ -0{,}4 & 0{,}9 \end{pmatrix}$, de déterminant $0{,}6$.",
        ],
        "final_answer": "175",
        "difficulty": 1,
        "primary_level": "BL1",
        "levels": ["BL1", "ECG1", "BCPST1", "L1"],
        "topics": ["algebre-lineaire", "calcul-matriciel"],
    },
    {
        "title": "Intégrale de $\\ln x / x^2$ sur $[1, +\\infty[$",
        "statement": (
            r"Justifier la convergence de l'intégrale $\displaystyle\int_1^{+\infty} \frac{\ln x}{x^2}\,\mathrm{d}x$ et calculer sa valeur."
        ),
        "hints": [
            r"Intégrer par parties sur $[1, A]$, en dérivant $\ln x$ et en primitivant $\dfrac{1}{x^2}$.",
            r"$\dfrac{\ln A}{A} \to 0$ quand $A \to +\infty$.",
        ],
        "final_answer": "1",
        "difficulty": 1,
        "primary_level": "BL2",
        "levels": ["BL2", "ECG2", "BCPST2", "L2"],
        "topics": ["analyse", "integrales-generalisees"],
    },
    {
        "title": "Appels à un standard : une loi de Poisson",
        "statement": (
            r"Le nombre $X$ d'appels reçus par un standard en une minute suit la loi de Poisson de paramètre $2$ : "
            r"$P(X = k) = e^{-2}\,\dfrac{2^k}{k!}$ pour tout $k \in \N$."
            "\n\n"
            r"1. Vérifier que la somme de ces probabilités vaut $1$, et rappeler l'espérance de $X$."
            "\n"
            r"2. Calculer la probabilité de recevoir au moins deux appels en une minute."
            "\n"
            r"3. Pour quelles valeurs de $k$ la probabilité $P(X = k)$ est-elle maximale ?"
        ),
        "hints": [
            r"Passer au complémentaire : $P(X \geq 2) = 1 - P(X = 0) - P(X = 1)$.",
            r"Pour 3, comparer $P(X = k + 1)$ et $P(X = k)$ : leur quotient vaut $\dfrac{2}{k + 1}$.",
        ],
        "final_answer": "1 - 3*exp(-2)",
        "difficulty": 1,
        "primary_level": "BL2",
        "levels": ["BL2", "ECG2", "BCPST2", "L2"],
        "topics": ["probabilites", "variables-aleatoires-discretes"],
    },
]
