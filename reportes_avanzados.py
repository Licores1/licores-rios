import tkinter as tk
from tkinter import ttk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

def ventana_reportes_avanzados():
    win = tk.Toplevel()
    win.title("Reportes Avanzados")

    tk.Label(win, text="Fecha inicio (YYYY-MM-DD):").pack()
    entry_inicio = tk.Entry(win)
    entry_inicio.pack()

    tk.Label(win, text="Fecha fin (YYYY-MM-DD):").pack()
    entry_fin = tk.Entry(win)
    entry_fin.pack()

    def generar_reportes():
        fecha_inicio = entry_inicio.get()
        fecha_fin = entry_fin.get()
        mostrar_grafico_ventas(win, fecha_inicio, fecha_fin)
        mostrar_top_productos(win, fecha_inicio, fecha_fin)

    tk.Button(win, text="Generar reportes", command=generar_reportes).pack(pady=5)

def mostrar_grafico_ventas(parent, fecha_inicio, fecha_fin):
    # Conecta a la base de datos y obtiene ventas agrupadas por día
    conn = sqlite3.connect('tu_basedatos.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, SUM(total) as total_ventas
        FROM ventas
        WHERE fecha BETWEEN ? AND ?
        GROUP BY fecha
        ORDER BY fecha ASC
    """, (fecha_inicio, fecha_fin))
    registros = cursor.fetchall()
    conn.close()

    # Prepara datos para el gráfico
    fechas = [r[0] for r in registros]
    totales = [r[1] for r in registros]

    fig, ax = plt.subplots(figsize=(5,3))
    ax.plot(fechas, totales, marker='o')
    ax.set_title("Ventas por Día")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Total Ventas")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack()

def mostrar_top_productos(parent, fecha_inicio, fecha_fin):
    # Conecta a la base de datos y obtiene productos más vendidos
    conn = sqlite3.connect('tu_basedatos.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT producto, SUM(cantidad) as total_vendido
        FROM ventas_detalle
        WHERE fecha BETWEEN ? AND ?
        GROUP BY producto
        ORDER BY total_vendido DESC
        LIMIT 10
    """, (fecha_inicio, fecha_fin))
    registros = cursor.fetchall()
    conn.close()

    frame = tk.Frame(parent)
    frame.pack(pady=10)
    tk.Label(frame, text="Top 10 productos más vendidos", font=('Arial', 12, 'bold')).pack()
    tree = ttk.Treeview(frame, columns=("Producto", "Cantidad"), show="headings")
    tree.heading("Producto", text="Producto")
    tree.heading("Cantidad", text="Cantidad Vendida")
    for producto, cantidad in registros:
        tree.insert('', 'end', values=(producto, cantidad))
    tree.pack()