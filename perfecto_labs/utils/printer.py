"""
Utilidades de impresion para impresora termica 80mm y sistema por defecto.
"""

import os
import platform
import subprocess


def print_pdf(filepath):
    """
    Envia un PDF a la impresora por defecto del sistema.
    Compatible con Windows, macOS y Linux.
    """
    if not os.path.exists(filepath):
        return False, "Archivo no encontrado."

    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(filepath, "print")
        elif system == "Darwin":
            subprocess.run(["lpr", filepath], check=True)
        else:
            subprocess.run(["lpr", filepath], check=True)
        return True, "Documento enviado a imprimir."
    except Exception as e:
        return False, f"Error al imprimir: {e}"


def print_thermal(filepath):
    """
    Envia un PDF a una impresora termica 80mm.
    Intenta usar python-escpos si esta disponible,
    de lo contrario usa lpr con configuracion de tamano.
    """
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(filepath, "print")
        else:
            subprocess.run(
                ["lpr", "-o", "media=Custom.80x200mm", filepath],
                check=True,
            )
        return True, "Documento enviado a impresora termica."
    except Exception as e:
        return False, f"Error al imprimir en termica: {e}"


def get_available_printers():
    """Retorna lista de impresoras disponibles en el sistema."""
    system = platform.system()
    try:
        if system == "Windows":
            result = subprocess.run(
                ["wmic", "printer", "get", "name"],
                capture_output=True, text=True,
            )
            printers = [
                line.strip()
                for line in result.stdout.split("\n")
                if line.strip() and line.strip() != "Name"
            ]
        else:
            result = subprocess.run(
                ["lpstat", "-p"],
                capture_output=True, text=True,
            )
            printers = []
            for line in result.stdout.split("\n"):
                if line.startswith("printer"):
                    parts = line.split()
                    if len(parts) >= 2:
                        printers.append(parts[1])
        return printers
    except Exception:
        return []
