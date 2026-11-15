---
titre: Irrationalité de e et de π
programmes: MP, MPI, L2
statut: hors-programme
ordre: 20
notion: nombres-reels
---

## Énoncé

> **Théorème.** Les nombres $e$ et $\pi$ sont irrationnels.

## Idée

Dans les deux cas, on suppose le nombre rationnel et on fabrique, à partir de cette écriture, un **entier strictement compris entre $0$ et $1$**. Pour $e$, l'entier vient de la série $\sum \frac{1}{k!}$ ; pour $\pi$ (preuve de Niven, 1947), d'une intégrale bien choisie qui est à la fois entière et minuscule.

## Démonstration pour $e$

On sait que $e = \sum_{k=0}^{+\infty} \frac{1}{k!}$. Supposons $e = \frac{p}{q}$ avec $p, q \in \N^*$. Posons

$$
A = q! \left( e - \sum_{k=0}^{q} \frac{1}{k!} \right) = q! \, \frac{p}{q} - \sum_{k=0}^{q} \frac{q!}{k!}.
$$

*$A$ est un entier* : $q! \, \frac{p}{q} = (q - 1)! \, p$ et chaque $\frac{q!}{k!}$, pour $k \leq q$, est un entier.

*$0 < A < 1$* : $A = \sum_{k=q+1}^{+\infty} \frac{q!}{k!} > 0$, et, pour $k \geq q + 1$, $\frac{q!}{k!} = \frac{1}{(q+1)(q+2) \cdots k} \leq \frac{1}{(q+1)^{k-q}}$, donc

$$
A \leq \sum_{j=1}^{+\infty} \frac{1}{(q+1)^j} = \frac{1}{q} \leq 1,
$$

l'inégalité $\frac{q!}{k!} \leq \frac{1}{(q+1)^{k-q}}$ étant stricte pour $k \geq q + 2$ ; donc $A < 1$. Un entier strictement compris entre $0$ et $1$ : contradiction.

## Démonstration pour $\pi$

Supposons $\pi = \frac{a}{b}$ avec $a, b \in \N^*$. Pour $n \geq 1$, on pose

$$
f_n(x) = \frac{x^n (a - bx)^n}{n!}, \qquad I_n = \int_0^\pi f_n(x) \sin x \, dx.
$$

**Étape 1 : les dérivées de $f_n$ en $0$ et en $\pi$ sont entières.** Le polynôme $n! \, f_n$ est à coefficients entiers et ses termes sont de degré compris entre $n$ et $2n$ : $f_n(x) = \frac{1}{n!} \sum_{j=n}^{2n} c_j x^j$ avec $c_j \in \Z$. Donc $f_n^{(j)}(0) = 0$ pour $j < n$ ou $j > 2n$, et $f_n^{(j)}(0) = \frac{j!}{n!} c_j \in \Z$ pour $n \leq j \leq 2n$. De plus, comme $a = b\pi$, $a - b(\pi - x) = bx$, d'où $f_n(\pi - x) = \frac{(\pi - x)^n (bx)^n}{n!} = \frac{x^n (a - bx)^n}{n!} = f_n(x)$. En dérivant $j$ fois, $f_n^{(j)}(\pi) = (-1)^j f_n^{(j)}(0) \in \Z$.

**Étape 2 : $I_n$ est un entier.** Posons $F = f_n - f_n'' + f_n^{(4)} - \dots + (-1)^n f_n^{(2n)}$. Comme $f_n^{(2n+2)} = 0$, on a $F + F'' = f_n$. Alors

$$
\big( F' \sin - F \cos \big)' = F'' \sin + F' \cos - F' \cos + F \sin = (F'' + F) \sin = f_n \sin,
$$

donc $I_n = \big[ F'(x) \sin x - F(x) \cos x \big]_0^\pi = F(\pi) + F(0)$, qui est un entier par l'étape 1.

**Étape 3 : $0 < I_n < 1$ pour $n$ grand.** Pour $0 < x < \pi = \frac{a}{b}$, on a $0 < x < \pi$ et $0 < a - bx < a$, donc $0 < f_n(x) \sin x \leq \frac{\pi^n a^n}{n!}$. La fonction intégrée étant continue, positive et non nulle sur $]0, \pi[$ :

$$
0 < I_n \leq \pi \, \frac{(\pi a)^n}{n!} \xrightarrow[n \to +\infty]{} 0.
$$

Pour $n$ assez grand, $I_n$ est un entier strictement compris entre $0$ et $1$ : contradiction. Donc $\pi$ est irrationnel.

## Remarques

- La même méthode que pour $e$ montre que $e$ n'est pas non plus racine d'un polynôme de degré $2$ à coefficients entiers. En revanche, montrer que $e$ et $\pi$ sont **transcendants** (racines d'aucun polynôme non nul à coefficients entiers) demande beaucoup plus : Hermite (1873) pour $e$, Lindemann (1882) pour $\pi$, ce qui règle la quadrature du cercle.
- On ne sait toujours pas si $e + \pi$ ou $e \pi$ est irrationnel.
