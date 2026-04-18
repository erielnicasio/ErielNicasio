"""
Modulo de Reportes Generales - Bitacora de ventas y movimientos.
"""

from datetime import datetime, timedelta
from tkinter import ttk

import customtkinter as ctk

from config import COLORS
from database.connection import execute_query


class ReportsModule:
    """Modulo de reportes con bitacora de ventas y movimientos."""

    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self._build_ui()
        self._load_reports()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent", height=60)
        header.pack(fill="x", padx=25, pady=(20, 10))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="\U0001F4CA Reportes Generales",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(side="left")

        # Filter bar
        filter_frame = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"],
                                    corner_radius=12, height=55)
        filter_frame.pack(fill="x", padx=25, pady=(0, 10))
        filter_frame.pack_propagate(False)

        ctk.CTkLabel(filter_frame, text="Periodo:",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(side="left", padx=(15, 8))

        self.period_var = ctk.StringVar(value="Semanal")
        ctk.CTkOptionMenu(
            filter_frame, values=["Semanal", "Mensual", "Todo"],
            variable=self.period_var, height=32, corner_radius=8,
            command=lambda _: self._load_reports(),
        ).pack(side="left", padx=5)

        ctk.CTkLabel(filter_frame, text="Tipo:",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(side="left", padx=(20, 8))

        self.type_var = ctk.StringVar(value="Todos")
        ctk.CTkOptionMenu(
            filter_frame, values=["Todos", "Ventas", "Mensualidades", "Patrocinios"],
            variable=self.type_var, height=32, corner_radius=8,
            command=lambda _: self._load_reports(),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            filter_frame, text="Actualizar", height=32, corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
            command=self._load_reports,
        ).pack(side="right", padx=15)

        # Summary cards row
        summary_frame = ctk.CTkFrame(self.parent, fg_color="transparent", height=100)
        summary_frame.pack(fill="x", padx=25, pady=(0, 10))
        summary_frame.pack_propagate(False)

        self.summary_cards = {}
        card_data = [
            ("Total Ingresos", "total_income", COLORS["primary"]),
            ("Ventas", "total_sales", COLORS["success"]),
            ("Mensualidades", "total_monthly", "#8b5cf6"),
            ("Movimientos", "total_movements", COLORS["warning"]),
        ]
        for title, key, color in card_data:
            card = ctk.CTkFrame(summary_frame, fg_color=COLORS["card_bg"], corner_radius=12)
            card.pack(side="left", fill="both", expand=True, padx=5)

            bar = ctk.CTkFrame(card, fg_color=color, width=4, corner_radius=2)
            bar.pack(side="left", fill="y")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=10)

            ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=10),
                         text_color=COLORS["text_light"], anchor="w").pack(fill="x")
            value_label = ctk.CTkLabel(inner, text="0",
                                       font=ctk.CTkFont(size=18, weight="bold"),
                                       text_color=COLORS["text_dark"], anchor="w")
            value_label.pack(fill="x")
            self.summary_cards[key] = value_label

        # Reports table
        table_card = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=12)
        table_card.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        ctk.CTkLabel(table_card, text="Bitacora de Movimientos",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(anchor="w", padx=15, pady=(12, 5))

        style = ttk.Style()
        style.configure("Reports.Treeview",
                        background="white", foreground="#1e293b",
                        fieldbackground="white", rowheight=36,
                        font=("Segoe UI", 11))
        style.configure("Reports.Treeview.Heading",
                        background="#f1f5f9", foreground="#1e293b",
                        font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Reports.Treeview",
                  background=[("selected", "#dbeafe")],
                  foreground=[("selected", "#1e293b")])

        columns = ("id", "fecha", "tipo", "descripcion", "monto", "usuario")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings",
                                 style="Reports.Treeview", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("descripcion", text="Descripcion")
        self.tree.heading("monto", text="Monto")
        self.tree.heading("usuario", text="Usuario")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("fecha", width=140)
        self.tree.column("tipo", width=120)
        self.tree.column("descripcion", width=300)
        self.tree.column("monto", width=110, anchor="e")
        self.tree.column("usuario", width=120)

        self.tree.tag_configure("venta", background="#dcfce7")
        self.tree.tag_configure("pago_mensualidad", background="#ede9fe")
        self.tree.tag_configure("patrocinio", background="#fef3c7")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side="right", fill="y", pady=(0, 10), padx=(0, 5))

    def _load_reports(self):
        period = self.period_var.get()
        type_filter = self.type_var.get()

        where_clauses = []
        params = []

        if period == "Semanal":
            where_clauses.append("r.fecha >= %s")
            params.append(datetime.now() - timedelta(days=7))
        elif period == "Mensual":
            where_clauses.append("r.fecha >= %s")
            params.append(datetime.now() - timedelta(days=30))

        type_map = {
            "Ventas": "venta",
            "Mensualidades": "pago_mensualidad",
            "Patrocinios": "patrocinio",
        }
        if type_filter in type_map:
            where_clauses.append("r.tipo = %s")
            params.append(type_map[type_filter])

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        query = (
            f"SELECT r.id, r.fecha, r.tipo, r.descripcion, r.monto, "
            f"COALESCE(u.nombre_completo, 'Sistema') as usuario "
            f"FROM reportes_log r "
            f"LEFT JOIN usuarios u ON r.usuario_id = u.id "
            f"{where_sql} "
            f"ORDER BY r.fecha DESC"
        )

        reports = execute_query(query, tuple(params) if params else None, fetch=True) or []

        # Populate table
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in reports:
            fecha = row.get("fecha", "")
            if hasattr(fecha, "strftime"):
                fecha = fecha.strftime("%d/%m/%Y %H:%M")

            tipo = row.get("tipo", "otro")
            tipo_display = {
                "venta": "Venta",
                "pago_mensualidad": "Mensualidad",
                "patrocinio": "Patrocinio",
                "ingreso_inventario": "Inventario",
                "otro": "Otro",
            }.get(tipo, tipo)

            monto = row.get("monto")
            monto_str = f"RD${float(monto):,.2f}" if monto else "N/A"

            self.tree.insert("", "end", values=(
                row["id"], fecha, tipo_display,
                row.get("descripcion", ""), monto_str,
                row.get("usuario", "Sistema"),
            ), tags=(tipo,))

        # Update summaries
        total_income = sum(float(r.get("monto") or 0) for r in reports)
        total_sales = sum(float(r.get("monto") or 0) for r in reports if r.get("tipo") == "venta")
        total_monthly = sum(float(r.get("monto") or 0) for r in reports if r.get("tipo") == "pago_mensualidad")

        self.summary_cards["total_income"].configure(text=f"RD${total_income:,.2f}")
        self.summary_cards["total_sales"].configure(text=f"RD${total_sales:,.2f}")
        self.summary_cards["total_monthly"].configure(text=f"RD${total_monthly:,.2f}")
        self.summary_cards["total_movements"].configure(text=str(len(reports)))
