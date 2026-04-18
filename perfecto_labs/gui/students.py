"""
Modulo de Estudiantes - Tabla con indicadores de rendimiento por colores.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox

from config import COLORS, PERFORMANCE_COLORS
from database.connection import execute_query


class StudentsModule:
    """Modulo para gestionar estudiantes con tabla e indicador de rendimiento."""

    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.is_admin = user["rol"] == "admin"
        self._build_ui()
        self._load_students()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent", height=60)
        header.pack(fill="x", padx=25, pady=(20, 10))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="\U0001F393 Estudiantes",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(side="left")

        if self.is_admin:
            ctk.CTkButton(
                header, text="+ Nuevo Estudiante", height=38, corner_radius=10,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                command=self._add_student_dialog,
            ).pack(side="right")

        # Search bar
        search_frame = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"],
                                    corner_radius=12, height=50)
        search_frame.pack(fill="x", padx=25, pady=(0, 10))
        search_frame.pack_propagate(False)

        ctk.CTkLabel(search_frame, text="\U0001F50D",
                     font=ctk.CTkFont(size=16)).pack(side="left", padx=(15, 5))
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar estudiante por nombre o apellido...",
            border_width=0, fg_color="transparent", height=36,
            font=ctk.CTkFont(size=13),
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_students())

        # Legend
        legend_frame = ctk.CTkFrame(self.parent, fg_color="transparent", height=30)
        legend_frame.pack(fill="x", padx=25, pady=(0, 5))
        ctk.CTkLabel(legend_frame, text="Rendimiento:",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=COLORS["text_light"]).pack(side="left", padx=(0, 10))
        for label, color in PERFORMANCE_COLORS.items():
            dot = ctk.CTkFrame(legend_frame, width=12, height=12,
                               fg_color=color, corner_radius=6)
            dot.pack(side="left", padx=(0, 3))
            ctk.CTkLabel(legend_frame, text=label,
                         font=ctk.CTkFont(size=11),
                         text_color=COLORS["text_light"]).pack(side="left", padx=(0, 12))

        # Table card
        table_card = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"], corner_radius=12)
        table_card.pack(fill="both", expand=True, padx=25, pady=(5, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Students.Treeview",
                        background="white", foreground="#1e293b",
                        fieldbackground="white", rowheight=38,
                        font=("Segoe UI", 11))
        style.configure("Students.Treeview.Heading",
                        background="#f1f5f9", foreground="#1e293b",
                        font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Students.Treeview",
                  background=[("selected", "#dbeafe")],
                  foreground=[("selected", "#1e293b")])

        columns = ("id", "nombre", "apellido", "edad", "grado", "rendimiento", "telefono")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings",
                                 style="Students.Treeview", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("edad", text="Edad")
        self.tree.heading("grado", text="Grado")
        self.tree.heading("rendimiento", text="Rendimiento")
        self.tree.heading("telefono", text="Tel. Padre")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=130)
        self.tree.column("apellido", width=130)
        self.tree.column("edad", width=60, anchor="center")
        self.tree.column("grado", width=120)
        self.tree.column("rendimiento", width=120, anchor="center")
        self.tree.column("telefono", width=130)

        self.tree.tag_configure("activo", background="#dcfce7")
        self.tree.tag_configure("intermedio", background="#fef9c3")
        self.tree.tag_configure("bajo", background="#fee2e2")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 5))

        if self.is_admin:
            self.tree.bind("<Double-1>", self._edit_student_dialog)

        # Stats bar
        self.stats_frame = ctk.CTkFrame(self.parent, fg_color="transparent", height=35)
        self.stats_frame.pack(fill="x", padx=25, pady=(0, 10))
        self.stats_label = ctk.CTkLabel(self.stats_frame, text="",
                                        font=ctk.CTkFont(size=11),
                                        text_color=COLORS["text_light"])
        self.stats_label.pack(side="left")

    def _load_students(self):
        """Carga todos los estudiantes activos de la base de datos."""
        self.students = execute_query(
            "SELECT id, nombre, apellido, edad, grado, rendimiento, telefono_padre "
            "FROM estudiantes WHERE activo = 1 ORDER BY apellido, nombre",
            fetch=True,
        ) or []
        self._populate_table(self.students)

    def _populate_table(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in data:
            rendimiento = row.get("rendimiento", "Activo")
            tag = rendimiento.lower()
            self.tree.insert("", "end", values=(
                row["id"], row["nombre"], row["apellido"],
                row["edad"], row.get("grado", ""),
                rendimiento, row.get("telefono_padre", ""),
            ), tags=(tag,))

        total = len(data)
        activos = sum(1 for r in data if r.get("rendimiento") == "Activo")
        intermedios = sum(1 for r in data if r.get("rendimiento") == "Intermedio")
        bajos = sum(1 for r in data if r.get("rendimiento") == "Bajo")
        self.stats_label.configure(
            text=f"Total: {total}  |  Activos: {activos}  |  Intermedios: {intermedios}  |  Bajo rendimiento: {bajos}"
        )

    def _filter_students(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self._populate_table(self.students)
            return
        filtered = [
            s for s in self.students
            if query in s["nombre"].lower() or query in s["apellido"].lower()
        ]
        self._populate_table(filtered)

    def _add_student_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Agregar Estudiante")
        dialog.geometry("450x520")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["card_bg"])

        ctk.CTkLabel(dialog, text="Nuevo Estudiante",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(20, 15))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(padx=30, fill="x")

        fields = {}
        for label_text in ["Nombre", "Apellido", "Edad", "Grado", "Telefono Padre", "Email Padre"]:
            ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, corner_radius=8,
                                 font=ctk.CTkFont(size=12))
            entry.pack(fill="x")
            fields[label_text.lower().replace(" ", "_")] = entry

        ctk.CTkLabel(form, text="Rendimiento", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
        rendimiento_var = ctk.StringVar(value="Activo")
        ctk.CTkOptionMenu(form, values=["Activo", "Intermedio", "Bajo"],
                          variable=rendimiento_var, height=36,
                          corner_radius=8).pack(fill="x")

        def save():
            nombre = fields["nombre"].get().strip()
            apellido = fields["apellido"].get().strip()
            edad_str = fields["edad"].get().strip()
            if not nombre or not apellido or not edad_str:
                messagebox.showwarning("Campos requeridos",
                                       "Nombre, Apellido y Edad son obligatorios.")
                return
            try:
                edad = int(edad_str)
            except ValueError:
                messagebox.showwarning("Error", "La edad debe ser un numero entero.")
                return

            execute_query(
                "INSERT INTO estudiantes (nombre, apellido, edad, rendimiento, grado, telefono_padre, email_padre) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (nombre, apellido, edad, rendimiento_var.get(),
                 fields["grado"].get().strip(),
                 fields["telefono_padre"].get().strip(),
                 fields["email_padre"].get().strip()),
            )
            dialog.destroy()
            self._load_students()

        ctk.CTkButton(form, text="Guardar", height=40, corner_radius=10,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                      command=save).pack(fill="x", pady=(20, 10))

    def _edit_student_dialog(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        student_id = values[0]

        student = execute_query(
            "SELECT * FROM estudiantes WHERE id = %s", (student_id,), fetch_one=True,
        )
        if not student:
            return

        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Editar Estudiante")
        dialog.geometry("450x560")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["card_bg"])

        ctk.CTkLabel(dialog, text="Editar Estudiante",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(20, 15))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(padx=30, fill="x")

        field_map = {
            "Nombre": "nombre", "Apellido": "apellido", "Edad": "edad",
            "Grado": "grado", "Telefono Padre": "telefono_padre",
            "Email Padre": "email_padre",
        }
        entries = {}
        for label_text, db_key in field_map.items():
            ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, corner_radius=8, font=ctk.CTkFont(size=12))
            entry.insert(0, str(student.get(db_key, "") or ""))
            entry.pack(fill="x")
            entries[db_key] = entry

        ctk.CTkLabel(form, text="Rendimiento", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
        rendimiento_var = ctk.StringVar(value=student.get("rendimiento", "Activo"))
        ctk.CTkOptionMenu(form, values=["Activo", "Intermedio", "Bajo"],
                          variable=rendimiento_var, height=36,
                          corner_radius=8).pack(fill="x")

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 10))

        def save():
            nombre = entries["nombre"].get().strip()
            apellido = entries["apellido"].get().strip()
            edad_str = entries["edad"].get().strip()
            if not nombre or not apellido or not edad_str:
                messagebox.showwarning("Campos requeridos",
                                       "Nombre, Apellido y Edad son obligatorios.")
                return
            try:
                edad = int(edad_str)
            except ValueError:
                messagebox.showwarning("Error", "La edad debe ser un numero.")
                return
            execute_query(
                "UPDATE estudiantes SET nombre=%s, apellido=%s, edad=%s, rendimiento=%s, "
                "grado=%s, telefono_padre=%s, email_padre=%s WHERE id=%s",
                (nombre, apellido, edad, rendimiento_var.get(),
                 entries["grado"].get().strip(),
                 entries["telefono_padre"].get().strip(),
                 entries["email_padre"].get().strip(),
                 student_id),
            )
            dialog.destroy()
            self._load_students()

        def delete():
            if messagebox.askyesno("Confirmar", "Desea eliminar este estudiante?"):
                execute_query("UPDATE estudiantes SET activo=0 WHERE id=%s", (student_id,))
                dialog.destroy()
                self._load_students()

        ctk.CTkButton(btn_frame, text="Guardar Cambios", height=40, corner_radius=10,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(btn_frame, text="Eliminar", height=40, corner_radius=10,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=COLORS["danger"], hover_color="#b91c1c",
                      command=delete).pack(side="right", fill="x", expand=True, padx=(5, 0))
