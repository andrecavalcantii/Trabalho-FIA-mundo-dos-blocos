#!/usr/bin/env python3
"""Traduz a saída do SAT solver (inteiros) em plano, estado final, relações on
e ordem parcial, usando o arquivo .map.

Uso:
    python3 interpretar.py resultado1.txt --mapa trab01_blocos2SAT.map [--verbose] [--verificar]
"""
import argparse
import re
from itertools import product
from cenarios import BLOCKS, LEN, TABLE, CENARIOS
import oraculo_bfs as orc


# ---------------------------------------------------------------- leitura
def ler_mapa(caminho):
    """{id: (nome, args)}; argumentos numéricos viram int."""
    mapa = {}
    with open(caminho) as f:
        for linha in f:
            m = re.match(r'^(\d+)\s+(\w+)\((.*)\)$', linha.strip())
            if m:
                args = tuple(int(a) if a.lstrip('-').isdigit() else a
                             for a in m.group(3).split(','))
                mapa[int(m.group(1))] = (m.group(2), args)
    return mapa


def ler_resultado(caminho):
    """(status, conjunto de variáveis verdadeiras). Aceita saída só com positivos."""
    with open(caminho) as f:
        linhas = f.read().strip().split('\n')
    status = linhas[0].strip()
    lits = [int(x) for x in linhas[1].split()] if status == 'SAT' and len(linhas) > 1 else []
    return status, {x for x in lits if x > 0}


def reconstruir(mapa, verdadeiras):
    """Devolve (plano, estados) com estados[t] = {bloco: (p, l)}."""
    estados, plano = {}, []
    for i in sorted(verdadeiras):
        nome, a = mapa[i]
        if nome == 'at':
            estados.setdefault(a[2], {}).setdefault(a[0], [None, None])[0] = a[1]
        if nome == 'lev':
            estados.setdefault(a[2], {}).setdefault(a[0], [None, None])[1] = a[1]
        if nome == 'mv':
            plano.append((a[3], a[0], a[1], a[2]))        # (t, b, y, p)
    estados = {t: {b: tuple(v) for b, v in e.items()} for t, e in estados.items()}
    return sorted(plano), estados


# ---------------------------------------------------------------- relações
def derivar_on(s):
    """on(b,y): b apoiado em y (mesa se l=0; ponte => vários apoios)."""
    rel = {}
    for b in BLOCKS:
        p, l = s[b]
        rel[b] = [TABLE] if l == 0 else [
            y for y in BLOCKS if y != b and s[y][1] == l - 1
            and orc.span(y, s[y][0]) & orc.span(b, p)]
    return rel


def texto_acao(b, y, p):
    destino = 'a MESA' if y == TABLE else f"CIMA de '{y}'"
    return f"mover bloco '{b}' para {destino} em p={p}"


# ---------------------------------------------------------------- ordem parcial
def pegadas(s, acao):
    """(escreve, le) da ação no estado s, como conjuntos de itens atômicos:
    ('blk',x) = posição do bloco x; ('cel',slot,nivel) = ocupação da célula."""
    b, y, p = acao
    po, lo = s[b]
    ln = 0 if y == TABLE else s[y][1] + 1
    velhas = {('cel', k, lo) for k in orc.span(b, po)}
    novas = {('cel', k, ln) for k in orc.span(b, p)}
    acima = {('cel', k, lo + 1) for k in orc.span(b, po)}
    sob = {('cel', k, ln - 1) for k in orc.span(b, p)} if ln > 0 else set()
    escreve = {('blk', b)} | velhas | novas
    le = ({('blk', y)} if y != TABLE else set()) | acima | sob | novas
    return escreve, le


def ordem_parcial(estado0, plano):
    """Arestas (i, j, tipo, itens): i deve preceder j.
    tipo: 'causal' (i produz P que j consome, A —P→ B), 'escrita' (WAW) ou
    'protecao' (j sobrescreve o que i leu). Reduzida transitivamente."""
    s, pg = dict(estado0), []
    for (_, b, y, p) in plano:
        pg.append(pegadas(s, (b, y, p)))
        s = orc.aplicar(s, (b, y, p))
    n = len(plano)
    bruto = {}
    for i in range(n):
        for j in range(i + 1, n):
            w1, r1 = pg[i]
            w2, r2 = pg[j]
            causal, waw, anti = w1 & r2, w1 & w2, r1 & w2
            if causal or waw or anti:
                bruto[(i, j)] = ('causal', causal) if causal else (
                    ('escrita', waw) if waw else ('protecao', anti))
    alcance = {(i, j) for (i, j) in bruto}
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if (i, k) in alcance and (k, j) in alcance:
                    alcance.add((i, j))
    reduzido = [(i, j) + bruto[(i, j)] for (i, j) in sorted(bruto)
                if not any((i, k) in alcance and (k, j) in alcance for k in range(n))]
    return reduzido


def descrever_itens(itens):
    partes = sorted(f"posicao de '{x[1]}'" if x[0] == 'blk' else f"celula(slot {x[1]}, nivel {x[2]})"
                    for x in itens)
    return ', '.join(partes[:3]) + ('...' if len(partes) > 3 else '')


def linearizacoes_validas(estado0, plano, arestas, limite=500):
    """Testa se TODA ordem topológica (até 'limite') é executável pelo oráculo."""
    n = len(plano)
    pred = {j: {i for (i, jj, *_ ) in arestas if jj == j} for j in range(n)}
    ok, total = 0, 0

    def rec(feitos, s):
        nonlocal ok, total
        if total >= limite:
            return
        if len(feitos) == n:
            total += 1
            ok += 1
            return
        for j in range(n):
            if j not in feitos and pred[j] <= feitos:
                novo = orc.aplicar(s, plano[j][1:])
                if novo is None:
                    total += 1
                else:
                    rec(feitos | {j}, novo)
    rec(frozenset(), dict(estado0))
    return ok, total


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('resultado')
    ap.add_argument('--mapa', default='trab01_blocos2SAT.map')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--verificar', action='store_true',
                    help='re-executa o plano no oráculo independente do SAT')
    a = ap.parse_args()
    status, verd = ler_resultado(a.resultado)
    if status != 'SAT':
        print(f"Plano inexistente com este horizonte ({status}).")
        return
    mapa = ler_mapa(a.mapa)
    plano, estados = reconstruir(mapa, verd)
    T = max(estados)
    print(f"PLANO ENCONTRADO ({len(plano)} acoes):")
    for k, (t, b, y, p) in enumerate(plano, 1):
        print(f"{k}. t={t}: {texto_acao(b, y, p)}")
    print(f"\nESTADO FINAL (t={T}):")
    for b in BLOCKS:
        print(f"{b}: ponto inicial p={estados[T][b][0]}, nivel l={estados[T][b][1]}")
    print(f"\nRELACOES 'on' em t={T}:")
    for b, ys in derivar_on(estados[T]).items():
        print(f"{b} esta " + ('na MESA' if ys == [TABLE] else 'sobre: ' + ', '.join(ys)
              + (' (ponte)' if len(ys) > 1 else '')))
    arestas = ordem_parcial(estados[0], plano)
    print("\nORDEM PARCIAL (A —P→ B), reduzida transitivamente:")
    for (i, j, tipo, itens) in arestas:
        print(f"  acao {i + 1} < acao {j + 1}  [{tipo}: {descrever_itens(itens)}]")
    if a.verbose:
        print("\nESTADOS (t: bloco@ponto/nivel)")
        for t in sorted(estados):
            print(f"t={t}: " + '  '.join(f"{b}@{estados[t][b][0]}/{estados[t][b][1]}" for b in BLOCKS))
    if a.verificar:
        s = dict(estados[0])
        for (_, b, y, p) in plano:
            s = orc.aplicar(s, (b, y, p)) if s is not None else None
        valido = s is not None and all(s[b] == estados[T][b] for b in BLOCKS) and orc.estavel(s)
        ok, tot = linearizacoes_validas(estados[0], plano, arestas)
        print(f"\nVERIFICACAO: plano valido no oraculo = {valido}; "
              f"linearizacoes validas da ordem parcial = {ok}/{tot}")


if __name__ == '__main__':
    main()
