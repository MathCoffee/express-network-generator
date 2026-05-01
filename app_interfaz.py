import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import datetime
import os
from GraphsGenerator import generate_network_graph

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Redes ICMI")
        self.root.geometry("450x300")
        self.root.configure(padx=20, pady=20)
        
        self.file_path = None
        self.sheet_names = []
        
        # UI Elements
        tk.Label(root, text="1. Cargar Archivo de Datos (.xlsx)", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.btn_load = tk.Button(root, text="Seleccionar Archivo Excel", command=self.load_file, width=25)
        self.btn_load.pack(pady=5)
        
        self.lbl_file = tk.Label(root, text="Ningún archivo seleccionado", fg="gray")
        self.lbl_file.pack()
        
        tk.Label(root, text="2. Seleccionar Pestaña", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))
        
        self.sheet_var = tk.StringVar()
        self.cb_sheets = ttk.Combobox(root, textvariable=self.sheet_var, state="readonly", width=25)
        self.cb_sheets.pack(pady=5)
        
        tk.Label(root, text="3. Generar Gráfica", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))
        
        self.btn_generate = tk.Button(root, text="Generar y Guardar Gráfica", command=self.generate_graph, state=tk.DISABLED, width=25, bg="lightblue")
        self.btn_generate.pack(pady=5)
        
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx *.xls")])
        if file_path:
            self.file_path = file_path
            self.lbl_file.config(text=os.path.basename(file_path), fg="black")
            try:
                # Leer las pestañas del archivo
                xl = pd.ExcelFile(file_path)
                self.sheet_names = xl.sheet_names
                self.cb_sheets['values'] = self.sheet_names
                
                # Seleccionar la primera por defecto o 'Datos' si existe
                if 'Datos' in self.sheet_names:
                    self.cb_sheets.set('Datos')
                elif self.sheet_names:
                    self.cb_sheets.current(0)
                    
                self.btn_generate.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
                
    def generate_graph(self):
        if not self.file_path or not self.sheet_var.get():
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo y una pestaña.")
            return
            
        # Generar nombre de salida único con marca de tiempo
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"Graph_ICMI_{timestamp}.png"
        output_path = os.path.join(os.path.dirname(self.file_path), output_name)
        
        try:
            self.btn_generate.config(text="Generando...", state=tk.DISABLED)
            self.root.update()
            
            # Llamar a la función del script original
            generate_network_graph(self.file_path, output_path, sheet_name=self.sheet_var.get())
            
            self.btn_generate.config(text="Generar y Guardar Gráfica", state=tk.NORMAL)
            messagebox.showinfo("Éxito", f"Gráfica generada exitosamente como:\n\n{output_name}")
            
        except Exception as e:
            self.btn_generate.config(text="Generar y Guardar Gráfica", state=tk.NORMAL)
            messagebox.showerror("Error", f"Ocurrió un error al generar la gráfica:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
