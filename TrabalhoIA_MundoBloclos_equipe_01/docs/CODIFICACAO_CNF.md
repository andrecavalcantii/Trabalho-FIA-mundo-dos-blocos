# Codificação CNF, mapeamento, execução e interpretação (item 5)

## 1. Variáveis proposicionais

Passos de estado `t = 0..T`; passos de ação `t = 0..T-1`. A ordem de criação define os IDs (`Codificador.criar_variaveis`).

| Variável | Índices | Significado | Qtd. por `t` |
|---|---|---|---|
| `at(b,p,t)` | `p ∈ 0..6-ℓ(b)` | `b` começa em `p` | 21 |
| `lev(b,l,t)` | `l ∈ 0..3` | nível de `b` | 16 |
| `clr(b,t)` | | topo de `b` livre | 4 |
| `cob(b,s,t)` | `s ∈ 0..5` | `b` cobre o slot `s` (auxiliar) | 24 |
| `ocb(b,s,l,t)` | | `b` ocupa a célula `(s,l)` (auxiliar) | 96 |
| `ocp(s,l,t)` | | alguém ocupa `(s,l)` (auxiliar) | 24 |
| `mv(b,y,p,t)` | `y ∈ B∖{b} ∪ {T}` | ação (só `t<T`) | 84 |

`on(b,y,t)` **não** é variável: é derivada na interpretação. Total: `|V| = 185·(T+1) + 84·T = 269·T + 185` (T=4 ⇒ 1261).

## 2. Grupos de cláusulas

| # | Regra | Cláusulas |
|---|---|---|
| 1 | Estado inicial / meta | unitárias `at(b,p,0)`, `lev(b,l,0)` e `at(b,p,T)`, `lev(b,l,T)` |
| 2 | Unicidade (A,B) | `⋁ₚ at(b,p,t)` e `¬at(b,p₁,t) ∨ ¬at(b,p₂,t)`; idem `lev` |
| 3 | Geometria | `cob ↔ ⋁ at(b,p,t)` (p cobrindo `s`); `ocb ↔ cob ∧ lev`; `ocp ↔ ⋁_b ocb` |
| 4 | Exclusão horizontal (C) | `¬ocb(b₁,s,l,t) ∨ ¬ocb(b₂,s,l,t)` |
| 5 | Estabilidade (D) | para `l>0`: `¬at ∨ ¬lev ∨ ⋁_{s∈S} ocp(s,l-1,t)` para todo `S ⊆ span` com `|S| = ℓ-⌈ℓ/2⌉+1` |
| 6 | Clear (E) | `clr(b,t) ↔ ⋀ₛ ¬ocp(s,l+1,t)` condicionado a `at(b,p,t) ∧ lev(b,l,t)` |
| 7 | Ação única (F) | `¬mv₁ ∨ ¬mv₂` para todo par em `t` (≤ 1 ação por passo) |
| 8 | Pré-condições (G) | `¬m ∨ clr(b,t)`; `¬m ∨ ¬at(y,p_y,t)` (`p_y` sem sobreposição); `¬m ∨ ¬lev(y,l_y,t) ∨ ¬ocb(x,s,l_y+1,t)`; sem no-op; `y` no nível máximo ⇒ `¬m` |
| 9 | Efeitos (H) | `¬m ∨ at(b,p,t+1)`; `¬m ∨ ¬lev(y,l_y,t) ∨ lev(b,l_y+1,t+1)` (ou `lev(b,0,t+1)` se `y=T`) |
| 10 | Frame (I) | `¬at(x,p,t) ∨ at(x,p,t+1) ∨ ⋁ moves de x`; idem `lev`. Sem frame para `clr`/`on` (derivados) |

"Pelo menos `k` de `n`" é codificado como "todo subconjunto de tamanho `n-k+1` contém um verdadeiro": `d` (n=3, k=2) usa pares; `c` (n=2, k=1) uma cláusula com 2 literais; `a`,`b` (n=k=1) unitárias.

**Otimalidade:** como há no máximo 1 ação por passo, `T` SAT ⇔ existe plano com ≤ T ações. O primeiro `T` SAT (com UNSAT em `T-1`) é o comprimento mínimo.

## 3. Exemplo concreto (Situação 1 → Sf4, T=4)

```
p cnf 1261 26397
13 0   at(c,0,0)      4 0   at(a,3,0)      12 0  at(b,5,0)      21 0  at(d,3,0)
30 0   lev(c,0,0)     22 0  lev(a,0,0)     26 0  lev(b,0,0)     35 0  lev(d,1,0)
```

`mv(d,c,0,0)` é a variável 1002. Algumas cláusulas:

```
-1002 41 0       move(d,c,0,0) → clr(d,0)
-1002 203 0      move(d,c,0,0) → at(d,0,1)
-1002 -16 0      move(d,c,0,0) → ¬at(c,3,0)    (c fora do span de d)
-1002 -30 220 0  (c no nível 0) → lev(d,1,1)
```

Formato DIMACS: positivo = verdadeiro, negativo = falso, `0` encerra a cláusula.

## 4. Mapeamento: descrição formal → código

| Regra formal | Código |
|---|---|
| Blocos, comprimentos, pontos | `BLOCKS, LEN, MAX_POINT, MAX_LEVEL` (`cenarios.py`) |
| Posições válidas, span, sobreposição | `positions`, `span`, `spans_overlap` |
| `at`, `lev`, `clr`, `mv` e auxiliares | `Codificador.novo(...)` em `criar_variaveis` |
| Estado inicial / meta | `estado_inicial`, `meta_final` |
| Unicidade (A,B) | `axiomas_estado` + `exatamente_um` |
| Geometria | `geometria` |
| Exclusão horizontal (C) | `exclusao_horizontal` |
| Estabilidade (D) | `estabilidade` |
| Clear (E) | `clear` |
| Ação única (F) | `axiomas_acao` |
| Pré-condições e efeitos (G,H) | `move`, `efeitos_nivel` |
| Frame (I) | `frame` |
| `on` derivado | `interpretar.py: derivar_on` |
| Ordem parcial | `interpretar.py: ordem_parcial`, `linearizacoes_validas` |
| Oráculo | `oraculo_bfs.py` |

Para mudar o problema, edite `src/cenarios.py` (estado inicial e meta como `{bloco: (ponto, nivel)}`); para outros blocos, `BLOCKS`/`LEN`.

## 5. Execução passo a passo

```bash
cd src
python3 bw2cnf_var.py --cenario 1 --alvo Sf4 --horizonte 4 --saida ../cenario1
#   Gerado: 1261 variaveis, 26397 clausulas
minisat ../cenario1/trab01_blocos2SAT.cnf ../cenario1/resultado1.txt        # ou rodar_sat.py (usa PySAT se não houver minisat)
python3 interpretar.py ../cenario1/resultado1.txt --mapa ../cenario1/trab01_blocos2SAT.map --verbose --verificar
python3 rodar_sat.py --cenario 1 --alvo Sf4 --saida ../cenario1               # T = 0,1,2,... até SAT
python3 rodar_todos.py                                                        # todos os cenários/alvos
```

## 6. Interpretação da saída do SAT solver

O miniSAT não conhece nomes simbólicos: devolve inteiros (todos os literais, com sinal). Para Sf4 os positivos que são ações:

```
1002 mv(d,c,0,0)    1015 mv(a,b,5,1)    1176 mv(d,T,2,2)    1184 mv(a,c,0,3)
```

`interpretar.py`: (1) lê o `.map`; (2) mantém literais positivos; (3) reconstrói `at`/`lev` por `t` e as ações; (4) deriva `on`
(nível 0 ⇒ mesa; senão blocos do nível `l-1` cujo span sobrepõe o de `b`; vários ⇒ ponte); (5) calcula a ordem parcial;
(6) `--verificar` re-executa o plano no oráculo e testa as linearizações.

```
PLANO ENCONTRADO (4 acoes):
1. t=0: mover bloco 'd' para CIMA de 'c' em p=0
2. t=1: mover bloco 'a' para CIMA de 'b' em p=5
3. t=2: mover bloco 'd' para a MESA em p=2
4. t=3: mover bloco 'a' para CIMA de 'c' em p=0
```

**Regra de ouro:** sem o `.map` a saída numérica é só uma lista de inteiros.

## 7. Resultados

Ver `resultados/RESUMO.md` (T mínimo, BFS, tamanhos, comparação com o manual). Os 15 alvos têm T do SAT = comprimento do BFS.
