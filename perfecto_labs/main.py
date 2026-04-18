"""
Perfecto Labs - Sistema de Gestion Profesional
Punto de entrada principal de la aplicacion.
"""

import os
import sys

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

from config import APP_NAME
from gui.login_window import LoginWindow
from gui.main_window import MainWindow


def start_app():
    """Inicia la aplicacion con la ventana de login."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.withdraw()

    def on_login_success(user):
        root.deiconify()
        MainWindow(root, user)

    LoginWindow(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    start_app()
