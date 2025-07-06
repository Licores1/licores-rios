import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

DB_NAME = 'inventario.db'

def obtener_proveedores():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM proveedores")
    proveedores = cur.fetchall()
    conn.close()
    return proveedores

def registrar_movimiento(producto_id, tipo, cantidad, descripcion=""):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO historial_movimientos (producto_id, tipo, cantidad, fecha, descripcion)
        VALUES (?, ?, ?, datetime('now','localtime'), ?)
    """, (producto_id, tipo, cantidad, descripcion))
    conn.commit()
    conn.close()

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
        registrar_movimiento(producto_id, "alta", cantidad_int, "Alta de producto")
        messagebox.showinfo("Éxito", "Producto agregado y asociado a proveedor.", parent=win)
        win.destroy()
        refrescar_tabla()

    tk.Button(win, text="Guardar", command=guardar, bg="#388E3C", fg="white").pack(pady=10)

def ventana_inventario():
    win = tk.Toplevel()
    win.title("Inventario - LICORES RIOS")
    win.geometry("1050x600")

    frame = tk.Frame(win)
    frame.pack(pady=10)

    search_var = tk.StringVar()

    tk.Label(win, text="Buscar producto (nombre/categoría):").pack()
    tk.Entry(win, textvariable=search_var).pack()
    
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

    def buscar():
        filtro = search_var.get().lower()
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, categoria, cantidad, precio, stock_minimo FROM inventario")
        for prod in cur.fetchall():
            if filtro in prod[1].lower() or filtro in prod[2].lower():
                tree.insert('', tk.END, values=prod)
        conn.close()

    def filtrar_stock_bajo():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, categoria, cantidad, precio, stock_minimo FROM inventario WHERE cantidad <= stock_minimo")
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
            registrar_movimiento(prod_id, "baja", 0, "Eliminación de producto")
            refrescar()

    def editar_producto():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selecciona", "Selecciona un producto para editar.")
            return
        datos = tree.item(selected[0])['values']
        prod_id, nombre, categoria, cantidad, precio, stock_minimo = datos

        edit_win = tk.Toplevel(win)
        edit_win.title("Editar Producto")
        edit_win.geometry("400x400")

        tk.Label(edit_win, text="Nombre:").pack()
        entry_nombre = tk.Entry(edit_win)
        entry_nombre.insert(0, nombre)
        entry_nombre.pack()

        tk.Label(edit_win, text="Categoría:").pack()
        entry_categoria = tk.Entry(edit_win)
        entry_categoria.insert(0, categoria)
        entry_categoria.pack()

        tk.Label(edit_win, text="Cantidad:").pack()
        entry_cantidad = tk.Entry(edit_win)
        entry_cantidad.insert(0, cantidad)
        entry_cantidad.pack()

        tk.Label(edit_win, text="Precio:").pack()
        entry_precio = tk.Entry(edit_win)
        entry_precio.insert(0, precio)
        entry_precio.pack()

        tk.Label(edit_win, text="Stock mínimo:").pack()
        entry_stock_minimo = tk.Entry(edit_win)
        entry_stock_minimo.insert(0, stock_minimo)
        entry_stock_minimo.pack()

        def guardar_edicion():
            try:
                nuevo_nombre = entry_nombre.get()
                nueva_categoria = entry_categoria.get()
                nueva_cantidad = int(entry_cantidad.get())
                nuevo_precio = float(entry_precio.get())
                nuevo_stock_minimo = int(entry_stock_minimo.get())
            except ValueError:
                messagebox.showerror("Error", "Cantidad, precio y stock mínimo deben ser numéricos.", parent=edit_win)
                return
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("""
                UPDATE inventario SET nombre=?, categoria=?, cantidad=?, precio=?, stock_minimo=?
                WHERE id=?
            """, (nuevo_nombre, nueva_categoria, nueva_cantidad, nuevo_precio, nuevo_stock_minimo, prod_id))
            conn.commit()
            conn.close()
            registrar_movimiento(prod_id, "edicion", nueva_cantidad, "Edición de producto")
            edit_win.destroy()
            refrescar()

        tk.Button(edit_win, text="Guardar cambios", command=guardar_edicion, bg="#388E3C", fg="white").pack(pady=10)

    def exportar_excel():
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not filename:
            return
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["ID", "Nombre", "Categoría", "Cantidad", "Precio", "Stock Mínimo"])
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, categoria, cantidad, precio, stock_minimo FROM inventario")
        for row in cur.fetchall():
            ws.append(row)
        conn.close()
        wb.save(filename)
        messagebox.showinfo("Exportado", f"Inventario exportado a {filename}")

    def exportar_pdf():
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not filename:
            return
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Helvetica", 10)
        c.drawString(30, 750, "Inventario - Licores Rios")
        y = 720
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT nombre, categoria, cantidad, precio, stock_minimo FROM inventario")
        c.drawString(30, y, "Nombre     Categoría    Cantidad    Precio    Stock Min")
        y -= 20
        for row in cur.fetchall():
            c.drawString(30, y, "   ".join([str(x) for x in row]))
            y -= 15
            if y < 40:
                c.showPage()
                y = 750
        conn.close()
        c.save()
        messagebox.showinfo("Exportado", f"Inventario exportado a {filename}")

    def ver_historial():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selecciona", "Selecciona un producto.")
            return
        prod_id = tree.item(selected[0])['values'][0]
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT tipo, cantidad, fecha, descripcion FROM historial_movimientos WHERE producto_id=? ORDER BY fecha DESC", (prod_id,))
        movimientos = cur.fetchall()
        conn.close()
        win_historial = tk.Toplevel(win)
        win_historial.title("Historial de movimientos")
        tree_hist = ttk.Treeview(win_historial, columns=("Tipo", "Cantidad", "Fecha", "Descripción"), show="headings")
        for col in ("Tipo", "Cantidad", "Fecha", "Descripción"):
            tree_hist.heading(col, text=col)
        tree_hist.pack(fill="both", expand=True)
        for mov in movimientos:
            tree_hist.insert("", tk.END, values=mov)

    # Botones
    tk.Button(frame, text="Agregar Producto", command=lambda: ventana_agregar_producto(refrescar), bg="#2196F3", fg="white").grid(row=0, column=0, pady=10)
    tk.Button(frame, text="Eliminar Producto", command=eliminar, bg="#F44336", fg="white").grid(row=0, column=1, pady=10)
    tk.Button(frame, text="Editar Producto", command=editar_producto, bg="#FF9800", fg="white").grid(row=0, column=2, pady=10)
    tk.Button(frame, text="Ver Historial", command=ver_historial, bg="#6A1B9A", fg="white").grid(row=0, column=3, pady=10)

    tk.Button(win, text="Buscar", command=buscar, bg="#1976D2", fg="white").pack(pady=4)
    tk.Button(win, text="Filtrar por stock bajo", command=filtrar_stock_bajo, bg="#FF5252", fg="white").pack(pady=4)
    tk.Button(win, text="Exportar a Excel", command=exportar_excel, bg="#1976D2", fg="white").pack(pady=4)
    tk.Button(win, text="Exportar a PDF", command=exportar_pdf, bg="#C62828", fg="white").pack(pady=4)

    refrescar()

# --- INTEGRACIÓN CON VENTAS ---
def descontar_stock_y_registrar_venta(producto_id, cantidad, descripcion="Venta realizada"):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE id = ?", (cantidad, producto_id))
    conn.commit()
    conn.close()
    registrar_movimiento(producto_id, "venta", -cantidad, descripcion)

# Si quieres probar directamente este archivo, descomenta:
# if __name__ == "__main__":
#     root = tk.Tk()
#     root.withdraw()
#     ventana_inventario()
#     root.mainloop()