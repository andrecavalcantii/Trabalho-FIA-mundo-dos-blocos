#!/usr/bin/env python3
"""Mundo dos Blocos de Tamanho Variável -> CNF (DIMACS) + mapa de variáveis.

Uso:
    python3 bw2cnf_var.py --cenario 1 --alvo Sf4 --horizonte 4 --saida ../cenario1

Gera ``trab01_blocos2SAT.cnf`` e ``trab01_blocos2SAT.map`` em ``--saida``.
Veja docs/CODIFICACAO_CNF.md para a correspondência regra formal -> código.
"""
import argparse
import os
from itertools import combinations
from math import ceil
from cenarios import (BLOCKS, LEN, TABLE, MAX_POINT, SLOTS, MAX_LEVEL, CENARIOS)

LEVELS = range(MAX_LEVEL + 1)


def positions(b):
    """Pontos iniciais válidos de b: 0 .. 6 - len(b)."""
    return range(MAX_POINT - LEN[b] + 1)


def span(b, p):
    """Slots cobertos por b quando começa em p."""
    return list(range(p, p + LEN[b]))


def spans_overlap(b1, p1, b2, p2):
    return bool(set(span(b1, p1)) & set(span(b2, p2)))


class Codificador:
    def __init__(self, inicial, meta, horizonte):
        self.T = horizonte
        self.inicial, self.meta = inicial, meta
        self.n = 0
        self.v = {}          # chave simbólica -> id
        self.clausulas = []
        self.criar_variaveis()
        self.estado_inicial()
        self.meta_final()
        for t in range(self.T + 1):
            self.axiomas_estado(t)
        for t in range(self.T):
            self.axiomas_acao(t)

    # ---------- variáveis (a ordem de criação define os IDs) ----------
    def novo(self, *chave):
        self.n += 1
        self.v[chave] = self.n
        return self.n

    def criar_variaveis(self):
        for t in range(self.T + 1):
            for b in BLOCKS:
                for p in positions(b):
                    self.novo('at', b, p, t)
            for b in BLOCKS:
                for l in LEVELS:
                    self.novo('lev', b, l, t)
            for b in BLOCKS:
                self.novo('clr', b, t)
            for b in BLOCKS:                       # auxiliares de geometria
                for s in SLOTS:
                    self.novo('cob', b, s, t)      # b cobre o slot s
            for b in BLOCKS:
                for s in SLOTS:
                    for l in LEVELS:
                        self.novo('ocb', b, s, l, t)   # b ocupa (s, l)
            for s in SLOTS:
                for l in LEVELS:
                    self.novo('ocp', s, l, t)          # alguém ocupa (s, l)
        for t in range(self.T):
            for b in BLOCKS:
                for y in self.destinos(b):
                    for p in positions(b):
                        self.novo('mv', b, y, p, t)

    @staticmethod
    def destinos(b):
        return [y for y in BLOCKS if y != b] + [TABLE]

    # ---------- utilidades de cláusulas ----------
    def add(self, *lits):
        self.clausulas.append(list(lits))

    def exatamente_um(self, vs):
        self.add(*vs)
        for x, y in combinations(vs, 2):
            self.add(-x, -y)

    # ---------- 3.1 estado inicial e 3.2 meta ----------
    def estado_inicial(self):
        for b, (p, l) in self.inicial.items():
            self.add(self.v[('at', b, p, 0)])
            self.add(self.v[('lev', b, l, 0)])

    def meta_final(self):
        for b, (p, l) in self.meta.items():
            self.add(self.v[('at', b, p, self.T)])
            self.add(self.v[('lev', b, l, self.T)])

    # ---------- axiomas de estado (para todo t) ----------
    def axiomas_estado(self, t):
        v = self.v
        for b in BLOCKS:                                   # (A)(B) unicidade
            self.exatamente_um([v[('at', b, p, t)] for p in positions(b)])
            self.exatamente_um([v[('lev', b, l, t)] for l in LEVELS])
        self.geometria(t)
        self.exclusao_horizontal(t)
        self.estabilidade(t)
        self.clear(t)

    def geometria(self, t):
        """cob, ocb e ocp definidos por equivalência."""
        v = self.v
        for b in BLOCKS:
            for s in SLOTS:
                ats = [v[('at', b, p, t)] for p in positions(b) if s in span(b, p)]
                cob = v[('cob', b, s, t)]
                self.add(-cob, *ats)
                for a in ats:
                    self.add(-a, cob)
                for l in LEVELS:
                    ocb = v[('ocb', b, s, l, t)]
                    lev = v[('lev', b, l, t)]
                    self.add(-ocb, cob)
                    self.add(-ocb, lev)
                    self.add(-cob, -lev, ocb)
        for s in SLOTS:
            for l in LEVELS:
                ocp = v[('ocp', s, l, t)]
                ocbs = [v[('ocb', b, s, l, t)] for b in BLOCKS]
                self.add(-ocp, *ocbs)
                for o in ocbs:
                    self.add(-o, ocp)

    def exclusao_horizontal(self, t):
        """(C) dois blocos no mesmo nível não compartilham slot."""
        for s in SLOTS:
            for l in LEVELS:
                for b1, b2 in combinations(BLOCKS, 2):
                    self.add(-self.v[('ocb', b1, s, l, t)], -self.v[('ocb', b2, s, l, t)])

    def estabilidade(self, t):
        """(D) l>0: pelo menos ceil(len/2) slots do span apoiados no nível l-1.
        'pelo menos k de n' == todo subconjunto de tamanho n-k+1 tem um verdadeiro."""
        v = self.v
        for b in BLOCKS:
            n = LEN[b]
            k = ceil(n / 2)
            for p in positions(b):
                for l in LEVELS:
                    if l > 0:
                        base = [-v[('at', b, p, t)], -v[('lev', b, l, t)]]
                        for sub in combinations(span(b, p), n - k + 1):
                            self.add(*base, *[v[('ocp', s, l - 1, t)] for s in sub])

    def clear(self, t):
        """(E) clr(b) <-> nenhum slot do span de b ocupado no nível acima."""
        v = self.v
        for b in BLOCKS:
            for p in positions(b):
                for l in LEVELS:
                    base = [-v[('at', b, p, t)], -v[('lev', b, l, t)]]
                    clr = v[('clr', b, t)]
                    if l == MAX_LEVEL:
                        self.add(*base, clr)
                    else:
                        acima = [v[('ocp', s, l + 1, t)] for s in span(b, p)]
                        for o in acima:
                            self.add(*base, -clr, -o)
                        self.add(*base, clr, *acima)

    # ---------- axiomas de ação (t < T) ----------
    def axiomas_acao(self, t):
        v = self.v
        todos = [v[k] for k in v if k[0] == 'mv' and k[-1] == t]
        for x, y in combinations(todos, 2):                # (F) ação única
            self.add(-x, -y)
        for b in BLOCKS:
            for y in self.destinos(b):
                for p in positions(b):
                    self.move(b, y, p, t)
        self.frame(t)

    def move(self, b, y, p, t):
        v = self.v
        m = v[('mv', b, y, p, t)]
        self.add(-m, v[('clr', b, t)])                       # pré: topo de b livre
        self.add(-m, v[('at', b, p, t + 1)])                 # efeito: at(b,p)
        if y != TABLE:                                       # pré: span sobrepõe y
            for py in positions(y):
                if not spans_overlap(b, p, y, py):
                    self.add(-m, -v[('at', y, py, t)])
        opcoes = [([], 0)] if y == TABLE else \
                 [([-v[('lev', y, ly, t)]], ly + 1) for ly in LEVELS]
        for cond, l in opcoes:
            if l > MAX_LEVEL:
                self.add(-m, *cond)                          # não cabe acima
            else:
                self.efeitos_nivel(m, b, p, l, cond, t)

    def efeitos_nivel(self, m, b, p, l, cond, t):
        v = self.v
        self.add(-m, *cond, v[('lev', b, l, t + 1)])         # efeito: lev(b,l)
        for x in BLOCKS:                                     # pré: slots-alvo livres
            if x != b:
                for s in span(b, p):
                    self.add(-m, *cond, -v[('ocb', x, s, l, t)])
        self.add(-m, *cond, -v[('at', b, p, t)], -v[('lev', b, l, t)])   # sem no-op

    def frame(self, t):
        """Quem não se move mantém at e lev."""
        v = self.v
        for x in BLOCKS:
            movs = [v[k] for k in v if k[0] == 'mv' and k[1] == x and k[-1] == t]
            for p in positions(x):
                self.add(-v[('at', x, p, t)], v[('at', x, p, t + 1)], *movs)
            for l in LEVELS:
                self.add(-v[('lev', x, l, t)], v[('lev', x, l, t + 1)], *movs)

    # ---------- saída ----------
    def escrever(self, pasta):
        os.makedirs(pasta, exist_ok=True)
        with open(os.path.join(pasta, 'trab01_blocos2SAT.cnf'), 'w') as f:
            f.write(f"p cnf {self.n} {len(self.clausulas)}\n")
            for c in self.clausulas:
                f.write(' '.join(str(x) for x in c) + ' 0\n')
        with open(os.path.join(pasta, 'trab01_blocos2SAT.map'), 'w') as f:
            for chave, i in sorted(self.v.items(), key=lambda kv: kv[1]):
                f.write(f"{i} {chave[0]}({','.join(str(a) for a in chave[1:])})\n")


def gerar(inicial, meta, horizonte, pasta):
    """Gera CNF e MAP; devolve (num_vars, num_clausulas)."""
    c = Codificador(inicial, meta, horizonte)
    c.escrever(pasta)
    return c.n, len(c.clausulas)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cenario', type=int, required=True, choices=[1, 2, 3])
    ap.add_argument('--alvo', help='nome do estado-meta (padrão: o principal do cenário)')
    ap.add_argument('--horizonte', type=int, required=True)
    ap.add_argument('--saida', default='.')
    a = ap.parse_args()
    cen = CENARIOS[a.cenario]
    alvo = a.alvo or cen['padrao']
    nv, nc = gerar(cen['inicial'], cen['alvos'][alvo], a.horizonte, a.saida)
    print(f"Gerado: {nv} variaveis, {nc} clausulas")
    print("Arquivos: trab01_blocos2SAT.cnf, trab01_blocos2SAT.map")


if __name__ == '__main__':
    main()
