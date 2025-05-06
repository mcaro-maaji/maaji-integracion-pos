"""Modulo para ejecutar cualquier otro modulo desde la raiz del proyecto."""

import os
import sys
import runpy
import subprocess
from .constants import SRC_DIR

# Establecer cwd en src/
os.chdir(SRC_DIR.resolve())

# Agregar src/ al path si no está
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

def main():
    """Ejecutar con Subprocess o con Runpy."""
    if len(sys.argv) < 2:
        print("Uso: python -m tests.runmod <modulo> [--as-subprocess] [args...]")
        return

    args = sys.argv[1:]
    as_subprocess = False

    if "--as-subprocess" in args:
        args.remove("--as-subprocess")
        as_subprocess = True

    module = args[0]
    module_args = args[1:]

    # forzar ejecución como subproceso
    if as_subprocess:
        subprocess.run([sys.executable, "-m", module, *module_args], check=False)
    else:
        # usar runpy equivalente a ejecutar python -m <module>
        try:
            runpy.run_module(module, run_name="__main__")
        except ModuleNotFoundError as e:
            print(f"❌ Módulo no encontrado: {module}")
            print(e)
        except Exception as e:
            print(f"❌ Error al ejecutar el módulo '{module}': {e}")
            raise

if __name__ == "__main__":
    main()
