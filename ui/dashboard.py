import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import random
from core.database import DatabaseManager

class Dashboard:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        # Usar la misma instancia de BD que la app principal
        self.db = app.database
        self.stats_data = self.load_real_stats()
        self.setup_ui()

        # self.db = DatabaseManager("https://cincomasuno.ar/api_cancionero_desk")
        # self.stats_data = self.load_real_stats()
        # self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz del dashboard mejorado"""
        # Frame principal con scroll - usar color de fondo desde app.colors
        self.main_canvas = tk.Canvas(self.parent, bg=self.app.colors.get('white', '#FFFFFF'), highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.main_canvas.yview)
        # scrollable_frame usa estilo TFrame (definido por setup_styles)
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
        
    def create_main_stats(self):
        """Crear sección de estadísticas principales con tarjetas"""
        stats_frame = ttk.Frame(self.scrollable_frame, style="TFrame")
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Usar colores de la app cuando estén disponibles
        color_map = {
            "blue": self.app.colors.get('secondary', '#3498DB'),
            "orange": self.app.colors.get('warning', '#F39C12'),
            "green": self.app.colors.get('success', '#27AE60'),
            "purple": self.app.colors.get('accent', '#9B59B6')
        }
        
        stats_cards = [
            {
                "title": "Total Canciones",
                "value": self.stats_data['total_songs'],
                "icon": "📝",
                "trend": "+12%",
                "color": color_map["blue"]
            },
            {
                "title": "Por Revisar",
                "value": self.stats_data['pending_review'],
                "icon": "⏳",
                "trend": "-5%",
                "color": color_map["orange"]
            },
            {
                "title": "Esta Semana",
                "value": self.stats_data['this_week'],
                "icon": "📈",
                "trend": "+8%",
                "color": color_map["green"]
            },
            {
                "title": "Categorías",
                "value": self.stats_data['categories'],
                "icon": "📂",
                "trend": "0%",
                "color": color_map["purple"]
            }
        ]
        
        for i, card in enumerate(stats_cards):
            card_frame = self.create_stat_card(stats_frame, card)
            card_frame.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)
            
    def create_stat_card(self, parent, card_data):
        """Crear tarjeta de estadística individual"""
        card = ttk.Frame(parent, relief="solid", borderwidth=1, style="TFrame")
        
        # Icono y título
        icon_frame = ttk.Frame(card, style="TFrame")
        icon_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        icon_label = ttk.Label(icon_frame, 
                             text=card_data["icon"], 
                             font=('Arial', 14))
        icon_label.pack(side=tk.LEFT)
        
        title_label = ttk.Label(icon_frame, 
                              text=card_data["title"],
                              font=('Arial', 10, 'bold'),
                              style="Secondary.TLabel")
        title_label.pack(side=tk.RIGHT)
        
        # Valor principal (usar tk.Label para poder colorear fácilmente)
        value_label = tk.Label(card, 
                              text=str(card_data["value"]),
                              font=('Arial', 24, 'bold'),
                              fg=card_data["color"],
                              bg=self.app.colors.get('white', '#FFFFFF'))
        value_label.pack(pady=(5, 0))
        
        # Tendencia
        trend_frame = ttk.Frame(card, style="TFrame")
        trend_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        trend_color = "green" if "+" in card_data["trend"] else "red" if "-" in card_data["trend"] else "gray"
        trend_label = ttk.Label(trend_frame, 
                              text=card_data["trend"],
                              font=('Arial', 9),
                              foreground=trend_color)
        trend_label.pack(side=tk.RIGHT)
        
        return card
        
    def create_charts_section(self):
        """Crear sección con gráficos y visualizaciones"""
        charts_frame = ttk.LabelFrame(self.scrollable_frame,
                                    text="📈 Análisis y Métricas",
                                    padding=15)
        charts_frame.pack(fill=tk.X, pady=10)
        
        # Dos columnas para gráficos
        left_chart_frame = ttk.Frame(charts_frame)
        left_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_chart_frame = ttk.Frame(charts_frame)
        right_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Gráfico de canciones por categoría
        self.create_category_chart(left_chart_frame)
        
        # Gráfico de actividad semanal
        self.create_activity_chart(right_chart_frame)
        
    def create_category_chart(self, parent):
        """Crear gráfico de canciones por categoría"""
        chart_frame = ttk.LabelFrame(parent, text="🎵 Canciones por Categoría", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Datos de ejemplo
        categories = ['Alabanza', 'Adoración', 'Cuaresma', 'Navidad', 'Comunión', 'Otros']
        song_counts = [45, 38, 22, 18, 15, 12]
        
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(categories, song_counts, color=['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6', '#95A5A6'])
        
        # Personalizar gráfico
        ax.set_ylabel('Número de Canciones')
        ax.set_title('Distribución por Categoría')
        plt.xticks(rotation=45, ha='right')
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        fig.tight_layout()
        
        # Integrar en Tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_activity_chart(self, parent):
        """Crear gráfico de actividad semanal"""
        chart_frame = ttk.LabelFrame(parent, text="📊 Actividad Semanal", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Datos de ejemplo para última semana
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        imports = [5, 3, 8, 6, 12, 2, 1]
        edits = [8, 6, 10, 7, 15, 4, 2]
        
        fig, ax = plt.subplots(figsize=(6, 4))
        
        width = 0.35
        x = range(len(days))
        
        ax.bar([i - width/2 for i in x], imports, width, label='Importaciones', color='#3498DB')
        ax.bar([i + width/2 for i in x], edits, width, label='Ediciones', color='#2ECC71')
        
        ax.set_xlabel('Días')
        ax.set_ylabel('Actividades')
        ax.set_title('Actividad Diaria')
        ax.set_xticks(x)
        ax.set_xticklabels(days)
        ax.legend()
        
        fig.tight_layout()
        
        # Integrar en Tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_advanced_quick_actions(self):
        """Crear sección de acciones rápidas avanzadas"""
        actions_frame = ttk.LabelFrame(self.scrollable_frame,
                                     text="🚀 Acciones Rápidas Avanzadas",
                                     padding=15,
                                     style="TFrame")
        actions_frame.pack(fill=tk.X, pady=10)
        
        # Primera fila de acciones principales
        main_actions_frame = ttk.Frame(actions_frame, style="TFrame")
        main_actions_frame.pack(fill=tk.X, pady=5)
        
        # Usar colores de app cuando sea posible
        main_actions = [
            ("📥 Importar Masivo", self.app.show_import, "Importar múltiples archivos", self.app.colors.get('secondary', '#3498DB')),
            ("✏️ Editor Avanzado", self.app.show_editor, "Editor completo de canciones", self.app.colors.get('success', '#27AE60')),
            ("📊 Gestor Contenido", self.app.show_content_manager, "Gestionar todo el contenido", self.app.colors.get('accent', '#9B59B6')),
            ("🔄 Sincronizar BD", self.sync_data, "Sincronizar con base de datos", self.app.colors.get('warning', '#F39C12'))
        ]
        
        for i, (text, command, tooltip, color) in enumerate(main_actions):
            btn_frame = ttk.Frame(main_actions_frame, style="TFrame")
            btn_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            main_actions_frame.columnconfigure(i, weight=1)
            
            btn = tk.Button(btn_frame, 
                          text=text,
                          command=command,
                          bg=color,
                          fg="white",
                          font=('Arial', 10, 'bold'),
                          relief="raised",
                          bd=2,
                          padx=10,
                          pady=8)
            btn.pack(fill=tk.BOTH, expand=True)
            self.create_tooltip(btn, tooltip)
            
        # Segunda fila de acciones secundarias
        secondary_actions_frame = ttk.Frame(actions_frame, style="TFrame")
        secondary_actions_frame.pack(fill=tk.X, pady=5)
        
        secondary_actions = [
            ("📤 Exportar JSON", self.export_json, "Exportar para app móvil", "#E74C3C"),
            ("🎵 Transponer Lote", self.batch_transpose, "Transposición masiva", "#1ABC9C"),
            ("🔍 Buscar/Reemplazar", self.batch_find_replace, "Buscar y reemplazar masivo", "#34495E"),
            ("📋 Reportes", self.generate_reports, "Generar reportes detallados", "#D35400")
        ]
        
        for i, (text, command, tooltip, color) in enumerate(secondary_actions):
            btn_frame = ttk.Frame(secondary_actions_frame, style="TFrame")
            btn_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            secondary_actions_frame.columnconfigure(i, weight=1)
            
            btn = tk.Button(btn_frame, 
                          text=text,
                          command=command,
                          bg=color,
                          fg="white",
                          font=('Arial', 9),
                          relief="raised",
                          bd=1,
                          padx=8,
                          pady=6)
            btn.pack(fill=tk.BOTH, expand=True)
            self.create_tooltip(btn, tooltip)
        
    def create_tasks_progress(self):
        """Crear sección de progreso de tareas"""
        progress_frame = ttk.LabelFrame(self.scrollable_frame,
                                      text="📋 Progreso de Tareas",
                                      padding=15)
        progress_frame.pack(fill=tk.X, pady=10)
        
        tasks = [
            {"name": "Procesamiento OCR imágenes", "progress": 75, "status": "En progreso"},
            {"name": "Sincronización con BD remota", "progress": 100, "status": "Completado"},
            {"name": "Exportación JSON app móvil", "progress": 30, "status": "En progreso"},
            {"name": "Validación canciones nuevas", "progress": 45, "status": "En progreso"}
        ]
        
        for task in tasks:
            task_frame = ttk.Frame(progress_frame)
            task_frame.pack(fill=tk.X, pady=5)
            
            # Nombre y estado
            info_frame = ttk.Frame(task_frame)
            info_frame.pack(fill=tk.X)
            
            ttk.Label(info_frame, text=task["name"], font=('Arial', 9)).pack(side=tk.LEFT)
            ttk.Label(info_frame, text=task["status"], font=('Arial', 8), foreground="gray").pack(side=tk.RIGHT)
            
            # Barra de progreso
            progress = ttk.Progressbar(task_frame, 
                                     orient="horizontal", 
                                     length=100, 
                                     mode="determinate",
                                     value=task["progress"])
            progress.pack(fill=tk.X, pady=2)
            
            # Porcentaje
            percent_frame = ttk.Frame(task_frame)
            percent_frame.pack(fill=tk.X)
            
            ttk.Label(percent_frame, text=f"{task['progress']}%", font=('Arial', 8)).pack(side=tk.RIGHT)
            
    def create_enhanced_recent_activity(self):
        """Crear sección de actividad reciente mejorada"""
        activity_frame = ttk.LabelFrame(self.scrollable_frame,
                                      text="📋 Actividad Reciente Detallada",
                                      padding=15)
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Filtros de actividad
        filter_frame = ttk.Frame(activity_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filtrar por:").pack(side=tk.LEFT, padx=5)
        
        self.activity_filter = tk.StringVar(value="todos")
        filters = [
            ("Todos", "todos"),
            ("Importaciones", "import"),
            ("Ediciones", "edit"),
            ("Aprobaciones", "approve"),
            ("Exportaciones", "export")
        ]
        
        for text, value in filters:
            ttk.Radiobutton(filter_frame, 
                          text=text, 
                          variable=self.activity_filter,
                          value=value,
                          command=self.filter_activity).pack(side=tk.LEFT, padx=5)
        
        # Treeview para actividad con más detalles
        columns = ('fecha', 'tipo', 'accion', 'detalle', 'usuario', 'estado')
        self.activity_tree = ttk.Treeview(activity_frame, 
                                        columns=columns, 
                                        show='headings',
                                        height=10)
        
        # Configurar columnas
        column_config = {
            'fecha': ('Fecha/Hora', 150),
            'tipo': ('Tipo', 80),
            'accion': ('Acción', 100),
            'detalle': ('Detalle', 250),
            'usuario': ('Usuario', 100),
            'estado': ('Estado', 80)
        }
        
        for col, (text, width) in column_config.items():
            self.activity_tree.heading(col, text=text)
            self.activity_tree.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(activity_frame, 
                                orient=tk.VERTICAL, 
                                command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        self.activity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de acción para actividad
        action_frame = ttk.Frame(activity_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, 
                  text="🔄 Actualizar",
                  command=self.refresh_activity).pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(action_frame,
                  text="📋 Exportar Actividad",
                  command=self.export_activity).pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(action_frame,
                  text="🗑️ Limpiar Registros",
                  command=self.clear_activity).pack(side=tk.RIGHT, padx=2)
        
        # Cargar datos de ejemplo
        self.load_enhanced_activity()
        
    def create_system_status(self):
        """Crear sección de estado del sistema"""
        status_frame = ttk.LabelFrame(self.scrollable_frame,
                                    text="⚙️ Estado del Sistema",
                                    padding=15)
        status_frame.pack(fill=tk.X, pady=10)
        
        # Grid para estados
        status_items = [
            ("Base de Datos", "🟢 Conectada", "green"),
            ("Servidor API", "🟢 En línea", "green"),
            ("Espacio Disco", "🟡 75% Usado", "orange"),
            ("Memoria RAM", "🟢 45% Usada", "green"),
            ("Procesamiento OCR", "🟢 Disponible", "green"),
            ("Conexión Internet", "🟢 Activa", "green")
        ]
        
        for i, (component, status, color) in enumerate(status_items):
            row = i // 3
            col = i % 3
            
            if col == 0:
                frame = ttk.Frame(status_frame)
                frame.pack(fill=tk.X, pady=5)
                
            item_frame = ttk.Frame(frame)
            item_frame.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
            
            ttk.Label(item_frame, text=component, font=('Arial', 9)).pack(anchor="w")
            ttk.Label(item_frame, text=status, font=('Arial', 9), foreground=color).pack(anchor="w")
            
    # def load_real_stats(self):
    #     """Cargar estadísticas reales desde la API"""
    #     try:
    #         # Obtener estadísticas desde la API
    #         stats_api = self.db.get_estadisticas()
            
    #         if stats_api:
    #             return {
    #                 'total_songs': stats_api.get('total_canciones', 0),
    #                 'pending_review': stats_api.get('pendientes_revision', 0),
    #                 'this_week': stats_api.get('canciones_semana', 0),
    #                 'categories': stats_api.get('total_categorias', 0),
    #                 'total_imports': stats_api.get('total_importaciones', 0),
    #                 'total_exports': stats_api.get('total_exportaciones', 0)
    #             }
    #         else:
    #             # Si falla la API, usar datos por defecto
    #             return self.load_fallback_stats()
                
    #     except Exception as e:
    #         print(f"Error cargando estadísticas: {e}")
    #         return self.load_fallback_stats()

    def load_real_stats(self):
        """Cargar estadísticas reales desde la BD"""
        try:
            # Obtener canciones reales
            canciones = self.db.get_canciones()
            
            # Obtener categorías
            categorias = self.db.get_categorias()
            
            # Calcular estadísticas básicas
            return {
                'total_songs': len(canciones),
                'pending_review': len([c for c in canciones if c.get('estado') == 'pendiente']),
                'this_week': self.get_songs_this_week(canciones),
                'categories': len(categorias),
                'total_imports': 0,  # Podrías agregar este campo en tu BD
                'total_exports': 0   # Podrías agregar este campo en tu BD
            }
        except Exception as e:
            print(f"Error cargando estadísticas reales: {e}")
            # Fallback a datos de ejemplo
            return self.load_sample_stats()
    
    def get_songs_this_week(self, canciones):
        """Obtener canciones creadas esta semana"""
        try:
            from datetime import datetime, timedelta
            week_ago = datetime.now() - timedelta(days=7)
            count = 0
            for cancion in canciones:
                if cancion.get('fecha_creacion'):
                    # Convertir string de fecha a datetime si es necesario
                    fecha_str = cancion['fecha_creacion']
                    # Manejar diferentes formatos de fecha
                    if 'T' in fecha_str:
                        fecha_creacion = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                    else:
                        fecha_creacion = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
                    
                    if fecha_creacion >= week_ago:
                        count += 1
            return count
        except:
            return 0
        
    def load_fallback_stats(self):
        """Estadísticas por defecto si falla la API"""
        return {
            'total_songs': 0,
            'pending_review': 0,
            'this_week': 0,
            'categories': 0,
            'total_imports': 0,
            'total_exports': 0
        }
        
    def refresh_stats(self):
        """Actualizar estadísticas desde la API"""
        self.stats_data = self.load_real_stats()
        # Recargar la UI completa
        for widget in self.parent.winfo_children():
            widget.destroy()
        self.setup_ui()

    def load_enhanced_activity(self):
        """Cargar actividad de ejemplo mejorada"""
        activity_types = {
            'import': ('📥', 'Importar', 'blue'),
            'edit': ('✏️', 'Editar', 'green'),
            'approve': ('✅', 'Aprobar', 'purple'),
            'export': ('📤', 'Exportar', 'orange'),
            'system': ('⚙️', 'Sistema', 'gray')
        }
        
        sample_activities = [
            ('2024-01-15 10:30:15', 'import', '15 canciones desde Word', 'admin', 'completado'),
            ('2024-01-15 09:15:42', 'edit', 'Corregir acordes - Aleluya', 'editor', 'completado'),
            ('2024-01-14 16:45:33', 'approve', '5 canciones nuevas', 'admin', 'completado'),
            ('2024-01-14 14:20:18', 'export', 'JSON para app móvil', 'system', 'completado'),
            ('2024-01-14 11:05:27', 'import', '10 imágenes OCR', 'editor', 'en progreso'),
            ('2024-01-13 17:30:55', 'edit', 'Transposición masiva - Cuaresma', 'admin', 'completado'),
            ('2024-01-13 15:20:41', 'export', 'PDF para impresión', 'editor', 'completado'),
            ('2024-01-12 12:15:08', 'system', 'Backup automático', 'system', 'completado')
        ]
        
        for fecha, tipo, detalle, usuario, estado in sample_activities:
            icon, accion, color = activity_types.get(tipo, ('', tipo, 'gray'))
            estado_color = "green" if estado == "completado" else "orange" if estado == "en progreso" else "red"
            
            # Insertar 6 valores para las columnas: fecha, tipo (icon+accion), acción, detalle, usuario, estado
            self.activity_tree.insert('', tk.END, values=(
                fecha, f"{icon} {accion}", accion, detalle, usuario, estado
            ), tags=(estado,))
            
        # Configurar colores para estados
        self.activity_tree.tag_configure('completado', foreground='green')
        self.activity_tree.tag_configure('en progreso', foreground='orange')
        self.activity_tree.tag_configure('error', foreground='red')
        
    def filter_activity(self):
        """Filtrar actividad según selección"""
        filter_type = self.activity_filter.get()
        
        for item in self.activity_tree.get_children():
            values = self.activity_tree.item(item)['values']
            activity_action = values[1].lower() if values else ""
            
            if filter_type == "todos":
                self.activity_tree.item(item, tags=())
            elif filter_type in activity_action:
                self.activity_tree.item(item, tags=())
            else:
                self.activity_tree.item(item, tags=('hidden',))
                
        # Ocultar elementos con tag 'hidden'
        self.activity_tree.tag_configure('hidden', foreground='')
        
    def refresh_activity(self):
        """Actualizar actividad"""
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        self.load_enhanced_activity()
        
    def export_activity(self):
        """Exportar actividad a archivo"""
        # Placeholder - implementar exportación
        print("Exportando actividad...")
        
    def clear_activity(self):
        """Limpiar registros de actividad"""
        if tk.messagebox.askyesno("Confirmar", "¿Estás seguro de limpiar todos los registros de actividad?"):
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
                
    def create_tooltip(self, widget, text):
        """Crear tooltip mejorado"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # usar tk.Label para aplicar background fácilmente
            label = tk.Label(tooltip, text=text, bg="lightyellow", 
                            relief="solid", borderwidth=1, padx=5, pady=3)
            label.pack()
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                try:
                    widget.tooltip.destroy()
                except Exception:
                    pass
                
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    # Métodos de acciones (placeholders)
    def sync_data(self):
        """Sincronizar datos con BD"""
        print("Sincronizando datos...")
        
    def export_json(self):
        """Exportar a JSON"""
        print("Exportando JSON...")
        
    def batch_transpose(self):
        """Transposición masiva"""
        print("Iniciando transposición masiva...")
        
    def batch_find_replace(self):
        """Buscar y reemplazar masivo"""
        print("Buscar y reemplazar...")
        
    def generate_reports(self):
        """Generar reportes"""
        print("Generando reportes...")