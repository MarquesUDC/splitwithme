"""
Script de población de datos de prueba.

Estrategia:
1) Intentar POST /admin/fixtures con datos deterministas (si el servidor lo soporta).
2) Si devuelve 404/405, informar y recordar que tu servidor ya inicializa la BD
   en el arranque con Faker si está vacía (init_db_if_empty()).
"""
import os
import json
import httpx
from pathlib import Path

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
FIXTURES = Path(__file__).parent / "fixtures" / "demo_data.json"

def try_post_fixtures():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    with httpx.Client(base_url=API_BASE, timeout=15.0) as c:
        r = c.post("/admin/fixtures", json=data)
        if r.status_code >= 400:
            raise RuntimeError(f"POST /admin/fixtures -> {r.status_code} {r.text}")
        print("Fixtures cargadas correctamente:", r.json())

if __name__ == "__main__":
    try:
        try_post_fixtures()
    except Exception as e:
        print("No se pudo cargar fixtures por endpoint /admin/fixtures.")
        print(f"Motivo: {e}")
        print("\nAlternativa: arranca el servidor sin datos; si la BD está vacía,")
        print("se poblará automáticamente con Faker (init_db_if_empty).")
        print("Si quieres datos deterministas, pídeme y te genero un script")
        print("que inserte directamente con SQLModel dentro del repo del servidor.")

