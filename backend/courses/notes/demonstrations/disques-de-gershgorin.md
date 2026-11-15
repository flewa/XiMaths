---
titre: Théorème des disques de Gershgorin
programmes: MP, MPI, L2
statut: hors-programme
ordre: 16
notion: reduction
---

## Énoncé

> **Théorème (Gershgorin).** Soit $A = (a_{ij}) \in \mathcal{M}_n(\C)$. Pour $i \in [\![1, n]\!]$, on pose $R_i = \sum_{j \neq i} |a_{ij}|$. Toute valeur propre complexe de $A$ appartient à la réunion des disques fermés
>
> $$
> \bigcup_{i=1}^{n} \overline{D}(a_{ii}, R_i), \qquad \text{où} \quad \overline{D}(a_{ii}, R_i) = \{ z \in \C : |z - a_{ii}| \leq R_i \}.
> $$

## Idée

Dans l'équation $AX = \lambda X$, on regarde la ligne correspondant à la plus grande coordonnée de $X$ en module : l'inégalité triangulaire suffit.

## Démonstration

Soit $\lambda$ une valeur propre de $A$ et $X = (x_1, \dots, x_n)^\top \in \C^n$ un vecteur propre associé, non nul. Choisissons un indice $i$ tel que $|x_i| = \max_{j} |x_j|$ ; comme $X \neq 0$, on a $|x_i| > 0$.

La $i$-ième ligne de l'égalité $AX = \lambda X$ s'écrit $\sum_{j=1}^{n} a_{ij} x_j = \lambda x_i$, c'est-à-dire

$$
(\lambda - a_{ii}) \, x_i = \sum_{j \neq i} a_{ij} x_j.
$$

Par l'inégalité triangulaire, et puisque $|x_j| \leq |x_i|$ pour tout $j$ :

$$
\lvert \lambda - a_{ii} \rvert \, |x_i| \leq \sum_{j \neq i} |a_{ij}| \, |x_j| \leq \left( \sum_{j \neq i} |a_{ij}| \right) |x_i| = R_i |x_i|.
$$

En divisant par $|x_i| > 0$, on obtient $|\lambda - a_{ii}| \leq R_i$ : $\lambda \in \overline{D}(a_{ii}, R_i)$.

## Remarques

- **Matrices à diagonale strictement dominante.** Si $|a_{ii}| > R_i$ pour tout $i$, alors $0$ n'appartient à aucun disque, donc $0$ n'est pas valeur propre : $A$ est **inversible**. C'est le critère utilisé pour les matrices issues de la discrétisation des équations différentielles.
- **Version par colonnes.** $A$ et $A^\top$ ont les mêmes valeurs propres ; on peut donc aussi utiliser les rayons $C_j = \sum_{i \neq j} |a_{ij}|$, calculés sur les colonnes, et garder la meilleure des deux localisations.
- **Exemple.** Pour $A = \begin{pmatrix} 4 & 1 & 0 \\ 1 & 4 & 1 \\ 0 & 1 & 4 \end{pmatrix}$, les disques sont centrés en $4$, de rayons $1$, $2$, $1$ : toutes les valeurs propres sont dans $[2, 6]$ (elles sont réelles car $A$ est symétrique réelle). En particulier $A$ est inversible, et même définie positive. Ses valeurs propres sont $4$ et $4 \pm \sqrt{2}$.
