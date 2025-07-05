import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DATABASE = "inventario.db"

def crear_tabla():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS caja (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        tipo TEXT NOT NULL,
        monto REAL NOT NULL,
        descripcion TEXT
    )
    """)
    conn.commit()
    conn.close()

def registrar_movimiento(tipo):
    def guardar():
        try:
            monto = float(entry_monto.get())
            descripcion = entry_desc.get().strip()
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO caja (fecha, tipo, monto, descripcion) VALUES (?, ?, ?, ?)",
                        (fecha, tipo, monto, descripcion))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", f"{'Ingreso' if tipo=='ingreso' else 'Egreso'} registrado correctamente.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar movimiento: {e}")

    win = tk.Toplevel()
    win.title(f"Registrar {'Ingreso' if tipo=='ingreso' else 'Egreso'}")
    win.geometry("350x200")

    tk.Label(win, text="Monto:").pack(pady=5)
    entry_monto = tk.Entry(win)
    entry_monto.pack()
    tk.Label(win, text="Descripción:").pack(pady=5)
    entry_desc = tk.Entry(win)
    entry_desc.pack()
    tk.Button(win, text="Guardar", command=guardar, bg="#2196F3", fg="white").pack(pady=15)

def ver_historial():
    win = tk.Toplevel()
    win.title("Historial de Caja")
    win.geometry("600x400")

    tree = ttk.Treeview(win, columns=("ID", "Fecha", "Tipo", "Monto", "Descripción"), show="headings")
    for col in ("ID", "Fecha", "Tipo", "Monto", "Descripción"):
        tree.heading(col, text=col)
        tree.column(col, width=100 if col!="Descripción" else 200)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT id, fecha, tipo, monto, descripcion FROM caja ORDER BY fecha DESC")
    for row in cur.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()

    saldo = calcular_saldo()
    tk.Label(win, text=f"Saldo actual de caja: ${saldo:,.2f}", font=("Calibri", 12, "bold")).pack(pady=5)

def calcular_saldo():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT SUM(CASE WHEN tipo='ingreso' THEN monto ELSE -monto END) FROM caja")
    saldo = cur.fetchone()[0] or 0
    conn.close()
    return saldo

# Puedes agregar estas funciones a tu menú principal:
#   caja.crear_tabla()  # Al iniciar la app, sólo una vez
#   caja.registrar_movimiento("ingreso")
#   caja.registrar_movimiento("egreso")
#   caja.ver_historial()

if __name__ == "__main__":
    crear_tabla()
    root = tk.Tk()
    root.title("Caja - Ingresos y Egresos")
    tk.Button(root, text="Registrar Ingreso", command=lambda: registrar_movimiento("ingreso"), width=25).pack(pady=8)
    tk.Button(root, text="Registrar Egreso", command=lambda: registrar_movimiento("egreso"), width=25).pack(pady=8)
    tk.Button(root, text="Ver Historial de Caja", command=ver_historial, width=25).pack(pady=8)
    saldo = calcular_saldo()
    tk.Label(root, text=f"Saldo actual de caja: ${saldo:,.2f}", font=("Calibri", 12, "bold")).pack(pady=8)
    root.mainloop()