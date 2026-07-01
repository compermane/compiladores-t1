"""
Testador automatico do compilador DOTA2Lang.
Executa todos os casos de teste em testes/ e verifica o resultado.
"""

import subprocess
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
TESTES_DIR = os.path.join(BASE, 'testes')
COMPILER = os.path.join(BASE, 'compilador.py')
VENV_PYTHON = os.path.join(BASE, '..', 'T4', 'venv', 'bin', 'python3')
PYTHON = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable

erros = 0
sucessos = 0

for f in sorted(os.listdir(TESTES_DIR)):
    if not f.endswith('.txt'):
        continue

    path = os.path.join(TESTES_DIR, f)
    nome = f.replace('.txt', '')
    print(f'Testando: {nome}...', end=' ')

    saida_path = '/tmp/saida_t6.html'
    result = subprocess.run(
        [PYTHON, COMPILER, path, saida_path],
        capture_output=True, text=True, timeout=30
    )

    with open(saida_path) as fp:
        saida = fp.read()

    if 'erro_' in f:
        if 'Fim da compilacao' in saida:
            print('OK (erro detectado)')
            sucessos += 1
        else:
            print('FALHA: esperava erro, mas nao houve')
            print(f'  Saida: {saida[:100]}')
            erros += 1
    elif 'sucesso_' in f or f == 'sucesso.txt':
        if 'Resultado: Partida viavel' in saida:
            print('OK (sucesso)')
            sucessos += 1
        else:
            print('FALHA: esperava sucesso')
            print(f'  Saida: {saida[:100]}')
            erros += 1

print(f'\nTotal: {sucessos + erros} | Sucessos: {sucessos} | Erros: {erros}')
