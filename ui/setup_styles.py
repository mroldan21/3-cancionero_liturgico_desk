import tkinter as tk
from tkinter import ttk

class StyleManager:
    def __init__(self):
        self.colors = self.define_colors()
        self.styles_configured = False
        
    def define_colors(self):
        """Definir paleta de colores corporativa"""
        return {
            'primary': "#2C3E50",      # Azul oscuro principal
            'secondary': "#3498DB",    # Azul corporativo
            'accent': "#E74C3C",       # Rojo/accent para acciones importantes
            'success': "#27AE60",      # Verde para éxito/completado
            'warning': "#F39C12",      # Naranja para advertencias
            'info': "#17A2B8",         # Azul claro para información
            'dark': "#34495E",         # Azul más oscuro
            'light': "#ECF0F1",        # Gris muy claro
            'gray': "#95A5A6",         # Gris medio
            'white': "#FFFFFF",        # Blanco
            'text_primary': "#2C3E50", # Color texto principal
            'text_secondary': "#5D6D7E", # Color texto secundario
            'text_light': "#7F8C8D",   # Color texto claro
            'border': "#BDC3C7"        # Color bordes
        }
    
    def setup_styles(self):
        """Configurar todos los estilos de la aplicación"""
        if self.styles_configured:
            return
            
        style = ttk.Style()
        style.theme_use('clam')  # Tema base más personalizable
        
        # ===== CONFIGURACIONES PRINCIPALES =====
        
        # Frame principal
        style.configure("TFrame", 
                       background=self.colors['white'])
        
        # LabelFrame
        style.configure("TLabelframe",
                       background=self.colors['white'],
                       bordercolor=self.colors['border'],
                       relief="solid",
                       borderwidth=1)
        
        style.configure("TLabelframe.Label",
                       font=('Arial', 10, 'bold'),
                       font=('Arial', 12, 'bold'), # Aumentado de 10 a 12
                       background=self.colors['white'])
        
        # ===== BOTONES =====
        
        # Botón primario
        style.configure("Primary.TButton",
                       background=self.colors['secondary'],
                       foreground=self.colors['white'],
                       borderwidth=0, # Reducido a 0 para un look más moderno
                       relief="raised",
                       focuscolor="none",
                       padding=(12, 6),
                       font=('Arial', 9, 'bold'))
        
        style.map("Primary.TButton",
                 background=[('active', self.colors['primary']),
                           ('pressed', self.colors['dark'])])
        
        # Botón éxito
        style.configure("Success.TButton",
                       background=self.colors['success'],
                       foreground=self.colors['white'],
                       padding=(15, 8), # Aumentado de (12, 6) a (15, 8)
                       font=('Arial', 9, 'bold'))
        
        style.map("Success.TButton",
                 background=[('active', '#219955'),
                           ('pressed', '#1e8449')])
        
        # Botón advertencia
        style.configure("Warning.TButton",
                       background=self.colors['warning'],
                       foreground=self.colors['white'],
                       padding=(15, 8), # Aumentado de (12, 6) a (15, 8)
                       font=('Arial', 9, 'bold'))
        
        style.map("Warning.TButton",
                 background=[('active', '#e67e22'),
                           ('pressed', '#d35400')])
        
        # Botón peligro
        style.configure("Danger.TButton",
                       background=self.colors['accent'],
                       foreground=self.colors['white'],
                       padding=(15, 8), # Aumentado de (12, 6) a (15, 8)
                       font=('Arial', 9, 'bold'))
        
        style.map("Danger.TButton",
                 background=[('active', '#c0392b'),
                           ('pressed', '#a93226')])
        
        # Botón info
        style.configure("Info.TButton",
                       background=self.colors['info'],
                       foreground=self.colors['white'],
                       padding=(15, 8), # Aumentado de (10, 5) a (15, 8)
                       font=('Arial', 11)) # Aumentado de 9 a 11
        
        # ===== LABELS =====
        
        # Label header principal
        style.configure("Header.TLabel",
                       font=('Arial', 20, 'bold'), # Aumentado de 16 a 20
                       foreground=self.colors['primary'],
                       background=self.colors['white'])
        
        # Label subheader
        style.configure("Subheader.TLabel",
                       font=('Arial', 14, 'bold'), # Aumentado de 12 a 14
                       foreground=self.colors['dark'],
                       background=self.colors['white'])
        
        # Label normal
        style.configure("Normal.TLabel",
                       font=('Arial', 12), # Aumentado de 10 a 12
                       foreground=self.colors['text_primary'],
                       background=self.colors['white'])
        
        # Label secundario
        style.configure("Secondary.TLabel",
                       font=('Arial', 11), # Aumentado de 9 a 11
                       foreground=self.colors['text_secondary'],
                       background=self.colors['white'])
        
        # Label pequeño
        style.configure("Small.TLabel",
                       font=('Arial', 10), # Aumentado de 8 a 10
                       foreground=self.colors['text_light'],
                       background=self.colors['white'])
        
        # ===== ENTRADAS DE TEXTO =====
        style.configure("TEntry",
                       font=('Arial', 11), # Añadido tamaño de fuente
                       fieldbackground=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief="solid",
                       padding=(8, 4)) # Aumentado de (5, 2) a (8, 4)
        
        style.configure("TEntry",
                       fieldbackground=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief="solid",
                       padding=(5, 2))
        
        style.map("TEntry",
                 fieldbackground=[('focus', self.colors['white']),
                                ('disabled', self.colors['light'])])
        
        # ===== COMBOBOX =====
        
        style.configure("TCombobox",
                       font=('Arial', 11), # Añadido tamaño de fuente
                       fieldbackground=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       background=self.colors['white'],
                       borderwidth=1,
                       padding=(8, 4), # Añadido padding
                       relief="solid")
        
        style.map("TCombobox",
                 fieldbackground=[('readonly', self.colors['white'])],
                 background=[('readonly', self.colors['white'])])
        
        # ===== TREEVIEW =====
        
        style.configure("Treeview",
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['white'],
                       borderwidth=1,
                       relief="flat", # Cambiado a flat para un look más limpio
                       rowheight=30) # Aumentado de 25 a 30
        
        style.configure("Treeview.Heading",
                       background=self.colors['light'],
                       foreground=self.colors['primary'],
                       relief="flat",
                       borderwidth=0, # Reducido a 0
                       font=('Arial', 9, 'bold'))
        
        style.map("Treeview.Heading",
                 background=[('active', self.colors['secondary']),
                           ('pressed', self.colors['primary'])])
        
        style.map("Treeview",
                 background=[('selected', self.colors['secondary'])],
                 foreground=[('selected', self.colors['white'])])
        
        # ===== SCROLLBARS =====
        
        style.configure("Vertical.TScrollbar",
                       background=self.colors['light'],
                       troughcolor=self.colors['white'],
                       borderwidth=1,
                       relief="solid",
                       arrowsize=12)
        
        style.configure("Horizontal.TScrollbar",
                       background=self.colors['light'],
                       troughcolor=self.colors['white'],
                       borderwidth=1,
                       relief="solid",
                       arrowsize=12)
        
        # ===== NOTEBOOK (Pestañas) =====
        
        style.configure("TNotebook",
                       background=self.colors['white'],
                       tabmargins=[2, 5, 2, 0])
        
        style.configure("TNotebook.Tab",
                       background=self.colors['light'],
                       foreground=self.colors['primary'], # Cambiado a primary para mejor contraste
                       padding=(18, 8), # Aumentado de (15, 5) a (18, 8)
                       font=('Arial', 9))
        
        style.map("TNotebook.Tab",
                 background=[('selected', self.colors['secondary']),
                           ('active', self.colors['info'])],
                 foreground=[('selected', self.colors['white']),
                           ('active', self.colors['white'])])
        
        # ===== PROGRESSBAR =====
        
        style.configure("Horizontal.TProgressbar",
                       background=self.colors['secondary'],
                       troughcolor=self.colors['light'],
                       borderwidth=0,
                       lightcolor=self.colors['secondary'],
                       darkcolor=self.colors['secondary'])
        
        style.configure("Success.Horizontal.TProgressbar",
                       background=self.colors['success'])
        
        style.configure("Warning.Horizontal.TProgressbar",
                       background=self.colors['warning'])
        
        style.configure("Danger.Horizontal.TProgressbar",
                       background=self.colors['accent'])
        
        # ===== SEPARADORES =====
        
        style.configure("Horizontal.TSeparator",
                       background=self.colors['border'])
        
        style.configure("Vertical.TSeparator",
                       background=self.colors['border'])
        
        # ===== CHECKBUTTON & RADIOBUTTON =====
        
        style.configure("TCheckbutton",
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'], # Aumentado de 9 a 11
                       font=('Arial', 11),
                       indicatorcolor=self.colors['white'])
        
        style.configure("TRadiobutton",
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'], # Aumentado de 9 a 11
                       font=('Arial', 11),
                       indicatorcolor=self.colors['white'])
        
        self.styles_configured = True
        
    def create_stat_card_style(self, color_name):
        """Crear estilo para tarjetas de estadísticas"""
        color = self.colors.get(color_name, self.colors['secondary'])
        
        # Crear estilo dinámico para tarjetas
        style_name = f"StatCard.{color_name}.TFrame"
        
        ttk.Style().configure(style_name,
                            background=self.colors['white'],
                            relief="solid",
                            borderwidth=1,
                            bordercolor=self.colors['border'])
        
        return style_name
    
    def get_color(self, color_name):
        """Obtener color por nombre"""
        return self.colors.get(color_name, self.colors['primary'])
    
    def create_gradient_button(self, parent, text, command, color_scheme="primary"):
        """Crear botón con gradiente personalizado (usando Canvas)"""
        colors_map = {
            'primary': (self.colors['secondary'], self.colors['primary']),
            'success': (self.colors['success'], '#219955'),
            'warning': (self.colors['warning'], '#e67e22'),
            'danger': (self.colors['accent'], '#c0392b'),
            'info': (self.colors['info'], '#148ea1')
        }
        
        color1, color2 = colors_map.get(color_scheme, colors_map['primary'])
        
        # Crear canvas para el botón con gradiente
        btn_canvas = tk.Canvas(parent, width=120, height=40, highlightthickness=0)
        btn_canvas.configure(bg=self.colors['white'])
        
        # Dibujar gradiente simple (ajustar tamaño del botón y texto)
        btn_canvas.create_rectangle(0, 0, 150, 50, fill=color1, outline=color1) # Aumentado tamaño del botón
        btn_canvas.create_text(75, 25, text=text, fill=self.colors['white'], # Centrado el texto
                              font=('Arial', 12, 'bold')) # Aumentado de 9 a 12
        
        # Bind events para efecto hover
        def on_enter(e):
            btn_canvas.configure(cursor="hand2")
            btn_canvas.delete("all")
            btn_canvas.create_rectangle(0, 0, 150, 50, fill=color2, outline=color2)
            btn_canvas.create_text(75, 25, text=text, fill=self.colors['white'], 
                                  font=('Arial', 12, 'bold'))
        
        def on_leave(e):
            btn_canvas.delete("all")
            btn_canvas.create_rectangle(0, 0, 120, 40, fill=color1, outline=color1)
            btn_canvas.create_text(60, 20, text=text, fill=self.colors['white'], 
                                  font=('Arial', 9, 'bold'))
        
        def on_click(e):
            command() # Mantener el comando original
        
        btn_canvas.bind("<Enter>", on_enter)
        btn_canvas.bind("<Leave>", on_leave)
        btn_canvas.bind("<Button-1>", on_click)
        
        return btn_canvas

# Instancia global del gestor de estilos
style_manager = StyleManager()