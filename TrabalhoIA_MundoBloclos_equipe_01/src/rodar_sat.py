#!/usr/bin/env python3
"""Executa o SAT solver e procura o menor horizonte T.

Usa o binário ``minisat`` se existir no PATH; caso contrário usa o motor
MiniSat 2.2 do PySAT (``pip install python-sat``). Em ambos os casos o arquivo
de resultado tem o formato do minisat: ``SAT`` + literais + ``0`` (ou ``UNSAT``).

Uso:
    python3 rodar_sat.py --cenario 1 --alvo Sf4 --saida ../cenario1 --resultado resultado1.txt
"""
import argparse
import os
import shutil
import subprocess
from bw2cnf_var import gerar
from cenarios import CENARIOS


def ler_dimacs(caminho):
    with open(caminho) as f:
        linhas = [l.split() for l in f if l.strip() and not l.startswith(('c', 'p'))]
    return [[int(x) for x in l if x != '0'] for l in linhas]


def resolver(cnf, resultado):
    """Resolve o CNF; escreve o resultado no formato minisat; devolve True se SAT."""
    if shutil.which('minisat'):
        subprocess.run(['minisat', cnf, resultado], capture_output=True)
        with open(resultado) as f:
            return f.readline().strip() == 'SAT'
    from pysat.solvers import Minisat22
    with Minisat22(bootstrap_with=ler_dimacs(cnf)) as s:
        sat = s.solve()
        with open(resultado, 'w') as f:
            f.write('SAT\n' + ' '.join(str(x) for x in s.get_model()) + ' 0\n' if sat else 'UNSAT\n')
    return sat


def procurar_minimo(inicial, meta, pasta, resultado, tmax=12):
    """Aumenta T = 0,1,2,... até SATISFIABLE. Devolve (T, log)."""
    log = []
    T, sat = 0, False
    while T <= tmax and not sat:
        nv, nc = gerar(inicial, meta, T, pasta)
        sat = resolver(os.path.join(pasta, 'trab01_blocos2SAT.cnf'),
                       os.path.join(pasta, resultado))
        log.append((T, nv, nc, 'SAT' if sat else 'UNSAT'))
        T += 1
    return (T - 1 if sat else None), log


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cenario', type=int, required=True, choices=[1, 2, 3])
    ap.add_argument('--alvo')
    ap.add_argument('--saida', default='.')
    ap.add_argument('--resultado', default='resultado.txt')
    ap.add_argument('--tmax', type=int, default=12)
    a = ap.parse_args()
    cen = CENARIOS[a.cenario]
    alvo = a.alvo or cen['padrao']
    T, log = procurar_minimo(cen['inicial'], cen['alvos'][alvo], a.saida, a.resultado, a.tmax)
    for t, nv, nc, st in log:
        print(f"T={t}: {nv} variaveis, {nc} clausulas -> {st}")
    print(f"T minimo = {T}" if T is not None else "sem plano ate tmax")


if __name__ == '__main__':
    main()
