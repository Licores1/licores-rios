import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

DB_PATH = "inventario.db"  # Cambia el nombre si tu base de datos es distinto

def ventana_editar_stock_minimo():
    ventana = tk.Toplevel()
    ventana.title("Editar Stock Mínimo de Productos")
    ventana.geometry("600x400")

    columns = ("ID", "Producto", "Stock Actual", "Stock Mínimo")
    tree = ttk.Treeview(ventana, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(fill="both", expand=True, pady=10)

    def cargar_productos():
        tree.delete(*tree.get_children())
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        try:
            cur.execute("SELECT id, nombre, cantidad, stock_minimo FROM productos")
            for row in cur.fetchall():
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo consultar productos: {e}")
        con.close()

    def editar_stock():
        seleccionado = tree.focus()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un producto para editar su stock mínimo.")
            return
        item = tree.item(seleccionado)
        id_producto, nombre, cantidad, stock_minimo = item["values"]
        nuevo_stock = simpledialog.askinteger(
            "Editar stock mínimo",
            f"Producto: {nombre}\nStock mínimo actual: {stock_minimo}\n\nNuevo stock mínimo:",
            minvalue=0
        )
        if nuevo_stock is not None:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            try:
                cur.execute("UPDATE productos SET stock_minimo = ? WHERE id = ?", (nuevo_stock, id_producto))
                con.commit()
                messagebox.showinfo("Éxito", f"Stock mínimo actualizado para '{nombre}'.")
                cargar_productos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
            con.close()

    btn_frame = tk.Frame(ventana)
    btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="Actualizar lista", command=cargar_productos).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Editar stock mínimo", command=editar_stock).pack(side="left", padx=5)

    cargar_productos()