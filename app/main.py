
import sys
import gi
import os

# --- CORRECCIÓN CLAVE PARA WAYLAND ---
os.environ.setdefault("GDK_BACKEND", "wayland")  # o "x11" si usas X11 en Hyprland
# -------------------------------------

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

from app.infra.config import AppConfig
from app.views.main_window import MainWindow


class SplitWithMeApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.splitwithme.desktop",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.config = AppConfig.load()
        self.window = None

    # ⚙️ ESTA FUNCIÓN ES LA QUE FALTABA
    def do_activate(self, *args):
        if not self.window:
            self.window = MainWindow(self)
        self.window.present()


def main():
    app = SplitWithMeApp()
    app.run(sys.argv)


if __name__ == "__main__":
    main()
