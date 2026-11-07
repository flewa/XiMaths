"""Deuxième lot : les chapitres du premier semestre, en prépa comme à l'université.

Les titres nomment la notion comme un étudiant la cherche (« équation différentielle
y'' + y = cos x », « rayon de convergence »…). Pas de corrigé : les solutions viennent
des membres, relues par trois d'entre eux.
"""

PREMIERE_ANNEE = ["L1", "MPSI", "MP2I", "PCSI", "PTSI"]
DEUXIEME_ANNEE = ["L2", "MP", "PC", "PSI", "PT"]

EXERCISES = [
    # ------------------------------------------------------------------ L1
    {
        "title": "Forme exponentielle d'un quotient de nombres complexes",
        "statement": (
            r"On pose $z = \dfrac{1+i}{1-i\sqrt{3}}$."
            "\n\n"
            r"1. Écrire $z$ sous forme exponentielle."
            "\n"
            r"2. En déduire la valeur de $z^{12}$."
        ),
        "hints": [
            r"Mettre séparément $1+i$ et $1-i\sqrt{3}$ sous forme exponentielle.",
            r"$|z| = \dfrac{\sqrt{2}}{2}$ et un argument de $z$ est $\dfrac{\pi}{4} + \dfrac{\pi}{3}$.",
        ],
        "final_answer": "-1/64",
        "difficulty": 1,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre", "nombres-complexes"],
    },
    {
        "title": "Équation du second degré à coefficients complexes",
        "statement": r"Résoudre dans $\C$ l'équation $z^2 - (3+2i)z + 5 + i = 0$.",
        "hints": [
            r"Le discriminant vaut $\Delta = -15 + 8i$.",
            r"Chercher $\delta = a + ib$ tel que $\delta^2 = \Delta$ : $a^2 - b^2 = -15$, $2ab = 8$ et $a^2 + b^2 = |\Delta| = 17$.",
            "Vérifier le résultat avec la somme et le produit des racines.",
        ],
        "difficulty": 1,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre", "nombres-complexes", "polynomes"],
    },
    {
        "title": "Méthode de Héron pour approcher racine de 2",
        "statement": (
            r"On définit la suite $(u_n)$ par $u_0 = 1$ et $u_{n+1} = \dfrac{1}{2}\left(u_n + \dfrac{2}{u_n}\right)$."
            "\n\n"
            r"1. Montrer que $u_n > 0$ pour tout $n$, puis que $u_n \geq \sqrt{2}$ pour tout $n \geq 1$."
            "\n"
            r"2. Montrer que $(u_n)_{n \geq 1}$ est décroissante, puis qu'elle converge ; déterminer sa limite."
            "\n"
            r"3. Établir $u_{n+1} - \sqrt{2} = \dfrac{(u_n - \sqrt{2})^2}{2u_n}$ et commenter la vitesse de convergence."
        ),
        "hints": [
            r"Pour 1, $u_{n+1} - \sqrt{2} = \dfrac{(u_n - \sqrt{2})^2}{2u_n}$ règle tout d'un coup.",
            r"Pour 2, calculer $u_{n+1} - u_n = \dfrac{2 - u_n^2}{2u_n}$.",
            r"La limite $\ell$ vérifie $\ell = \dfrac{1}{2}\left(\ell + \dfrac{2}{\ell}\right)$ et $\ell \geq \sqrt{2}$.",
        ],
        "final_answer": "sqrt(2)",
        "difficulty": 2,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "suites-numeriques"],
    },
    {
        "title": "Borne supérieure de l'ensemble des 1/n − 1/m",
        "statement": (
            r"On note $A = \left\{ \dfrac{1}{n} - \dfrac{1}{m} \;:\; n, m \in \N^* \right\}$."
            "\n\n"
            r"Montrer que $A$ est bornée, déterminer $\sup A$ et $\inf A$, et dire si elles sont atteintes."
        ),
        "hints": [
            r"Pour tous $n, m \geq 1$, $-1 < \dfrac{1}{n} - \dfrac{1}{m} < 1$.",
            r"Faire $n = 1$ et $m \to +\infty$ : $1 - \dfrac{1}{m} \to 1$.",
        ],
        "difficulty": 2,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "nombres-reels"],
    },
    {
        "title": "Intégrale de x e²ˣ par intégration par parties",
        "former_titles": ["Intégrale de x·e^(2x) par intégration par parties"],
        "statement": r"Calculer $\displaystyle\int_0^1 x\,e^{2x}\,\mathrm{d}x$.",
        "hints": [
            r"Intégrer par parties en dérivant $x$ et en intégrant $e^{2x}$.",
            r"Une primitive de $e^{2x}$ est $\dfrac{e^{2x}}{2}$.",
        ],
        "final_answer": "(e^2 + 1)/4",
        "difficulty": 1,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "calcul-integral"],
        "challenge": {
            "statement": r"Calculer $\displaystyle\int_0^1 x\,e^{{{a}}x}\,\mathrm{d}x$.",
            "parameters": {"a": [1, 2, 3, 4]},
            "answer": "((a - 1)*e^a + 1)/a^2",
        },
    },
    {
        "title": "Polynôme ayant 1 pour racine double",
        "statement": (
            r"Soit $P = X^4 + aX + b$ avec $a, b \in \R$."
            "\n\n"
            r"1. Déterminer $a$ et $b$ pour que $1$ soit racine au moins double de $P$."
            "\n"
            r"2. Factoriser alors $P$ en produit de polynômes irréductibles de $\R[X]$."
        ),
        "hints": [
            r"$1$ est racine au moins double si et seulement si $P(1) = P'(1) = 0$.",
            r"Diviser $P$ par $(X-1)^2$, puis regarder le discriminant du quotient.",
        ],
        "difficulty": 1,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre", "polynomes"],
    },
    {
        "title": "Dérivée n-ième par la formule de Leibniz",
        "statement": (
            r"Soit $f(x) = x^2 e^x$. Pour tout $n \geq 2$, calculer $f^{(n)}(x)$, puis $f^{(n)}(0)$."
        ),
        "hints": [
            r"Formule de Leibniz : $(uv)^{(n)} = \sum_{k=0}^{n} \binom{n}{k} u^{(k)} v^{(n-k)}$.",
            r"Avec $u = x^2$, seuls les termes $k = 0, 1, 2$ sont non nuls.",
        ],
        "final_answer": "n(n-1)",
        "difficulty": 1,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "derivation"],
    },
    {
        "title": "Équation diophantienne 21x + 15y = 6",
        "statement": r"Déterminer tous les couples $(x, y) \in \Z^2$ tels que $21x + 15y = 6$.",
        "hints": [
            r"$\gcd(21, 15) = 3$ divise $6$ : simplifier en $7x + 5y = 2$.",
            r"Trouver une solution particulière, puis utiliser le lemme de Gauss sur $7(x - x_0) = -5(y - y_0)$.",
        ],
        "difficulty": 1,
        "primary_level": "L1",
        "levels": ["L1", "MPSI", "MP2I"],
        "topics": ["arithmetique", "divisibilite-pgcd"],
    },
    {
        "title": "Point fixe d'une fonction continue de [0, 1] dans lui-même",
        "statement": (
            r"Soit $f : [0, 1] \to [0, 1]$ continue. Montrer que $f$ admet un point fixe."
            "\n\n"
            r"Le résultat subsiste-t-il pour $f : [0, 1[ \to [0, 1[$ continue ?"
        ),
        "hints": [
            r"Étudier le signe de $g(x) = f(x) - x$ en $0$ et en $1$.",
            r"Pour la seconde question, penser à $f(x) = \dfrac{1 + x}{2}$.",
        ],
        "difficulty": 1,
        "primary_level": "L1",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "limites-continuite"],
    },
    # ------------------------------------------------------------------ MPSI
    {
        "title": "Linéarisation de sin³ x par les formules d'Euler",
        "statement": (
            r"1. Linéariser $\sin^3 x$ à l'aide des formules d'Euler."
            "\n"
            r"2. En déduire $\displaystyle\int_0^{\pi} \sin^3 x \,\mathrm{d}x$."
        ),
        "hints": [
            r"Écrire $\sin x = \dfrac{e^{ix} - e^{-ix}}{2i}$ et développer le cube.",
            r"On obtient $\sin^3 x = \dfrac{3\sin x - \sin(3x)}{4}$.",
        ],
        "final_answer": "4/3",
        "difficulty": 1,
        "primary_level": "MPSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "nombres-complexes", "calcul-integral"],
    },
    {
        "title": "Somme arctan x + arctan(1/x)",
        "statement": (
            r"Montrer que pour tout $x > 0$, $\arctan x + \arctan \dfrac{1}{x} = \dfrac{\pi}{2}$."
            "\n\n"
            r"Que vaut cette somme pour $x < 0$ ?"
        ),
        "hints": [
            r"Dériver $g(x) = \arctan x + \arctan \dfrac{1}{x}$ sur $]0, +\infty[$ et sur $]-\infty, 0[$.",
            r"Une fonction de dérivée nulle sur un intervalle y est constante : évaluer en $1$ et en $-1$.",
        ],
        "difficulty": 1,
        "primary_level": "MPSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "fonctions-usuelles", "derivation"],
    },
    {
        "title": "Calcul de arctan(1/2) + arctan(1/3)",
        "statement": r"Calculer $\arctan \dfrac{1}{2} + \arctan \dfrac{1}{3}$.",
        "hints": [
            r"Calculer la tangente de la somme avec $\tan(a + b) = \dfrac{\tan a + \tan b}{1 - \tan a \tan b}$.",
            r"Situer la somme dans un intervalle où $\tan$ est injective.",
        ],
        "final_answer": "pi/4",
        "difficulty": 1,
        "primary_level": "MPSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "fonctions-usuelles"],
    },
    {
        "title": "Équation ch x = 2 et fonctions hyperboliques",
        "statement": (
            r"Résoudre dans $\R$ l'équation $\operatorname{ch} x = 2$, puis donner sa solution positive."
        ),
        "hints": [
            r"Poser $X = e^x$ : l'équation devient $X^2 - 4X + 1 = 0$.",
            r"Les deux solutions sont opposées, puisque $\operatorname{ch}$ est paire.",
        ],
        "final_answer": "ln(2 + sqrt(3))",
        "difficulty": 1,
        "primary_level": "MPSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "fonctions-usuelles"],
        "challenge": {
            "statement": r"Donner la solution positive de l'équation $\operatorname{ch} x = {{a}}$.",
            "parameters": {"a": [2, 3, 4, 5]},
            "answer": "ln(a + sqrt(a^2 - 1))",
        },
    },
    {
        "title": "Un nombre pseudo-premier : 2³⁴⁰ modulo 341",
        "former_titles": ["Un nombre pseudo-premier : 2^340 modulo 341"],
        "statement": (
            r"1. Montrer que $341$ n'est pas premier."
            "\n"
            r"2. Montrer pourtant que $2^{340} \equiv 1 \pmod{341}$."
            "\n\n"
            "La réciproque du petit théorème de Fermat est donc fausse."
        ),
        "hints": [
            r"$341 = 11 \times 31$.",
            r"$2^{10} = 1024$ : regarder ce nombre modulo $341$.",
        ],
        "difficulty": 2,
        "primary_level": "MPSI",
        "levels": ["L1", "MPSI", "MP2I", "L2", "MP"],
        "topics": ["arithmetique", "congruences"],
    },
    {
        "title": "Limite de 1/sin² x − 1/x² en 0",
        "statement": r"Déterminer $\displaystyle\lim_{x \to 0} \left( \frac{1}{\sin^2 x} - \frac{1}{x^2} \right)$.",
        "hints": [
            r"Réduire au même dénominateur : $\dfrac{x^2 - \sin^2 x}{x^2 \sin^2 x}$.",
            r"Le dénominateur est équivalent à $x^4$ ; développer $\sin^2 x$ à l'ordre $4$.",
        ],
        "final_answer": "1/3",
        "difficulty": 2,
        "primary_level": "MPSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "limites-continuite", "developpements-limites"],
    },
    {
        "title": "Développement limité de ln(1 + sin x) à l'ordre 3",
        "statement": (
            r"Déterminer le développement limité à l'ordre $3$ en $0$ de $\ln(1 + \sin x)$, "
            r"puis donner le coefficient de $x^3$."
        ),
        "hints": [
            r"Composer : $\sin x = x - \dfrac{x^3}{6} + o(x^3)$, puis $\ln(1 + u) = u - \dfrac{u^2}{2} + \dfrac{u^3}{3} + o(u^3)$.",
            r"$u^2 = x^2 + o(x^3)$ et $u^3 = x^3 + o(x^3)$.",
        ],
        "final_answer": "1/6",
        "difficulty": 2,
        "primary_level": "MPSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "developpements-limites"],
    },
    # ------------------------------------------------------------------ MP2I
    {
        "title": "Image réciproque, image directe et intersection",
        "statement": (
            r"Soit $f : E \to F$ une application, $A$ et $B$ deux parties de $F$, $C$ et $D$ deux parties de $E$."
            "\n\n"
            r"1. Montrer que $f^{-1}(A \cap B) = f^{-1}(A) \cap f^{-1}(B)$."
            "\n"
            r"2. Montrer que $f(C \cap D) \subset f(C) \cap f(D)$, et trouver un exemple où l'inclusion est stricte."
            "\n"
            r"3. Montrer que l'égalité a lieu pour toutes parties $C, D$ si $f$ est injective."
        ),
        "hints": [
            "Pour 1, raisonner par équivalences sur l'appartenance d'un élément.",
            r"Pour 2, prendre $f(x) = x^2$ sur $\R$, $C = \{-1\}$ et $D = \{1\}$.",
        ],
        "difficulty": 1,
        "primary_level": "MP2I",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre", "ensembles-applications"],
    },
    {
        "title": "Relation d'équivalence x − y entier",
        "statement": (
            r"Sur $\R$, on pose $x \mathrel{\mathcal{R}} y$ si $x - y \in \Z$."
            "\n\n"
            r"1. Montrer que $\mathcal{R}$ est une relation d'équivalence."
            "\n"
            r"2. Montrer que chaque classe d'équivalence contient un et un seul élément de $[0, 1[$."
        ),
        "hints": [
            r"Pour la transitivité, $x - z = (x - y) + (y - z)$.",
            r"Pour l'existence, penser à $x - \lfloor x \rfloor$ ; pour l'unicité, deux éléments de $[0, 1[$ diffèrent de moins de $1$.",
        ],
        "difficulty": 1,
        "primary_level": "MP2I",
        "levels": ["L1", "MPSI", "MP2I"],
        "topics": ["algebre", "ensembles-applications"],
    },
    {
        "title": "Nombre de chemins monotones dans une grille",
        "statement": (
            r"On se déplace sur les points à coordonnées entières du plan, en faisant des pas "
            r"$(1, 0)$ ou $(0, 1)$. Combien de chemins mènent de $(0, 0)$ à $(6, 4)$ ?"
        ),
        "hints": [
            "Un chemin compte 10 pas, dont 4 vers le haut.",
            "Un chemin est déterminé par la position de ses pas vers le haut parmi les 10.",
        ],
        "final_answer": "210",
        "difficulty": 1,
        "primary_level": "MP2I",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre", "denombrement"],
    },
    {
        "title": "Générateurs du groupe Z/12Z",
        "statement": (
            r"Déterminer les générateurs du groupe additif $\Z/12\Z$, puis leur nombre."
        ),
        "hints": [
            r"$\bar{k}$ engendre $\Z/12\Z$ si et seulement si $\bar{1}$ est un multiple de $\bar{k}$.",
            r"Cela revient à $\gcd(k, 12) = 1$ (relation de Bézout).",
        ],
        "final_answer": "4",
        "difficulty": 1,
        "primary_level": "MP2I",
        "levels": ["L1", "MPSI", "MP2I", "L2", "MP"],
        "topics": ["arithmetique", "groupes-anneaux", "congruences"],
    },
    {
        "title": "Dernier chiffre de 7²⁰²⁶",
        "former_titles": ["Dernier chiffre de 7^2026"],
        "statement": r"Quel est le chiffre des unités de $7^{2026}$ ?",
        "hints": [
            r"Calculer les puissances successives de $7$ modulo $10$.",
            r"$7^4 \equiv 1 \pmod{10}$ et $2026 = 4 \times 506 + 2$.",
        ],
        "final_answer": "9",
        "difficulty": 1,
        "primary_level": "MP2I",
        "levels": ["L1", "MPSI", "MP2I"],
        "topics": ["arithmetique", "congruences"],
    },
    {
        "title": "Nombre d'anagrammes du mot MISSISSIPPI",
        "statement": (
            "Combien de mots distincts (ayant un sens ou non) peut-on écrire avec toutes "
            "les lettres du mot MISSISSIPPI ?"
        ),
        "hints": [
            "Le mot compte 11 lettres : un M, quatre I, quatre S et deux P.",
            r"Diviser $11!$ par le nombre de façons de permuter les lettres identiques entre elles.",
        ],
        "final_answer": "34650",
        "difficulty": 1,
        "primary_level": "MP2I",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre", "denombrement"],
    },
    # ------------------------------------------------------------------ PCSI
    {
        "title": "Équation différentielle y' + 2xy = 2x",
        "statement": (
            r"Résoudre sur $\R$ l'équation $y' + 2xy = 2x$ avec la condition $y(0) = 0$, puis calculer $y(1)$."
        ),
        "hints": [
            r"Solutions de l'équation homogène : $x \mapsto C e^{-x^2}$.",
            "Chercher une solution particulière constante.",
        ],
        "final_answer": "1 - e^(-1)",
        "difficulty": 1,
        "primary_level": "PCSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "equations-differentielles"],
        "challenge": {
            "statement": (
                r"Résoudre $y' + {{a}}xy = {{a}}x$ avec $y(0) = 0$, puis calculer $y(1)$."
            ),
            "parameters": {"a": [2, 4, 6]},
            "answer": "1 - sqrt(e^(-a))",
        },
    },
    {
        "title": "Formule de Bayes : fiabilité d'un test de dépistage",
        "statement": (
            "Une maladie touche 1 % de la population. Un test la détecte chez 99 % des malades, "
            "et donne un résultat positif à tort chez 5 % des personnes saines."
            "\n\n"
            "Une personne prise au hasard a un test positif. Quelle est la probabilité qu'elle soit malade ?"
        ),
        "hints": [
            r"Noter $M$ l'événement « malade » et $T$ « test positif » ; on cherche $P(M \mid T)$.",
            r"Formule des probabilités totales : $P(T) = P(T \mid M)P(M) + P(T \mid \overline{M})P(\overline{M})$.",
        ],
        "final_answer": "1/6",
        "difficulty": 1,
        "primary_level": "PCSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["probabilites", "probabilites-conditionnelles"],
    },
    {
        "title": "Intégrale de 1/(x² + x + 1) sur [0, 1]",
        "statement": r"Calculer $\displaystyle\int_0^1 \frac{\mathrm{d}x}{x^2 + x + 1}$.",
        "hints": [
            r"Forme canonique : $x^2 + x + 1 = \left(x + \frac{1}{2}\right)^2 + \frac{3}{4}$.",
            r"Poser $u = \dfrac{2x + 1}{\sqrt{3}}$ pour se ramener à $\dfrac{1}{1 + u^2}$.",
        ],
        "final_answer": "pi/(3*sqrt(3))",
        "difficulty": 1,
        "primary_level": "PCSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "calcul-integral"],
    },
    {
        "title": "Encadrement de ln(1 + x) par les accroissements finis",
        "statement": (
            r"1. Montrer que pour tout $x > 0$, $\dfrac{x}{1 + x} < \ln(1 + x) < x$."
            "\n"
            r"2. En déduire $\displaystyle\lim_{n \to +\infty} \left(1 + \frac{1}{n}\right)^n$."
        ),
        "hints": [
            r"Appliquer le théorème des accroissements finis à $\ln$ entre $1$ et $1 + x$.",
            r"Pour 2, encadrer $n \ln\left(1 + \frac{1}{n}\right)$.",
        ],
        "difficulty": 1,
        "primary_level": "PCSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "derivation"],
    },
    {
        "title": "Somme des k fois k parmi n",
        "statement": r"Pour $n \geq 1$, calculer $\displaystyle\sum_{k=0}^{n} k \binom{n}{k}$.",
        "hints": [
            r"Vérifier que $k \binom{n}{k} = n \binom{n-1}{k-1}$ pour $k \geq 1$.",
            r"Autre méthode : dériver $(1 + x)^n = \sum_{k} \binom{n}{k} x^k$, puis prendre $x = 1$.",
        ],
        "final_answer": "n*2^(n-1)",
        "difficulty": 1,
        "primary_level": "PCSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre", "sommes-recurrence", "denombrement"],
    },
    {
        "title": "Somme télescopique de 1/(k(k+1)(k+2))",
        "statement": (
            r"Pour $n \geq 1$, calculer $S_n = \displaystyle\sum_{k=1}^{n} \frac{1}{k(k+1)(k+2)}$ en fonction de $n$."
        ),
        "hints": [
            r"Vérifier que $\dfrac{2}{k(k+1)(k+2)} = \dfrac{1}{k(k+1)} - \dfrac{1}{(k+1)(k+2)}$.",
            "La somme devient télescopique.",
        ],
        "final_answer": "1/4 - 1/(2(n+1)(n+2))",
        "difficulty": 1,
        "primary_level": "PCSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre", "sommes-recurrence"],
    },
    {
        "title": "Vitesse de convergence de (1 + 1/n)ⁿ vers e",
        "former_titles": ["Vitesse de convergence de (1 + 1/n)^n vers e"],
        "statement": (
            r"Déterminer $\displaystyle\lim_{n \to +\infty} n\left(e - \left(1 + \frac{1}{n}\right)^n\right)$."
        ),
        "hints": [
            r"Écrire $\left(1 + \frac{1}{n}\right)^n = \exp\left(n \ln\left(1 + \frac{1}{n}\right)\right)$.",
            r"$n \ln\left(1 + \frac{1}{n}\right) = 1 - \dfrac{1}{2n} + o\left(\dfrac{1}{n}\right)$.",
        ],
        "final_answer": "e/2",
        "difficulty": 2,
        "primary_level": "PCSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "developpements-limites", "suites-numeriques"],
    },
    # ------------------------------------------------------------------ PTSI
    {
        "title": "Équation différentielle à racine double y'' + 2y' + y = 0",
        "statement": (
            r"Résoudre $y'' + 2y' + y = 0$ avec $y(0) = 1$ et $y'(0) = 0$, puis calculer $y(1)$."
        ),
        "hints": [
            r"L'équation caractéristique $r^2 + 2r + 1 = 0$ a une racine double.",
            r"Les solutions sont $x \mapsto (A + Bx)e^{-x}$.",
        ],
        "final_answer": "2/e",
        "difficulty": 1,
        "primary_level": "PTSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "equations-differentielles"],
    },
    {
        "title": "Équation différentielle y'' + y = cos x : la résonance",
        "statement": (
            r"Résoudre $y'' + y = \cos x$ avec $y(0) = y'(0) = 0$, puis calculer $y\left(\dfrac{\pi}{2}\right)$."
        ),
        "hints": [
            r"Le second membre est solution de l'équation homogène : chercher une solution particulière de la forme $x(a\cos x + b\sin x)$.",
            r"Autre méthode : chercher une solution particulière complexe de $y'' + y = e^{ix}$ sous la forme $\lambda x e^{ix}$.",
        ],
        "final_answer": "pi/4",
        "difficulty": 2,
        "primary_level": "PTSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "equations-differentielles"],
        "challenge": {
            "statement": (
                r"Résoudre $y'' + {{a}}^2 y = \cos({{a}}x)$ avec $y(0) = y'(0) = 0$, "
                r"puis calculer $y\left(\dfrac{\pi}{2 \times {{a}}}\right)$."
            ),
            "parameters": {"a": [2, 3, 4]},
            "answer": "pi/(4*a^2)",
        },
    },
    {
        "title": "Noyau et image d'une application linéaire de R³",
        "statement": (
            r"Soit $f : \R^3 \to \R^3$, $(x, y, z) \mapsto (x + y,\, y + z,\, x - z)$."
            "\n\n"
            r"Déterminer une base du noyau de $f$, le rang de $f$ et une équation de son image."
        ),
        "hints": [
            r"Résoudre le système $x + y = 0$, $y + z = 0$, $x - z = 0$.",
            r"Le théorème du rang donne la dimension de l'image ; chercher une relation entre les trois coordonnées de $f(x, y, z)$.",
        ],
        "difficulty": 1,
        "primary_level": "PTSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre-lineaire", "applications-lineaires"],
    },
    {
        "title": "Rang d'une matrice selon un paramètre",
        "statement": (
            r"Pour $a \in \R$, déterminer le rang de la matrice"
            "\n\n"
            r"$$A = \begin{pmatrix} 1 & 1 & a \\ 1 & a & 1 \\ a & 1 & 1 \end{pmatrix}.$$"
        ),
        "hints": [
            r"Calculer $\det A$ : ajouter les deux dernières colonnes à la première.",
            r"$\det A = -(a - 1)^2 (a + 2)$ ; étudier à part $a = 1$ et $a = -2$.",
        ],
        "difficulty": 2,
        "primary_level": "PTSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre-lineaire", "applications-lineaires", "determinants"],
    },
    {
        "title": "Puissance n-ième d'une matrice par la formule du binôme",
        "statement": (
            r"Soit $A = \begin{pmatrix} 2 & 1 \\ 0 & 2 \end{pmatrix}$. Calculer $A^n$ pour tout $n \geq 1$, "
            r"puis donner son coefficient en position $(1, 2)$."
        ),
        "hints": [
            r"Écrire $A = 2I_2 + N$ avec $N^2 = 0$.",
            r"$I_2$ et $N$ commutent : la formule du binôme s'applique et s'arrête au rang $1$.",
        ],
        "final_answer": "n*2^(n-1)",
        "difficulty": 1,
        "primary_level": "PTSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["algebre-lineaire", "calcul-matriciel"],
    },
    {
        "title": "Nature et aire de la conique x² + xy + y² = 1",
        "statement": (
            r"Déterminer la nature de la courbe d'équation $x^2 + xy + y^2 = 1$, ses axes de symétrie, "
            r"puis l'aire du domaine $x^2 + xy + y^2 \leq 1$."
        ),
        "hints": [
            r"Tourner le repère de $\dfrac{\pi}{4}$ : poser $x = \dfrac{u - v}{\sqrt{2}}$ et $y = \dfrac{u + v}{\sqrt{2}}$.",
            r"On obtient $\dfrac{3}{2}u^2 + \dfrac{1}{2}v^2 = 1$ ; l'aire d'une ellipse de demi-axes $a$ et $b$ vaut $\pi ab$.",
        ],
        "final_answer": "2*pi/sqrt(3)",
        "difficulty": 2,
        "primary_level": "PTSI",
        "levels": ["L1", "MPSI", "PCSI", "PTSI"],
        "topics": ["geometrie", "courbes-coniques"],
    },
    {
        "title": "Intégrale de 1/(x² − 1) par décomposition en éléments simples",
        "statement": r"Calculer $\displaystyle\int_2^3 \frac{\mathrm{d}x}{x^2 - 1}$.",
        "hints": [
            r"$\dfrac{1}{x^2 - 1} = \dfrac{1}{2}\left(\dfrac{1}{x - 1} - \dfrac{1}{x + 1}\right)$.",
            r"Une primitive est $\dfrac{1}{2} \ln \dfrac{x - 1}{x + 1}$ sur $]1, +\infty[$.",
        ],
        "final_answer": "ln(3/2)/2",
        "difficulty": 1,
        "primary_level": "PTSI",
        "levels": PREMIERE_ANNEE,
        "topics": ["analyse", "calcul-integral"],
    },
    {
        "title": "Longueur de l'astroïde",
        "statement": (
            r"L'astroïde est la courbe paramétrée $x(t) = \cos^3 t$, $y(t) = \sin^3 t$, $t \in [0, 2\pi]$."
            "\n\n"
            "Calculer sa longueur."
        ),
        "hints": [
            r"$\sqrt{x'(t)^2 + y'(t)^2} = 3|\cos t \sin t|$.",
            r"Par symétrie, calculer la longueur sur $\left[0, \frac{\pi}{2}\right]$ et multiplier par $4$.",
        ],
        "final_answer": "6",
        "difficulty": 2,
        "primary_level": "PTSI",
        "levels": ["L1", "MPSI", "PCSI", "PTSI", "PT"],
        "topics": ["geometrie", "courbes-coniques"],
    },
    # ------------------------------------------------------------------ L2
    {
        "title": "Somme de la série de terme général (n + 1)/n!",
        "statement": r"Calculer $\displaystyle\sum_{n=0}^{+\infty} \frac{n + 1}{n!}$.",
        "hints": [
            r"Séparer en $\displaystyle\sum \frac{n}{n!} + \sum \frac{1}{n!}$.",
            r"Pour $n \geq 1$, $\dfrac{n}{n!} = \dfrac{1}{(n-1)!}$ ; et $\displaystyle\sum_{n \geq 0} \frac{1}{n!} = e$.",
        ],
        "final_answer": "2e",
        "difficulty": 1,
        "primary_level": "L2",
        "levels": ["L1", "L2", "MPSI", "MP2I", "MP", "PC", "PSI", "PT"],
        "topics": ["analyse", "series-numeriques"],
        "challenge": {
            "statement": r"Calculer $\displaystyle\sum_{n=0}^{+\infty} \frac{n + {{a}}}{n!}$.",
            "parameters": {"a": [1, 2, 3, 4, 5]},
            "answer": "(1 + a)*e",
        },
    },
    {
        "title": "Convergence simple mais non uniforme de nx e⁻ⁿˣ",
        "former_titles": ["Convergence simple mais non uniforme de n x e^(−nx)"],
        "statement": (
            r"Pour $n \geq 1$ et $x \geq 0$, on pose $f_n(x) = n x e^{-nx}$."
            "\n\n"
            r"1. Étudier la convergence simple de $(f_n)$ sur $[0, +\infty[$."
            "\n"
            r"2. Calculer $\displaystyle\sup_{x \geq 0} f_n(x)$. La convergence est-elle uniforme sur $[0, +\infty[$ ?"
            "\n"
            r"3. Montrer qu'elle est uniforme sur $[a, +\infty[$ pour tout $a > 0$."
        ),
        "hints": [
            r"Étudier les variations de $f_n$ : le maximum est atteint en $x = \dfrac{1}{n}$.",
            r"Pour 3, $f_n$ est décroissante sur $[a, +\infty[$ dès que $\dfrac{1}{n} \leq a$.",
        ],
        "final_answer": "1/e",
        "difficulty": 2,
        "primary_level": "L2",
        "levels": DEUXIEME_ANNEE,
        "topics": ["analyse", "suites-series-fonctions"],
    },
    {
        "title": "Somme des 1/n² par une série de Fourier",
        "statement": (
            r"Soit $f$ la fonction $2\pi$-périodique telle que $f(x) = x^2$ pour $x \in [-\pi, \pi]$."
            "\n\n"
            r"1. Calculer les coefficients de Fourier de $f$."
            "\n"
            r"2. Justifier que la série de Fourier de $f$ converge vers $f$ en tout point."
            "\n"
            r"3. En déduire $\displaystyle\sum_{n=1}^{+\infty} \frac{1}{n^2}$."
        ),
        "hints": [
            r"$f$ est paire : les $b_n$ sont nuls. Deux intégrations par parties donnent $a_n = \dfrac{4(-1)^n}{n^2}$ pour $n \geq 1$.",
            r"$f$ est continue et $C^1$ par morceaux : appliquer le théorème de Dirichlet en $x = \pi$.",
        ],
        "final_answer": "pi^2/6",
        "difficulty": 3,
        "primary_level": "L2",
        "levels": ["L2", "L3", "PSI", "PT"],
        "topics": ["analyse", "series-de-fourier", "series-numeriques"],
    },
    {
        "title": "Série de Leibniz : somme des (−1)ⁿ/(2n + 1)",
        "former_titles": ["Série de Leibniz : somme des (−1)^n/(2n + 1)"],
        "statement": (
            r"1. Pour $N \geq 0$, montrer que $\displaystyle\sum_{n=0}^{N} \frac{(-1)^n}{2n+1} = \int_0^1 \frac{1 - (-t^2)^{N+1}}{1 + t^2}\,\mathrm{d}t$."
            "\n"
            r"2. En déduire la somme $\displaystyle\sum_{n=0}^{+\infty} \frac{(-1)^n}{2n+1}$."
        ),
        "hints": [
            r"$\dfrac{1}{2n+1} = \displaystyle\int_0^1 t^{2n}\,\mathrm{d}t$, puis sommer une suite géométrique.",
            r"Majorer le reste : $\displaystyle\int_0^1 \frac{t^{2N+2}}{1 + t^2}\,\mathrm{d}t \leq \frac{1}{2N+3}$.",
        ],
        "final_answer": "pi/4",
        "difficulty": 2,
        "primary_level": "L2",
        "levels": DEUXIEME_ANNEE,
        "topics": ["analyse", "series-numeriques"],
    },
    {
        "title": "Fonction Gamma : relation fonctionnelle et Γ(5/2)",
        "statement": (
            r"Pour $x > 0$, on pose $\Gamma(x) = \displaystyle\int_0^{+\infty} t^{x-1} e^{-t}\,\mathrm{d}t$."
            "\n\n"
            r"1. Justifier que cette intégrale converge."
            "\n"
            r"2. Montrer que $\Gamma(x + 1) = x\,\Gamma(x)$, puis que $\Gamma(n + 1) = n!$."
            "\n"
            r"3. Sachant que $\displaystyle\int_0^{+\infty} e^{-u^2}\,\mathrm{d}u = \frac{\sqrt{\pi}}{2}$, calculer $\Gamma\left(\frac{1}{2}\right)$ puis $\Gamma\left(\frac{5}{2}\right)$."
        ),
        "hints": [
            r"Pour 1, comparer à $t^{x-1}$ près de $0$ et à $\dfrac{1}{t^2}$ en $+\infty$.",
            r"Pour 3, poser $t = u^2$.",
        ],
        "final_answer": "3*sqrt(pi)/4",
        "difficulty": 2,
        "primary_level": "L2",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "integrales-generalisees"],
    },
    {
        "title": "Un groupe d'ordre premier est cyclique",
        "statement": (
            r"Soit $G$ un groupe fini d'ordre $p$ premier. Montrer que $G$ est cyclique, "
            r"et que tout élément autre que le neutre l'engendre."
        ),
        "hints": [
            r"Prendre $g \neq e$ et considérer le sous-groupe $\langle g \rangle$.",
            "Théorème de Lagrange : l'ordre d'un sous-groupe divise l'ordre du groupe.",
        ],
        "difficulty": 1,
        "primary_level": "L2",
        "levels": ["L2", "L3", "MP", "MP2I", "MPSI"],
        "topics": ["algebre", "groupes-anneaux"],
    },
    # ------------------------------------------------------------------ MP
    {
        "title": "Série de terme général ln(1 + (−1)ⁿ/√n)",
        "former_titles": ["Série de terme général ln(1 + (−1)^n/√n)"],
        "statement": (
            r"Étudier la nature de la série de terme général $u_n = \ln\left(1 + \dfrac{(-1)^n}{\sqrt{n}}\right)$, $n \geq 2$."
            "\n\n"
            r"Pourquoi l'équivalent $u_n \sim \dfrac{(-1)^n}{\sqrt{n}}$ ne suffit-il pas à conclure ?"
        ),
        "hints": [
            r"Développer : $u_n = \dfrac{(-1)^n}{\sqrt{n}} - \dfrac{1}{2n} + O\left(\dfrac{1}{n^{3/2}}\right)$.",
            r"Étudier séparément les trois séries : alternée, harmonique, absolument convergente.",
            "Le critère des équivalents ne vaut que pour des séries de signe constant.",
        ],
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["analyse", "series-numeriques", "developpements-limites"],
    },
    {
        "title": "Somme de la série entière de terme général xⁿ/(n(n + 1))",
        "former_titles": ["Somme de la série entière de terme général x^n/(n(n+1))"],
        "statement": (
            r"1. Déterminer le rayon de convergence de $\displaystyle\sum_{n \geq 1} \frac{x^n}{n(n+1)}$."
            "\n"
            r"2. Calculer sa somme $S(x)$ pour $0 < |x| < 1$."
            "\n"
            r"3. En déduire $S\left(\frac{1}{2}\right)$."
        ),
        "hints": [
            r"Décomposer $\dfrac{1}{n(n+1)} = \dfrac{1}{n} - \dfrac{1}{n+1}$.",
            r"$\displaystyle\sum_{n \geq 1} \frac{x^n}{n} = -\ln(1 - x)$ pour $|x| < 1$.",
        ],
        "final_answer": "1 - ln(2)",
        "difficulty": 2,
        "primary_level": "MP",
        "levels": DEUXIEME_ANNEE,
        "topics": ["analyse", "series-entieres"],
    },
    {
        "title": "Intégrale à paramètre et arctangente",
        "statement": (
            r"Pour $x \in \R$, on pose $F(x) = \displaystyle\int_0^{+\infty} e^{-t} \frac{\sin(xt)}{t}\,\mathrm{d}t$."
            "\n\n"
            r"1. Montrer que $F$ est définie et de classe $C^1$ sur $\R$."
            "\n"
            r"2. Calculer $F'(x)$, puis $F(x)$."
            "\n"
            r"3. En déduire $F(1)$."
        ),
        "hints": [
            r"$|\sin(xt)| \leq |x|t$, et $\left|\dfrac{\partial}{\partial x}\left(e^{-t}\dfrac{\sin(xt)}{t}\right)\right| \leq e^{-t}$ : domination.",
            r"$\displaystyle\int_0^{+\infty} e^{-t}\cos(xt)\,\mathrm{d}t = \frac{1}{1 + x^2}$ (partie réelle de $\int e^{(-1 + ix)t}$).",
        ],
        "final_answer": "pi/4",
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "integrales-a-parametre"],
    },
    {
        "title": "Deux normes non équivalentes sur R[X]",
        "statement": (
            r"Pour $P = \sum_k a_k X^k \in \R[X]$, on pose $N_1(P) = \sum_k |a_k|$ et $N_\infty(P) = \displaystyle\sup_{x \in [0, 1]} |P(x)|$."
            "\n\n"
            r"1. Montrer que $N_1$ et $N_\infty$ sont des normes sur $\R[X]$, et que $N_\infty \leq N_1$."
            "\n"
            r"2. Montrer qu'elles ne sont pas équivalentes."
        ),
        "hints": [
            r"Pour la séparation de $N_\infty$ : un polynôme nul sur $[0, 1]$ a une infinité de racines.",
            r"Considérer $P_n = (1 - X)^n$ : calculer $N_\infty(P_n)$ et $N_1(P_n)$.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP"],
        "topics": ["topologie", "espaces-vectoriels-normes"],
    },
    {
        "title": "La distance à un fermé est atteinte en dimension finie",
        "statement": (
            r"Soit $E$ un espace vectoriel normé de dimension finie, $F$ un fermé non vide de $E$ et $a \in E$."
            "\n\n"
            r"Montrer qu'il existe $y_0 \in F$ tel que $\|a - y_0\| = d(a, F) = \displaystyle\inf_{y \in F} \|a - y\|$."
        ),
        "hints": [
            r"Prendre une suite $(y_n)$ de $F$ telle que $\|a - y_n\| \to d(a, F)$ : elle est bornée.",
            "En dimension finie, une suite bornée admet une sous-suite convergente ; sa limite est dans $F$, fermé.",
        ],
        "difficulty": 2,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["topologie", "espaces-vectoriels-normes"],
    },
    {
        "title": "Nombre moyen de lancers pour obtenir deux 6 consécutifs",
        "statement": (
            "On lance un dé équilibré jusqu'à obtenir deux 6 consécutifs. "
            "Quel est le nombre moyen de lancers ?"
        ),
        "hints": [
            r"Noter $a$ l'espérance du nombre de lancers restants au départ, et $b$ celle juste après un 6.",
            r"Conditionner par le résultat du lancer suivant : $a = 1 + \frac{1}{6}b + \frac{5}{6}a$ et $b = 1 + \frac{5}{6}a$.",
        ],
        "final_answer": "42",
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["probabilites", "variables-aleatoires-discretes", "probabilites-conditionnelles"],
    },
    {
        "title": "Nombre d'inversibles de Z/360Z",
        "statement": (
            r"Combien l'anneau $\Z/360\Z$ compte-t-il d'éléments inversibles ?"
        ),
        "hints": [
            r"$\bar{k}$ est inversible dans $\Z/n\Z$ si et seulement si $\gcd(k, n) = 1$ : on cherche $\varphi(360)$.",
            r"$360 = 2^3 \times 3^2 \times 5$, et $\varphi$ est multiplicative, avec $\varphi(p^k) = p^k - p^{k-1}$.",
        ],
        "final_answer": "96",
        "difficulty": 1,
        "primary_level": "MP",
        "levels": ["L2", "L3", "MP", "MP2I"],
        "topics": ["arithmetique", "congruences", "groupes-anneaux"],
        "challenge": {
            "statement": (
                r"Combien l'anneau $\Z/2^{{{a}}} 3^{{{b}}}\Z$ compte-t-il d'éléments inversibles ?"
            ),
            "parameters": {"a": [2, 3, 4, 5], "b": [1, 2, 3]},
            "answer": "2^a*3^(b - 1)",
        },
    },
    {
        "title": "Suite récurrente u(n+1) = sin(u(n)) : équivalent",
        "statement": (
            r"Soit $u_0 \in \left]0, \pi\right[$ et $u_{n+1} = \sin u_n$."
            "\n\n"
            r"1. Montrer que $(u_n)$ converge vers $0$."
            "\n"
            r"2. Déterminer la limite de $\dfrac{1}{u_{n+1}^2} - \dfrac{1}{u_n^2}$."
            "\n"
            r"3. En déduire $\displaystyle\lim_{n \to +\infty} n u_n^2$."
        ),
        "hints": [
            r"Pour 1, $u_1 \in \left]0, 1\right]$ et $\sin x < x$ pour $x > 0$.",
            r"$\dfrac{1}{\sin^2 x} - \dfrac{1}{x^2} \to \dfrac{1}{3}$ quand $x \to 0$.",
            r"Pour 3, appliquer le théorème de Cesàro ; on en tire $u_n \sim \sqrt{3/n}$.",
        ],
        "final_answer": "3",
        "difficulty": 3,
        "primary_level": "MP",
        "levels": ["L2", "MP", "MPSI", "MP2I", "PSI"],
        "topics": ["analyse", "suites-numeriques", "developpements-limites"],
    },
    # ------------------------------------------------------------------ PC
    {
        "title": "Une matrice 2×2 non diagonalisable et ses puissances",
        "statement": (
            r"Soit $A = \begin{pmatrix} 1 & 1 \\ -1 & 3 \end{pmatrix}$."
            "\n\n"
            r"1. Montrer que $A$ n'est pas diagonalisable."
            "\n"
            r"2. Calculer $A^n$ pour $n \geq 1$ et donner son coefficient en position $(1, 2)$."
        ),
        "hints": [
            r"Le polynôme caractéristique est $(X - 2)^2$, et $A \neq 2I_2$.",
            r"$N = A - 2I_2$ vérifie $N^2 = 0$ : développer $(2I_2 + N)^n$.",
        ],
        "final_answer": "n*2^(n-1)",
        "difficulty": 2,
        "primary_level": "PC",
        "levels": DEUXIEME_ANNEE,
        "topics": ["algebre-lineaire", "reduction"],
    },
    {
        "title": "Problème du collectionneur : compléter une collection de 6 images",
        "statement": (
            "Chaque paquet contient une image prise au hasard parmi 6, de façon uniforme et indépendante. "
            "Combien de paquets faut-il ouvrir en moyenne pour obtenir les 6 images ?"
        ),
        "hints": [
            r"Quand on possède déjà $k$ images, le nombre de paquets pour en obtenir une nouvelle suit une loi géométrique de paramètre $\dfrac{6 - k}{6}$.",
            r"Sommer les espérances : $\displaystyle\sum_{k=0}^{5} \frac{6}{6 - k}$.",
        ],
        "final_answer": "147/10",
        "difficulty": 2,
        "primary_level": "PC",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["probabilites", "variables-aleatoires-discretes"],
    },
    {
        "title": "Covariance nulle sans indépendance",
        "statement": (
            r"Soit $X$ une variable aléatoire de loi uniforme sur $\{-1, 0, 1\}$, et $Y = X^2$."
            "\n\n"
            r"1. Calculer $\operatorname{Cov}(X, Y)$."
            "\n"
            r"2. $X$ et $Y$ sont-elles indépendantes ?"
        ),
        "hints": [
            r"$\operatorname{Cov}(X, Y) = E(XY) - E(X)E(Y)$, avec $XY = X^3$.",
            r"Comparer $P(X = 0, Y = 1)$ et $P(X = 0)P(Y = 1)$.",
        ],
        "difficulty": 1,
        "primary_level": "PC",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["probabilites", "variables-aleatoires-discretes"],
    },
    {
        "title": "Intégrale de 1/(1 + x³) sur [0, +∞[",
        "statement": r"Justifier la convergence de $\displaystyle\int_0^{+\infty} \frac{\mathrm{d}x}{1 + x^3}$ et la calculer.",
        "hints": [
            r"Le changement de variable $x = \dfrac{1}{u}$ montre que l'intégrale vaut aussi $\displaystyle\int_0^{+\infty} \frac{x\,\mathrm{d}x}{1 + x^3}$.",
            r"Faire la demi-somme : $\dfrac{1 + x}{1 + x^3} = \dfrac{1}{x^2 - x + 1}$.",
        ],
        "final_answer": "2*pi/(3*sqrt(3))",
        "difficulty": 3,
        "primary_level": "PC",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["analyse", "integrales-generalisees"],
    },
    {
        "title": "Diagonalisation d'une matrice 3×3 avec une valeur propre double",
        "statement": (
            r"Soit $A = \begin{pmatrix} 0 & 1 & 1 \\ -1 & 2 & 1 \\ -1 & 1 & 2 \end{pmatrix}$."
            "\n\n"
            r"1. Déterminer les valeurs propres de $A$ et une base de chaque sous-espace propre."
            "\n"
            r"2. En déduire que $A$ est diagonalisable, puis calculer $\operatorname{tr}(A^n)$."
        ),
        "hints": [
            r"Le polynôme caractéristique est $(X - 1)^2 (X - 2)$.",
            r"$A - I_3$ est de rang $1$ : le sous-espace propre de $1$ est de dimension $2$.",
        ],
        "final_answer": "2^n + 2",
        "difficulty": 2,
        "primary_level": "PC",
        "levels": DEUXIEME_ANNEE,
        "topics": ["algebre-lineaire", "reduction"],
    },
    # ------------------------------------------------------------------ PSI
    {
        "title": "Un projecteur est diagonalisable et son rang est sa trace",
        "statement": (
            r"Soit $A \in M_n(\R)$ telle que $A^2 = A$."
            "\n\n"
            r"1. Montrer que $A$ est diagonalisable et que ses valeurs propres sont dans $\{0, 1\}$."
            "\n"
            r"2. En déduire que $\operatorname{rg}(A) = \operatorname{tr}(A)$."
        ),
        "hints": [
            r"$X^2 - X = X(X - 1)$ est un polynôme annulateur scindé à racines simples.",
            r"Dans une base de diagonalisation, $A$ est semblable à $\operatorname{diag}(1, \dots, 1, 0, \dots, 0)$.",
        ],
        "difficulty": 2,
        "primary_level": "PSI",
        "levels": DEUXIEME_ANNEE,
        "topics": ["algebre-lineaire", "reduction"],
    },
    {
        "title": "Rayon de convergence d'une série entière lacunaire",
        "statement": (
            r"Déterminer le rayon de convergence de la série entière $\displaystyle\sum_{n \geq 0} \frac{n^2 + 1}{3^n} x^{2n}$."
        ),
        "hints": [
            r"La règle de d'Alembert pour les séries entières ne s'applique pas directement : un coefficient sur deux est nul.",
            r"Appliquer la règle de d'Alembert à la série numérique $\sum \dfrac{n^2 + 1}{3^n} |x|^{2n}$ pour $x$ fixé.",
        ],
        "final_answer": "sqrt(3)",
        "difficulty": 2,
        "primary_level": "PSI",
        "levels": DEUXIEME_ANNEE,
        "topics": ["analyse", "series-entieres"],
        "challenge": {
            "statement": (
                r"Déterminer le rayon de convergence de $\displaystyle\sum_{n \geq 0} \frac{n^2 + 1}{{{a}}^n} x^{2n}$."
            ),
            "parameters": {"a": [2, 3, 5, 7]},
            "answer": "sqrt(a)",
        },
    },
    {
        "title": "Intégrale de Gauss par la méthode de l'intégrale à paramètre",
        "statement": (
            r"Pour $x \in \R$, on pose $F(x) = \displaystyle\int_0^1 \frac{e^{-x^2(1 + t^2)}}{1 + t^2}\,\mathrm{d}t$ "
            r"et $G(x) = \left(\displaystyle\int_0^x e^{-t^2}\,\mathrm{d}t\right)^2$."
            "\n\n"
            r"1. Montrer que $F + G$ est constante sur $\R$, égale à $\dfrac{\pi}{4}$."
            "\n"
            r"2. En déduire la valeur de $\displaystyle\int_0^{+\infty} e^{-t^2}\,\mathrm{d}t$."
        ),
        "hints": [
            r"Dériver $F$ sous l'intégrale, puis poser $u = xt$ dans l'expression obtenue.",
            r"$F(0) = \dfrac{\pi}{4}$, et $|F(x)| \leq e^{-x^2}$ tend vers $0$.",
        ],
        "final_answer": "sqrt(pi)/2",
        "difficulty": 3,
        "primary_level": "PSI",
        "levels": ["L2", "L3", "MP", "PSI", "PC"],
        "topics": ["analyse", "integrales-a-parametre", "integrales-generalisees"],
    },
    {
        "title": "Somme de trois dés et fonction génératrice",
        "statement": (
            "On lance trois dés équilibrés indépendants. À l'aide d'une fonction génératrice, "
            "calculer la probabilité que la somme des trois faces vaille 10."
        ),
        "hints": [
            r"La fonction génératrice de la somme est $\left(\dfrac{t + t^2 + \dots + t^6}{6}\right)^3 = \dfrac{t^3}{216}\left(\dfrac{1 - t^6}{1 - t}\right)^3$.",
            r"On cherche le coefficient de $t^7$ dans $\left(\dfrac{1 - t^6}{1 - t}\right)^3$.",
        ],
        "final_answer": "1/8",
        "difficulty": 2,
        "primary_level": "PSI",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["probabilites", "variables-aleatoires-discretes"],
    },
    {
        "title": "Matrices symétriques et antisymétriques sont orthogonales",
        "statement": (
            r"On munit $M_n(\R)$ du produit scalaire $(A \mid B) = \operatorname{tr}(A^\top B)$."
            "\n\n"
            r"1. Montrer que les sous-espaces $S_n(\R)$ et $A_n(\R)$ des matrices symétriques et antisymétriques sont orthogonaux et supplémentaires."
            "\n"
            r"2. En déduire la distance de $M = \begin{pmatrix} 1 & 2 \\ 0 & 3 \end{pmatrix}$ à $S_2(\R)$."
        ),
        "hints": [
            r"Pour $S$ symétrique et $A$ antisymétrique, $\operatorname{tr}(SA) = \operatorname{tr}((SA)^\top) = -\operatorname{tr}(AS)$.",
            r"Le projeté orthogonal de $M$ sur $S_n(\R)$ est $\dfrac{M + M^\top}{2}$.",
        ],
        "final_answer": "sqrt(2)",
        "difficulty": 1,
        "primary_level": "PSI",
        "levels": DEUXIEME_ANNEE,
        "topics": ["algebre-lineaire", "espaces-euclidiens"],
    },
    {
        "title": "Équation d'Euler x²y'' + xy' − y = 0",
        "statement": (
            r"Résoudre sur $]0, +\infty[$ l'équation $x^2 y'' + x y' - y = 0$ avec $y(1) = 2$ et $y'(1) = 0$, "
            r"puis calculer $y(2)$."
        ),
        "hints": [
            r"Chercher des solutions de la forme $x \mapsto x^r$.",
            r"Autre méthode : poser $x = e^s$ et $z(s) = y(e^s)$ pour se ramener à des coefficients constants.",
        ],
        "final_answer": "5/2",
        "difficulty": 2,
        "primary_level": "PSI",
        "levels": DEUXIEME_ANNEE,
        "topics": ["analyse", "equations-differentielles"],
    },
    # ------------------------------------------------------------------ PT
    {
        "title": "Système différentiel linéaire à coefficients constants",
        "statement": (
            r"Résoudre le système $x' = x + 2y$, $y' = 2x + y$ avec $x(0) = 1$ et $y(0) = 0$, "
            r"puis calculer $x(\ln 2)$."
        ),
        "hints": [
            r"Diagonaliser $\begin{pmatrix} 1 & 2 \\ 2 & 1 \end{pmatrix}$ : valeurs propres $3$ et $-1$.",
            r"Plus directement : $u = x + y$ et $v = x - y$ vérifient $u' = 3u$ et $v' = -v$.",
        ],
        "final_answer": "17/4",
        "difficulty": 2,
        "primary_level": "PT",
        "levels": DEUXIEME_ANNEE,
        "topics": ["analyse", "equations-differentielles", "reduction"],
    },
    {
        "title": "Extremums de f(x, y) = x³ + y³ − 3xy",
        "statement": (
            r"Soit $f(x, y) = x^3 + y^3 - 3xy$ sur $\R^2$."
            "\n\n"
            r"1. Déterminer les points critiques de $f$."
            "\n"
            r"2. Étudier la nature de chacun et donner la valeur du minimum local."
            "\n"
            r"3. Ce minimum est-il global ?"
        ),
        "hints": [
            r"Points critiques : $x^2 = y$ et $y^2 = x$, d'où $(0, 0)$ et $(1, 1)$.",
            r"Utiliser la hessienne, ou étudier $f(x, x)$ et $f(x, -x)$ près de $(0, 0)$.",
            r"Pour 3, regarder $f(x, 0)$ quand $x \to -\infty$.",
        ],
        "final_answer": "-1",
        "difficulty": 2,
        "primary_level": "PT",
        "levels": DEUXIEME_ANNEE,
        "topics": ["analyse", "fonctions-plusieurs-variables"],
    },
    {
        "title": "Aire d'une ellipse par la formule de Green-Riemann",
        "statement": (
            r"À l'aide de la formule de Green-Riemann, calculer l'aire du domaine limité par l'ellipse "
            r"$\dfrac{x^2}{3^2} + \dfrac{y^2}{2^2} = 1$."
        ),
        "hints": [
            r"L'aire d'un domaine $D$ vaut $\dfrac{1}{2}\displaystyle\oint_{\partial D} (x\,\mathrm{d}y - y\,\mathrm{d}x)$.",
            r"Paramétrer le bord par $x = 3\cos t$, $y = 2\sin t$, $t \in [0, 2\pi]$.",
        ],
        "final_answer": "6pi",
        "difficulty": 2,
        "primary_level": "PT",
        "levels": ["L2", "PT", "PSI", "PC"],
        "topics": ["geometrie", "courbes-coniques"],
        "challenge": {
            "statement": (
                r"Calculer l'aire du domaine limité par l'ellipse $\dfrac{x^2}{{{a}}^2} + \dfrac{y^2}{{{b}}^2} = 1$."
            ),
            "parameters": {"a": [2, 3, 4, 5], "b": [1, 2, 3]},
            "answer": "pi*a*b",
        },
    },
    {
        "title": "Absence de mémoire de la loi géométrique",
        "statement": (
            r"Soit $X$ une variable aléatoire de loi géométrique de paramètre $p \in \left]0, 1\right[$."
            "\n\n"
            r"1. Calculer $P(X > n)$ pour $n \in \N$."
            "\n"
            r"2. Montrer que $P(X > n + k \mid X > n) = P(X > k)$ pour tous $n, k \in \N$."
        ),
        "hints": [
            r"$P(X > n) = \displaystyle\sum_{j > n} p(1 - p)^{j-1}$, ou bien : les $n$ premières épreuves sont des échecs.",
            r"$\{X > n + k\} \subset \{X > n\}$.",
        ],
        "difficulty": 1,
        "primary_level": "PT",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["probabilites", "variables-aleatoires-discretes", "probabilites-conditionnelles"],
    },
    {
        "title": "Espérance et variance d'une loi binomiale par la fonction génératrice",
        "statement": (
            r"Soit $X$ de loi binomiale $\mathcal{B}(n, p)$."
            "\n\n"
            r"1. Calculer sa fonction génératrice $G_X(t) = E(t^X)$."
            "\n"
            r"2. En déduire $E(X)$ et $V(X)$."
        ),
        "hints": [
            r"Formule du binôme : $G_X(t) = (1 - p + pt)^n$.",
            r"$E(X) = G_X'(1)$ et $V(X) = G_X''(1) + G_X'(1) - G_X'(1)^2$.",
        ],
        "final_answer": "n*p*(1 - p)",
        "difficulty": 1,
        "primary_level": "PT",
        "levels": ["L2", "MP", "PC", "PSI", "PT"],
        "topics": ["probabilites", "variables-aleatoires-discretes"],
    },
    {
        "title": "Maximum d'une forme quadratique sur le cercle unité",
        "statement": (
            r"1. Soit $A \in S_n(\R)$ de valeurs propres $\lambda_1 \leq \dots \leq \lambda_n$. "
            r"Montrer que $\lambda_1 \|X\|^2 \leq X^\top A X \leq \lambda_n \|X\|^2$ pour tout $X \in \R^n$."
            "\n"
            r"2. En déduire le maximum de $2x^2 + 2xy + 2y^2$ sur le cercle $x^2 + y^2 = 1$."
        ),
        "hints": [
            r"Théorème spectral : écrire $X$ dans une base orthonormée de vecteurs propres de $A$.",
            r"La forme s'écrit $X^\top A X$ avec $A = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}$.",
        ],
        "final_answer": "3",
        "difficulty": 2,
        "primary_level": "PT",
        "levels": DEUXIEME_ANNEE,
        "topics": ["algebre-lineaire", "espaces-euclidiens", "reduction"],
    },
    # ------------------------------------------------------------------ L3
    {
        "title": "Convergence dominée : limite de l'intégrale de (1 − x/n)ⁿ exp(x/2)",
        "former_titles": ["Convergence dominée : limite de l'intégrale de (1 − x/n)^n e^(x/2)"],
        "statement": (
            r"Déterminer $\displaystyle\lim_{n \to +\infty} \int_0^n \left(1 - \frac{x}{n}\right)^n e^{x/2}\,\mathrm{d}x$."
        ),
        "hints": [
            r"Écrire l'intégrale sur $[0, +\infty[$ avec l'indicatrice de $[0, n]$.",
            r"Pour $0 \leq x \leq n$, $\ln\left(1 - \frac{x}{n}\right) \leq -\frac{x}{n}$, donc $\left(1 - \frac{x}{n}\right)^n \leq e^{-x}$ : domination par $e^{-x/2}$.",
        ],
        "final_answer": "2",
        "difficulty": 2,
        "primary_level": "L3",
        "levels": ["L3", "M1", "MP", "PSI"],
        "topics": ["analyse", "integration-lebesgue"],
    },
    {
        "title": "Intégrale de ln x/(1 + x) sur [0, 1]",
        "statement": (
            r"Montrer que $\displaystyle\int_0^1 \frac{\ln x}{1 + x}\,\mathrm{d}x = \sum_{n=0}^{+\infty} \frac{(-1)^{n+1}}{(n+1)^2}$, "
            r"puis calculer cette intégrale, sachant que $\displaystyle\sum_{n \geq 1} \frac{1}{n^2} = \frac{\pi^2}{6}$."
        ),
        "hints": [
            r"Développer $\dfrac{1}{1 + x} = \sum_{n \geq 0} (-1)^n x^n$ et intégrer terme à terme, en justifiant l'échange.",
            r"$\displaystyle\int_0^1 x^n \ln x\,\mathrm{d}x = -\frac{1}{(n+1)^2}$.",
            r"$\displaystyle\sum_{n \geq 1} \frac{(-1)^{n+1}}{n^2} = \frac{\pi^2}{12}$ : séparer termes pairs et impairs.",
        ],
        "final_answer": "-pi^2/12",
        "difficulty": 3,
        "primary_level": "L3",
        "levels": ["L2", "L3", "MP", "PSI"],
        "topics": ["analyse", "integration-lebesgue", "series-numeriques"],
    },
    {
        "title": "Éléments d'ordre 2 du groupe symétrique S4",
        "statement": (
            r"Combien le groupe symétrique $\mathfrak{S}_4$ compte-t-il d'éléments d'ordre $2$ ?"
        ),
        "hints": [
            "L'ordre d'une permutation est le PPCM des longueurs des cycles de sa décomposition.",
            "Les éléments d'ordre 2 sont les transpositions et les produits de deux transpositions à supports disjoints.",
        ],
        "final_answer": "9",
        "difficulty": 2,
        "primary_level": "L3",
        "levels": ["L2", "L3", "MP", "MP2I"],
        "topics": ["algebre", "groupes-anneaux"],
    },
    {
        "title": "Transformée de Fourier de la gaussienne par une équation différentielle",
        "statement": (
            r"Soit $f(x) = e^{-x^2}$ et $\hat{f}(\xi) = \displaystyle\int_{\R} f(x) e^{-ix\xi}\,\mathrm{d}x$."
            "\n\n"
            r"1. Montrer que $\hat{f}$ est dérivable et que $\hat{f}'(\xi) = -\dfrac{\xi}{2}\hat{f}(\xi)$."
            "\n"
            r"2. En déduire $\hat{f}(\xi)$, sachant que $\displaystyle\int_{\R} e^{-x^2}\,\mathrm{d}x = \sqrt{\pi}$, puis $\hat{f}(2)$."
        ),
        "hints": [
            r"Dériver sous l'intégrale (domination par $|x|e^{-x^2}$), puis intégrer par parties avec $-2xe^{-x^2} = f'(x)$.",
            r"Résoudre l'équation différentielle linéaire avec $\hat{f}(0) = \sqrt{\pi}$.",
        ],
        "final_answer": "sqrt(pi)/e",
        "difficulty": 2,
        "primary_level": "L3",
        "levels": ["L3", "M1"],
        "topics": ["analyse", "integrales-a-parametre"],
    },
    # ------------------------------------------------------------------ M1
    {
        "title": "Une isométrie d'un compact dans lui-même est surjective",
        "statement": (
            r"Soit $(K, d)$ un espace métrique compact et $f : K \to K$ telle que $d(f(x), f(y)) = d(x, y)$ pour tous $x, y$."
            "\n\n"
            r"Montrer que $f$ est surjective."
        ),
        "hints": [
            r"Par l'absurde : si $a \notin f(K)$, alors $\varepsilon = d(a, f(K)) > 0$ car $f(K)$ est compact.",
            r"Considérer la suite $a_n = f^n(a)$ et montrer que $d(a_n, a_m) \geq \varepsilon$ pour $n \neq m$.",
            "Une telle suite n'a aucune sous-suite convergente.",
        ],
        "difficulty": 4,
        "primary_level": "M1",
        "levels": ["L3", "M1"],
        "topics": ["topologie", "espaces-metriques"],
    },
    {
        "title": "L'opérateur de Volterra n'a aucune valeur propre",
        "statement": (
            r"Sur $E = C([0, 1], \R)$ muni de la norme uniforme, on définit $V(f)(x) = \displaystyle\int_0^x f(t)\,\mathrm{d}t$."
            "\n\n"
            r"1. Montrer que $V$ est un endomorphisme continu de $E$ et qu'il n'a aucune valeur propre."
            "\n"
            r"2. Montrer que $|V^n(f)(x)| \leq \dfrac{x^n}{n!}\|f\|_\infty$, puis que $\|V^n\|^{1/n} \to 0$."
        ),
        "hints": [
            r"Si $V(f) = \lambda f$ avec $\lambda \neq 0$, alors $f$ est $C^1$, $f' = \dfrac{f}{\lambda}$ et $f(0) = 0$.",
            r"Le cas $\lambda = 0$ se traite en dérivant $\displaystyle\int_0^x f = 0$.",
            "Pour 2, raisonner par récurrence sur $n$.",
        ],
        "difficulty": 3,
        "primary_level": "M1",
        "levels": ["L3", "M1"],
        "topics": ["analyse", "analyse-fonctionnelle"],
    },
    {
        "title": "Minimum de n variables uniformes : convergence en loi",
        "statement": (
            r"Soit $(U_k)$ une suite de variables indépendantes de loi uniforme sur $[0, 1]$, "
            r"et $M_n = \min(U_1, \dots, U_n)$."
            "\n\n"
            r"1. Calculer $P(n M_n > x)$ pour $x \geq 0$."
            "\n"
            r"2. Montrer que $n M_n$ converge en loi vers une loi exponentielle, et donner $\displaystyle\lim_{n \to +\infty} P(n M_n > 1)$."
        ),
        "hints": [
            r"$\{M_n > y\} = \bigcap_k \{U_k > y\}$, donc $P(M_n > y) = (1 - y)^n$ pour $y \in [0, 1]$.",
            r"$\left(1 - \dfrac{x}{n}\right)^n \to e^{-x}$.",
        ],
        "final_answer": "1/e",
        "difficulty": 2,
        "primary_level": "M1",
        "levels": ["L3", "M1"],
        "topics": ["probabilites", "theoremes-limites"],
    },
    {
        "title": "Processus de Poisson : nombre d'arrivées sur un intervalle",
        "statement": (
            r"Des clients arrivent selon un processus de Poisson d'intensité $1$ par minute : "
            r"le nombre d'arrivées sur un intervalle de durée $t$ suit une loi de Poisson de paramètre $t$, "
            "et les nombres d'arrivées sur des intervalles disjoints sont indépendants."
            "\n\n"
            r"1. Calculer la probabilité qu'exactement 3 clients arrivent en 2 minutes."
            "\n"
            r"2. Sachant que 3 clients sont arrivés en 2 minutes, quelle est la probabilité qu'aucun ne soit arrivé pendant la première minute ?"
        ),
        "hints": [
            r"$P(N = k) = e^{-t}\dfrac{t^k}{k!}$ pour une loi de Poisson de paramètre $t$.",
            r"Pour 2, écrire $N_2 = N_1 + (N_2 - N_1)$ avec deux termes indépendants de loi $\mathcal{P}(1)$.",
        ],
        "final_answer": "1/8",
        "difficulty": 1,
        "primary_level": "M1",
        "levels": ["L3", "M1"],
        "topics": ["probabilites", "marches-aleatoires"],
    },
    # ------------------------------------------------------------------ M2
    {
        "title": "Dérivées de la valeur absolue au sens des distributions",
        "statement": (
            r"Soit $T$ la distribution sur $\R$ associée à la fonction $x \mapsto |x|$."
            "\n\n"
            r"Calculer $T'$ et $T''$ au sens des distributions."
        ),
        "hints": [
            r"Pour $\varphi \in C_c^\infty(\R)$, $\langle T', \varphi \rangle = -\displaystyle\int_{\R} |x| \varphi'(x)\,\mathrm{d}x$ : couper en $0$ et intégrer par parties.",
            r"On trouve $T' = \operatorname{sgn}$, puis $T'' = 2\delta_0$.",
        ],
        "difficulty": 2,
        "primary_level": "M2",
        "levels": ["L3", "M1", "M2"],
        "topics": ["analyse", "analyse-fonctionnelle"],
    },
    {
        "title": "Inégalité de Poincaré sur ]0, 1[ et sa constante optimale",
        "statement": (
            r"Soit $u \in C^1([0, 1])$ telle que $u(0) = u(1) = 0$."
            "\n\n"
            r"1. Montrer que $\displaystyle\int_0^1 u^2 \leq \frac{1}{2} \int_0^1 u'^2$."
            "\n"
            r"2. À l'aide du développement de $u$ en série de sinus $u(x) = \sum_{k \geq 1} b_k \sin(k\pi x)$, "
            r"déterminer la meilleure constante $C$ telle que $\displaystyle\int_0^1 u^2 \leq C \int_0^1 u'^2$ pour toute telle fonction $u$."
        ),
        "hints": [
            r"Pour 1, $u(x) = \displaystyle\int_0^x u'$, puis l'inégalité de Cauchy-Schwarz : $u(x)^2 \leq x \int_0^1 u'^2$.",
            r"Pour 2, Parseval : $\displaystyle\int_0^1 u^2 = \frac{1}{2}\sum b_k^2$ et $\displaystyle\int_0^1 u'^2 = \frac{1}{2}\sum k^2 \pi^2 b_k^2$.",
            r"Regarder $u(x) = \sin(\pi x)$.",
        ],
        "final_answer": "1/pi^2",
        "difficulty": 3,
        "primary_level": "M2",
        "levels": ["L3", "M1", "M2"],
        "topics": ["analyse", "analyse-fonctionnelle", "series-de-fourier"],
    },
]
