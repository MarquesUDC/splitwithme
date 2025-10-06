import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

from app.infra.config import AppConfig
from app.services.api_client import ApiClient
from app.views.friends_view import FriendsView
from app.views.expenses_view import ExpensesView


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, self_app):
        super().__init__(application=self_app, title="SplitWithMe (Desktop)")
        self.set_default_size(1000, 680)

        self.config = AppConfig(api_base_url="http://127.0.0.1:8000")
        self.api = ApiClient(self.config.api_base_url, self.config.request_timeout_s)

        # Header
        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label="SplitWithMe — Lectura"))
        self.set_titlebar(header)

        # Notebook con dos pestañas
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.TOP)

        # Friends tab
        self.friends_view = FriendsView(api_client=self.api)
        friends_label = Gtk.Label(label="Amigos")
        notebook.append_page(self.friends_view, friends_label)

        # Expenses tab
        self.expenses_view = ExpensesView(api_client=self.api)
        expenses_label = Gtk.Label(label="Gastos")
        notebook.append_page(self.expenses_view, expenses_label)

        self.set_child(notebook)

    def do_close_request(self, *args):
        try:
            self.api.close()
        except Exception:
            pass
        return super().do_close_request(*args)

