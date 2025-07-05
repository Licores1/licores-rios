import sqlite3
from tkinter import messagebox

def alerta_stock_bajo():
    conn = sqlite3.connect("inventario.db")
    cur = conn.cursor()
    try:
        cur.execute("SELECT nombre, cantidad, stock_minimo FROM productos WHERE cantidad < stock_minimo")
        productos = cur.fetchall()
        if productos:
            mensaje = "¡Atención! Los siguientes productos tienen stock por debajo del mínimo:\n\n"
            mensaje += "\n".join([f"{nombre}: {cantidad} (mín: {stock_minimo})" for nombre, cantidad, stock_minimo in productos])
            messagebox.showwarning("Stock bajo", mensaje)
    except Exception as e:
        print("Error verificando stock bajo:", e)
    finally:
        conn.close()