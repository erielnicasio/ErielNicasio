"""
Modulo de Inventario - Vista visual con imagenes, busqueda y pedidos.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import os

from config import COLORS
from database.connection import execute_query


class InventoryModule:
    """Modulo de inventario con tarjetas visuales de productos."""

    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.is_admin = user["rol"] == "admin"
        self.cart = []
        self._build_ui()
        self._load_products()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self.parent, fg_color="transparent", height=60)
        header.pack(fill="x", padx=25, pady=(20, 10))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="\U0001F4E6 Inventario",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(side="left")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        self.cart_btn = ctk.CTkButton(
            btn_frame, text="\U0001F6D2 Pedido (0)", height=38, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#f59e0b", hover_color="#d97706", text_color="white",
            command=self._show_cart,
        )
        self.cart_btn.pack(side="right", padx=(10, 0))

        if self.is_admin:
            ctk.CTkButton(
                btn_frame, text="+ Nuevo Producto", height=38, corner_radius=10,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                command=self._add_product_dialog,
            ).pack(side="right")

        # Search bar
        search_frame = ctk.CTkFrame(self.parent, fg_color=COLORS["card_bg"],
                                    corner_radius=12, height=50)
        search_frame.pack(fill="x", padx=25, pady=(0, 10))
        search_frame.pack_propagate(False)

        ctk.CTkLabel(search_frame, text="\U0001F50D",
                     font=ctk.CTkFont(size=16)).pack(side="left", padx=(15, 5))
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar producto por nombre...",
            border_width=0, fg_color="transparent", height=36,
            font=ctk.CTkFont(size=13),
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_products())

        # Category filter
        cat_frame = ctk.CTkFrame(self.parent, fg_color="transparent", height=40)
        cat_frame.pack(fill="x", padx=25, pady=(0, 5))
        ctk.CTkLabel(cat_frame, text="Categoria:",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_light"]).pack(side="left", padx=(0, 8))
        self.cat_var = ctk.StringVar(value="Todas")
        self.cat_menu = ctk.CTkOptionMenu(
            cat_frame, values=["Todas"],
            variable=self.cat_var, height=32,
            corner_radius=8, command=lambda _: self._filter_products(),
        )
        self.cat_menu.pack(side="left")

        # Products grid (scrollable)
        self.grid_container = ctk.CTkScrollableFrame(
            self.parent, fg_color="transparent",
        )
        self.grid_container.pack(fill="both", expand=True, padx=25, pady=(5, 20))

    def _load_products(self):
        self.products = execute_query(
            "SELECT * FROM inventario WHERE activo = 1 ORDER BY categoria, nombre",
            fetch=True,
        ) or []

        categories = sorted(set(p.get("categoria", "General") for p in self.products))
        self.cat_menu.configure(values=["Todas"] + categories)

        self._render_products(self.products)

    def _render_products(self, products):
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        if not products:
            ctk.CTkLabel(self.grid_container, text="No se encontraron productos.",
                         font=ctk.CTkFont(size=14),
                         text_color=COLORS["text_light"]).pack(pady=40)
            return

        cols = 3
        row_frame = None
        for i, product in enumerate(products):
            if i % cols == 0:
                row_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
                row_frame.pack(fill="x", pady=5)

            self._create_product_card(row_frame, product)

    def _create_product_card(self, parent, product):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=12,
                            width=280, height=220)
        card.pack(side="left", padx=8, pady=5)
        card.pack_propagate(False)

        # Image placeholder
        img_frame = ctk.CTkFrame(card, fg_color="#e2e8f0", corner_radius=10,
                                 height=80)
        img_frame.pack(fill="x", padx=12, pady=(12, 5))
        img_frame.pack_propagate(False)

        category = product.get("categoria", "General")
        category_icons = {
            "Uniformes": "\U0001F455",
            "Accesorios": "\U0001F392",
            "Utiles": "\U0000270F",
        }
        icon = category_icons.get(category, "\U0001F4E6")
        ctk.CTkLabel(img_frame, text=icon, font=ctk.CTkFont(size=36)).place(
            relx=0.5, rely=0.5, anchor="center")

        # Category badge
        badge_color = {"Uniformes": "#3b82f6", "Accesorios": "#8b5cf6",
                       "Utiles": "#10b981"}.get(category, "#64748b")
        badge = ctk.CTkLabel(card, text=f" {category} ",
                             font=ctk.CTkFont(size=9, weight="bold"),
                             fg_color=badge_color, text_color="white",
                             corner_radius=5, height=20)
        badge.pack(anchor="w", padx=12)

        ctk.CTkLabel(card, text=product["nombre"],
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", padx=12, pady=(2, 0))

        # Price and stock row
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=12, pady=(2, 0))

        ctk.CTkLabel(info_frame, text=f"RD${product['precio']:,.2f}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["primary"]).pack(side="left")

        stock = product.get("stock", 0)
        stock_color = COLORS["success"] if stock > 10 else (COLORS["warning"] if stock > 0 else COLORS["danger"])
        ctk.CTkLabel(info_frame, text=f"Stock: {stock}",
                     font=ctk.CTkFont(size=11),
                     text_color=stock_color).pack(side="right")

        # Add to cart button
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=(5, 10))

        ctk.CTkButton(
            btn_frame, text="Agregar al Pedido", height=32, corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
            command=lambda p=product: self._add_to_cart(p),
        ).pack(fill="x")

    def _filter_products(self):
        query = self.search_entry.get().strip().lower()
        cat = self.cat_var.get()

        filtered = self.products
        if query:
            filtered = [p for p in filtered if query in p["nombre"].lower()]
        if cat != "Todas":
            filtered = [p for p in filtered if p.get("categoria") == cat]
        self._render_products(filtered)

    def _add_to_cart(self, product):
        for item in self.cart:
            if item["id"] == product["id"]:
                item["cantidad"] += 1
                item["subtotal"] = item["cantidad"] * item["precio_unitario"]
                self._update_cart_btn()
                return
        self.cart.append({
            "id": product["id"],
            "nombre": product["nombre"],
            "precio_unitario": float(product["precio"]),
            "cantidad": 1,
            "subtotal": float(product["precio"]),
        })
        self._update_cart_btn()

    def _update_cart_btn(self):
        total_items = sum(item["cantidad"] for item in self.cart)
        self.cart_btn.configure(text=f"\U0001F6D2 Pedido ({total_items})")

    def _show_cart(self):
        if not self.cart:
            messagebox.showinfo("Pedido", "El pedido esta vacio.")
            return

        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Pedido Actual")
        dialog.geometry("500x500")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["card_bg"])

        ctk.CTkLabel(dialog, text="\U0001F6D2 Pedido Actual",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(20, 15))

        items_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent", height=280)
        items_frame.pack(fill="x", padx=20, pady=(0, 10))

        for item in self.cart:
            row = ctk.CTkFrame(items_frame, fg_color="#f8fafc", corner_radius=8, height=45)
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=item["nombre"],
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["text_dark"]).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"x{item['cantidad']}",
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["text_light"]).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"RD${item['subtotal']:,.2f}",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["primary"]).pack(side="right", padx=10)

            ctk.CTkButton(
                row, text="X", width=30, height=28,
                fg_color=COLORS["danger"], hover_color="#b91c1c",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda item_id=item["id"]: self._remove_from_cart(item_id, dialog),
            ).pack(side="right", padx=5)

        total = sum(item["subtotal"] for item in self.cart)
        ctk.CTkLabel(dialog, text=f"Total: RD${total:,.2f}",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=10)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(
            btn_frame, text="Ir a Facturar", height=40, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["success"], hover_color="#16a34a",
            command=lambda: self._go_to_billing(dialog),
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text="Vaciar Pedido", height=40, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["danger"], hover_color="#b91c1c",
            command=lambda: self._clear_cart(dialog),
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def _remove_from_cart(self, item_id, dialog):
        self.cart = [i for i in self.cart if i["id"] != item_id]
        self._update_cart_btn()
        dialog.destroy()
        if self.cart:
            self._show_cart()

    def _clear_cart(self, dialog):
        self.cart.clear()
        self._update_cart_btn()
        dialog.destroy()

    def _go_to_billing(self, dialog):
        dialog.destroy()
        messagebox.showinfo("Facturacion",
                            "Los articulos del pedido han sido preparados.\n"
                            "Vaya al modulo de Facturacion para completar el pago.")

    def _add_product_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Agregar Producto")
        dialog.geometry("450x520")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["card_bg"])

        ctk.CTkLabel(dialog, text="Nuevo Producto",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(20, 15))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(padx=30, fill="x")

        fields = {}
        for label_text in ["Nombre", "Descripcion", "Precio", "Stock"]:
            ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, corner_radius=8,
                                 font=ctk.CTkFont(size=12))
            entry.pack(fill="x")
            fields[label_text.lower()] = entry

        ctk.CTkLabel(form, text="Categoria", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
        cat_var = ctk.StringVar(value="Uniformes")
        ctk.CTkOptionMenu(form, values=["Uniformes", "Accesorios", "Utiles", "Otro"],
                          variable=cat_var, height=36, corner_radius=8).pack(fill="x")

        def save():
            nombre = fields["nombre"].get().strip()
            precio_str = fields["precio"].get().strip()
            stock_str = fields["stock"].get().strip()
            if not nombre or not precio_str:
                messagebox.showwarning("Campos requeridos", "Nombre y Precio son obligatorios.")
                return
            try:
                precio = float(precio_str)
                stock = int(stock_str) if stock_str else 0
            except ValueError:
                messagebox.showwarning("Error", "Precio y Stock deben ser numericos.")
                return
            execute_query(
                "INSERT INTO inventario (nombre, descripcion, categoria, precio, stock) "
                "VALUES (%s, %s, %s, %s, %s)",
                (nombre, fields["descripcion"].get().strip(), cat_var.get(), precio, stock),
            )
            dialog.destroy()
            self._load_products()

        ctk.CTkButton(form, text="Guardar", height=40, corner_radius=10,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                      command=save).pack(fill="x", pady=(20, 10))
