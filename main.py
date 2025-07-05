import caja
import tkinter as tk
from PIL import Image, ImageTk
import gestionar_usuarios
import inventario
import ventas
import proveedores
import alertas

def abrir_proveedores():
    proveedores.ventana_proveedores()

def abrir_menu(usuario, rol):
    ventana = tk.Tk()
    ventana.title("LICORES RIOS - Menú Principal")
    ventana.geometry("400x550")
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

    tk.Label(ventana, text=f"Bienvenido, {usuario}", font=("Arial", 14)).pack(pady=5)
    tk.Label(ventana, text=f"Rol: {rol}", font=("Arial", 10)).pack(pady=3)

    if rol == "admin":
        tk.Button(
            ventana, text="Gestión de Inventario", width=30,
            command=inventario.main, bg="#2196F3", fg="white"
        ).pack(pady=10)
        tk.Button(
            ventana, text="Gestión de Usuarios", width=30,
            command=gestionar_usuarios.ventana_gestion_usuarios, bg="#FF9800", fg="white"
        ).pack(pady=10)
        tk.Button(
            ventana, text="Registro y Consulta de Ventas", width=30,
            command=ventas.main, bg="#4CAF50", fg="white"
        ).pack(pady=10)
        # --- Botones de caja (solo admin) ---
        tk.Button(
            ventana, text="Registrar Ingreso a Caja", width=30,
            command=lambda: caja.registrar_movimiento("ingreso"), bg="#42a5f5", fg="white"
        ).pack(pady=5)
        tk.Button(
            ventana, text="Registrar Egreso de Caja", width=30,
            command=lambda: caja.registrar_movimiento("egreso"), bg="#ef5350", fg="white"
        ).pack(pady=5)
        tk.Button(
            ventana, text="Ver Historial de Caja", width=30,
            command=caja.ver_historial, bg="#8bc34a", fg="white"
        ).pack(pady=5)
        # --- Botón de Proveedores ---
        tk.Button(
            ventana, text="Proveedores",
            width=30,
            command=abrir_proveedores,
            bg="#00796B",
            fg="white"
        ).pack(pady=10)
    else:
        tk.Button(
            ventana, text="Registrar Venta", width=30,
            command=ventas.main, bg="#4CAF50", fg="white"
        ).pack(pady=10)

    tk.Button(
        ventana, text="Salir", width=30,
        command=ventana.destroy, bg="#F44336", fg="white"
    ).pack(pady=20)

    # Alerta de stock bajo
    alertas.alerta_stock_bajo()

    ventana.mainloop()

if __name__ == "__main__":
    caja.crear_tabla()  # Asegura la tabla de caja al iniciar
    import login
    login.abrir_login(abrir_menu)