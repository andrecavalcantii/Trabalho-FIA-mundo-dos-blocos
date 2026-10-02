# Trabalho 01 — Mundo dos Blocos de Tamanho Variável via SAT

**Fundamentos de Inteligência Artificial — Prof. Edjard Mota (UFAM/ICOMP)** · entrega: 02/10/2026

**Alunos:** André Cavalcanti, Tiago Gil de Brito, Ygor Gutierrz, Sofia Braga

Planejamento em um mundo de blocos com comprimentos diferentes (`a`,`b`=1, `c`=2, `d`=3), espaços vazios,
movimentos laterais, pontes e regra de estabilidade, resolvido por (1) modelagem em LPO, (2) resolução manual,
(3) codificação CNF + SAT solver e (4) comparação com um planejador BFS independente.

> Substitua `01` pelo número da sua equipe no nome da pasta: `TrabalhoIA_MundoBloclos_equipe_XX`.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `docs/MODELO_LPO.md` | Itens 1, 2 e 4: representação em LPO, adds/deletes, ordem parcial |
| `docs/RESOLUCAO_MANUAL.md` | Item 3: execução manual das Situações 1, 2 e 3 |
| `docs/CODIFICACAO_CNF.md` | Item 5: CNF, mapeamento formal → código, execução, interpretação da saída |
| `latex/trab01.tex` (+ `trab01.pdf`) | Manual em LaTeX (Overleaf): as 7 seções pedidas |
| `src/bw2cnf_var.py` | Gerador de CNF/MAP |
| `src/rodar_sat.py` | Executa o SAT (minisat ou PySAT) e procura o menor T |
| `src/interpretar.py` | Traduz a saída: plano, estado final, `on`, ordem parcial, verificação |
| `src/oraculo_bfs.py` | Planejador BFS (oráculo, sem SAT) |
| `src/cenarios.py` | Blocos, `INITIAL`/`GOAL` de todas as situações |
| `src/rodar_todos.py` | Roda tudo e gera `resultados/RESUMO.md` |
| `cenario1/`, `cenario2/`, `cenario3/` | `trab01_blocos2SAT.cnf`, `trab01_blocos2SAT.map`, `resultado{1,2,3}.txt`, `plano{1,2,3}.txt`; subpastas por alvo (`resultado.txt`, `plano.txt`) |
| `resultados/RESUMO.md` | Tabela: T mínimo, BFS, variáveis, cláusulas, comparação com o manual |

Alvos principais (os arquivos da raiz de cada `cenarioN/`): cenário 1 → **Sf4** (T=4); cenário 2 → **S5** (T=5); cenário 3 → **S7** (T=6).
Todos os demais alvos (Sf1–Sf3, S1–S4, S1–S6) estão nas subpastas.

## Como executar

```bash
pip install -r requirements.txt            # só se não houver o binário `minisat`
cd src
python3 bw2cnf_var.py --cenario 1 --alvo Sf4 --horizonte 4 --saida ../cenario1
minisat ../cenario1/trab01_blocos2SAT.cnf ../cenario1/resultado1.txt      # ou: python3 rodar_sat.py ...
python3 interpretar.py ../cenario1/resultado1.txt --mapa ../cenario1/trab01_blocos2SAT.map --verbose --verificar
```

Tudo de uma vez (regenera dados, figuras e PDF): `./executar_tudo.sh`

## Resultados (resumo)

| Cenário | Alvo | T mínimo | BFS | Variáveis | Cláusulas |
|---|---|---|---|---|---|
| 1 | Sf1 / Sf2 / Sf3 / Sf4 | 8 / 9 / 2 / 4 | 8 / 9 / 2 / 4 | 2337 / 2606 / 723 / 1261 | 51817 / 58172 / 13687 / 26397 |
| 2 | S5 | 5 | 5 | 1530 | 32752 |
| 3 | S7 | 6 | 6 | 1799 | 39107 |

Nos 15 alvos testados o T mínimo do SAT coincide com o BFS, todos os planos foram validados pelo oráculo e,
nos 6 alvos resolvidos à mão, o comprimento manual é igual a T. Detalhes em `resultados/RESUMO.md`.

## Pontos importantes (leia antes de corrigir/entregar)

* **Correção ao esboço do manual:** `clr(y)` **não** é pré-condição de `move(b,y,p)`; senão `a` e `b` não poderiam ficar lado a lado sobre `c`
  (estados S5/S7). O exemplo de plano do esboço (`a` para a mesa em p=4 e depois `d` em p=2) era inválido.
* A relação `on` é **derivada**, não codificada; `clr` também é derivado (sem axioma de frame).
* Ordem parcial: derivada do plano do SAT (ligações causais `A —P→ B`), reduzida transitivamente e verificada por linearização (`--verificar`).
* O binário `minisat` não é obrigatório: `rodar_sat.py` usa MiniSat 2.2 via PySAT com o mesmo formato de saída.
* **Uso de IA (item 5 do enunciado):** o código Python foi gerado com auxílio de um chatbot (Claude, Anthropic) a partir da descrição formal e depois testado.
