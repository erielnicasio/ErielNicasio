"""
Configuracion central de Perfecto Labs Management System.
"""

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "admin",
    "database": "perfecto_labs",
}

APP_NAME = "Perfecto Labs - Sistema de Gestion"
APP_VERSION = "1.0.0"

COLORS = {
    "primary": "#1a73e8",
    "primary_dark": "#0d47a1",
    "sidebar_bg": "#1e293b",
    "sidebar_hover": "#334155",
    "sidebar_active": "#1a73e8",
    "bg_main": "#f1f5f9",
    "card_bg": "#ffffff",
    "text_dark": "#1e293b",
    "text_light": "#64748b",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "border": "#e2e8f0",
}

PERFORMANCE_COLORS = {
    "Activo": "#22c55e",
    "Intermedio": "#f59e0b",
    "Bajo": "#ef4444",
}

ROLES = {
    "admin": "Administrador",
    "user": "Usuario/Padre",
}
