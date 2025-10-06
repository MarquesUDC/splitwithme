import httpx

class ApiClient:
    """
    Cliente HTTP hacia tu servidor FastAPI, solo lectura.

    Endpoints asumidos (según tu backend):
      - GET /friends/
      - GET /friends/{id}/
      - GET /friends/{id}/expenses/
      - GET /expenses/
      - GET /expenses/{id}/
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout_s: float = 10.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout_s, follow_redirects=True)

    # ---- Friends ----
    def list_friends(self):
        r = self._client.get("/friends/")
        r.raise_for_status()
        return r.json()

    def get_friend(self, friend_id: int | str):
        r = self._client.get(f"/friends/{friend_id}/")
        r.raise_for_status()
        return r.json()

    def list_friend_expenses(self, friend_id: int | str):
        r = self._client.get(f"/friends/{friend_id}/expenses/")
        r.raise_for_status()
        return r.json()

    # ---- Expenses ----
    def list_expenses(self, query: str | None = None):
        """Obtiene los gastos desde el backend, opcionalmente filtrando por id o descripción."""
        if query:
            # Si la búsqueda parece un número, busca por ID exacto
            if query.isdigit():
                r = self._client.get(f"/expenses/{query}")
                r.raise_for_status()
                # Devuelve una lista con un solo gasto para mantener formato uniforme
                return [r.json()]
            else:
                # Si no es número, asume búsqueda por descripción (si el backend soporta ?search=)
                r = self._client.get("/expenses/", params={"search": query})
                r.raise_for_status()
                return r.json()
        else:
            # Sin filtro: devuelve todos
            r = self._client.get("/expenses/")
            r.raise_for_status()
            return r.json()

    def get_expense(self, expense_id: int | str):
        r = self._client.get(f"/expenses/{expense_id}/")
        r.raise_for_status()
        return r.json()

    # ---- Util ----
    def close(self):
        try:
            self._client.close()
        except Exception:
            pass
    def create_expense(self, description: str, date: str, amount: float):
        """Crea un nuevo gasto."""
        data = {
            "id": 0,
            "description": description,
            "date": date,
            "amount": amount,
            "credit_balance": 0.0,
            "num_friends": 1
        }
        r = self._client.post("/expenses/", json=data)
        r.raise_for_status()
        return r.json()

    def update_expense(self, expense_id: int | str, data: dict):
        """Actualiza un gasto existente."""
        # completamos campos faltantes
        data.setdefault("credit_balance", 0.0)
        data.setdefault("num_friends", 1)
        r = self._client.put(f"/expenses/{expense_id}/", json=data)
        r.raise_for_status()
        return r.json() if r.text else {}    

    def delete_expense(self, expense_id: int | str):
        r = self._client.delete(f"/expenses/{expense_id}/")
        r.raise_for_status()
        # ---- Crear, editar y eliminar gastos ----

    def create_expense(self, description: str, date: str, amount: float):
        """Crea un nuevo gasto."""
        data = {"description": description, "date": date, "amount": amount}
        r = self._client.post("/expenses/", json=data)
        r.raise_for_status()
        return r.json()

    def update_expense(self, expense_id: int, description: str, date: str, amount: float):
        """Modifica un gasto existente."""
        data = {"description": description, "date": date, "amount": amount}
        r = self._client.put(f"/expenses/{expense_id}", json=data)
        r.raise_for_status()
        return r.json()

    def delete_expense(self, expense_id: int):
        """Elimina un gasto existente."""
        r = self._client.delete(f"/expenses/{expense_id}")
        r.raise_for_status()
        return {"deleted": expense_id}

