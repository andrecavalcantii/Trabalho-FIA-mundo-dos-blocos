# Resolução manual (item 3 do enunciado)

Notação: `x@p/l` = bloco `x` começando no ponto `p`, nível `l` (0 = mesa). `move(b,y,p)` = mover `b` para cima de `y` (bloco ou `T`) começando em `p`.
Em cada passo verificaram-se as pré-condições do modelo (`docs/MODELO_LPO.md`): topo de `b` livre, slots-alvo livres no nível de destino, span de `b` sobre `y`, e apoio ≥ ⌈ℓ(b)/2⌉ no nível abaixo.
A coluna *on* mostra a relação derivada (ponte = vários apoios).

> Os estados abaixo foram gerados mecanicamente pelo oráculo (`src/oraculo_bfs.py`) executando o plano manual, o que confirma que cada passo é legal e que o estado final é o da figura. Os planos têm o comprimento mínimo (provado pelo SAT: UNSAT em T−1).

## Situação 1 → Sf3 — 2 ações

| t | Ação | Estado após a ação | on (derivado) |
|---|---|---|---|
| — | S0 | a@3/0 b@5/0 c@0/0 d@3/1 | a→T; b→T; c→T; d→a+b |
| 0 | `move(d,c,0)` | a@3/0 b@5/0 c@0/0 d@0/1 | a→T; b→T; c→T; d→c |
| 1 | `move(a,T,2)` | a@2/0 b@5/0 c@0/0 d@0/1 | a→T; b→T; c→T; d→a+c |

Estado final = **Sf3** ✔

## Situação 1 → Sf4 — 4 ações

| t | Ação | Estado após a ação | on (derivado) |
|---|---|---|---|
| — | S0 | a@3/0 b@5/0 c@0/0 d@3/1 | a→T; b→T; c→T; d→a+b |
| 0 | `move(d,c,0)` | a@3/0 b@5/0 c@0/0 d@0/1 | a→T; b→T; c→T; d→c |
| 1 | `move(a,b,5)` | a@5/1 b@5/0 c@0/0 d@0/1 | a→b; b→T; c→T; d→c |
| 2 | `move(d,T,2)` | a@5/1 b@5/0 c@0/0 d@2/0 | a→b; b→T; c→T; d→T |
| 3 | `move(a,c,0)` | a@0/1 b@5/0 c@0/0 d@2/0 | a→c; b→T; c→T; d→T |

Estado final = **Sf4** ✔

## Situação 1 → Sf1 — 8 ações

| t | Ação | Estado após a ação | on (derivado) |
|---|---|---|---|
| — | S0 | a@3/0 b@5/0 c@0/0 d@3/1 | a→T; b→T; c→T; d→a+b |
| 0 | `move(d,c,0)` | a@3/0 b@5/0 c@0/0 d@0/1 | a→T; b→T; c→T; d→c |
| 1 | `move(a,T,2)` | a@2/0 b@5/0 c@0/0 d@0/1 | a→T; b→T; c→T; d→a+c |
| 2 | `move(d,a,1)` | a@2/0 b@5/0 c@0/0 d@1/1 | a→T; b→T; c→T; d→a+c |
| 3 | `move(b,c,0)` | a@2/0 b@0/1 c@0/0 d@1/1 | a→T; b→c; c→T; d→a+c |
| 4 | `move(d,T,3)` | a@2/0 b@0/1 c@0/0 d@3/0 | a→T; b→c; c→T; d→T |
| 5 | `move(a,d,4)` | a@4/1 b@0/1 c@0/0 d@3/0 | a→d; b→c; c→T; d→T |
| 6 | `move(b,d,5)` | a@4/1 b@5/1 c@0/0 d@3/0 | a→d; b→d; c→T; d→T |
| 7 | `move(c,a,4)` | a@4/1 b@5/1 c@4/2 d@3/0 | a→d; b→d; c→a+b; d→T |

Estado final = **Sf1** ✔

## Situação 1 → Sf2 — 9 ações

| t | Ação | Estado após a ação | on (derivado) |
|---|---|---|---|
| — | S0 | a@3/0 b@5/0 c@0/0 d@3/1 | a→T; b→T; c→T; d→a+b |
| 0 | `move(c,T,1)` | a@3/0 b@5/0 c@1/0 d@3/1 | a→T; b→T; c→T; d→a+b |
| 1 | `move(d,c,0)` | a@3/0 b@5/0 c@1/0 d@0/1 | a→T; b→T; c→T; d→c |
| 2 | `move(a,T,0)` | a@0/0 b@5/0 c@1/0 d@0/1 | a→T; b→T; c→T; d→a+c |
| 3 | `move(d,c,1)` | a@0/0 b@5/0 c@1/0 d@1/1 | a→T; b→T; c→T; d→c |
| 4 | `move(b,a,0)` | a@0/0 b@0/1 c@1/0 d@1/1 | a→T; b→a; c→T; d→c |
| 5 | `move(d,T,3)` | a@0/0 b@0/1 c@1/0 d@3/0 | a→T; b→a; c→T; d→T |
| 6 | `move(c,d,4)` | a@0/0 b@0/1 c@4/1 d@3/0 | a→T; b→a; c→d; d→T |
| 7 | `move(b,c,5)` | a@0/0 b@5/2 c@4/1 d@3/0 | a→T; b→c; c→d; d→T |
| 8 | `move(a,c,4)` | a@4/2 b@5/2 c@4/1 d@3/0 | a→c; b→c; c→d; d→T |

Estado final = **Sf2** ✔

## Situação 2 → S5 — 5 ações

| t | Ação | Estado após a ação | on (derivado) |
|---|---|---|---|
| — | S0 | a@0/1 b@1/1 c@0/0 d@3/0 | a→c; b→c; c→T; d→T |
| 0 | `move(a,d,3)` | a@3/1 b@1/1 c@0/0 d@3/0 | a→d; b→c; c→T; d→T |
| 1 | `move(b,a,3)` | a@3/1 b@3/2 c@0/0 d@3/0 | a→d; b→a; c→T; d→T |
| 2 | `move(c,d,4)` | a@3/1 b@3/2 c@4/1 d@3/0 | a→d; b→a; c→d; d→T |
| 3 | `move(b,c,5)` | a@3/1 b@5/2 c@4/1 d@3/0 | a→d; b→c; c→d; d→T |
| 4 | `move(a,c,4)` | a@4/2 b@5/2 c@4/1 d@3/0 | a→c; b→c; c→d; d→T |

Estado final = **S5** ✔

## Situação 3 → S7 — 6 ações

| t | Ação | Estado após a ação | on (derivado) |
|---|---|---|---|
| — | S0 | a@3/0 b@5/0 c@0/0 d@3/1 | a→T; b→T; c→T; d→a+b |
| 0 | `move(d,c,0)` | a@3/0 b@5/0 c@0/0 d@0/1 | a→T; b→T; c→T; d→c |
| 1 | `move(a,b,5)` | a@5/1 b@5/0 c@0/0 d@0/1 | a→b; b→T; c→T; d→c |
| 2 | `move(d,T,2)` | a@5/1 b@5/0 c@0/0 d@2/0 | a→b; b→T; c→T; d→T |
| 3 | `move(a,c,0)` | a@0/1 b@5/0 c@0/0 d@2/0 | a→c; b→T; c→T; d→T |
| 4 | `move(b,c,1)` | a@0/1 b@1/1 c@0/0 d@2/0 | a→c; b→c; c→T; d→T |
| 5 | `move(d,T,3)` | a@0/1 b@1/1 c@0/0 d@3/0 | a→c; b→c; c→T; d→T |

Estado final = **S7** ✔

## Observações

* **Ordem parcial.** Em quase todos os planos a ordem é total (os blocos se bloqueiam em cadeia). Em Sf1, `move(a,d,4)` e `move(b,d,5)` são independentes
  (ambos dependem só de `move(d,T,3)`). Em S5 (plano do SAT) as ações `move(b,d,3)` e `move(a,T,2)` são independentes. `interpretar.py` calcula as ligações causais `A —P→ B`.
* **Planos distintos, mesmo comprimento.** Em Sf1 e S5 o SAT encontrou outro plano ótimo (ver `cenario1/Sf1/plano.txt`, `cenario2/S5/plano.txt`).
* **Sit. 3:** S5 e S6 são idênticos na figura do enunciado; o plano de S7 passa por S1, S2, S3, S4 e S5 (os estados intermediários da figura).
