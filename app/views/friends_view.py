import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

from app.presenters.friends_presenter import FriendsPresenter


class FriendsView(Gtk.Box):
    """
    Vista de Amigos modernizada:
    - Búsqueda de amigos
    - Lista visual con nombre, usuario y balances (Debit / Credit)
    - Sin opción de añadir amigo
    """
    def __init__(self, api_client):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10,
                         margin_top=12, margin_bottom=12, margin_start=12, margin_end=12)

        self.presenter = FriendsPresenter(self, api_client)
        self._friends_data = []

        # --- Barra superior (búsqueda) ---
        top_bar = Gtk.Box(spacing=8)
        self.search_entry = Gtk.Entry(placeholder_text="Search for your friend")
        btn_search = Gtk.Button(label="Search")
        btn_search.connect("clicked", self.on_search_clicked)

        btn_reload = Gtk.Button(label="Reload")
        btn_reload.connect("clicked", self.on_reload_clicked)

        top_bar.append(self.search_entry)
        top_bar.append(btn_search)
        top_bar.append(btn_reload)

        # --- Contenedor principal de contenido ---
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)

        # Título
        title = Gtk.Label(label="List of friends")
        title.set_xalign(0)
        title.add_css_class("section-title")
        self.content_box.append(title)

        # Scrolled window para lista de amigos
        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("friends-list")
        self.list_box.connect("row_selected", self.on_row_selected)

        scrolled = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        scrolled.set_child(self.list_box)
        self.content_box.append(scrolled)

        # Estado / mensajes
        self.status = Gtk.Label(xalign=0)
        self.status.add_css_class("status-label")

        # Montaje final
        self.append(top_bar)
        self.append(self.content_box)
        self.append(self.status)

        # Carga inicial
        self.presenter.load_friends()

    # --- Callbacks ---
    def on_search_clicked(self, _btn):
        query = self.search_entry.get_text().strip()
        self.presenter.load_friends(query if query else None)

    def on_reload_clicked(self, _btn):
        self.search_entry.set_text("")
        self.presenter.load_friends()

    def on_row_selected(self, _listbox, row):
        if not row:
            return
        idx = row.get_index()
        friend = self._friends_data[idx]
        self.presenter.select_friend(friend.get("id"))

    # --- Métodos llamados por el Presenter ---
    def show_friends(self, friends):
        self._friends_data = friends or []

        # Limpiar lista previa
        for row in list(self.list_box):
            self.list_box.remove(row)

        # Crear filas con nombre + usuario + balances
        for f in self._friends_data:
            name = f.get("name", f"Amigo {f.get('id')}")
            username = f.get("username", f"user{f.get('id')}")
            debit = f.get("debit_balance", 0)
            credit = f.get("credit_balance", 0)

            # Fila contenedora
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row_box.add_css_class("friend-row")

            lbl_name = Gtk.Label(label=name, xalign=0)
            lbl_name.add_css_class("friend-name")

            lbl_user = Gtk.Label(label=username, xalign=0)
            lbl_user.add_css_class("friend-username")

            lbl_debit = Gtk.Label(label=f"Debit: {debit}€")
            lbl_debit.add_css_class("debit-label")

            lbl_credit = Gtk.Label(label=f"Credit: {credit}€")
            lbl_credit.add_css_class("credit-label")

            # Empaquetar
            row_box.append(lbl_name)
            row_box.append(lbl_user)
            row_box.append(lbl_debit)
            row_box.append(lbl_credit)

            self.list_box.append(row_box)

        self.list_box.show()
        self.status.set_text(f"{len(self._friends_data)} friend(s) loaded")

    def show_friend_detail(self, friend):
        # Mantener compatibilidad para presenter
        pass

    def show_friend_expenses(self, expenses):
        pass

    def show_error(self, message: str):
        self.status.set_text(message)

