"""
Modulo de Facturacion - Pagos de mensualidad y productos con PDF e impresion.
"""

import os
import random
import string
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from config import COLORS
from database.connection import execute_query
from utils.pdf_generator import generate_invoice_pdf
from utils.printer import print_pdf, print_thermal


class BillingModule:
    """Modulo de facturacion con generacion de PDF y soporte de impresion."""

    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.is_admin = user["rol"] == "admin"
        self.items = []
        self._build_ui()
        self._load_recent_invoices()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent", height=60)
        header.pack(fill="x", padx=25, pady=(20, 10))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="\U0001F4B3 Facturacion",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(side="left")

        ctk.CTkButton(
            header, text="+ Nueva Factura", height=38, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
            command=self._new_invoice_dialog,
        ).pack(side="right")

        # Main content: split into two columns
        content = ctk.CTkFrame(self.parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # Left: recent invoices
        left = ctk.CTkFrame(content, fg_color=COLORS["card_bg"], corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(left, text="Facturas Recientes",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(anchor="w", padx=15, pady=(15, 10))

        self.invoices_frame = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.invoices_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Right: quick stats
        right = ctk.CTkFrame(content, fg_color="transparent", width=280)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        # Stat cards
        self._create_stat_card(right, "Ventas del Mes", "stat_month", COLORS["primary"])
        self._create_stat_card(right, "Pendientes", "stat_pending", COLORS["warning"])
        self._create_stat_card(right, "Total Pagado", "stat_paid", COLORS["success"])

        # Quick action: Monthly payment
        ctk.CTkButton(
            right, text="\U0001F4C5 Pago de Mensualidad", height=42, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8b5cf6", hover_color="#7c3aed",
            command=self._monthly_payment_dialog,
        ).pack(fill="x", pady=(15, 5))

    def _create_stat_card(self, parent, title, attr_name, color):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=12, height=90)
        card.pack(fill="x", pady=5)
        card.pack_propagate(False)

        dot = ctk.CTkFrame(card, fg_color=color, width=4, corner_radius=2)
        dot.pack(side="left", fill="y", padx=(0, 0))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_light"], anchor="w").pack(fill="x")
        label = ctk.CTkLabel(inner, text="RD$0.00",
                             font=ctk.CTkFont(size=20, weight="bold"),
                             text_color=COLORS["text_dark"], anchor="w")
        label.pack(fill="x")
        setattr(self, attr_name, label)

    def _load_recent_invoices(self):
        for widget in self.invoices_frame.winfo_children():
            widget.destroy()

        invoices = execute_query(
            "SELECT id, numero_pedido, cliente_nombre, total, estado, tipo, fecha_creacion "
            "FROM pedidos ORDER BY fecha_creacion DESC LIMIT 20",
            fetch=True,
        ) or []

        if not invoices:
            ctk.CTkLabel(self.invoices_frame, text="No hay facturas registradas.",
                         font=ctk.CTkFont(size=13),
                         text_color=COLORS["text_light"]).pack(pady=30)
        else:
            for inv in invoices:
                self._create_invoice_row(inv)

        # Update stats
        stats = execute_query(
            "SELECT "
            "SUM(CASE WHEN MONTH(fecha_creacion) = MONTH(NOW()) AND YEAR(fecha_creacion) = YEAR(NOW()) THEN total ELSE 0 END) AS mes, "
            "SUM(CASE WHEN estado = 'pendiente' THEN total ELSE 0 END) AS pendiente, "
            "SUM(CASE WHEN estado = 'pagado' THEN total ELSE 0 END) AS pagado "
            "FROM pedidos",
            fetch_one=True,
        )
        if stats:
            self.stat_month.configure(text=f"RD${float(stats.get('mes') or 0):,.2f}")
            self.stat_pending.configure(text=f"RD${float(stats.get('pendiente') or 0):,.2f}")
            self.stat_paid.configure(text=f"RD${float(stats.get('pagado') or 0):,.2f}")

    def _create_invoice_row(self, inv):
        row = ctk.CTkFrame(self.invoices_frame, fg_color="#f8fafc", corner_radius=8, height=55)
        row.pack(fill="x", pady=3)
        row.pack_propagate(False)

        estado = inv.get("estado", "pendiente")
        estado_colors = {"pagado": COLORS["success"], "pendiente": COLORS["warning"],
                         "cancelado": COLORS["danger"]}
        dot = ctk.CTkFrame(row, width=8, height=8,
                           fg_color=estado_colors.get(estado, COLORS["text_light"]),
                           corner_radius=4)
        dot.pack(side="left", padx=(12, 8), pady=23)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=5)

        ctk.CTkLabel(info, text=f"{inv['numero_pedido']} - {inv['cliente_nombre']}",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x")

        fecha = inv.get("fecha_creacion", "")
        if hasattr(fecha, "strftime"):
            fecha = fecha.strftime("%d/%m/%Y %H:%M")
        tipo_label = "Mensualidad" if inv.get("tipo") == "mensualidad" else "Producto"
        ctk.CTkLabel(info, text=f"{tipo_label} | {fecha}",
                     font=ctk.CTkFont(size=10),
                     text_color=COLORS["text_light"], anchor="w").pack(fill="x")

        ctk.CTkLabel(row, text=f"RD${float(inv['total']):,.2f}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["primary"]).pack(side="right", padx=(5, 5))

        ctk.CTkButton(
            row, text="PDF", width=50, height=28, corner_radius=6,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#6366f1", hover_color="#4f46e5",
            command=lambda inv_id=inv["id"]: self._generate_pdf(inv_id),
        ).pack(side="right", padx=3, pady=13)

        ctk.CTkButton(
            row, text="\U0001F5A8", width=35, height=28, corner_radius=6,
            font=ctk.CTkFont(size=12),
            fg_color="#64748b", hover_color="#475569",
            command=lambda inv_id=inv["id"]: self._print_invoice(inv_id),
        ).pack(side="right", padx=(3, 0), pady=13)

    def _generate_order_number(self):
        prefix = "PL"
        date_part = datetime.now().strftime("%y%m%d")
        rand_part = "".join(random.choices(string.digits, k=4))
        return f"{prefix}-{date_part}-{rand_part}"

    def _new_invoice_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Nueva Factura")
        dialog.geometry("550x650")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["card_bg"])

        ctk.CTkLabel(dialog, text="Nueva Factura",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(20, 15))

        form = ctk.CTkScrollableFrame(dialog, fg_color="transparent", height=450)
        form.pack(padx=25, fill="x")

        # Client name
        ctk.CTkLabel(form, text="Cliente", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(5, 2))
        client_entry = ctk.CTkEntry(form, height=36, corner_radius=8,
                                    placeholder_text="Nombre del cliente",
                                    font=ctk.CTkFont(size=12))
        client_entry.pack(fill="x")

        # Type
        ctk.CTkLabel(form, text="Tipo", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(10, 2))
        tipo_var = ctk.StringVar(value="producto")
        ctk.CTkOptionMenu(form, values=["producto", "mensualidad"],
                          variable=tipo_var, height=36, corner_radius=8).pack(fill="x")

        # Payment method
        ctk.CTkLabel(form, text="Metodo de Pago", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(10, 2))
        metodo_var = ctk.StringVar(value="Efectivo")
        ctk.CTkOptionMenu(form, values=["Efectivo", "Tarjeta", "Transferencia"],
                          variable=metodo_var, height=36, corner_radius=8).pack(fill="x")

        # Items section
        ctk.CTkLabel(form, text="Articulos", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(15, 5))

        items_list = []
        items_container = ctk.CTkFrame(form, fg_color="transparent")
        items_container.pack(fill="x")

        total_label = ctk.CTkLabel(form, text="Total: RD$0.00",
                                   font=ctk.CTkFont(size=16, weight="bold"),
                                   text_color=COLORS["primary"])
        total_label.pack(pady=(10, 5))

        def update_total():
            subtotal = sum(item["subtotal"] for item in items_list)
            total_label.configure(text=f"Total: RD${subtotal:,.2f}")

        def add_item_row():
            item_frame = ctk.CTkFrame(items_container, fg_color="#f8fafc", corner_radius=8)
            item_frame.pack(fill="x", pady=3)

            desc_entry = ctk.CTkEntry(item_frame, placeholder_text="Descripcion",
                                      height=32, corner_radius=6, width=180,
                                      font=ctk.CTkFont(size=11))
            desc_entry.pack(side="left", padx=(8, 5), pady=5)

            qty_entry = ctk.CTkEntry(item_frame, placeholder_text="Cant",
                                     height=32, corner_radius=6, width=50,
                                     font=ctk.CTkFont(size=11))
            qty_entry.insert(0, "1")
            qty_entry.pack(side="left", padx=3, pady=5)

            price_entry = ctk.CTkEntry(item_frame, placeholder_text="Precio",
                                       height=32, corner_radius=6, width=80,
                                       font=ctk.CTkFont(size=11))
            price_entry.pack(side="left", padx=3, pady=5)

            item_data = {"frame": item_frame, "desc": desc_entry,
                         "qty": qty_entry, "price": price_entry, "subtotal": 0}
            items_list.append(item_data)

            def remove():
                items_list.remove(item_data)
                item_frame.destroy()
                update_total()

            ctk.CTkButton(item_frame, text="X", width=28, height=28,
                          fg_color=COLORS["danger"], hover_color="#b91c1c",
                          font=ctk.CTkFont(size=10, weight="bold"),
                          corner_radius=6, command=remove).pack(side="right", padx=5, pady=5)

        ctk.CTkButton(form, text="+ Agregar Articulo", height=34, corner_radius=8,
                      font=ctk.CTkFont(size=12),
                      fg_color="#64748b", hover_color="#475569",
                      command=add_item_row).pack(fill="x", pady=5)

        add_item_row()

        def save_invoice():
            client_name = client_entry.get().strip()
            if not client_name:
                messagebox.showwarning("Error", "Ingrese el nombre del cliente.")
                return

            valid_items = []
            for item in items_list:
                desc = item["desc"].get().strip()
                qty_str = item["qty"].get().strip()
                price_str = item["price"].get().strip()
                if not desc or not price_str:
                    continue
                try:
                    qty = int(qty_str) if qty_str else 1
                    price = float(price_str)
                except ValueError:
                    continue
                valid_items.append({
                    "descripcion": desc,
                    "cantidad": qty,
                    "precio_unitario": price,
                    "subtotal": qty * price,
                })

            if not valid_items:
                messagebox.showwarning("Error", "Agregue al menos un articulo valido.")
                return

            subtotal = sum(i["subtotal"] for i in valid_items)
            impuesto = round(subtotal * 0.18, 2)
            total = round(subtotal + impuesto, 2)
            numero = self._generate_order_number()

            pedido_id = execute_query(
                "INSERT INTO pedidos (numero_pedido, cliente_nombre, tipo, subtotal, impuesto, total, estado, metodo_pago, usuario_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, 'pagado', %s, %s)",
                (numero, client_name, tipo_var.get(), subtotal, impuesto, total,
                 metodo_var.get(), self.user["id"]),
            )

            if pedido_id:
                for item in valid_items:
                    execute_query(
                        "INSERT INTO pedido_items (pedido_id, descripcion, cantidad, precio_unitario, subtotal) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (pedido_id, item["descripcion"], item["cantidad"],
                         item["precio_unitario"], item["subtotal"]),
                    )

                # Log
                execute_query(
                    "INSERT INTO reportes_log (tipo, descripcion, monto, referencia_id, usuario_id) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    ("venta", f"Factura {numero} - {client_name}", total, pedido_id, self.user["id"]),
                )

                # Generate PDF
                pedido_data = {
                    "numero_pedido": numero, "cliente_nombre": client_name,
                    "subtotal": subtotal, "impuesto": impuesto, "total": total,
                    "metodo_pago": metodo_var.get(), "fecha_creacion": datetime.now(),
                }
                try:
                    pdf_path = generate_invoice_pdf(pedido_data, valid_items)
                    messagebox.showinfo("Factura Guardada",
                                        f"Factura {numero} guardada exitosamente.\n\nPDF: {pdf_path}")
                except Exception as e:
                    messagebox.showwarning("PDF", f"Factura guardada pero error en PDF: {e}")

                dialog.destroy()
                self._load_recent_invoices()

        ctk.CTkButton(form, text="Guardar y Generar PDF", height=42, corner_radius=10,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color=COLORS["success"], hover_color="#16a34a",
                      command=save_invoice).pack(fill="x", pady=(15, 10))

    def _monthly_payment_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Pago de Mensualidad")
        dialog.geometry("450x450")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["card_bg"])

        ctk.CTkLabel(dialog, text="\U0001F4C5 Pago de Mensualidad",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(20, 15))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(padx=30, fill="x")

        # Student selector
        students = execute_query(
            "SELECT id, CONCAT(nombre, ' ', apellido) AS nombre_completo FROM estudiantes WHERE activo=1 ORDER BY nombre",
            fetch=True,
        ) or []
        student_names = [s["nombre_completo"] for s in students]

        ctk.CTkLabel(form, text="Estudiante", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(5, 2))
        student_var = ctk.StringVar(value=student_names[0] if student_names else "")
        ctk.CTkOptionMenu(form, values=student_names if student_names else ["Sin estudiantes"],
                          variable=student_var, height=36, corner_radius=8).pack(fill="x")

        ctk.CTkLabel(form, text="Monto de Mensualidad", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(10, 2))
        monto_entry = ctk.CTkEntry(form, height=36, corner_radius=8,
                                   font=ctk.CTkFont(size=12))
        monto_entry.insert(0, "3500.00")
        monto_entry.pack(fill="x")

        ctk.CTkLabel(form, text="Mes", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(10, 2))
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        mes_actual = meses[datetime.now().month - 1]
        mes_var = ctk.StringVar(value=mes_actual)
        ctk.CTkOptionMenu(form, values=meses, variable=mes_var,
                          height=36, corner_radius=8).pack(fill="x")

        ctk.CTkLabel(form, text="Metodo de Pago", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(10, 2))
        metodo_var = ctk.StringVar(value="Efectivo")
        ctk.CTkOptionMenu(form, values=["Efectivo", "Tarjeta", "Transferencia"],
                          variable=metodo_var, height=36, corner_radius=8).pack(fill="x")

        def save_payment():
            try:
                monto = float(monto_entry.get().strip())
            except ValueError:
                messagebox.showwarning("Error", "Monto invalido.")
                return

            student_name = student_var.get()
            numero = self._generate_order_number()
            descripcion = f"Mensualidad {mes_var.get()} - {student_name}"

            impuesto = 0.0
            total = monto

            pedido_id = execute_query(
                "INSERT INTO pedidos (numero_pedido, cliente_nombre, tipo, subtotal, impuesto, total, estado, metodo_pago, usuario_id) "
                "VALUES (%s, %s, 'mensualidad', %s, %s, %s, 'pagado', %s, %s)",
                (numero, student_name, monto, impuesto, total, metodo_var.get(), self.user["id"]),
            )

            if pedido_id:
                execute_query(
                    "INSERT INTO pedido_items (pedido_id, descripcion, cantidad, precio_unitario, subtotal) "
                    "VALUES (%s, %s, 1, %s, %s)",
                    (pedido_id, descripcion, monto, monto),
                )
                execute_query(
                    "INSERT INTO reportes_log (tipo, descripcion, monto, referencia_id, usuario_id) "
                    "VALUES ('pago_mensualidad', %s, %s, %s, %s)",
                    (descripcion, total, pedido_id, self.user["id"]),
                )

                pedido_data = {
                    "numero_pedido": numero, "cliente_nombre": student_name,
                    "subtotal": monto, "impuesto": 0, "total": total,
                    "metodo_pago": metodo_var.get(), "fecha_creacion": datetime.now(),
                }
                items_data = [{"descripcion": descripcion, "cantidad": 1,
                               "precio_unitario": monto, "subtotal": monto}]
                try:
                    pdf_path = generate_invoice_pdf(pedido_data, items_data)
                    messagebox.showinfo("Pago Registrado",
                                        f"Pago registrado exitosamente.\n\nPDF: {pdf_path}")
                except Exception as e:
                    messagebox.showwarning("PDF", f"Pago guardado pero error en PDF: {e}")

                dialog.destroy()
                self._load_recent_invoices()

        ctk.CTkButton(form, text="Registrar Pago", height=42, corner_radius=10,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color=COLORS["success"], hover_color="#16a34a",
                      command=save_payment).pack(fill="x", pady=(20, 10))

    def _generate_pdf(self, pedido_id):
        pedido = execute_query("SELECT * FROM pedidos WHERE id=%s", (pedido_id,), fetch_one=True)
        items = execute_query("SELECT * FROM pedido_items WHERE pedido_id=%s", (pedido_id,), fetch=True) or []
        if not pedido:
            return
        try:
            pdf_path = generate_invoice_pdf(pedido, items)
            messagebox.showinfo("PDF Generado", f"PDF guardado en:\n{pdf_path}")
            if os.name == "nt":
                os.startfile(pdf_path)
            else:
                import subprocess
                subprocess.Popen(["xdg-open", pdf_path])
        except Exception as e:
            messagebox.showerror("Error", f"Error generando PDF: {e}")

    def _print_invoice(self, pedido_id):
        pedido = execute_query("SELECT * FROM pedidos WHERE id=%s", (pedido_id,), fetch_one=True)
        items = execute_query("SELECT * FROM pedido_items WHERE pedido_id=%s", (pedido_id,), fetch=True) or []
        if not pedido:
            return
        try:
            pdf_path = generate_invoice_pdf(pedido, items, thermal=True)
            success, msg = print_thermal(pdf_path)
            if success:
                messagebox.showinfo("Impresion", msg)
            else:
                messagebox.showwarning("Impresion", f"No se pudo imprimir.\n{msg}\n\nPDF guardado en: {pdf_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
