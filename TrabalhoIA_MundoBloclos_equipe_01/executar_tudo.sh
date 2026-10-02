#!/usr/bin/env bash
# Regenera CNF/MAP/resultados de todos os cenários, figuras e o PDF do relatório.
set -e
cd "$(dirname "$0")/src"
pip install -r ../requirements.txt --break-system-packages -q 2>/dev/null || pip install -r ../requirements.txt -q
python3 rodar_todos.py
python3 gerar_figuras_tikz.py
cd ../latex && pdflatex -interaction=nonstopmode trab01.tex >/dev/null && pdflatex -interaction=nonstopmode trab01.tex >/dev/null
echo "Pronto: resultados/RESUMO.md e latex/trab01.pdf"
