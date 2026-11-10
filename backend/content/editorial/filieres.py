"""Exercices de la rédaction qui conviennent aussi aux prépas BCPST, ECG et B/L.

Triés à la main, énoncé par énoncé, d'après les programmes de ces filières : pas de nombres
complexes ni d'équations différentielles en ECG et en B/L, pas de géométrie euclidienne hors
BCPST, pas de fonctions génératrices ni de déterminants. Dans le doute, l'exercice n'y est pas.
Les exercices de MP vont aussi en MPI, dont le programme de mathématiques est le même.
"""

FILIERES = {
    "BCPST1": [
        'Limite de $\\sin(3x)/(2x)$ en 0',
        'Somme des cubes des $n$ premiers entiers, par récurrence',
        "Injectivité d'une composée $g \\circ f$",
        'Puissances de la matrice $I + J$, $J$ remplie de 1',
        'Formule du binôme : somme des $\\binom{5}{k} 2^k$',
        'Suite récurrente $u_{n+1} = \\sqrt{2 + u_n}$ : convergence et limite',
        'Intégrales de Wallis : relation de récurrence et valeur de $W_4$',
        'Nombre de surjections de $\\{1, \\dots, n\\}$ sur $\\{1, 2\\}$',
        'Module du nombre complexe $(1 + i\\sqrt{3})^5$',
        "Équation différentielle $y'' - 3y' + 2y = 0$ avec conditions initiales",
        'Aire entre les courbes $y = x^2$ et $y = \\sqrt{x}$',
        'Distance du point $A(1, 2)$ à la droite $3x + 4y = 0$',
        "Équation différentielle $y' + 2y = 0$ avec condition initiale",
        "Équation différentielle $y' + y = x e^{-x}$",
        "Forme exponentielle d'un quotient de nombres complexes",
        'Intégrale de $x e^{2x}$ par intégration par parties',
        "Point fixe d'une fonction continue de $[0, 1]$ dans lui-même",
        "Linéarisation de $\\sin^3 x$ par les formules d'Euler",
        'Somme $\\arctan x + \\arctan(1/x)$',
        'Calcul de $\\arctan(1/2) + \\arctan(1/3)$',
        'Nombre de chemins monotones dans une grille',
        "Nombre d'anagrammes du mot MISSISSIPPI",
        "Équation différentielle $y' + 2xy = 2x$",
        "Formule de Bayes : fiabilité d'un test de dépistage",
        'Encadrement de $\\ln(1 + x)$ par les accroissements finis',
        'Somme des $k \\binom{n}{k}$',
        'Somme télescopique de $1/(k(k+1)(k+2))$',
        "Équation différentielle à racine double $y'' + 2y' + y = 0$",
        "Noyau et image d'une application linéaire de $\\R^3$",
        "Rang d'une matrice selon un paramètre",
        "Puissance $n$-ième d'une matrice par la formule du binôme",
        "Projeté orthogonal et symétrique d'un point par rapport à un plan",
    ],
    "BCPST2": [
        'Somme de la série de terme général $n/2^n$',
        "Diagonalisation d'une matrice symétrique et trace de $A^{10}$",
        'Minimum de $f(x, y) = x^2 + xy + y^2 - 3x$',
        "Moment d'ordre 2 d'une loi géométrique : calcul de $E(X^2)$",
        'Somme de deux lois de Poisson indépendantes',
        'Inégalité de Bienaymé-Tchebychev : combien de lancers pour estimer une proportion',
        'Intégrale de $x^2 \\ln x$ sur $]0, 1]$',
        'Somme de la série de terme général $(n + 1)/n!$',
        'Une matrice $2 \\times 2$ non diagonalisable et ses puissances',
        'Problème du collectionneur : compléter une collection de 6 images',
        'Covariance nulle sans indépendance',
        "Diagonalisation d'une matrice $3 \\times 3$ avec une valeur propre double",
        'Absence de mémoire de la loi géométrique',
    ],
    "ECG1": [
        'Somme des cubes des $n$ premiers entiers, par récurrence',
        "Injectivité d'une composée $g \\circ f$",
        'Partie entière : $\\lfloor 2x \\rfloor = \\lfloor x \\rfloor + \\lfloor x + 1/2 \\rfloor$',
        'Somme de la série de terme général $n/2^n$',
        'Noyau, image et rang de la dérivation sur $\\R_n[X]$',
        'Puissances de la matrice $I + J$, $J$ remplie de 1',
        'Formule du binôme : somme des $\\binom{5}{k} 2^k$',
        'Suite récurrente $u_{n+1} = \\sqrt{2 + u_n}$ : convergence et limite',
        'Nombre de surjections de $\\{1, \\dots, n\\}$ sur $\\{1, 2\\}$',
        'Aire entre les courbes $y = x^2$ et $y = \\sqrt{x}$',
        'Méthode de Héron pour approcher $\\sqrt{2}$',
        'Intégrale de $x e^{2x}$ par intégration par parties',
        'Polynôme ayant 1 pour racine double',
        'Dérivée $n$-ième par la formule de Leibniz',
        "Point fixe d'une fonction continue de $[0, 1]$ dans lui-même",
        'Image réciproque, image directe et intersection',
        'Nombre de chemins monotones dans une grille',
        "Nombre d'anagrammes du mot MISSISSIPPI",
        "Formule de Bayes : fiabilité d'un test de dépistage",
        'Encadrement de $\\ln(1 + x)$ par les accroissements finis',
        'Somme des $k \\binom{n}{k}$',
        'Somme télescopique de $1/(k(k+1)(k+2))$',
        'Vitesse de convergence de $(1 + 1/n)^n$ vers $e$',
        "Noyau et image d'une application linéaire de $\\R^3$",
        "Rang d'une matrice selon un paramètre",
        "Puissance $n$-ième d'une matrice par la formule du binôme",
        'Somme de la série de terme général $(n + 1)/n!$',
    ],
    "ECG2": [
        "Inverse d'une matrice par un polynôme annulateur",
        'Meilleure approximation affine de $x^2$ dans $L^2$, par projection orthogonale',
        "Diagonalisation d'une matrice symétrique et trace de $A^{10}$",
        'Minimum de $f(x, y) = x^2 + xy + y^2 - 3x$',
        "Moment d'ordre 2 d'une loi géométrique : calcul de $E(X^2)$",
        'Somme de deux lois de Poisson indépendantes',
        'Inégalité de Bienaymé-Tchebychev : combien de lancers pour estimer une proportion',
        "Commutant d'une matrice diagonale à coefficients distincts",
        'Intégrale de $x^2 \\ln x$ sur $]0, 1]$',
        'Fonction Gamma : relation fonctionnelle et $\\Gamma(5/2)$',
        'Nombre moyen de lancers pour obtenir deux 6 consécutifs',
        'Une matrice $2 \\times 2$ non diagonalisable et ses puissances',
        'Problème du collectionneur : compléter une collection de 6 images',
        'Covariance nulle sans indépendance',
        "Diagonalisation d'une matrice $3 \\times 3$ avec une valeur propre double",
        'Un projecteur est diagonalisable et son rang est sa trace',
        'Matrices symétriques et antisymétriques sont orthogonales',
        'Extremums de $f(x, y) = x^3 + y^3 - 3xy$',
        'Absence de mémoire de la loi géométrique',
        "Maximum d'une forme quadratique sur le cercle unité",
    ],
    "BL1": [
        'Somme des cubes des $n$ premiers entiers, par récurrence',
        "Injectivité d'une composée $g \\circ f$",
        'Puissances de la matrice $I + J$, $J$ remplie de 1',
        'Formule du binôme : somme des $\\binom{5}{k} 2^k$',
        'Suite récurrente $u_{n+1} = \\sqrt{2 + u_n}$ : convergence et limite',
        'Nombre de surjections de $\\{1, \\dots, n\\}$ sur $\\{1, 2\\}$',
        'Aire entre les courbes $y = x^2$ et $y = \\sqrt{x}$',
        'Intégrale de $x e^{2x}$ par intégration par parties',
        "Point fixe d'une fonction continue de $[0, 1]$ dans lui-même",
        'Image réciproque, image directe et intersection',
        'Nombre de chemins monotones dans une grille',
        "Nombre d'anagrammes du mot MISSISSIPPI",
        "Formule de Bayes : fiabilité d'un test de dépistage",
        'Encadrement de $\\ln(1 + x)$ par les accroissements finis',
        'Somme des $k \\binom{n}{k}$',
        'Somme télescopique de $1/(k(k+1)(k+2))$',
        "Noyau et image d'une application linéaire de $\\R^3$",
        "Puissance $n$-ième d'une matrice par la formule du binôme",
    ],
    "BL2": [
        'Somme de la série de terme général $n/2^n$',
        'Minimum de $f(x, y) = x^2 + xy + y^2 - 3x$',
        "Moment d'ordre 2 d'une loi géométrique : calcul de $E(X^2)$",
        'Somme de deux lois de Poisson indépendantes',
        'Inégalité de Bienaymé-Tchebychev : combien de lancers pour estimer une proportion',
        'Intégrale de $x^2 \\ln x$ sur $]0, 1]$',
        'Somme de la série de terme général $(n + 1)/n!$',
        'Une matrice $2 \\times 2$ non diagonalisable et ses puissances',
        'Problème du collectionneur : compléter une collection de 6 images',
        'Covariance nulle sans indépendance',
        "Diagonalisation d'une matrice $3 \\times 3$ avec une valeur propre double",
        'Absence de mémoire de la loi géométrique',
    ],
}


def with_filieres(specs):
    """Les exercices, avec les niveaux des filières ajoutés à leur liste `levels`."""
    extra = {}
    for code, titles in FILIERES.items():
        for title in titles:
            extra.setdefault(title, []).append(code)
    known = {spec["title"] for spec in specs}
    unknown = sorted(set(extra) - known)
    if unknown:
        raise ValueError(f"Filières : titres inconnus de la rédaction : {unknown}")
    result = []
    for spec in specs:
        added = list(extra.get(spec["title"], []))
        if "MP" in spec["levels"]:
            added.append("MPI")
        levels = spec["levels"] + [code for code in added if code not in spec["levels"]]
        result.append({**spec, "levels": levels})
    return result
