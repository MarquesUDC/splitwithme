

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from app.presenters.friends_presenter import FriendsPresenter

class FriendsView(Gtk.Box):
    """
    Vista de Amigos:
    - Búsqueda por nombre
    - Lista de amigos
    - Panel de detalle (datos + balances)
    - Lista de gastos del amigo
    """
    def __init__(self, api_client):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10,
                         margin_top=12, margin_bottom=12, margin_start=12, margin_end=12)

        self.presenter = FriendsPresenter(self, api_client)
        self._friends_data = []  # cache simple

        # Barra superior: búsqueda + botón recargar
        top = Gtk.Box(spacing=8)
        self.search_entry = Gtk.Entry(placeholder_text="Buscar amigo...")
        btn_search = Gtk.Button(label="Buscar")
        btn_search.connect("clicked", self.on_search_clicked)
        btn_reload = Gtk.Button(label="Recargar")
        btn_reload.connect("clicked", self.on_reload_clicked)
        top.append(self.search_entry)
        top.append(btn_search)
        top.append(btn_reload)

        # Panel central: lista (izquierda) + detalle (derecha)
        center = Gtk.Box(spacing=10)

        # Lista de amigos
        self.list_box = Gtk.ListBox()
        self.list_box.connect("row_selected", self.on_row_selected)
        sc_left = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        sc_left.set_child(self.list_box)

        # Detalle del amigo
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.friend_detail = Gtk.TextView(editable=False, monospace=True, hexpand=True, vexpand=True)
        sc_detail = Gtk.ScrolledWindow()
        sc_detail.set_child(self.friend_detail)

        # Gastos del amigo
        self.friend_expenses = Gtk.TextView(editable=False, monospace=True, hexpand=True, vexpand=True)
        sc_exp = Gtk.ScrolledWindow()
        sc_exp.set_child(self.friend_expenses)

        right.append(Gtk.Label(label="Detalle del amigo"))
        right.append(sc_detail)
        right.append(Gtk.Label(label="Gastos del amigo"))
        right.append(sc_exp)

        center.append(sc_left)
        center.append(right)

        # Mensajes
        self.status = Gtk.Label(xalign=0)

        # Montaje
        self.append(top)
        self.append(center)
        self.append(self.status)

        # Cargar inicial
        self.presenter.load_friends()

    # ---- Callbacks ----
    def on_search_clicked(self, _btn):
        self.presenter.load_friends(self.search_entry.get_text())

    def on_reload_clicked(self, _btn):
        self.search_entry.set_text("")
        self.presenter.load_friends()

    def on_row_selected(self, _listbox, row):
        if not row: 
            return
        idx = row.get_index()
        friend = self._friends_data[idx]
        self.presenter.select_friend(friend.get("id"))

    # ---- Métodos llamados por el Presenter ----
    def show_friends(self, friends):
        self._friends_data = friends or []
        # Limpiar lista previa (GTK4 no tiene foreach)
        for row in list(self.list_box):
             self.list_box.remove(row)

        for f in self._friends_data:
            name = f.get("name", f"Amigo {f.get('id')}")
            balance = f.get("credit_balance")
            label = f"{name} (saldo: {balance})" if balance is not None else name
            self.list_box.append(Gtk.Label(label=label, xalign=0))
        self.list_box.show()

        self.status.set_text(f"{len(self._friends_data)} amigo(s)")

    def show_friend_detail(self, friend):
        txt = []
        for k in ("id", "name", "credit_balance", "debit_balance", "net_balance", "num_expenses"):
            if k in friend:
                txt.append(f"{k}: {friend[k]}")
        self._set_text(self.friend_detail, "\n".join(txt) or "—")

    def show_friend_expenses(self, expenses):
        # expenses: lista de objetos con id, description, amount, date, etc.
        lines = []
        for e in expenses or []:
            lines.append(f"[{e.get('id')}] {e.get('date','?')}  {e.get('description','')}  — {e.get('amount')}€  (amigos: {e.get('num_friends')})")
        self._set_text(self.friend_expenses, "\n".join(lines) if lines else "—")

    def show_error(self, message: str):
        self.status.set_text(message)

    # ---- Util ----
    def _set_text(self, textview: Gtk.TextView, text: str):
        buf = textview.get_buffer()
        buf.set_text(text or "")
