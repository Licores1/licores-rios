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

    # === NUEVA FUNCIÓN PARA OBTENER PROVEEDORES ===
    def obtener_proveedores():
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM proveedores")
        proveedores = cursor.fetchall()
        conn.close()
        return proveedores

    def agregar():
        nombre = entry_nombre.get().strip()
        categoria = entry_categoria.get().strip()
        cantidad = entry_cantidad.get().strip()
        precio = entry_precio.get().strip()
        stock_minimo = entry_stock_minimo.get().strip()
        proveedor_nombre = proveedor_var.get()
        if not nombre or not cantidad or not precio or not stock_minimo or not proveedor_nombre:
            messagebox.showwarning("Campos requeridos", "Completa todos los campos obligatorios (incluido proveedor).")
            return
        try:
            cantidad_int = int(cantidad)
            precio_float = float(precio)
            stock_minimo_int = int(stock_minimo)
        except Exception:
            messagebox.showerror("Error", "Cantidad, precio y stock mínimo deben ser numéricos.")
            return
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            # Insertar producto
            cursor.execute(
                "INSERT INTO productos (nombre, categoria, cantidad, precio, stock_minimo) VALUES (?, ?, ?, ?, ?)",
                (nombre, categoria, cantidad_int, precio_float, stock_minimo_int)
            )
            producto_id = cursor.lastrowid
            # Obtener proveedor_id
            cursor.execute("SELECT id FROM proveedores WHERE nombre = ?", (proveedor_nombre,))
            row = cursor.fetchone()
            if not row:
                raise Exception("Proveedor no encontrado. Actualiza la lista.")
            proveedor_id = row[0]
            # Registrar asociación en proveedor_producto
            cursor.execute(
                "INSERT INTO proveedor_producto (proveedor_id, producto_id) VALUES (?, ?)",
                (proveedor_id, producto_id)
            )
            conn.commit()
            conn.close()
            refrescar()
            entry_nombre.delete(0, tk.END)
            entry_categoria.delete(0, tk.END)
            entry_cantidad.delete(0, tk.END)
            entry_precio.delete(0, tk.END)
            entry_stock_minimo.delete(0, tk.END)
            proveedor_combo.set('')
            messagebox.showinfo("Éxito", "Producto y proveedor asociados correctamente.")
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
            # También borra la asociación en proveedor_producto
            cursor.execute("DELETE FROM proveedor_producto WHERE producto_id = ?", (prod_id,))
            conn.commit()
            conn.close()
            refrescar()

    window = tk.Toplevel()
    window.title("Inventario - LICORES RIOS")
    window.geometry("900x470")

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
    entry_precio
