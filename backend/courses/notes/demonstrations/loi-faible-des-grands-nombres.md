---
titre: Loi faible des grands nombres
programmes: MP, MPI, L2
statut: au-programme
ordre: 14
notion: theoremes-limites
---

## Énoncé

> **Théorème (loi faible des grands nombres).** Soit $(X_n)_{n \geq 1}$ une suite de variables aléatoires réelles discrètes, indépendantes, de même loi, admettant une variance. On note $m$ leur espérance, $\sigma^2$ leur variance et $S_n = X_1 + \dots + X_n$. Alors, pour tout $\varepsilon > 0$,
>
> $$
> P\left( \left| \frac{S_n}{n} - m \right| \geq \varepsilon \right) \leq \frac{\sigma^2}{n \varepsilon^2} \xrightarrow[n \to +\infty]{} 0.
> $$

## Idée

La moyenne $\frac{S_n}{n}$ a pour espérance $m$ et pour variance $\frac{\sigma^2}{n}$, qui tend vers $0$ : elle se concentre autour de $m$. L'inégalité de Bienaymé-Tchebychev traduit cette concentration en probabilité.

## Démonstration

**Inégalité de Markov.** Si $Y$ est une variable aléatoire positive d'espérance finie et $a > 0$, alors $P(Y \geq a) \leq \frac{E(Y)}{a}$. En effet, $a \mathbf{1}_{\{Y \geq a\}} \leq Y$ (si $Y \geq a$, le membre de gauche vaut $a \leq Y$ ; sinon il vaut $0 \leq Y$). Par croissance de l'espérance, $a P(Y \geq a) = E\left( a \mathbf{1}_{\{Y \geq a\}} \right) \leq E(Y)$.

**Inégalité de Bienaymé-Tchebychev.** Si $Z$ admet une variance et $\varepsilon > 0$, alors $P\big( |Z - E(Z)| \geq \varepsilon \big) \leq \frac{V(Z)}{\varepsilon^2}$. On applique l'inégalité de Markov à $Y = \big( Z - E(Z) \big)^2$, positive d'espérance $V(Z)$, avec $a = \varepsilon^2$, en remarquant que $|Z - E(Z)| \geq \varepsilon \iff Y \geq \varepsilon^2$.

**Espérance et variance de la moyenne.** Par linéarité, $E(S_n) = \sum_{i=1}^{n} E(X_i) = nm$, donc $E\left( \frac{S_n}{n} \right) = m$. Les $X_i$ étant indépendantes, elles sont deux à deux décorrélées ($\operatorname{Cov}(X_i, X_j) = 0$ pour $i \neq j$), donc

$$
V(S_n) = \sum_{i=1}^{n} V(X_i) + 2 \sum_{1 \leq i < j \leq n} \operatorname{Cov}(X_i, X_j) = n\sigma^2, \qquad V\left( \frac{S_n}{n} \right) = \frac{1}{n^2} V(S_n) = \frac{\sigma^2}{n}.
$$

**Conclusion.** L'inégalité de Bienaymé-Tchebychev appliquée à $Z = \frac{S_n}{n}$ donne exactement l'inégalité annoncée, et son majorant tend vers $0$.

## Remarques

- **Interprétation fréquentiste.** Si $X_i = \mathbf{1}_{A_i}$ indique le succès de la $i$-ième répétition indépendante d'une expérience de probabilité de succès $p$, alors $\frac{S_n}{n}$ est la fréquence de succès, $m = p$ et $\sigma^2 = p(1 - p) \leq \frac{1}{4}$ : $P\left( \left| \frac{S_n}{n} - p \right| \geq \varepsilon \right) \leq \frac{1}{4n\varepsilon^2}$. Pour garantir une erreur d'au plus $0{,}01$ avec probabilité au moins $0{,}95$, il suffit de $n = 50\,000$ répétitions.
- **Hypothèses.** La preuve n'utilise que la décorrélation deux à deux, et des variances bornées suffiraient au lieu d'une loi commune. La loi **forte** des grands nombres (convergence presque sûre de $\frac{S_n}{n}$ vers $m$) est hors programme.
