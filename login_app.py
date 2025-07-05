import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

# Configurar modo de apariencia de la app
ctk.set_appearance_mode("dark")  # Puedes cambiar a "light" si prefieres
ctk.set_default_color_theme("blue")

# Datos de usuarios
USUARIOS = {
    "LicoresRios": {
        "password": "Rios2109",
        "rol": "admin"
    },
    "yieisyRios": {
        "password": "Yieisy2025",
        "rol": "ventas"
    }
}

# Ventana principal de login
class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Licores RIOS&CO - Login")
        self.geometry("400x300")
        self.resizable(False, False)

        self.label_title = ctk.CTkLabel(self, text="Inicio de sesión", font=("Arial", 22, "bold"))
        self.label_title.pack(pady=20)

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Usuario")
        self.entry_user.pack(pady=10, ipadx=10, ipady=5)

        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*")
        self.entry_pass.pack(pady=10, ipadx=10, ipady=5)

        self.btn_login = ctk.CTkButton(self, text="Ingresar", command=self.verificar_login)
        self.btn_login.pack(pady=20)

    def verificar_login(self):
        user = self.entry_user.get()
        password = self.entry_pass.get()

        if user in USUARIOS and USUARIOS[user]["password"] == password:
            rol = USUARIOS[user]["rol"]
            messagebox.showinfo("Éxito", f"Bienvenido, {user} ({rol})")
            self.destroy()
            abrir_menu_principal(user, rol)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

# Menú principal según el rol del usuario
class MenuPrincipal(ctk.CTk):
    def __init__(self, usuario, rol):
        super().__init__()

        self.title("Panel Principal - Licores RIOS&CO")
        self.geometry("600x400")

        label = ctk.CTkLabel(self, text=f"Bienvenido, {usuario} ({rol})", font=("Arial", 20))
        label.pack(pady=30)

        if rol == "admin":
            ctk.CTkButton(self, text="Gestión de Inventario", width=200).pack(pady=10)
            ctk.CTkButton(self, text="Registrar Venta", width=200).pack(pady=10)
        elif rol == "ventas":
            ctk.CTkButton(self, text="Registrar Venta", width=200).pack(pady=10)

        ctk.CTkButton(self, text="Cerrar sesión", command=self.salir, fg_color="red").pack(pady=20)

    def salir(self):
        self.destroy()
        app = LoginApp()
        app.mainloop()

# Función para abrir menú luego de login

def abrir_menu_principal(usuario, rol):
    ventana = MenuPrincipal(usuario, rol)
    ventana.mainloop()

# Ejecutar login
if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
