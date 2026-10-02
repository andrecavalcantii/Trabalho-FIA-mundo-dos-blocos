#!/usr/bin/env python3
"""Roda todos os cenários/alvos: acha T mínimo, grava CNF/MAP/resultado, interpreta,
compara com o oráculo BFS e com os planos manuais. Gera resultados/RESUMO.md e
resultados/tabela.tex.   Uso:  python3 rodar_todos.py
"""
import os
import shutil
import subprocess
import sys
from cenarios import CENARIOS
from rodar_sat import procurar_minimo
from interpretar import ler_mapa, ler_resultado, reconstruir
from planos_manuais import MANUAIS
import oraculo_bfs as orc

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def rodar_alvo(n, alvo, cen):
    pasta = os.path.join(RAIZ, f'cenario{n}', alvo)
    os.makedirs(pasta, exist_ok=True)
    T, log = procurar_minimo(cen['inicial'], cen['alvos'][alvo], pasta, 'resultado.txt')
    saida = subprocess.run([sys.executable, 'interpretar.py', os.path.join(pasta, 'resultado.txt'),
                            '--mapa', os.path.join(pasta, 'trab01_blocos2SAT.map'),
                            '--verbose', '--verificar'], capture_output=True, text=True,
                           cwd=os.path.dirname(__file__)).stdout
    with open(os.path.join(pasta, 'plano.txt'), 'w') as f:
        f.write(saida)
    _, verd = ler_resultado(os.path.join(pasta, 'resultado.txt'))
    plano, _ = reconstruir(ler_mapa(os.path.join(pasta, 'trab01_blocos2SAT.map')), verd)
    return T, log, [(b, y, p) for (_, b, y, p) in plano], 'True' in saida.split('VERIFICACAO')[-1].split(';')[0]


def promover_padrao(n, alvo):
    """Copia CNF/MAP/resultado do alvo principal para cenarioN/ (nomes do enunciado)."""
    base = os.path.join(RAIZ, f'cenario{n}')
    for nome, dest in [('trab01_blocos2SAT.cnf', 'trab01_blocos2SAT.cnf'),
                       ('trab01_blocos2SAT.map', 'trab01_blocos2SAT.map'),
                       ('resultado.txt', f'resultado{n}.txt'),
                       ('plano.txt', f'plano{n}.txt')]:
        shutil.copy(os.path.join(base, alvo, nome), os.path.join(base, dest))


def limpar_extras(n, padrao):
    """Nas subpastas por alvo mantém só resultado e plano (CNF/MAP se regeneram)."""
    base = os.path.join(RAIZ, f'cenario{n}')
    for alvo in CENARIOS[n]['alvos']:
        for nome in ('trab01_blocos2SAT.cnf', 'trab01_blocos2SAT.map'):
            os.remove(os.path.join(base, alvo, nome))


def main():
    linhas, tex = [], []
    for n, cen in CENARIOS.items():
        for alvo in cen['alvos']:
            T, log, plano, valido = rodar_alvo(n, alvo, cen)
            ref = orc.bfs(cen['inicial'], cen['alvos'][alvo])
            man = MANUAIS.get((n, alvo))
            cmp_man = '-' if man is None else ('igual' if man == plano else f'{len(man)} acoes, plano distinto')
            nv, nc = log[-1][1], log[-1][2]
            unsat = ', '.join(str(t) for t, _, _, st in log if st == 'UNSAT') or '-'
            linhas.append((n, alvo, T, len(ref), nv, nc, unsat, valido, cmp_man))
            print(f"cenario {n} {alvo}: T*={T} BFS={len(ref)} vars={nv} cls={nc} valido={valido} manual={cmp_man}")
        promover_padrao(n, cen['padrao'])
        limpar_extras(n, cen['padrao'])
    os.makedirs(os.path.join(RAIZ, 'resultados'), exist_ok=True)
    with open(os.path.join(RAIZ, 'resultados', 'RESUMO.md'), 'w') as f:
        f.write('| Cenario | Alvo | T minimo (SAT) | BFS | Vars | Clausulas | UNSAT em T= | Plano valido | vs. manual |\n')
        f.write('|---|---|---|---|---|---|---|---|---|\n')
        for l in linhas:
            f.write('| ' + ' | '.join(str(x) for x in l) + ' |\n')
    with open(os.path.join(RAIZ, 'latex', 'tabela_resultados.tex'), 'w') as f:
        f.write('\\begin{center}\\small\\begin{tabular}{@{}rlrrrrl@{}}\\toprule\n')
        f.write('Cen. & Alvo & $T^*$ (SAT) & BFS & Vars & Cl\\\'ausulas & V\\\'alido \\\\\\midrule\n')
        for (n, alvo, T, bfs_len, nv, nc, unsat, valido, cm) in linhas:
            f.write(f"{n} & {alvo} & {T} & {bfs_len} & {nv} & {nc} & {'sim' if valido else 'nao'} \\\\\n")
        f.write('\\bottomrule\\end{tabular}\\end{center}\n')


if __name__ == '__main__':
    main()
