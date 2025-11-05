import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import random

class Dashboard:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.stats_data = self.load_sample_stats()
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz del dashboard mejorado"""
        # Frame principal con scroll
        self.main_canvas = tk.Canvas(self.parent, bg=self.app.colors['white'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas, style="TFrame")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Título y bienvenida
        self.create_header()
        
        # Estadísticas principales
        self.create_main_stats()
        
        # Gráficos y visualizaciones
        self.create_charts_section()
        
        # Accesos rápidos avanzados
        self.create_advanced_quick_actions()
        
        # Progreso de tareas
        self.create_tasks_progress()
        
        # Actividad reciente mejorada
        self.create_enhanced_recent_activity()
        
        # Estado del sistema
        self.create_system_status()
        
    def create_header(self):
        """Crear header con bienvenida y resumen"""
        header_frame = ttk.Frame(self.scrollable_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Información de bienvenida
        welcome_frame = ttk.Frame(header_frame, style="TFrame")
        welcome_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        welcome_label = ttk.Label(welcome_frame, 
                                text="¡Bienvenido de vuelta! 👋", 
                                style="Header.TLabel")
        welcome_label.pack(anchor="w")
        
        date_label = ttk.Label(welcome_frame, 
                             text=f"{datetime.now().strftime('%A, %d %B %Y')}",
                             style="Secondary.TLabel")
        date_label.pack(anchor="w")
        
        # Resumen rápido
        summary_frame = ttk.Frame(header_frame, style="TFrame")
        summary_frame.pack(side=tk.RIGHT)
        
        summary_text = f"📊 {self.stats_data['total_songs']} canciones • ⏳ {self.stats_data['pending_review']} por revisar"
        summary_label = ttk.Label(summary_frame, 
                                text=summary_text,
                                style="Secondary.TLabel")
        summary_label.pack()
        
    # ... (el resto del código del dashboard se mantiene similar, 
    # pero usando self.app.colors en lugar de colores hardcodeados)