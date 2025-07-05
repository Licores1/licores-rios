import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_PATH = "inventario.db"  # Ajusta si tu archivo de base de datos se llama diferente

def ventana_reporte_stock_bajo():
    ventana = tk.Toplevel()
    ventana.title("Inventario bajo stock mínimo")
    ventana.geometry("600x400")

    tk.Label(ventana, text="Productos con stock por debajo del mínimo", font=("Arial", 13)).pack(pady=8)

    columns = ("Producto", "Stock Actual", "Stock Mínimo")
    tree = ttk.Treeview(ventana, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True, pady=10)

    def cargar_stock_bajo():
        tree.delete(*tree.get_children())
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        # Ajusta los nombres de tabla y columnas según tu estructura de inventario
        try:
            cur.execute("""
                SELECT nombre, cantidad, stock_minimo
                FROM productos
                WHERE cantidad < stock_minimo
            """)
            rows = cur.fetchall()
            for row in rows:
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo consultar el inventario: {e}")
        con.close()

    tk.Button(ventana, text="Actualizar", command=cargar_stock_bajo).pack(pady=5)
    cargar_stock_bajo()