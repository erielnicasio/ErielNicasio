"""
Modulo de Patrocinadores - Gestion de sponsors y aportes.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox

from config import COLORS
from database.connection import execute_query


class SponsorsModule:
    """Modulo para gestionar patrocinadores."""

    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.is_admin = user["rol"] == "admin"
        self._build_ui()
        self._load_sponsors()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent", height=60)
        header.pack(fill="x", padx=25, pady=(20, 10))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="\U0001F91D Patrocinadores",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(side="left")

        if self.is_admin:
            ctk.CTkButton(
                header, text="+ Nuevo Patrocinador", height=38, corner_radius=10,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                command=self._add_sponsor_dialog,
            ).pack(side="right")

        # Summary cards
        summary = ctk.CTkFrame(self.parent, fg_color="transparent", height=100)
        summary.pack(fill="x", padx=25, pady=(0, 10))
        summary.pack_propagate(False)

        self.total_sponsors_label = self._make_summary_card(
            summary, "Total Patrocinadores", COLORS["primary"])
        self.total_amount_label = self._make_summary_card(
            summary, "Total Aportes", COLORS["success"])
        self.monetary_label = self._make_summary_card(
            summary, "Monetario", "#8b5cf6")
        self.especie_label = self._make_summary_card(
            summary, "En Especie", COLORS["warning"])

        # Search
        search_frame = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"],
                                    corner_radius=12, height=50)
        search_frame.pack(fill="x", padx=25, pady=(0, 10))
        search_frame.pack_propagate(False)

        ctk.CTkLabel(search_frame, text="\U0001F50D",
                     font=ctk.CTkFont(size=16)).pack(side="left", padx=(15, 5))
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar patrocinador...",
            border_width=0, fg_color="transparent", height=36,
            font=ctk.CTkFont(size=13),
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_sponsors())

        # Table
        table_card = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=12)
        table_card.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        style = ttk.Style()
        style.configure("Sponsors.Treeview",
                        background="white", foreground="#1e293b",
                        fieldbackground="white", rowheight=38,
                        font=("Segoe UI", 11))
        style.configure("Sponsors.Treeview.Heading",
                        background="#f1f5f9", foreground="#1e293b",
                        font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Sponsors.Treeview",
                  background=[("selected", "#dbeafe")],
                  foreground=[("selected", "#1e293b")])

        columns = ("id", "nombre", "empresa", "telefono", "email", "monto", "tipo")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings",
                                 style="Sponsors.Treeview", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("empresa", text="Empresa")
        self.tree.heading("telefono", text="Telefono")
        self.tree.heading("email", text="Email")
        self.tree.heading("monto", text="Aporte")
        self.tree.heading("tipo", text="Tipo")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=130)
        self.tree.column("empresa", width=150)
        self.tree.column("telefono", width=120)
        self.tree.column("email", width=160)
        self.tree.column("monto", width=110, anchor="right")
        self.tree.column("tipo", width=100, anchor="center")

        self.tree.tag_configure("monetario", background="#dcfce7")
        self.tree.tag_configure("especie", background="#fef3c7")
        self.tree.tag_configure("mixto", background="#ede9fe")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 5))

        if self.is_admin:
            self.tree.bind("<Double-1>", self._edit_sponsor_dialog)

    def _make_summary_card(self, parent, title, color):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=12)
        card.pack(side="left", fill="both", expand=True, padx=5)

        bar = ctk.CTkFrame(card, fg_color=color, width=4, corner_radius=2)
        bar.pack(side="left", fill="y")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=10),
                     text_color=COLORS["text_light"], anchor="w").pack(fill="x")
        label = ctk.CTkLabel(inner, text="0",
                             font=ctk.CTkFont(size=18, weight="bold"),
                             text_color=COLORS["text_dark"], anchor="w")
        label.pack(fill="x")
        return label

    def _load_sponsors(self):
        self.sponsors = execute_query(
            "SELECT * FROM patrocinadores WHERE activo = 1 ORDER BY nombre",
            fetch=True,
        ) or []
        self._populate_table(self.sponsors)

    def _populate_table(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in data:
            tipo = row.get("tipo_aporte", "monetario")
            tipo_display = {"monetario": "Monetario", "especie": "En Especie",
                            "mixto": "Mixto"}.get(tipo, tipo)
            self.tree.insert("", "end", values=(
                row["id"], row["nombre"], row.get("empresa", ""),
                row.get("telefono", ""), row.get("email", ""),
                f"RD${float(row.get('monto_aporte', 0)):,.2f}",
                tipo_display,
            ), tags=(tipo,))

        # Update summary
        total = len(data)
        total_amount = sum(float(s.get("monto_aporte", 0)) for s in data)
        monetario = sum(float(s.get("monto_aporte", 0)) for s in data
                        if s.get("tipo_aporte") == "monetario")
        especie = sum(float(s.get("monto_aporte", 0)) for s in data
                      if s.get("tipo_aporte") == "especie")

        self.total_sponsors_label.configure(text=str(total))
        self.total_amount_label.configure(text=f"RD${total_amount:,.2f}")
        self.monetary_label.configure(text=f"RD${monetario:,.2f}")
        self.especie_label.configure(text=f"RD${especie:,.2f}")

    def _filter_sponsors(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self._populate_table(self.sponsors)
            return
        filtered = [
            s for s in self.sponsors
            if query in s["nombre"].lower()
            or query in (s.get("empresa") or "").lower()
        ]
        self._populate_table(filtered)

    def _add_sponsor_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Agregar Patrocinador")
        dialog.geometry("450x550")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["card_bg"])

        ctk.CTkLabel(dialog, text="Nuevo Patrocinador",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(20, 15))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(padx=30, fill="x")

        fields = {}
        for label_text in ["Nombre", "Empresa", "Telefono", "Email", "Monto Aporte"]:
            ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, corner_radius=8,
                                 font=ctk.CTkFont(size=12))
            entry.pack(fill="x")
            fields[label_text.lower().replace(" ", "_")] = entry

        ctk.CTkLabel(form, text="Tipo de Aporte", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
        tipo_var = ctk.StringVar(value="monetario")
        ctk.CTkOptionMenu(form, values=["monetario", "especie", "mixto"],
                          variable=tipo_var, height=36, corner_radius=8).pack(fill="x")

        ctk.CTkLabel(form, text="Notas", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
        notas_entry = ctk.CTkEntry(form, height=36, corner_radius=8,
                                   font=ctk.CTkFont(size=12))
        notas_entry.pack(fill="x")

        def save():
            nombre = fields["nombre"].get().strip()
            if not nombre:
                messagebox.showwarning("Error", "El nombre es obligatorio.")
                return
            monto_str = fields["monto_aporte"].get().strip()
            try:
                monto = float(monto_str) if monto_str else 0
            except ValueError:
                messagebox.showwarning("Error", "Monto debe ser numerico.")
                return

            execute_query(
                "INSERT INTO patrocinadores (nombre, empresa, telefono, email, monto_aporte, tipo_aporte, notas) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (nombre, fields["empresa"].get().strip(),
                 fields["telefono"].get().strip(), fields["email"].get().strip(),
                 monto, tipo_var.get(), notas_entry.get().strip()),
            )

            if monto > 0:
                execute_query(
                    "INSERT INTO reportes_log (tipo, descripcion, monto, usuario_id) "
                    "VALUES ('patrocinio', %s, %s, %s)",
                    (f"Patrocinio de {nombre}", monto, self.user["id"]),
                )

            dialog.destroy()
            self._load_sponsors()

        ctk.CTkButton(form, text="Guardar", height=40, corner_radius=10,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                      command=save).pack(fill="x", pady=(20, 10))

    def _edit_sponsor_dialog(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        sponsor_id = values[0]

        sponsor = execute_query(
            "SELECT * FROM patrocinadores WHERE id = %s", (sponsor_id,), fetch_one=True,
        )
        if not sponsor:
            return

        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Editar Patrocinador")
        dialog.geometry("450x580")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["card_bg"])

        ctk.CTkLabel(dialog, text="Editar Patrocinador",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(20, 15))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(padx=30, fill="x")

        field_map = {
            "Nombre": "nombre", "Empresa": "empresa", "Telefono": "telefono",
            "Email": "email", "Monto Aporte": "monto_aporte",
        }
        entries = {}
        for label_text, db_key in field_map.items():
            ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, corner_radius=8,
                                 font=ctk.CTkFont(size=12))
            val = sponsor.get(db_key, "")
            entry.insert(0, str(val) if val else "")
            entry.pack(fill="x")
            entries[db_key] = entry

        ctk.CTkLabel(form, text="Tipo de Aporte", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
        tipo_var = ctk.StringVar(value=sponsor.get("tipo_aporte", "monetario"))
        ctk.CTkOptionMenu(form, values=["monetario", "especie", "mixto"],
                          variable=tipo_var, height=36, corner_radius=8).pack(fill="x")

        ctk.CTkLabel(form, text="Notas", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
        notas_entry = ctk.CTkEntry(form, height=36, corner_radius=8,
                                   font=ctk.CTkFont(size=12))
        notas_entry.insert(0, sponsor.get("notas", "") or "")
        notas_entry.pack(fill="x")

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 10))

        def save():
            nombre = entries["nombre"].get().strip()
            if not nombre:
                messagebox.showwarning("Error", "El nombre es obligatorio.")
                return
            monto_str = entries["monto_aporte"].get().strip()
            try:
                monto = float(monto_str) if monto_str else 0
            except ValueError:
                messagebox.showwarning("Error", "Monto debe ser numerico.")
                return

            execute_query(
                "UPDATE patrocinadores SET nombre=%s, empresa=%s, telefono=%s, "
                "email=%s, monto_aporte=%s, tipo_aporte=%s, notas=%s WHERE id=%s",
                (nombre, entries["empresa"].get().strip(),
                 entries["telefono"].get().strip(), entries["email"].get().strip(),
                 monto, tipo_var.get(), notas_entry.get().strip(), sponsor_id),
            )
            dialog.destroy()
            self._load_sponsors()

        def delete():
            if messagebox.askyesno("Confirmar", "Desea eliminar este patrocinador?"):
                execute_query("UPDATE patrocinadores SET activo=0 WHERE id=%s", (sponsor_id,))
                dialog.destroy()
                self._load_sponsors()

        ctk.CTkButton(btn_frame, text="Guardar", height=40, corner_radius=10,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(btn_frame, text="Eliminar", height=40, corner_radius=10,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=COLORS["danger"], hover_color="#b91c1c",
                      command=delete).pack(side="right", fill="x", expand=True, padx=(5, 0))
