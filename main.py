import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import matplotlib
matplotlib.use('TkAgg')  # Usar backend compatible con Tkinter

# Agregar paths para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from ui.dashboard import Dashboard
from ui.import_module import ImportModule
from ui.editor import Editor
from ui.content_manager import ContentManager
from ui.admin import AdminPanel
from setup_styles import style_manager  # Importar el gestor de estilos

class LiturgyConverterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Liturgy Converter Pro - v1.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configurar estilos globales primero (desde setup_styles)
        style_manager.setup_styles()
        # Hacer disponibles los colores en la app
        self.colors = style_manager.colors
        self.primary_color = self.colors['primary']
        self.secondary_color = self.colors['secondary']
        self.accent_color = self.colors['accent']
        self.success_color = self.colors['success']
        self.warning_color = self.colors['warning']
        self.info_color = self.colors.get('info', "#2980B9")
        
        # Estado de la aplicación
        self.current_module = None
        self.db_connected = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz principal"""
        # Configurar el color de fondo de la ventana principal
        self.root.configure(bg=self.colors.get('white', '#FFFFFF'))
        
        # Frame principal (usar estilo TFrame)
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header()
        
        # Contenido principal
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Crear header de la aplicación"""
        header_frame = ttk.Frame(self.main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo y título
        title_frame = ttk.Frame(header_frame, style="TFrame")
        title_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, 
                               text="🎵 Liturgy Converter Pro", 
                               style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Barra de navegación
        nav_frame = ttk.Frame(header_frame, style="TFrame")
        nav_frame.pack(side=tk.RIGHT)
        
        # Botones de navegación
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard, "primary"),
            ("📥 Importar", self.show_import, "primary"),
            ("✏️ Editor", self.show_editor, "primary"),
            ("📊 Gestor", self.show_content_manager, "primary"),
            ("⚙️ Admin", self.show_admin, "primary")
        ]
        
        for text, command, style_type in nav_buttons:
            btn = ttk.Button(nav_frame, 
                           text=text, 
                           command=command,
                           style=f"{style_type.title()}.TButton")
            btn.pack(side=tk.LEFT, padx=2)
            
    def create_main_content(self):
        """Crear área de contenido principal"""
        self.content_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar dashboard por defecto
        self.show_dashboard()
        
    def create_status_bar(self):
        """Crear barra de estado"""
        status_frame = ttk.Frame(self.main_frame, style="TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Estado BD
        self.db_status = ttk.Label(status_frame, 
                                  text="🔴 BD No conectada", 
                                  style="Secondary.TLabel")
        self.db_status.pack(side=tk.LEFT)
        
        # Contador de canciones
        self.song_count = ttk.Label(status_frame, 
                                   text="Canciones: 0",
                                   style="Secondary.TLabel")
        self.song_count.pack(side=tk.LEFT, padx=20)
        
        # Versión
        version_label = ttk.Label(status_frame, 
                                 text="v1.0.0",
                                 style="Secondary.TLabel")
        version_label.pack(side=tk.RIGHT)
        
    def show_dashboard(self):
        """Mostrar dashboard principal"""
        self.clear_content()
        self.current_module = Dashboard(self.content_frame, self)
        self.update_status()
        
    def show_import(self):
        """Mostrar módulo de importación"""
        self.clear_content()
        self.current_module = ImportModule(self.content_frame, self)
        
    def show_editor(self):
        """Mostrar editor avanzado"""
        self.clear_content()
        self.current_module = Editor(self.content_frame, self)
        
    def show_content_manager(self):
        """Mostrar gestor de contenido"""
        self.clear_content()
        self.current_module = ContentManager(self.content_frame, self)
        
    def show_admin(self):
        """Mostrar panel de administración"""
        self.clear_content()
        self.current_module = AdminPanel(self.content_frame, self)
        
    def clear_content(self):
        """Limpiar contenido actual"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def update_status(self):
        """Actualizar barra de estado"""
        status_text = "🟢 BD Conectada" if self.db_connected else "🔴 BD No conectada"
        # Actualizar texto (el estilo maneja colores de etiqueta)
        # self.db_status.config(text=status_text)
        
    def set_db_status(self, connected):
        """Establecer estado de conexión BD"""
        self.db_connected = connected
        # self.update_status()
        
    def run(self):
        """Ejecutar aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = LiturgyConverterApp()
    app.run()