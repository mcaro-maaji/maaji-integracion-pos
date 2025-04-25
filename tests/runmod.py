"""Modulo para ejecutar cualquier otro modulo desde la raiz del proyecto."""

import os
import sys
import runpy
from .constants import SRC_DIR

# Establecer cwd en src/
os.chdir(SRC_DIR)

# Hacer que python busque los modulos en src/
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

if len(sys.argv) < 2:
    print("Uso: python tests/runmod.py core.utilidad")
    print("Uso: python -m tests.runmod core.utilidad")
else:
    runpy.run_module(sys.argv[1], run_name="__main__")
