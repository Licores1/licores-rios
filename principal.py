from ventas import registrar_venta_window, historial_ventas_window
import tkinter as tk

# Puedes agregar aquí otros imports si tu sistema lo requiere

def mostrar_menu_principal(rol_usuario):
    ventana = tk.Tk()
    ventana.title("Menú Principal - LICORES RIOS")

    tk.Label(ventana, text="Bienvenido al sistema LICORES RIOS", font=("Arial", 16)).pack(pady=10)

    tk.Button(ventana, text="Gestión de Inventario", width=25, command=abrir_gestion_inventario).pack(pady=5)
    tk.Button(ventana, text="Registrar Venta", width=25, command=registrar_venta_window).pack(pady=5)
    tk.Button(ventana, text="Historial de Ventas", width=25, command=historial_ventas_window).pack(pady=5)

    if rol_usuario == "admin":
        tk.Button(ventana, text="Gestión de Usuarios", width=25, command=abrir_gestion_usuarios).pack(pady=5)
        tk.Button(ventana, text="Reportes", width=25, command=abrir_reportes).pack(pady=5)

    tk.Button(ventana, text="Salir", width=25, command=ventana.destroy).pack(pady=20)
    ventana.mainloop()

def abrir_gestion_inventario():
    # Abre la ventana de gestión de inventario
    from inventario import main
    main()

def abrir_gestion_usuarios():
    # Abre la ventana de gestión de usuarios
    from usuarios import ventana_gestion_usuarios
    ventana_gestion_usuarios()

def abrir_reportes():
    # Abre la ventana de reportes
    from reportes import ventana_reportes
    ventana_reportes()

# Ejemplo de inicio (puedes ajustar rol_usuario según tu lógica de login)
if __name__ == "__main__":
    # Supón que obtienes el rol desde tu sistema de login
    rol_usuario = "admin"  # O "vendedor"
    mostrar_menu_principal(rol_usuario)