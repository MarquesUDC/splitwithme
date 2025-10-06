from app.services.api_client import ApiClient

class ExpensesPresenter:
    def __init__(self, view, api_client):
        self.view = view
        self.api_client = api_client

    def load_expenses(self, query=None):
        try:
            if query:
                # Si hay texto en el campo de búsqueda
                expenses = [self.api_client.get_expense(query)]
            else:
                # Si no hay texto, carga todos los gastos
                expenses = self.api_client.list_expenses()
            self.view.show_expenses(expenses)
        except Exception as e:
            self.view.show_error(f"Error cargando gastos: {e}")

    def select_expense(self, expense_id):
        try:
            expense = self.api_client.get_expense(expense_id)
            self.view.show_expense_detail(expense)
        except Exception as e:
            self.view.show_error(f"Error cargando detalle del gasto: {e}")
    def create_expense(self, description, date, amount):
        data = {
            "id": 0,
            "description": description,
            "date": date,
            "amount": amount,
            "credit_balance": 0,
            "num_friends": 1
        }
        r = self._client.post("/expenses/", json=data)
        r.raise_for_status()
        return r.json()


    def update_expense(self, expense_id, data):
        try:
            self.api_client.update_expense(expense_id, data)
            self.load_expenses()
            self.view.show_status("Gasto actualizado correctamente.")
        except Exception as e:
            self.view.show_error(f"Error al actualizar gasto: {e}")

    def delete_expense(self, expense_id):
        try:
            self.api_client.delete_expense(expense_id)
            self.load_expenses()
            self.view.show_status("Gasto eliminado.")
        except Exception as e:
            self.view.show_error(f"Error al eliminar gasto: {e}")
    def add_expense(self, description, amount):
        try:
            data = {
                "description": description,
                "date": "2025-10-06",  # o datetime.date.today().isoformat()
                "amount": float(amount)
            }
            self.api_client.create_expense(data)
            self.view.show_status("Gasto añadido correctamente.")
            self.load_expenses()
        except Exception as e:
            self.view.show_error(f"Error creando gasto: {e}")

