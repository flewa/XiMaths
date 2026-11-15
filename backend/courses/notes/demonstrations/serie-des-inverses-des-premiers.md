---
titre: Divergence de la série des inverses des nombres premiers
programmes: MP, MPI, L2
statut: hors-programme
ordre: 21
notion: series-numeriques
---

## Énoncé

> **Théorème (Euler).** Si $(p_k)_{k \geq 1}$ est la suite croissante des nombres premiers, la série $\sum_{k \geq 1} \dfrac{1}{p_k}$ diverge.

En particulier, il y a une infinité de nombres premiers, et ils sont « assez nombreux » : bien plus que les carrés, puisque $\sum \frac{1}{n^2}$ converge. On donne la démonstration d'Erdős (1938), par dénombrement.

## Idée

Si la série convergeait, à partir d'un rang $K$ ses restes seraient inférieurs à $\frac{1}{2}$. On sépare alors les entiers $n \leq N$ en deux paquets : ceux qui n'ont que des petits facteurs premiers (parmi $p_1, \dots, p_K$), très peu nombreux, et ceux qui ont un grand facteur premier, moins de $\frac{N}{2}$. Les deux paquets ne suffisent pas à contenir les $N$ entiers.

## Démonstration

Supposons que $\sum \frac{1}{p_k}$ converge. Il existe $K \geq 1$ tel que $\sum_{k > K} \frac{1}{p_k} < \frac{1}{2}$. Soit $N \geq 1$ un entier. On répartit les entiers $n \in [\![1, N]\!]$ en deux ensembles :

- $\mathcal{G}$ : ceux qui ont au moins un facteur premier $p_k$ avec $k > K$ (les « grands ») ;
- $\mathcal{P}$ : ceux dont tous les facteurs premiers sont parmi $p_1, \dots, p_K$ (les « petits »), y compris $n = 1$.

**Les grands sont moins de $\frac{N}{2}$.** Pour un premier $p$, le nombre de multiples de $p$ dans $[\![1, N]\!]$ est $\left\lfloor \frac{N}{p} \right\rfloor \leq \frac{N}{p}$. Tout élément de $\mathcal{G}$ est multiple d'un $p_k$ avec $k > K$, donc

$$
\lvert \mathcal{G} \rvert \leq \sum_{k > K} \frac{N}{p_k} < \frac{N}{2}.
$$

(La somme ne porte en fait que sur les $p_k \leq N$, en nombre fini.)

**Les petits sont au plus $2^K \sqrt{N}$.** Tout entier $n \geq 1$ s'écrit $n = r s^2$, où $s^2$ est le plus grand carré qui divise $n$ et où $r$ n'est divisible par aucun carré autre que $1$. Pour $n \in \mathcal{P}$, l'entier $r$ est un produit de nombres premiers **distincts** pris parmi $p_1, \dots, p_K$ : il y a au plus $2^K$ choix pour $r$ (une partie de $\{ p_1, \dots, p_K \}$). Et $s^2 \leq n \leq N$ donne $s \leq \sqrt{N}$ : au plus $\sqrt{N}$ choix pour $s$. Comme $n$ est déterminé par $(r, s)$ :

$$
\lvert \mathcal{P} \rvert \leq 2^K \sqrt{N}.
$$

**Contradiction.** Les deux ensembles recouvrent $[\![1, N]\!]$, donc $N = |\mathcal{G}| + |\mathcal{P}| < \frac{N}{2} + 2^K \sqrt{N}$, soit $\sqrt{N} < 2^{K+1}$. C'est faux pour $N = 2^{2K+2}$. La série $\sum \frac{1}{p_k}$ diverge donc.

## Remarques

- **Ordre de grandeur.** On sait plus précisément que $\sum_{p \leq x} \frac{1}{p} = \ln \ln x + M + o(1)$, où $M \approx 0{,}2615$ est la constante de Meissel-Mertens : la divergence est extrêmement lente.
- **Lien avec le théorème des nombres premiers.** Le nombre $\pi(x)$ de nombres premiers inférieurs à $x$ vérifie $\pi(x) \sim \frac{x}{\ln x}$ (Hadamard et de La Vallée Poussin, 1896), ce qui donne $p_k \sim k \ln k$. Avec la comparaison série-intégrale, on retrouve la divergence de $\sum \frac{1}{k \ln k}$, donc de $\sum \frac{1}{p_k}$.
