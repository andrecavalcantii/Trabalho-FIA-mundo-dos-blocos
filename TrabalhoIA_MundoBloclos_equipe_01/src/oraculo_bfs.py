"""Oráculo: planejador BFS com as MESMAS regras do modelo, sem SAT.

Serve para (i) validar planos do SAT e (ii) comparar com os planos manuais.
Ação: ``(b, y, p)`` = mover b para cima de y (bloco ou 'T') começando no ponto p.
"""
from collections import deque
from math import ceil
from cenarios import BLOCKS, LEN, TABLE, MAX_POINT, MAX_LEVEL


def span(b, p):
    return set(range(p, p + LEN[b]))


def livre(s, b):
    """clr(b): nenhum bloco no nível acima sobrepondo o span de b."""
    p, l = s[b]
    return not any(s[x][1] == l + 1 and span(x, s[x][0]) & span(b, p)
                   for x in BLOCKS if x != b)


def acoes(s):
    """Gera (acao, novo_estado) para todas as ações legais em s."""
    for b in BLOCKS:
        if livre(s, b):
            yield from acoes_de(s, b)


def acoes_de(s, b):
    for y in [x for x in BLOCKS if x != b] + [TABLE]:
        l = 0 if y == TABLE else s[y][1] + 1
        if l > MAX_LEVEL:
            continue
        for p in range(MAX_POINT - LEN[b] + 1):
            novo = tentar(s, b, y, p, l)
            if novo is not None:
                yield (b, y, p), novo


def tentar(s, b, y, p, l):
    sp = span(b, p)
    if (p, l) == s[b]:
        return None
    if y != TABLE and not sp & span(y, s[y][0]):
        return None
    if any(s[x][1] == l and span(x, s[x][0]) & sp for x in BLOCKS if x != b):
        return None
    if l > 0:
        apoio = set()
        for x in BLOCKS:
            if x != b and s[x][1] == l - 1:
                apoio |= span(x, s[x][0]) & sp
        if len(apoio) < ceil(LEN[b] / 2):
            return None
    n = dict(s)
    n[b] = (p, l)
    return n


def aplicar(s, acao):
    """Aplica uma ação; devolve o novo estado ou None se ilegal."""
    b, y, p = acao
    if not livre(s, b):
        return None
    l = 0 if y == TABLE else s[y][1] + 1
    return tentar(s, b, y, p, l) if l <= MAX_LEVEL else None


def chave(s):
    return tuple(s[b] for b in BLOCKS)


def bfs(inicial, meta):
    """Plano mínimo (lista de ações) de inicial até satisfazer meta."""
    fila = deque([(inicial, [])])
    visto = {chave(inicial)}
    while fila:
        s, plano = fila.popleft()
        if all(s[b] == meta[b] for b in meta):
            return plano
        for a, n in acoes(s):
            k = chave(n)
            if k not in visto:
                visto.add(k)
                fila.append((n, plano + [a]))
    return None


def estavel(s):
    """Verifica integridade de um estado (sem sobreposição, apoio suficiente)."""
    for b in BLOCKS:
        p, l = s[b]
        for x in BLOCKS:
            if x != b and s[x][1] == l and span(x, s[x][0]) & span(b, p):
                return False
        if l > 0:
            apoio = set()
            for x in BLOCKS:
                if x != b and s[x][1] == l - 1:
                    apoio |= span(x, s[x][0]) & span(b, p)
            if len(apoio) < ceil(LEN[b] / 2):
                return False
    return True
