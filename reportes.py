import tkinter as tk
from tkinter import ttk
from reportes_ventas import ventana_reporte_ventas
from reportes_mas_vendidos import ventana_reporte_mas_vendidos
from reportes_stock_bajo import ventana_reporte_stock_bajo  # <--- NUEVO

def ventana_reportes():
    ventana = tk.Toplevel()
    ventana.title("Reportes - LICORES RIOS")
    ventana.geometry("350x200")

    tk.Label(ventana, text="Seleccione un tipo de reporte:", font=("Arial", 12)).pack(pady=10)

    opciones = ["Ventas por período", "Productos más vendidos", "Inventario bajo stock mínimo"]
    combo = ttk.Combobox(ventana, values=opciones, state="readonly", width=30)
    combo.pack(pady=10)
    combo.current(0)

    def abrir_reporte_seleccionado():
        seleccion = combo.get()
        if seleccion == "Ventas por período":
            ventana.destroy()
            ventana_reporte_ventas()
        elif seleccion == "Productos más vendidos":
            ventana.destroy()
            ventana_reporte_mas_vendidos()
        elif seleccion == "Inventario bajo stock mínimo":
            ventana.destroy()
            ventana_reporte_stock_bajo()

    tk.Button(ventana, text="Abrir reporte", command=abrir_reporte_seleccionado).pack(pady=10)