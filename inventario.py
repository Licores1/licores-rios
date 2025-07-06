import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = 'inventario.db'

def obtener_proveedores():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM proveedores")
    proveedores = cur.fetchall()
    conn.close()
    return proveedores

def ventana_agregar_producto(refrescar_tabla):
    win = tk.Toplevel()
    win.title("Agregar Producto")
    win.geometry("400x400")

    tk.Label(win, text="Nombre:").pack()
    entry_nombre = tk.Entry(win)
    entry_nombre.pack()

    tk.Label(win, text="Categoría:").pack()
    entry_categoria = tk.Entry(win)
    entry_categoria.pack()

    tk.Label(win, text="Cantidad:").pack()
    entry_cantidad = tk.Entry(win)
    entry_cantidad.pack()

    tk.Label(win, text="Precio:").pack()
    entry_precio = tk.Entry(win)
    entry_precio.pack()

    tk.Label(win, text="Stock mínimo:").pack()
    entry_stock_minimo = tk.Entry(win)
    entry_stock_minimo.pack()

    tk.Label(win, text="Proveedor:").pack()
    proveedores = obtener_proveedores()
    prov_dict = {nombre: pid for pid, nombre in proveedores}
    prov_names = list(prov_dict.keys())
    prov_var = tk.StringVar()
    proveedor_combo = ttk.Combobox(win, textvariable=prov_var, values=prov_names, state="readonly")
    proveedor_combo.pack()

    def guardar():
        nombre = entry_nombre.get()
        categoria = entry_categoria.get()
        cantidad = entry_cantidad.get()
        precio = entry_precio.get()
        stock_minimo = entry_stock_minimo.get()
        proveedor_nombre = prov_var.get()
        if not (nombre and categoria and cantidad and precio and stock_minimo and proveedor_nombre):
            messagebox.showerror("Error", "Completa todos los campos.", parent=win)
            return
        try:
            cantidad_int = int(cantidad)
            precio_float = float(precio)
            stock_minimo_int = int(stock_minimo)
        except ValueError:
            messagebox.showerror("Error", "Cantidad, precio y stock mínimo deben ser numéricos.", parent=win)
            return
        proveedor_id = prov_dict[proveedor_nombre]
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO inventario (nombre, categoria, cantidad, precio, stock_minimo) VALUES (?, ?, ?, ?, ?)",
                    (nombre, categoria, cantidad_int, precio_float, stock_minimo_int))
        producto_id = cur.lastrowid
        cur.execute("INSERT INTO proveedor_producto (proveedor_id, producto_id) VALUES (?, ?)", (proveedor_id, producto_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Producto agregado y asociado a proveedor.", parent=win)
        win.destroy()
        refrescar_tabla()

    tk.Button(win, text="Guardar", command=guardar, bg="#388E3C", fg="white").pack(pady=10)

def ventana_inventario():
    win = tk.Toplevel()
    win.title("Inventario - LICORES RIOS")
    win.geometry("900x470")

    frame = tk.Frame(win)
    frame.pack(pady=10)

    # Treeview para productos
    tree = ttk.Treeview(win, columns=("ID", "Nombre", "Categoría", "Cantidad", "Precio", "Stock mínimo"), show="headings")
    for col in ("ID", "Nombre", "Categoría", "Cantidad", "Precio", "Stock mínimo"):
        tree.heading(col, text=col)
        if col == "Nombre":
            tree.column(col, width=150)
        elif col == "Stock mínimo":
            tree.column(col, width=100)
        else:
            tree.column(col, width=80)
    tree.pack(expand=True, fill="both")

    def refrescar():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, categoria, cantidad, precio, stock_minimo FROM inventario")
        for prod in cur.fetchall():
            tree.insert('', tk.END, values=prod)
        conn.close()

    def eliminar():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selecciona", "Selecciona un producto para eliminar.")
            return
        prod_id = tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("DELETE FROM inventario WHERE id = ?", (prod_id,))
            cur.execute("DELETE FROM proveedor_producto WHERE producto_id = ?", (prod_id,))
            conn.commit()
            conn.close()
            refrescar()

    tk.Button(frame, text="Agregar Producto", command=lambda: ventana_agregar_producto(refrescar), bg="#2196F3", fg="white").grid(row=0, column=0, pady=10)
    tk.Button(frame, text="Eliminar Producto", command=eliminar, bg="#F44336", fg="white").grid(row=0, column=1, pady=10)

    refrescar()

# Si quieres probar directamente este archivo, descomenta:
# if __name__ == "__main__":
#     root = tk.Tk()
#     root.withdraw()
#     ventana_inventario()
#     root.mainloop()