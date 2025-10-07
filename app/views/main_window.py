import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk

from app.views.friends_view import FriendsView
from app.views.expenses_view import ExpensesView
from app.services.api_client import ApiClient


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, self_app):
        super().__init__(application=self_app, title="SplitWithMe")
        self.set_default_size(900, 600)

        # --- CSS ---
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("style.css")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # --- Layout principal ---
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.set_child(main_box)

        # --- Sidebar ---
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sidebar.set_size_request(200, -1)
        sidebar.add_css_class("sidebar")

        title_label = Gtk.Label(label="SplitWithMe")
        title_label.add_css_class("sidebar-title")
        sidebar.append(title_label)

        self.friends_button = Gtk.Button(label="Friends")
        self.friends_button.add_css_class("sidebar-button")

        self.expenses_button = Gtk.Button(label="Expenses")
        self.expenses_button.add_css_class("sidebar-button")

        sidebar.append(self.friends_button)
        sidebar.append(self.expenses_button)

        # --- Área principal ---
        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.stack.set_hexpand(True)

        # API client
        self.api_client = ApiClient("http://127.0.0.1:8000")

        # Vistas
        self.friends_view = FriendsView(self.api_client)
        self.expenses_view = ExpensesView(self.api_client)

        self.stack.add_titled(self.friends_view, "friends", "Friends")
        self.stack.add_titled(self.expenses_view, "expenses", "Expenses")

        self.stack.set_visible_child_name("friends")

        self.friends_button.connect("clicked", self.show_friends)
        self.expenses_button.connect("clicked", self.show_expenses)

        # --- Botón "Create an expense" ---
        create_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        create_box.set_margin_top(40)
        create_box.set_margin_bottom(20)
        create_box.set_margin_start(20)
        create_box.set_margin_end(20)
        create_box.set_spacing(15)

        create_button = Gtk.Button(label="Create an expense")
        create_button.add_css_class("create-button")

        # 👉 conecta al método de ExpensesView
        create_button.connect("clicked", self.expenses_view.on_add_clicked)

        create_box.append(create_button)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.append(self.stack)
        content_box.append(create_box)

        main_box.append(sidebar)
        main_box.append(content_box)

    # --- Acciones ---
    def show_friends(self, button):
        self.stack.set_visible_child_name("friends")

    def show_expenses(self, button):
        self.stack.set_visible_child_name("expenses")

