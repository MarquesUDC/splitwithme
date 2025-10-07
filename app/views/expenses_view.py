import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

from app.presenters.expenses_presenter import ExpensesPresenter


class ExpensesView(Gtk.Box):
    """
    Vista de Gastos (GTK4):
    - Tabla alineada con Grid
    - Búsqueda + botones (Create / Delete)
    - Selección de fila con resaltado
    """
    def __init__(self, api_client):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10,
                         margin_top=12, margin_bottom=12, margin_start=12, margin_end=12)

        self.presenter = ExpensesPresenter(self, api_client)
        self._expenses_data = []
        self.selected_row_widget = None
        self.selected_id = None

        # --- Barra superior ---
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        top_bar.add_css_class("top-bar")

        self.search_entry = Gtk.Entry(placeholder_text="Buscar gasto...")
        self.search_entry.set_hexpand(True)

        btn_search = Gtk.Button(label="Buscar")
        btn_search.connect("clicked", self.on_search_clicked)

        btn_reload = Gtk.Button(label="Recargar")
        btn_reload.connect("clicked", self.on_reload_clicked)

        btn_create = Gtk.Button(label="Create an expense")
        btn_create.add_css_class("create-expense-button")
        btn_create.connect("clicked", self.on_add_clicked)

        btn_delete = Gtk.Button(label="Delete")
        btn_delete.add_css_class("delete-expense-button")
        btn_delete.connect("clicked", self.on_delete_clicked)

        top_bar.append(self.search_entry)
        top_bar.append(btn_search)
        top_bar.append(btn_reload)
        top_bar.append(btn_create)
        top_bar.append(btn_delete)

        # --- Tabla principal ---
        self.grid = Gtk.Grid(column_spacing=25, row_spacing=6)
        self.grid.add_css_class("expenses-grid")

        scrolled = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        scrolled.set_child(self.grid)

        # --- Estado inferior ---
        self.status = Gtk.Label(xalign=0)
        self.status.add_css_class("status-label")

        # --- Montaje ---
        self.append(top_bar)
        self.append(scrolled)
        self.append(self.status)

        self.presenter.load_expenses()

    # --- Callbacks ---
    def on_reload_clicked(self, _btn):
        self.search_entry.set_text("")
        self.presenter.load_expenses()

    def on_search_clicked(self, _btn):
        query = self.search_entry.get_text().strip()
        self.presenter.load_expenses(query if query else None)

    def on_add_clicked(self, _btn):
        self.show_expense_dialog("Añadir gasto")

    def on_delete_clicked(self, _btn):
        """Elimina el gasto seleccionado."""
        if not self.selected_id:
            self.show_error("Selecciona un gasto primero.")
            return
        try:
            self.presenter.api_client.delete_expense(self.selected_id)
            self.presenter.load_expenses()
            self.show_error(f"Gasto eliminado: {self.selected_id}")
            self.selected_id = None
            self.selected_row_widget = None
        except Exception as e:
            self.show_error(f"Error eliminando gasto: {e}")

    # --- Presenter callbacks ---
    def show_expenses(self, expenses):
        self._expenses_data = expenses or []

        for child in list(self.grid):
            self.grid.remove(child)

        headers = ["ID", "DESCRIPTION", "DATE", "AMOUNT", "CREDIT", "FRIENDS"]
        for col, text in enumerate(headers):
            lbl = Gtk.Label(label=text, xalign=0)
            lbl.add_css_class("table-header")
            self.grid.attach(lbl, col, 0, 1, 1)

        for row, e in enumerate(self._expenses_data, start=1):
            values = [
                str(e.get("id", "")),
                e.get("description", ""),
                e.get("date", ""),
                f"{e.get('amount', 0)}€",
                f"{e.get('credit_balance', 0)}€",
                str(e.get("num_friends", 0)),
            ]

            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=25)
            row_box.add_css_class("table-row")

            for col, val in enumerate(values):
                lbl = Gtk.Label(label=val, xalign=0)
                lbl.add_css_class("table-cell")

                if col == 3:
                    try:
                        amount = float(e.get("amount", 0))
                        if amount < 0:
                            lbl.add_css_class("amount-negative")
                        elif amount > 0:
                            lbl.add_css_class("amount-positive")
                    except Exception:
                        pass
                row_box.append(lbl)

            # Detectar clic en fila
            click = Gtk.GestureClick()
            click.connect("pressed", self.on_row_clicked, e, row_box)
            row_box.add_controller(click)

            self.grid.attach(row_box, 0, row, len(headers), 1)

        self.status.set_text(f"{len(self._expenses_data)} gasto(s)")

    def on_row_clicked(self, _gesture, _n_press, _x, _y, expense, row_widget):
        """Resalta la fila seleccionada."""
        if self.selected_row_widget:
            self.selected_row_widget.remove_css_class("table-row-selected")
        row_widget.add_css_class("table-row-selected")
        self.selected_row_widget = row_widget
        self.selected_id = expense.get("id")
        self.show_error(f"Seleccionado: ID {self.selected_id}")

    def show_error(self, message: str):
        self.status.set_text(message)

    # --- Diálogo para crear/editar ---
    def show_expense_dialog(self, title, expense=None):
        dialog = Gtk.Dialog(
            title=title,
            transient_for=self.get_root(),
            modal=True,
        )
        dialog.set_default_size(320, 180)
        box = dialog.get_content_area()

        grid = Gtk.Grid(column_spacing=10, row_spacing=10,
                        margin_top=10, margin_bottom=10,
                        margin_start=10, margin_end=10)
        box.append(grid)

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

        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        dialog.add_button("Aceptar", Gtk.ResponseType.OK)

        def on_response(dlg, response_id):
            if response_id == Gtk.ResponseType.OK:
                description = entry_desc.get_text().strip()
                date = entry_date.get_text().strip()
                amount_text = entry_amount.get_text().strip()
                try:
                    amount = float(amount_text.replace(',', '.')) if amount_text else 0.0
                except ValueError:
                    self.show_error("Introduce una cantidad válida.")
                    return

                if expense is None:
                    try:
                        new_expense = self.presenter.api_client.create_expense(
                            description=description,
                            date=date,
                            amount=amount
                        )
                        self.presenter.load_expenses()
                        self.show_error(f"Gasto creado: {new_expense.get('id', '?')}")
                    except Exception as e:
                        self.show_error(f"Error creando gasto: {e}")
                else:
                    try:
                        expense["description"] = description
                        expense["date"] = date
                        expense["amount"] = amount
                        self.presenter.api_client.update_expense(expense["id"], expense)
                        self.presenter.load_expenses()
                        self.show_error(f"Gasto actualizado: {expense['id']}")
                    except Exception as e:
                        self.show_error(f"Error actualizando gasto: {e}")
            dlg.destroy()

        dialog.connect("response", on_response)
        dialog.present()

