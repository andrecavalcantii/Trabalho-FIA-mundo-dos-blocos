#!/usr/bin/env python3
"""Gera latex/figuras_cenarioN.tex (estados desenhados em TikZ) a partir de cenarios.py."""
import os
from cenarios import CENARIOS, LEN

COR = {'a': 'violet!70', 'b': 'yellow!90', 'c': 'cyan!70', 'd': 'red!80'}
U, H = 0.42, 0.42      # unidade horizontal e altura de cada nível (cm)


def desenho(estado):
    s = ['\\begin{tikzpicture}[x=%.2fcm,y=%.2fcm,font=\\scriptsize]' % (U, H)]
    for b, (p, l) in estado.items():
        s.append(f"\\draw[fill={COR[b]}] ({p},{l}) rectangle ({p + LEN[b]},{l + 1});"
                 f"\\node at ({p + LEN[b] / 2},{l + 0.5}) {{{b}}};")
    s.append('\\draw[thick] (0,0) -- (6,0);')
    for k in range(7):
        s.append(f"\\draw (%d,0) -- (%d,-0.15) node[below,font=\\tiny] {{%d}};" % (k, k, k))
    s.append('\\end{tikzpicture}')
    return '\n'.join(s)


def figura(n, cen):
    estados = [('$S_0$', cen['inicial'])] + [(f"${k[0]}_{{{k[1:]}}}$" if k.startswith('Sf')
               else f"$S_{{{k[1:]}}}$", v) for k, v in cen['alvos'].items()]
    linhas = []
    for i, (nome, est) in enumerate(estados):
        linhas.append('\\begin{minipage}[b]{0.31\\textwidth}\\centering\n' + desenho(est)
                      + f'\\\\[2pt] {nome}\\end{{minipage}}' + ('\\\\[8pt]' if i % 3 == 2 else '\\hfill'))
    return '\n'.join(linhas)


def main():
    pasta = os.path.join(os.path.dirname(__file__), '..', 'latex')
    os.makedirs(pasta, exist_ok=True)
    for n, cen in CENARIOS.items():
        with open(os.path.join(pasta, f'figuras_cenario{n}.tex'), 'w') as f:
            f.write(figura(n, cen))


if __name__ == '__main__':
    main()
