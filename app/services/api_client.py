import httpx


class ApiClient:
    """
    Cliente HTTP hacia tu servidor FastAPI.

    Endpoints asumidos:
      - GET /friends/
      - GET /friends/{id}/
      - GET /friends/{id}/expenses/
      - GET /expenses/
      - GET /expenses/{id}/
      - POST /expenses/
      - PUT /expenses/{id}/
      - DELETE /expenses/{id}/
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout_s: float = 10.0):
        self._base_url = base_url
        self._timeout_s = timeout_s
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=self._timeout_s,
            follow_redirects=True
        )

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
        """Obtiene los gastos desde el backend, opcionalmente filtrando por ID o descripción."""
        if query:
            if query.isdigit():
                r = self._client.get(f"/expenses/{query}")
                r.raise_for_status()
                return [r.json()]
            else:
                r = self._client.get("/expenses/", params={"search": query})
                r.raise_for_status()
                return r.json()
        else:
            r = self._client.get("/expenses/")
            r.raise_for_status()
            return r.json()

    def get_expense(self, expense_id: int | str):
        r = self._client.get(f"/expenses/{expense_id}/")
        r.raise_for_status()
        return r.json()

    def create_expense(self, description: str, date: str, amount: float):
        """Crea un nuevo gasto."""
        data = {
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
        data.pop("id", None)
        data.setdefault("credit_balance", 0.0)
        data.setdefault("num_friends", 1)
        r = self._client.put(f"/expenses/{expense_id}/", json=data)
        r.raise_for_status()
        return r.json() if r.text else {}

    def delete_expense(self, expense_id: int | str):
        """Elimina un gasto."""
        r = self._client.delete(f"/expenses/{expense_id}/")
        r.raise_for_status()
        return {"deleted": expense_id}

    # ---- Util ----
    def close(self):
        """Cierra la sesión HTTP limpia y segura."""
        try:
            self._client.close()
        except Exception:
            pass

    def __del__(self):
        self.close()

