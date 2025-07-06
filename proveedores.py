import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl

DATABASE = "inventario.db"
STOCK_MIN = 5  # Puedes ajustar el mínimo de stock según tu política

def conectar():
    return sqlite3.connect(DATABASE)

# Sugerir pedidos automáticos por bajo stock
def sugerir_pedidos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.nombre, p.stock, p.precio_compra, pr.nombre 
        FROM productos p
        LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
        WHERE p.stock <= ?;
    """, (STOCK_MIN,))
    productos_bajo_stock = cur.fetchall()
    conn.close()
    return productos_bajo_stock

# Productos sin proveedor asignado
def productos_sin_proveedor():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nombre, stock FROM productos WHERE proveedor_id IS NULL OR proveedor_id = '';
    """)
    sin_prov = cur.fetchall()
    conn.close()
    return sin_prov

# Pedidos pendientes (no recibidos)
def pedidos_pendientes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, proveedor_id, fecha, estado FROM pedidos WHERE estado != 'recibido';
    """)
    pendientes = cur.fetchall()
    conn.close()
    return pendientes

# Actualizar stock y estado de pedido al recibirlo
def recibir_pedido(pedido_id):
    conn = conectar()
    cur = conn.cursor()
    # Obtener los productos y cantidades del pedido
    cur.execute("SELECT producto_id, cantidad, precio_compra FROM detalles_pedido WHERE pedido_id = ?", (pedido_id,))
    detalles = cur.fetchall()
    # Sumar cantidades al inventario y actualizar precio de compra si cambió
    for prod_id, cantidad, nuevo_precio in detalles:
        cur.execute("SELECT precio_compra FROM productos WHERE id = ?", (prod_id,))
        precio_actual = cur.fetchone()
        if precio_actual and precio_actual[0] != nuevo_precio:
            cur.execute("UPDATE productos SET precio_compra = ? WHERE id = ?", (nuevo_precio, prod_id))
        cur.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (cantidad, prod_id))
    # Marcar pedido como recibido
    cur.execute("UPDATE pedidos SET estado = 'recibido', fecha_recibido = ? WHERE id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pedido_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Pedido recibido", "Stock actualizado y pedido marcado como recibido.")

# Exportar orden de compra a PDF
def exportar_pedido_pdf(pedido_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT proveedor_id, fecha FROM pedidos WHERE id = ?", (pedido_id,))
    pedido = cur.fetchone()
    cur.execute("SELECT nombre FROM proveedores WHERE id = ?", (pedido[0],))
    proveedor = cur.fetchone()
    cur.execute("""
        SELECT p.nombre, d.cantidad, d.precio_compra
        FROM detalles_pedido d
        JOIN productos p ON d.producto_id = p.id
        WHERE d.pedido_id = ?
    """, (pedido_id,))
    detalles = cur.fetchall()
    conn.close()

    filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not filename:
        return

    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(30, 750, f"Orden de Compra ID: {pedido_id}")
    c.drawString(30, 735, f"Proveedor: {proveedor[0] if proveedor else 'N/A'}")
    c.drawString(30, 720, f"Fecha: {pedido[1]}")
    c.drawString(30, 700, "Productos:")
    y = 680
    c.drawString(40, y, "Nombre")
    c.drawString(220, y, "Cantidad")
    c.drawString(320, y, "Precio Compra")
    y -= 20
    for nombre, cantidad, precio in detalles:
        c.drawString(40, y, str(nombre))
        c.drawString(220, y, str(cantidad))
        c.drawString(320, y, f"${precio:.2f}")
        y -= 20
        if y < 80:
            c.showPage()
            y = 750
    c.save()
    messagebox.showinfo("Exportado", f"PDF guardado en {filename}")

# Exportar orden de compra a Excel
def exportar_pedido_excel(pedido_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT proveedor_id, fecha FROM pedidos WHERE id = ?", (pedido_id,))
    pedido = cur.fetchone()
    cur.execute("SELECT nombre FROM proveedores WHERE id = ?", (pedido[0],))
    proveedor = cur.fetchone()
    cur.execute("""
        SELECT p.nombre, d.cantidad, d.precio_compra
        FROM detalles_pedido d
        JOIN productos p ON d.producto_id = p.id
        WHERE d.pedido_id = ?
    """, (pedido_id,))
    detalles = cur.fetchall()
    conn.close()

    filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if not filename:
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Orden de Compra"
    ws.append(["Orden de Compra ID", pedido_id])
    ws.append(["Proveedor", proveedor[0] if proveedor else 'N/A'])
    ws.append(["Fecha", pedido[1]])
    ws.append([])
    ws.append(["Nombre", "Cantidad", "Precio Compra"])
    for nombre, cantidad, precio in detalles:
        ws.append([nombre, cantidad, precio])
    wb.save(filename)
    messagebox.showinfo("Exportado", f"Excel guardado en {filename}")

# Historial de compras por proveedor
def historial_compras_proveedor(proveedor_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.fecha, SUM(d.cantidad), SUM(d.cantidad*d.precio_compra)
        FROM pedidos p
        JOIN detalles_pedido d ON d.pedido_id = p.id
        WHERE p.proveedor_id = ?
        GROUP BY p.id
        ORDER BY p.fecha DESC
    """, (proveedor_id,))
    compras = cur.fetchall()
    conn.close()
    return compras

# ----------- NUEVO: VENTANA NUEVO PEDIDO ----------
def ventana_nuevo_pedido():
    win_pedido = tk.Toplevel()
    win_pedido.title("Nuevo Pedido")
    win_pedido.geometry("500x550")

    # Seleccionar proveedor
    tk.Label(win_pedido, text="Proveedor:").pack()
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM proveedores")
    proveedores = cur.fetchall()
    conn.close()
    proveedor_var = tk.StringVar()
    proveedor_menu = ttk.Combobox(win_pedido, textvariable=proveedor_var, values=[f"{pid} - {nombre}" for pid, nombre in proveedores])
    proveedor_menu.pack()

    # Seleccionar productos y cantidades
    tk.Label(win_pedido, text="Producto:").pack()
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM productos")
    productos = cur.fetchall()
    conn.close()
    producto_var = tk.StringVar()
    producto_menu = ttk.Combobox(win_pedido, textvariable=producto_var, values=[f"{pid} - {nombre}" for pid, nombre in productos])
    producto_menu.pack()

    tk.Label(win_pedido, text="Cantidad:").pack()
    cantidad_var = tk.IntVar(value=1)
    cantidad_entry = tk.Entry(win_pedido, textvariable=cantidad_var)
    cantidad_entry.pack()

    tk.Label(win_pedido, text="Precio compra:").pack()
    precio_var = tk.DoubleVar(value=0)
    precio_entry = tk.Entry(win_pedido, textvariable=precio_var)
    precio_entry.pack()

    items = []

    def agregar_producto():
        if producto_var.get() and cantidad_var.get() > 0:
            items.append((producto_var.get(), cantidad_var.get(), precio_var.get()))
            lista.insert(tk.END, f"{producto_var.get()} x{cantidad_var.get()} - ${precio_var.get():.2f}")

    lista = tk.Listbox(win_pedido)
    lista.pack(fill="both", expand=True)

    btn_agregar = tk.Button(win_pedido, text="Agregar producto", command=agregar_producto)
    btn_agregar.pack()

    def guardar_pedido():
        if not proveedor_var.get() or not items:
            messagebox.showerror("Error", "Completa todos los datos")
            return
        proveedor_id = int(proveedor_var.get().split(" - ")[0])
        conn = conectar()
        cur = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d")
        cur.execute("INSERT INTO pedidos (proveedor_id, fecha, estado) VALUES (?, ?, 'pendiente')", (proveedor_id, fecha))
        pedido_id = cur.lastrowid
        for prod, cantidad, precio in items:
            producto_id = int(prod.split(" - ")[0])
            cur.execute("INSERT INTO detalles_pedido (pedido_id, producto_id, cantidad, precio_compra) VALUES (?, ?, ?, ?)",
                        (pedido_id, producto_id, cantidad, precio))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Pedido registrado")
        win_pedido.destroy()

    btn_guardar = tk.Button(win_pedido, text="Guardar Pedido", command=guardar_pedido, bg="#2196F3", fg="white")
    btn_guardar.pack(pady=10)
# ----------- FIN NUEVO ----------

# Ventana principal de proveedores
def proveedores_window():
    win = tk.Toplevel()
    win.title("Gestión de Proveedores")
    win.geometry("1050x700")

    # Panel de sugerencias
    frame_alertas = tk.Frame(win)
    frame_alertas.pack(fill="x", pady=5)

    # Bajo stock
    bajo_stock = sugerir_pedidos()
    if bajo_stock:
        alert = tk.Label(frame_alertas, text="¡Atención! Los siguientes productos están por debajo del stock mínimo:", fg="red", font=("Arial", 10, "bold"))
        alert.pack(anchor="w")
        for p in bajo_stock:
            txt = f"Producto: {p[1]} | Stock: {p[2]} | Proveedor: {p[4] or 'No asignado'}"
            tk.Label(frame_alertas, text=txt, fg="black").pack(anchor="w")

    # Productos sin proveedor
    sin_prov = productos_sin_proveedor()
    if sin_prov:
        alert2 = tk.Label(frame_alertas, text="¡Atención! Hay productos sin proveedor asignado:", fg="orange", font=("Arial", 10, "bold"))
        alert2.pack(anchor="w")
        for p in sin_prov:
            tk.Label(frame_alertas, text=f"Producto: {p[1]} | Stock: {p[2]}", fg="black").pack(anchor="w")

    # Pedidos pendientes
    pendientes = pedidos_pendientes()
    if pendientes:
        alert3 = tk.Label(frame_alertas, text="Pedidos pendientes de recibir:", fg="blue", font=("Arial", 10, "bold"))
        alert3.pack(anchor="w")
        for p in pendientes:
            txt = f"Pedido ID: {p[0]} | Proveedor ID: {p[1]} | Fecha: {p[2]} | Estado: {p[3]}"
            tk.Label(frame_alertas, text=txt, fg="black").pack(anchor="w")

    # Tabla de proveedores
    frame_prov = tk.Frame(win)
    frame_prov.pack(fill="x", pady=10)
    tk.Label(frame_prov, text="Proveedores:").pack(anchor="w")
    tree_prov = ttk.Treeview(win, columns=("ID", "Nombre", "Contacto", "Teléfono", "Email"), show="headings", height=8)
    for col in ("ID", "Nombre", "Contacto", "Teléfono", "Email"):
        tree_prov.heading(col, text=col)
    tree_prov.pack(fill="x", padx=10)

    def cargar_proveedores():
        tree_prov.delete(*tree_prov.get_children())
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, contacto, telefono, email FROM proveedores")
        for p in cur.fetchall():
            tree_prov.insert("", tk.END, values=p)
        conn.close()
    cargar_proveedores()

    # NUEVO: Botón para nuevo pedido
    tk.Button(win, text="Nuevo Pedido", command=ventana_nuevo_pedido, bg="#4CAF50", fg="white").pack(pady=10)

    # Historial de compras por proveedor
    def mostrar_historial():
        sel = tree_prov.selection()
        if not sel:
            messagebox.showinfo("Seleccione", "Seleccione un proveedor")
            return
        proveedor_id = tree_prov.item(sel[0])["values"][0]
        historial = historial_compras_proveedor(proveedor_id)
        win2 = tk.Toplevel(win)
        win2.title("Historial de compras")
        tree = ttk.Treeview(win2, columns=("Pedido", "Fecha", "Total Unidades", "Total Gasto"), show="headings")
        for col in ("Pedido", "Fecha", "Total Unidades", "Total Gasto"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=10, pady=5)
        for h in historial:
            tree.insert("", tk.END, values=h)

    tk.Button(win, text="Ver historial de compras", command=mostrar_historial).pack(pady=5)

    # Tabla de pedidos para recibir, marcar recibido, exportar
    frame_pedidos = tk.Frame(win)
    frame_pedidos.pack(fill="x", pady=10)
    tk.Label(frame_pedidos, text="Pedidos:").pack(anchor="w")
    tree_pedidos = ttk.Treeview(win, columns=("ID", "Proveedor", "Fecha", "Estado"), show="headings", height=8)
    for col in ("ID", "Proveedor", "Fecha", "Estado"):
        tree_pedidos.heading(col, text=col)
    tree_pedidos.pack(fill="x", padx=10)

    def cargar_pedidos():
        tree_pedidos.delete(*tree_pedidos.get_children())
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, pr.nombre, p.fecha, p.estado FROM pedidos p
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            ORDER BY p.fecha DESC
        """)
        for p in cur.fetchall():
            tree_pedidos.insert("", tk.END, values=p)
        conn.close()
    cargar_pedidos()

    def marcar_recibido():
        sel = tree_pedidos.selection()
        if not sel:
            messagebox.showinfo("Seleccione", "Seleccione un pedido")
            return
        pedido_id = tree_pedidos.item(sel[0])["values"][0]
        recibir_pedido(pedido_id)
        cargar_pedidos()

    def exportar_pdf():
        sel = tree_pedidos.selection()
        if not sel:
            messagebox.showinfo("Seleccione", "Seleccione un pedido")
            return
        pedido_id = tree_pedidos.item(sel[0])["values"][0]
        exportar_pedido_pdf(pedido_id)

    def exportar_excel():
        sel = tree_pedidos.selection()
        if not sel:
            messagebox.showinfo("Seleccione", "Seleccione un pedido")
            return
        pedido_id = tree_pedidos.item(sel[0])["values"][0]
        exportar_pedido_excel(pedido_id)

    btns = tk.Frame(win)
    btns.pack(pady=5)
    tk.Button(btns, text="Marcar como recibido", command=marcar_recibido, bg="#4CAF50", fg="white").pack(side="left", padx=5)
    tk.Button(btns, text="Exportar pedido a PDF", command=exportar_pdf).pack(side="left", padx=5)
    tk.Button(btns, text="Exportar pedido a Excel", command=exportar_excel).pack(side="left", padx=5)

# Para pruebas o llamada desde menú principal:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Proveedores - Licores Ríos")
    tk.Button(root, text="Módulo de proveedores", command=proveedores_window, width=40).pack(pady=30)
    root.mainloop()