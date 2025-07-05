import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_PATH = "base_datos_licoresrios.db"  # Ajusta si tu base tiene otro nombre

def ventana_reporte_ventas():
    ventana = tk.Toplevel()
    ventana.title("Reporte de Ventas por Período")
    ventana.geometry("700x400")

    tk.Label(ventana, text="Seleccione el período:", font=("Arial", 12)).pack(pady=5)

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

    columns = ("Fecha", "Producto", "Cantidad", "Total", "Vendedor")
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
        cur.execute("""
            SELECT fecha, producto, cantidad, total, vendedor
            FROM ventas
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha ASC
        """, (desde, hasta))
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        con.close()

    tk.Button(ventana, text="Consultar", command=consultar).pack()
    consultar()  # Carga por defecto
