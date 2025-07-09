from pathlib import Path
from src.core.clients import ClientsCegid

path = Path(r"C:\Users\MC\OneDrive - MAS S.A.S (1)\Documentos\INTERFAZ CONTABLE\2025-ABRIL\Clientes\Planos")
path_saved = path.parent / "Planos corregidos"

for f in path.glob(".txt"):
    print(f)
