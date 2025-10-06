
from typing import Any

class FriendsPresenter:
    """
    Orquesta casos de uso de Amigos para la FriendsView.
    Respeta MVP: el Presenter NO conoce widgets; solo llama a métodos de la vista.
    """
    def __init__(self, view, api_client):
        self.view = view
        self.api = api_client

    def load_friends(self, query: str = ""):
        try:
            friends = self.api.list_friends()
            if query:
                q = query.strip().lower()
                friends = [f for f in friends if q in str(f.get("name","")).lower()]
            self.view.show_friends(friends)
        except Exception as e:
            self.view.show_error(f"Error cargando amigos: {e}")

    def select_friend(self, friend_id: Any):
        try:
            friend = self.api.get_friend(friend_id)
            self.view.show_friend_detail(friend)
            # Cargar gastos asociados
            expenses = self.api.list_friend_expenses(friend_id)
            self.view.show_friend_expenses(expenses)
        except Exception as e:
            self.view.show_error(f"Error cargando detalle del amigo: {e}")
