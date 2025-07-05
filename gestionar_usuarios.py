import tkinter as tk
from tkinter import ttk, messagebox
import usuarios

def ventana_gestion_usuarios():
    def refrescar_usuarios():
        for row in tree.get_children():
            tree.delete(row)
        for user in usuarios.obtener_usuarios():
            tree.insert('', tk.END, values=user)

    def registrar():
        usuario = entry_usuario.get().strip()
        nombre = entry_nombre.get().strip()
        password = entry_password.get().strip()
        rol = combo_rol.get()
        if not usuario or not nombre or not password or not rol:
            messagebox.showwarning("Campos requeridos", "Completa todos los campos.")
            return
        if usuarios.registrar_usuario(usuario, nombre, password, rol):
            messagebox.showinfo("Éxito", "Usuario registrado.")
            refrescar_usuarios()
            entry_usuario.delete(0, tk.END)
            entry_nombre.delete(0, tk.END)
            entry_password.delete(0, tk.END)
            combo_rol.set("")
        else:
            messagebox.showerror("Error", "El usuario ya existe.")

    def eliminar():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selecciona", "Selecciona un usuario a eliminar.")
            return
        usuario_id = tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este usuario?"):
            usuarios.eliminar_usuario(usuario_id)
            refrescar_usuarios()

    window = tk.Toplevel()
    window.title("Gestión de Usuarios - LICORES RIOS")
    window.geometry("600x400")

    tk.Label(window, text="Usuario:").pack()
    entry_usuario = tk.Entry(window)
    entry_usuario.pack()
    tk.Label(window, text="Nombre:").pack()
    entry_nombre = tk.Entry(window)
    entry_nombre.pack()
    tk.Label(window, text="Contraseña:").pack()
    entry_password = tk.Entry(window, show='*')
    entry_password.pack()
    tk.Label(window, text="Rol:").pack()
    combo_rol = ttk.Combobox(window, values=["admin", "vendedor"])
    combo_rol.pack()
    tk.Button(window, text="Registrar Usuario", command=registrar, bg="#4caf50", fg="white").pack(pady=5)

    tree = ttk.Treeview(window, columns=("ID", "Usuario", "Nombre", "Rol"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Usuario", text="Usuario")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Rol", text="Rol")
    tree.pack(expand=True, fill="both", pady=10)

    tk.Button(window, text="Eliminar Usuario", command=eliminar, bg="#FF5252", fg="white").pack()
    refrescar_usuarios()