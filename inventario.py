import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DATABASE = "inventario.db"

def main():
    def refrescar():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, categoria, cantidad, precio, stock_minimo FROM productos")
        for prod in cursor.fetchall():
            tree.insert('', tk.END, values=prod)
        conn.close()

    def agregar():
        nombre = entry_nombre.get().strip()
        categoria = entry_categoria.get().strip()
        cantidad = entry_cantidad.get().strip()
        precio = entry_precio.get().strip()
        stock_minimo = entry_stock_minimo.get().strip()
        if not nombre or not cantidad or not precio or not stock_minimo:
            messagebox.showwarning("Campos requeridos", "Completa los campos obligatorios.")
            return
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO productos (nombre, categoria, cantidad, precio, stock_minimo) VALUES (?, ?, ?, ?, ?)",
                (nombre, categoria, int(cantidad), float(precio), int(stock_minimo))
            )
            conn.commit()
            conn.close()
            refrescar()
            entry_nombre.delete(0, tk.END)
            entry_categoria.delete(0, tk.END)
            entry_cantidad.delete(0, tk.END)
            entry_precio.delete(0, tk.END)
            entry_stock_minimo.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selecciona", "Selecciona un producto para eliminar.")
            return
        prod_id = tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (prod_id,))
            conn.commit()
            conn.close()
            refrescar()

    window = tk.Toplevel()
    window.title("Inventario - LICORES RIOS")
    window.geometry("820x420")

    frame = tk.Frame(window)
    frame.pack(pady=10)

    tk.Label(frame, text="Nombre*").grid(row=0, column=0)
    entry_nombre = tk.Entry(frame)
    entry_nombre.grid(row=0, column=1)
    tk.Label(frame, text="Categoría").grid(row=0, column=2)
    entry_categoria = tk.Entry(frame)
    entry_categoria.grid(row=0, column=3)
    tk.Label(frame, text="Cantidad*").grid(row=1, column=0)
    entry_cantidad = tk.Entry(frame)
    entry_cantidad.grid(row=1, column=1)
    tk.Label(frame, text="Precio*").grid(row=1, column=2)
    entry_precio = tk.Entry(frame)
    entry_precio.grid(row=1, column=3)
    tk.Label(frame, text="Stock mínimo*").grid(row=2, column=0)
    entry_stock_minimo = tk.Entry(frame)
    entry_stock_minimo.grid(row=2, column=1)
    tk.Button(frame, text="Agregar", command=agregar, bg="#2196F3", fg="white").grid(row=3, column=0, pady=10)
    tk.Button(frame, text="Eliminar", command=eliminar, bg="#F44336", fg="white").grid(row=3, column=1, pady=10)

    tree = ttk.Treeview(window, columns=("ID", "Nombre", "Categoría", "Cantidad", "Precio", "Stock mínimo"), show="headings")
    for col in ("ID", "Nombre", "Categoría", "Cantidad", "Precio", "Stock mínimo"):
        tree.heading(col, text=col)
        if col == "Nombre":
            tree.column(col, width=150)
        elif col == "Stock mínimo":
            tree.column(col, width=100)
        else:
            tree.column(col, width=80)
    tree.pack(expand=True, fill="both")
    refrescar()

if __name__ == "__main__":
    main()