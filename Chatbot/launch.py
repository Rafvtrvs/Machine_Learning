"""
Arranca el chatbot usando SIEMPRE el paquete `backend` de esta misma carpeta.

Se pone esta carpeta al *inicio* de sys.path y se importa con el importador normal
(`from backend.main import app`). Es lo que corrige errores raros de Pydantic con
`/chat` cuando se usaba exec_module / nombre de módulo artificial.
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent
_root_str = str(_PROJECT_ROOT)

if sys.path[0] != _root_str:
    if _root_str in sys.path:
        sys.path.remove(_root_str)
    sys.path.insert(0, _root_str)

from backend.main import app  # noqa: E402 — necesita PATH ya ajustado

__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn

    print("Servidor Chatbot malvekee:")
    print(f"   Código: {_PROJECT_ROOT / 'backend' / 'main.py'}")
    print("   Panel:   http://127.0.0.1:8855/")
    print("   Prueba:  http://127.0.0.1:8855/malvekee-identidad")

    uvicorn.run(app, host="127.0.0.1", port=8855)
