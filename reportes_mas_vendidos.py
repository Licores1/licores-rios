import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_PATH = "inventario.db"  # Asegúrate que coincide con tu archivo de base de datos

def ventana_reporte_mas_vendidos():
    ventana = tk.Toplevel()
    ventana.title("Productos más vendidos")
    ventana.geometry("600x400")

    tk.Label(ventana, text="Productos más vendidos en un período", font=("Arial", 13)).pack(pady=8)

    frame = tk.Frame(ventana)
    frame.pack(pady=5)

    tk.Label(frame, text="Desde (AAAA-MM-DD):").grid(row=0, column=0, padx=5)
    desde_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-01"))
    desde_entry = tk.Entry(frame, textvariable=desde_var, width=12)
    desde_entry.grid(row=0, column=1, padx=5)

    tk.Label(frame, text="Hasta (AAAA-MM-DD):").grid(row=0, column=2, padx=5)
    hasta_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    hasta_entry = tk.Entry(frame, textvariable=hasta_var, width=12)
    hasta_entry.grid(row=0, column=3, padx=5)

    columns = ("Producto", "Cantidad Vendida", "Total Vendido ($)")
    tree = ttk.Treeview(ventana, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True, pady=10)

    def consultar():
        tree.delete(*tree.get_children())
        desde = desde_var.get()
        hasta = hasta_var.get()
        try:
            datetime.strptime(desde, "%Y-%m-%d")
            datetime.strptime(hasta, "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Formato de fecha incorrecto (use AAAA-MM-DD)")
            return
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        # Ajusta los campos según tu tabla 'ventas' y su estructura
        cur.execute("""
            SELECT producto, SUM(cantidad) as total_cantidad, SUM(total) as total_ventas
            FROM ventas
            WHERE fecha BETWEEN ? AND ?
            GROUP BY producto
            ORDER BY total_cantidad DESC
        """, (desde, hasta))
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        con.close()

    tk.Button(ventana, text="Consultar", command=consultar).pack()
    consultar()  # Carga los datos por defecto
