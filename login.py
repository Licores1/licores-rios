import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import usuarios

def abrir_login(callback_al_autenticar):
    def intentar_login():
        usuario = entry_usuario.get().strip()
        password = entry_password.get().strip()
        rol = usuarios.autenticar(usuario, password)
        if rol:
            ventana.destroy()
            callback_al_autenticar(usuario, rol)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    ventana = tk.Tk()
    ventana.title("LICORES RIOS - Iniciar sesión")
    ventana.geometry("400x400")
    ventana.resizable(False, False)

    # Logo
    try:
        logo = Image.open("logo.png")
        logo = logo.resize((150, 150))
        logo_img = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(ventana, image=logo_img)
        logo_label.image = logo_img
        logo_label.pack(pady=5)
    except Exception:
        tk.Label(ventana, text="LICORES RIOS", font=("Arial", 16, "bold")).pack(pady=10)

    tk.Label(ventana, text="Usuario:").pack(pady=5)
    entry_usuario = tk.Entry(ventana)
    entry_usuario.pack()

    tk.Label(ventana, text="Contraseña:").pack(pady=5)
    entry_password = tk.Entry(ventana, show="*")
    entry_password.pack()

    tk.Button(ventana, text="Ingresar", command=intentar_login, bg="#4caf50", fg="white").pack(pady=20)
    ventana.mainloop()