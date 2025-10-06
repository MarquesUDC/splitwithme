import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from app.presenters.expenses_presenter import ExpensesPresenter

class ExpensesView(Gtk.Box):
    """
    Vista de Gastos:
    - Lista de gastos a la izquierda
    - Detalle a la derecha
    - Campo de búsqueda por descripción
    """
    def __init__(self, api_client):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10,
                         margin_top=12, margin_bottom=12, margin_start=12, margin_end=12)

        self.presenter = ExpensesPresenter(self, api_client)
        self._expenses_data = []

        # ---- Barra superior: búsqueda + botones ----
        top = Gtk.Box(spacing=8)

        # Campo de búsqueda
        self.search_entry = Gtk.Entry(placeholder_text="Buscar gasto...")
        btn_search = Gtk.Button(label="Buscar")
        btn_search.connect("clicked", self.on_search_clicked)

        # Botón recargar
        btn_reload = Gtk.Button(label="Recargar")
        btn_reload.connect("clicked", self.on_reload_clicked)

        # Añadir elementos a la barra
        top.append(self.search_entry)
        top.append(btn_search)
        top.append(btn_reload)
        # Botones de acciones CRUD
        btn_add = Gtk.Button(label="Añadir")
        btn_edit = Gtk.Button(label="Editar")
        btn_delete = Gtk.Button(label="Eliminar")

        btn_add.connect("clicked", self.on_add_clicked)
        btn_edit.connect("clicked", self.on_edit_clicked)
        btn_delete.connect("clicked", self.on_delete_clicked)

        top.append(btn_add)
        top.append(btn_edit)
        top.append(btn_delete)

        # ---- Panel central ----
        center = Gtk.Box(spacing=10)

        # Lista de gastos (izquierda)
        self.list_box = Gtk.ListBox()
        self.list_box.connect("row_selected", self.on_row_selected)
        sc_left = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        sc_left.set_child(self.list_box)

        # Detalle del gasto (derecha)
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.expense_detail = Gtk.TextView(editable=False, monospace=True, hexpand=True, vexpand=True)
        sc_detail = Gtk.ScrolledWindow()
        sc_detail.set_child(self.expense_detail)

        right.append(Gtk.Label(label="Detalle del gasto"))
        right.append(sc_detail)

        # Añadir paneles
        center.append(sc_left)
        center.append(right)

        # ---- Estado inferior ----
        self.status = Gtk.Label(xalign=0)

        # Montaje final
        self.append(top)
        self.append(center)
        self.append(self.status)

        # Cargar gastos iniciales
        self.presenter.load_expenses()

    # ---- Callbacks ----
    def on_reload_clicked(self, _btn):
        self.search_entry.set_text("")
        self.presenter.load_expenses()
    def on_search_clicked(self, _btn):
        """Callback del botón Buscar."""
        query = self.search_entry.get_text().strip()
        self.presenter.load_expenses(query if query else None)

    def on_row_selected(self, _listbox, row):
        if not row:
            return
        idx = row.get_index()
        exp = self._expenses_data[idx]
        self.presenter.select_expense(exp.get("id"))

    # ---- Métodos llamados por el Presenter ----
    def show_expenses(self, expenses):
        self._expenses_data = expenses or []

        # Limpiar lista previa
        for row in list(self.list_box):
            self.list_box.remove(row)

        # Añadir gastos nuevos
        for e in self._expenses_data:
            desc = e.get("description", f"Gasto {e.get('id')}")
            date = e.get("date", "?")
            amount = e.get("amount", "?")
            label = f"{desc} — {date} — {amount}€"
            self.list_box.append(Gtk.Label(label=label, xalign=0))

        self.list_box.show()
        self.status.set_text(f"{len(self._expenses_data)} gasto(s)")

    def show_expense_detail(self, expense):
        lines = []
        for k in ("id", "description", "date", "amount", "credit_balance", "debit_balance", "num_friends"):
            if k in expense:
                lines.append(f"{k}: {expense[k]}")

        participants = expense.get("friends") or expense.get("participants")
        if participants:
            lines.append("Participantes:")
            for f in participants:
                lines.append(f"  - {f}")

        self._set_text(self.expense_detail, "\n".join(lines) or "-")

    def show_error(self, message: str):
        self.status.set_text(message)

    # ---- Util ----
    def _set_text(self, textview: Gtk.TextView, text: str):
        buf = textview.get_buffer()
        buf.set_text(text or "")
    
    def on_add_clicked(self, _btn):
        """Crea un nuevo gasto desde un diálogo."""
        data = self.show_expense_dialog("Añadir gasto")
        if not data:
            return  # usuario canceló

        try:
            new_expense = self.presenter.api_client.create_expense(
                description=data["description"],
                date=data["date"],
                amount=data["amount"]
            )
            self.presenter.load_expenses()
            self.show_error(f"Gasto creado: {new_expense.get('id', '?')}")
        except Exception as e:
            self.show_error(f"Error creando gasto: {e}")


    def on_edit_clicked(self, _btn):
        """Edita el gasto seleccionado."""
        selected_row = self.list_box.get_selected_row()
        if not selected_row:
            self.show_error("Selecciona un gasto primero.")
            return

        idx = selected_row.get_index()
        expense = self._expenses_data[idx]
        data = self.show_expense_dialog("Editar gasto", expense)
        if not data:
            return

        try:
            self.presenter.api_client.update_expense(expense["id"], data)
            self.presenter.load_expenses()
            self.show_error("Gasto actualizado correctamente.")
        except Exception as e:
            self.show_error(f"Error editando gasto: {e}")

    def on_delete_clicked(self, _btn):
        """Elimina el gasto seleccionado."""
        try:
            row = self.list_box.get_selected_row()
            if not row:
                self.show_error("Selecciona un gasto para eliminar.")
                return
            idx = row.get_index()
            expense = self._expenses_data[idx]
            self.presenter.api_client.delete_expense(expense["id"])
            self.presenter.load_expenses()
            self.show_error(f"Gasto eliminado: {expense['id']}")
        except Exception as e:
            self.show_error(f"Error eliminando gasto: {e}")
    def show_expense_dialog(self, title, expense=None):
        dialog = Gtk.Dialog(title=title, transient_for=self.get_root(), modal=True)
        dialog.set_default_size(300, 150)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        box = dialog.get_content_area()
        box.append(grid)

        # Campos
        lbl_desc = Gtk.Label(label="Descripción:")
        entry_desc = Gtk.Entry(text=expense["description"] if expense else "")
        lbl_date = Gtk.Label(label="Fecha (YYYY-MM-DD):")
        entry_date = Gtk.Entry(text=expense["date"] if expense else "")
        lbl_amount = Gtk.Label(label="Cantidad (€):")
        entry_amount = Gtk.Entry(text=str(expense["amount"]) if expense else "")

        grid.attach(lbl_desc, 0, 0, 1, 1)
        grid.attach(entry_desc, 1, 0, 1, 1)
        grid.attach(lbl_date, 0, 1, 1, 1)
        grid.attach(entry_date, 1, 1, 1, 1)
        grid.attach(lbl_amount, 0, 2, 1, 1)
        grid.attach(entry_amount, 1, 2, 1, 1)

        # Botones
        btn_cancel = Gtk.Button(label="Cancelar")
        btn_ok = Gtk.Button(label="Aceptar")
        btn_box = Gtk.Box(spacing=6)
        btn_box.append(btn_cancel)
        btn_box.append(btn_ok)
        box.append(btn_box)

        # Variable local para guardar la respuesta
        result = {"data": None}

        # Handlers de botones
        def on_accept(_btn):
            result["data"] = {
                "description": entry_desc.get_text(),
                "date": entry_date.get_text(),
                "amount": float(entry_amount.get_text() or 0)
            }
            dialog.close()

        def on_cancel(_btn):
            dialog.close()

        btn_ok.connect("clicked", on_accept)
        btn_cancel.connect("clicked", on_cancel)

        dialog.present()
        dialog.connect("close-request", lambda *_: dialog.destroy())

        # Esperar hasta que se cierre el diálogo
        while dialog.get_visible():
            while Gtk.main_iteration_do(False):
                pass

        return result["data"]

