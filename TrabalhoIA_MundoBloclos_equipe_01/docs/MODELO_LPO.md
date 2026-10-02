# Modelo em Lógica de Primeira Ordem (itens 1, 2 e 4)

## 1. Domínio

* Blocos `B = {a,b,c,d}`; locais de apoio `L = B ∪ {T}` (`T` = mesa).
* Comprimentos: `ℓ(a)=ℓ(b)=1`, `ℓ(c)=2`, `ℓ(d)=3`.
* Eixo com **pontos** `0..6` e **6 slots** `[i,i+1]`, `i=0..5` (os números da figura são pontos, não slots).
* Um bloco que começa no ponto `p` cobre os slots `p..p+ℓ(b)-1`; posições válidas `p ∈ {0..6-ℓ(b)}`.
* Níveis `0..3` (0 = mesa).

## 2. Representação (cálculo de situações)

**Fluentes primitivos**

| Fluente | Significado |
|---|---|
| `at(b,p,s)` | `b` começa no ponto `p` na situação `s` |
| `lev(b,l,s)` | `b` está no nível `l` |

**Relações derivadas** (definidas, nunca armazenadas ⇒ sem axiomas de frame para elas)

```
cov(b,k,l,s)  ↔ ∃p. at(b,p,s) ∧ lev(b,l,s) ∧ p ≤ k < p+ℓ(b)          (b cobre o slot k no nível l)
free(k,l,s)   ↔ ¬∃x. cov(x,k,l,s)
on(b,y,s)     ↔ ∃k. cov(b,k,l,s) ∧ cov(y,k,l-1,s)       on(b,T,s) ↔ lev(b,0,s)   (vários apoios = ponte)
clr(b,s)      ↔ ¬∃x,k. cov(b,k,l,s) ∧ lev(b,l,s) ∧ cov(x,k,l+1,s)
stable(b,p,l,s) ↔ l=0 ∨ #{k∈[p,p+ℓ(b)-1] : ∃y≠b. cov(y,k,l-1,s)} ≥ ⌈ℓ(b)/2⌉
```

Exemplo de ponte (S0 da Situação 1): `d@3/1` sobre `a@3/0` e `b@5/0` ⇒ `on(d,a) ∧ on(d,b)`, com o slot 4 vazio embaixo.

## 3. Ação `move(b,y,p)`

"Mover `b` para cima de `y ∈ (B∖{b}) ∪ {T}`, começando no ponto `p`." O nível de destino é `l_y(s) = 0` se `y=T`, ou `lev(y)+1`.

**Pré-condições** `Poss(move(b,y,p), s)`

1. `clr(b,s)` — topo de `b` livre.
2. Destino ≠ posição atual: `¬(at(b,p,s) ∧ lev(b,l_y,s))`.
3. Se `y ∈ B`: o span de `b` em `p` sobrepõe o span de `y`.
4. Slots `p..p+ℓ(b)-1` livres de outros blocos no nível `l_y`.
5. `stable(b,p,l_y,s)`.
6. `l_y ≤ 3`.

> **Correção ao esboço do manual:** *não* se exige `clr(y)`. Com `clr(y)`, `a` e `b` nunca poderiam ficar lado a lado sobre `c`
> (estados S5/S7 da Situação 3 e S5 da Situação 2). Basta que os slots-alvo estejam livres (condição 4).

**Efeitos** (estado sucessor)

```
at (x,q,do(move(b,y,p),s)) ↔ (x=b ∧ q=p) ∨ (at (x,q,s) ∧ x≠b)
lev(x,m,do(move(b,y,p),s)) ↔ (x=b ∧ m=l_y) ∨ (lev(x,m,s) ∧ x≠b)
```

## 4. Elementos novos e ações associadas (item 2)

| Elemento | Tipo | Add | Delete |
|---|---|---|---|
| `ℓ(b)`, `B`, pontos | termos/constantes | — | — (rígidos) |
| `at(b,p)` | fluente | `at(b,p)` | `at(b,p₀)` (posição antiga) |
| `lev(b,l)` | fluente | `lev(b,l_y)` | `lev(b,l₀)` (nível antigo) |
| `clr(y)` | derivado | — | deixa de valer se `b` passa a cobrir `y` |
| `clr(z)` (antigo apoio) | derivado | vale se nada mais o cobre | — |
| `on(b,y)` | derivado | novos apoios sob `[p,p+ℓ(b))` | apoios antigos |
| `free(k,l)` | derivado | células deixadas por `b` | células ocupadas por `b` |
| `stable` | pré-condição | — | — |

Só `at` e `lev` mudam por ação; as relações derivadas são recalculadas.

## 5. Ordem parcial (item 4): `A —P→ B`

Um plano é uma **ordem parcial** de ações com **ligações causais** `A —P→ B`: `A` produz `P` e `B` consome `P`.
Em nossa representação `P` é uma *célula* `(slot, nível)` ou a *posição de um bloco*. Para `α = move(b,y,p)` em um estado `s`:

```
W(α) = { pos(b) } ∪ células_antigas(b) ∪ células_novas(b)
R(α) = { pos(y) } ∪ células_acima_das_antigas(b) ∪ apoio_novo(b) ∪ células_novas(b)
```

`αᵢ ≺ αⱼ` (i<j) se `Wᵢ∩Rⱼ ≠ ∅` (**causal**), `Wᵢ∩Wⱼ ≠ ∅` (**escrita**) ou `Rᵢ∩Wⱼ ≠ ∅` (**proteção**).
Ações sem relação são independentes. A ordem é reduzida transitivamente (diagrama de Hasse).
`src/interpretar.py` calcula isso e, com `--verificar`, executa **todas** as linearizações no oráculo.

Exemplo (S5, plano do SAT): `1: move(b,d,3)` e `2: move(a,T,2)` são independentes; ambas precedem `3: move(c,d,4)`, que precede `4: move(a,c,4)` e `5: move(b,c,5)`.
Há 4 linearizações e as 4 são válidas.
