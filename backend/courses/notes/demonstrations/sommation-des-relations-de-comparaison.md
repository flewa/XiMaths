---
titre: Sommation des relations de comparaison
programmes: MP, MPI, L2
statut: au-programme
ordre: 11
notion: series-numeriques
---

## Énoncé

> **Théorème.** Soient $(u_n)$ une suite complexe et $(v_n)$ une suite de **réels positifs** telles que $u_n = o(v_n)$.
>
> 1. **Cas convergent.** Si $\sum v_n$ converge, alors $\sum u_n$ converge absolument et les restes vérifient
>
> $$
> \sum_{k=n+1}^{+\infty} u_k = o\left( \sum_{k=n+1}^{+\infty} v_k \right).
> $$
>
> 2. **Cas divergent.** Si $\sum v_n$ diverge, alors les sommes partielles vérifient
>
> $$
> \sum_{k=0}^{n} u_k = o\left( \sum_{k=0}^{n} v_k \right).
> $$
>
> Les mêmes énoncés valent avec $O$ à la place de $o$, et avec $\sim$ (pour $u_n$ réels positifs) : si $u_n \sim v_n$, les séries sont de même nature, et les restes (cas convergent) ou les sommes partielles (cas divergent) sont équivalents.

## Idée

À partir d'un rang $N$, $|u_k| \leq \varepsilon v_k$. Dans le cas convergent, on somme cette inégalité sur un reste. Dans le cas divergent, les termes d'indice inférieur à $N$ forment une constante, que la somme $\sum v_k$, qui tend vers $+\infty$, finit par écraser.

## Démonstration

Soit $\varepsilon > 0$. Comme $u_n = o(v_n)$, il existe $N \in \N$ tel que $|u_k| \leq \varepsilon v_k$ pour tout $k \geq N$.

**Cas convergent.** La série $\sum v_k$ converge, donc $\sum |u_k|$ converge par comparaison de séries à termes positifs : $\sum u_k$ converge absolument. Pour $n \geq N$, en sommant l'inégalité de $k = n + 1$ à $+\infty$ :

$$
\left| \sum_{k=n+1}^{+\infty} u_k \right| \leq \sum_{k=n+1}^{+\infty} |u_k| \leq \varepsilon \sum_{k=n+1}^{+\infty} v_k.
$$

C'est la définition de la négligeabilité des restes.

**Cas divergent.** Notons $V_n = \sum_{k=0}^{n} v_k$ ; comme $v_k \geq 0$ et $\sum v_k$ diverge, $V_n \to +\infty$. Pour $n \geq N$ :

$$
\left| \sum_{k=0}^{n} u_k \right| \leq \underbrace{\left| \sum_{k=0}^{N-1} u_k \right|}_{= C} + \sum_{k=N}^{n} \varepsilon \, v_k \leq C + \varepsilon V_n.
$$

La constante $C$ ne dépend pas de $n$ ; comme $V_n \to +\infty$, il existe $N' \geq N$ tel que $C \leq \varepsilon V_n$ pour $n \geq N'$. Alors $\left| \sum_{k=0}^{n} u_k \right| \leq 2\varepsilon V_n$ pour $n \geq N'$.

**Cas des équivalents.** Si $u_n \sim v_n$, alors $u_n - v_n = o(v_n)$. Les séries sont de même nature (comparaison de séries à termes positifs, $u_n$ et $v_n$ étant positifs à partir d'un certain rang). Dans le cas convergent, $\sum_{k>n} u_k - \sum_{k>n} v_k = \sum_{k>n} (u_k - v_k) = o\left( \sum_{k>n} v_k \right)$, c'est l'équivalence des restes ; de même pour les sommes partielles dans le cas divergent. La version avec $O$ se démontre comme la version avec $o$, en remplaçant $\varepsilon$ par une constante fixe.

## Remarques

- **Théorème de Cesàro.** Si $u_n \to \ell \in \C$, alors $\frac{1}{n} \sum_{k=1}^{n} u_k \to \ell$. En effet $u_n - \ell = o(1)$, et $\sum 1$ diverge : $\sum_{k=1}^{n} (u_k - \ell) = o(n)$.
- **Exemple.** $\frac{1}{k} \sim \ln(k + 1) - \ln k$, terme général d'une série divergente à termes positifs dont les sommes partielles valent $\ln(n + 1)$. Donc $\sum_{k=1}^{n} \frac{1}{k} \sim \ln(n + 1) \sim \ln n$.
- **Le signe de $v_n$ compte.** Pour $u_n = \frac{(-1)^n}{\sqrt{n}} + \frac{1}{n}$ et $v_n = \frac{(-1)^n}{\sqrt{n}}$, on a $u_n \sim v_n$, mais $\sum v_n$ converge et $\sum u_n$ diverge.
