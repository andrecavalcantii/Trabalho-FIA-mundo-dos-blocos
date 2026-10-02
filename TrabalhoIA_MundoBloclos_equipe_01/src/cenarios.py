"""Definição dos blocos e dos cenários (Situações 1, 2 e 3 do enunciado).

Convenção de estado: ``{bloco: (ponto_inicial, nivel)}``.
O eixo tem pontos 0..6 e, portanto, 6 slots [0,1],...,[5,6].
"""

BLOCKS = ['a', 'b', 'c', 'd']
LEN = {'a': 1, 'b': 1, 'c': 2, 'd': 3}   # comprimento em unidades (uc)
TABLE = 'T'
MAX_POINT = 6                            # pontos 0..6 => slots 0..5
SLOTS = range(MAX_POINT)
MAX_LEVEL = 3                            # níveis 0 (mesa) .. 3


def est(**k):
    return dict(k)


# ---------------- Situação 1 (e S0 da Situação 3) ----------------
S0_SIT1 = est(c=(0, 0), a=(3, 0), b=(5, 0), d=(3, 1))
SIT1 = {
    'Sf1': est(d=(3, 0), a=(4, 1), b=(5, 1), c=(4, 2)),
    'Sf2': est(d=(3, 0), c=(4, 1), a=(4, 2), b=(5, 2)),
    'Sf3': est(c=(0, 0), a=(2, 0), b=(5, 0), d=(0, 1)),
    'Sf4': est(c=(0, 0), d=(2, 0), b=(5, 0), a=(0, 1)),
}

# ---------------- Situação 2 ----------------
S0_SIT2 = est(c=(0, 0), d=(3, 0), a=(0, 1), b=(1, 1))
SIT2 = {
    'S1': est(c=(0, 0), b=(2, 0), d=(3, 0), a=(0, 1)),
    'S2': est(c=(0, 0), b=(2, 0), d=(3, 0), a=(2, 1)),
    'S3': est(b=(2, 0), d=(3, 0), a=(2, 1), c=(4, 1)),
    'S4': est(b=(2, 0), d=(3, 0), c=(4, 1), a=(4, 2)),
    'S5': est(d=(3, 0), c=(4, 1), a=(4, 2), b=(5, 2)),
}

# ---------------- Situação 3 ----------------
SIT3 = {
    'S1': est(c=(0, 0), d=(0, 1), a=(3, 0), b=(5, 0)),
    'S2': est(c=(0, 0), d=(0, 1), b=(5, 0), a=(5, 1)),
    'S3': est(c=(0, 0), d=(2, 0), b=(5, 0), a=(5, 1)),
    'S4': est(c=(0, 0), d=(2, 0), b=(5, 0), a=(0, 1)),
    'S5': est(c=(0, 0), d=(2, 0), a=(0, 1), b=(1, 1)),
    'S6': est(c=(0, 0), d=(2, 0), a=(0, 1), b=(1, 1)),   # idêntico a S5 na figura
    'S7': est(c=(0, 0), d=(3, 0), a=(0, 1), b=(1, 1)),
}

CENARIOS = {
    1: {'inicial': S0_SIT1, 'alvos': SIT1, 'padrao': 'Sf4'},
    2: {'inicial': S0_SIT2, 'alvos': SIT2, 'padrao': 'S5'},
    3: {'inicial': S0_SIT1, 'alvos': SIT3, 'padrao': 'S7'},
}
