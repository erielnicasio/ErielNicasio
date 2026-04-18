"""
Ventana de inicio de sesion para Perfecto Labs.
"""

import customtkinter as ctk

from auth.auth_manager import authenticate
from config import APP_NAME, COLORS


class LoginWindow(ctk.CTkToplevel):
    """Ventana de login con diseno moderno."""

    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.title(f"{APP_NAME} - Iniciar Sesion")
        self.geometry("480x600")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_main"])
        self.grab_set()

        self._build_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=20)
        main_frame.pack(padx=40, pady=40, fill="both", expand=True)

        # Logo area
        logo_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["primary"], corner_radius=15,
                                  height=80, width=80)
        logo_frame.pack(pady=(30, 5))
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="PL", font=ctk.CTkFont(size=32, weight="bold"),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(main_frame, text="Perfecto Labs",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(10, 0))
        ctk.CTkLabel(main_frame, text="Sistema de Gestion",
                     font=ctk.CTkFont(size=13),
                     text_color=COLORS["text_light"]).pack(pady=(0, 25))

        # Form
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(padx=35, fill="x")

        ctk.CTkLabel(form_frame, text="Usuario",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x")
        self.username_entry = ctk.CTkEntry(
            form_frame, height=42, corner_radius=10,
            placeholder_text="Ingrese su usuario",
            font=ctk.CTkFont(size=13),
        )
        self.username_entry.pack(fill="x", pady=(3, 15))

        ctk.CTkLabel(form_frame, text="Contrasena",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["text_dark"], anchor="w").pack(fill="x")
        self.password_entry = ctk.CTkEntry(
            form_frame, height=42, corner_radius=10,
            placeholder_text="Ingrese su contrasena",
            show="*", font=ctk.CTkFont(size=13),
        )
        self.password_entry.pack(fill="x", pady=(3, 5))

        self.show_pw_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            form_frame, text="Mostrar contrasena",
            variable=self.show_pw_var,
            command=self._toggle_password,
            font=ctk.CTkFont(size=11),
            checkbox_height=18, checkbox_width=18,
        ).pack(anchor="w", pady=(0, 15))

        self.error_label = ctk.CTkLabel(
            form_frame, text="", font=ctk.CTkFont(size=12),
            text_color=COLORS["danger"],
        )
        self.error_label.pack(fill="x")

        self.login_btn = ctk.CTkButton(
            form_frame, text="Iniciar Sesion", height=44,
            corner_radius=10, font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
            command=self._login,
        )
        self.login_btn.pack(fill="x", pady=(10, 15))

        ctk.CTkLabel(main_frame, text="v1.0.0 | Perfecto Labs 2026",
                     font=ctk.CTkFont(size=10),
                     text_color=COLORS["text_light"]).pack(side="bottom", pady=10)

        self.username_entry.focus_set()
        self.password_entry.bind("<Return>", lambda e: self._login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus_set())

    def _toggle_password(self):
        self.password_entry.configure(show="" if self.show_pw_var.get() else "*")

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="Complete todos los campos.")
            return

        self.login_btn.configure(state="disabled", text="Verificando...")
        self.update()

        user, message = authenticate(username, password)

        if user:
            self.on_login_success(user)
            self.destroy()
        else:
            self.error_label.configure(text=message)
            self.login_btn.configure(state="normal", text="Iniciar Sesion")
