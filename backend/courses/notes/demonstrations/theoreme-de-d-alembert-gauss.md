---
titre: Théorème de d'Alembert-Gauss
programmes: MPSI, MP, L2
statut: preuve-hors-programme
ordre: 13
notion: polynomes
---

## Énoncé

> **Théorème (d'Alembert-Gauss).** Tout polynôme non constant à coefficients complexes admet au moins une racine dans $\C$.

Au programme de MPSI et de MP, la démonstration est hors programme. Celle-ci n'utilise que le théorème de Bolzano-Weierstrass et l'existence des racines $k$-ièmes d'un complexe.

## Idée

Le module $|P|$ tend vers $+\infty$ à l'infini, donc il atteint un minimum en un point $z_0$. Si $P(z_0)$ n'était pas nul, on trouverait une direction dans laquelle $|P|$ diminue encore (lemme de d'Alembert) : contradiction.

## Démonstration

Soit $P = \sum_{j=0}^{d} c_j X^j$ avec $d \geq 1$ et $c_d \neq 0$.

**Étape 1 : $|P|$ atteint son minimum.** Pour $z \neq 0$,

$$
\lvert P(z) \rvert \geq |c_d| |z|^d - \sum_{j=0}^{d-1} |c_j| |z|^j = |z|^d \left( |c_d| - \sum_{j=0}^{d-1} \frac{|c_j|}{|z|^{d-j}} \right),
$$

qui tend vers $+\infty$ quand $|z| \to +\infty$. Il existe donc $\rho > 0$ tel que $|P(z)| > |P(0)|$ pour $|z| > \rho$. Soit $m = \inf_{|z| \leq \rho} |P(z)|$ et $(z_k)$ une suite du disque $\overline{D}(0, \rho)$ telle que $|P(z_k)| \to m$. Les suites $(\operatorname{Re} z_k)$ et $(\operatorname{Im} z_k)$ sont bornées ; par le théorème de Bolzano-Weierstrass (appliqué deux fois), une suite extraite $(z_{\varphi(k)})$ converge vers un $z_0$ tel que $|z_0| \leq \rho$. Par continuité de $z \mapsto |P(z)|$, $|P(z_0)| = m$. Enfin, $|P(z_0)| \leq |P(0)| < |P(z)|$ pour $|z| > \rho$ : $z_0$ est un **minimum global** de $|P|$ sur $\C$.

**Étape 2 : lemme de d'Alembert.** Supposons par l'absurde $P(z_0) \neq 0$. Le polynôme $h \mapsto P(z_0 + h)$ est de degré $d$ ; écrivons-le

$$
P(z_0 + h) = P(z_0) + b_k h^k + h^{k+1} Q(h),
$$

où $k \in [\![1, d]\!]$ est le plus petit indice tel que le coefficient $b_k$ de $h^k$ soit non nul (il existe, car $P$ n'est pas constant) et $Q$ est un polynôme. Choisissons $\omega \in \C$ tel que $\omega^k = -\dfrac{P(z_0)}{b_k}$ : c'est une racine $k$-ième d'un complexe non nul, qui existe. Alors $b_k \omega^k = -P(z_0)$, et pour $t \in \, ]0, 1]$ :

$$
P(z_0 + t\omega) = P(z_0) (1 - t^k) + t^{k+1} \omega^{k+1} Q(t\omega).
$$

Soit $M = |\omega|^{k+1} \max_{|h| \leq |\omega|} |Q(h)|$, fini par continuité de $Q$ sur un disque fermé (même argument qu'à l'étape 1). On obtient

$$
\lvert P(z_0 + t\omega) \rvert \leq |P(z_0)| (1 - t^k) + t^{k+1} M = |P(z_0)| - t^k \big( |P(z_0)| - tM \big).
$$

Pour $t \in \, ]0, 1]$ assez petit pour que $tM < |P(z_0)|$, ce majorant est strictement inférieur à $|P(z_0)|$ : $|P(z_0 + t\omega)| < |P(z_0)|$, ce qui contredit la minimalité de $|P(z_0)|$. Donc $P(z_0) = 0$.

## Remarques

- **Conséquences.** Par récurrence sur le degré, tout polynôme complexe de degré $d \geq 1$ est scindé : $P = c_d \prod_{j=1}^{d} (X - z_j)$. Les irréductibles de $\C[X]$ sont les polynômes de degré $1$ ; ceux de $\R[X]$ sont les polynômes de degré $1$ et ceux de degré $2$ sans racine réelle.
- **Où la preuve utilise $\C$.** À l'étape 2, on a besoin d'une racine $k$-ième de $-\frac{P(z_0)}{b_k}$. Dans $\R$, elle peut ne pas exister : pour $P = X^2 + 1$ et $z_0 = 0$, il faudrait $\omega^2 = -1$. C'est exactement pourquoi $X^2 + 1$ n'a pas de racine réelle alors que $|P|$ atteint son minimum sur $\R$ en $0$.
