"""
Ventana principal con sidebar de navegacion para Perfecto Labs.
"""

import customtkinter as ctk

from config import APP_NAME, COLORS, ROLES
from gui.students import StudentsModule
from gui.inventory import InventoryModule
from gui.billing import BillingModule
from gui.reports import ReportsModule
from gui.sponsors import SponsorsModule


class MainWindow:
    """Ventana principal con barra lateral y area de contenido."""

    MODULES = [
        ("Estudiantes", "students"),
        ("Inventario", "inventory"),
        ("Facturacion", "billing"),
        ("Reportes", "reports"),
        ("Patrocinadores", "sponsors"),
    ]

    MODULE_ICONS = {
        "students": "\U0001F393",
        "inventory": "\U0001F4E6",
        "billing": "\U0001F4B3",
        "reports": "\U0001F4CA",
        "sponsors": "\U0001F91D",
    }

    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.current_module = None
        self.nav_buttons = {}
        self.module_instances = {}

        self.root.title(APP_NAME)
        self.root.geometry("1280x780")
        self.root.minsize(1100, 650)
        self.root.configure(fg_color=COLORS["bg_main"])

        self._build_layout()
        self._show_module("students")
        self._center_window()

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

    def _build_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=230, fg_color=COLORS["sidebar_bg"],
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar header
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=90)
        header.pack(fill="x", padx=15, pady=(20, 10))
        header.pack_propagate(False)

        logo_frame = ctk.CTkFrame(header, fg_color=COLORS["primary"], corner_radius=12,
                                  width=48, height=48)
        logo_frame.pack(side="left", padx=(0, 12))
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="PL", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(info_frame, text="Perfecto Labs",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="white", anchor="w").pack(fill="x")
        ctk.CTkLabel(info_frame, text="Sistema de Gestion",
                     font=ctk.CTkFont(size=11),
                     text_color="#94a3b8", anchor="w").pack(fill="x")

        # Divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#334155").pack(fill="x", padx=15, pady=5)

        # User info
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="#334155", corner_radius=10, height=50)
        user_frame.pack(fill="x", padx=15, pady=(5, 15))
        user_frame.pack_propagate(False)

        avatar = ctk.CTkFrame(user_frame, fg_color=COLORS["primary"], corner_radius=8,
                              width=32, height=32)
        avatar.pack(side="left", padx=(10, 8), pady=9)
        avatar.pack_propagate(False)
        initial = self.user["nombre_completo"][0].upper()
        ctk.CTkLabel(avatar, text=initial, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        u_info = ctk.CTkFrame(user_frame, fg_color="transparent")
        u_info.pack(side="left", fill="both", expand=True, pady=5)
        ctk.CTkLabel(u_info, text=self.user["nombre_completo"],
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="white", anchor="w").pack(fill="x")
        ctk.CTkLabel(u_info, text=ROLES.get(self.user["rol"], "Usuario"),
                     font=ctk.CTkFont(size=10),
                     text_color="#94a3b8", anchor="w").pack(fill="x")

        # Navigation label
        ctk.CTkLabel(self.sidebar, text="NAVEGACION",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#64748b", anchor="w").pack(fill="x", padx=20, pady=(5, 5))

        # Navigation buttons
        for label, key in self.MODULES:
            if self.user["rol"] != "admin" and key in ("reports", "sponsors"):
                continue
            icon = self.MODULE_ICONS.get(key, "")
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {label}",
                font=ctk.CTkFont(size=13),
                height=42,
                corner_radius=10,
                fg_color="transparent",
                text_color="#cbd5e1",
                hover_color=COLORS["sidebar_hover"],
                anchor="w",
                command=lambda k=key: self._show_module(k),
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[key] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Logout button
        ctk.CTkButton(
            self.sidebar, text="  Cerrar Sesion",
            font=ctk.CTkFont(size=13),
            height=42, corner_radius=10,
            fg_color="#dc2626", hover_color="#b91c1c",
            text_color="white",
            command=self._logout,
        ).pack(fill="x", padx=12, pady=(5, 20))

        # Content area
        self.content_frame = ctk.CTkFrame(self.root, fg_color=COLORS["bg_main"],
                                          corner_radius=0)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def _show_module(self, module_key):
        if self.current_module == module_key:
            return

        for btn_key, btn in self.nav_buttons.items():
            if btn_key == module_key:
                btn.configure(fg_color=COLORS["sidebar_active"], text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#cbd5e1")

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.current_module = module_key
        module_map = {
            "students": StudentsModule,
            "inventory": InventoryModule,
            "billing": BillingModule,
            "reports": ReportsModule,
            "sponsors": SponsorsModule,
        }

        module_class = module_map.get(module_key)
        if module_class:
            instance = module_class(self.content_frame, self.user)
            self.module_instances[module_key] = instance

    def _logout(self):
        self.root.destroy()
        import main
        main.start_app()
