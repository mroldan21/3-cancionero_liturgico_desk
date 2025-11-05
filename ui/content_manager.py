import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

class ContentManager:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.songs_data = []
        self.filtered_data = []
        self.current_filters = {}
        self.setup_ui()
        self.load_sample_data()
        
    def setup_ui(self):
        """Configurar interfaz del gestor de contenido"""
        self.main_frame = ttk.Frame(self.parent, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título y controles superiores
        self.create_header()
        
        # Panel de filtros y búsqueda
        self.create_filters_panel()
        
        # Panel principal con lista y preview
        self.create_main_content()
        
        # Barra de herramientas inferior
        self.create_toolbar()
        
    def create_header(self):
        """Crear header con título y controles"""
        header_frame = ttk.Frame(self.main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title_label = ttk.Label(header_frame, 
                               text="📊 Gestor de Contenido", 
                               style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Controles de acción rápida
        control_frame = ttk.Frame(header_frame, style="TFrame")
        control_frame.pack(side=tk.RIGHT)
        
        # Búsqueda rápida
        search_frame = ttk.Frame(control_frame, style="TFrame")
        search_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(search_frame, text="🔍", style="Normal.TLabel").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, 
                                     textvariable=self.search_var, 
                                     width=25)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Botones de acción
        action_buttons = [
            ("🔄 Actualizar", self.refresh_data, "Primary.TButton"),
            ("📤 Exportar", self.export_data, "Success.TButton"),
            ("📊 Estadísticas", self.show_stats, "Info.TButton")
        ]
        
        for text, command, style in action_buttons:
            ttk.Button(control_frame,
                      text=text,
                      command=command,
                      style=style).pack(side=tk.LEFT, padx=2)
        
    def create_filters_panel(self):
        """Crear panel de filtros avanzados"""
        filters_frame = ttk.LabelFrame(self.main_frame,
                                     text="🎛️ Filtros y Búsqueda Avanzada",
                                     padding=15)
        filters_frame.pack(fill=tk.X, pady=10)
        
        # Primera fila de filtros
        filter_row1 = ttk.Frame(filters_frame, style="TFrame")
        filter_row1.pack(fill=tk.X, pady=5)
        
        # Filtro por categoría
        ttk.Label(filter_row1, text="Categoría:", style="Normal.TLabel").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar(value="Todas")
        categories = ["Todas", "Alabanza", "Adoración", "Cuaresma", "Navidad", "Comunión", "General"]
        self.category_combo = ttk.Combobox(filter_row1, 
                                         textvariable=self.category_var,
                                         values=categories,
                                         state="readonly",
                                         width=12)
        self.category_combo.pack(side=tk.LEFT, padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Filtro por estado
        ttk.Label(filter_row1, text="Estado:", style="Normal.TLabel").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="Todos")
        statuses = ["Todos", "Aprobado", "Pendiente", "En revisión", "Borrador"]
        self.status_combo = ttk.Combobox(filter_row1,
                                       textvariable=self.status_var,
                                       values=statuses,
                                       state="readonly",
                                       width=12)
        self.status_combo.pack(side=tk.LEFT, padx=5)
        self.status_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Filtro por tono
        ttk.Label(filter_row1, text="Tono:", style="Normal.TLabel").pack(side=tk.LEFT, padx=5)
        self.key_var = tk.StringVar(value="Todos")
        keys = ["Todos", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.key_combo = ttk.Combobox(filter_row1,
                                    textvariable=self.key_var,
                                    values=keys,
                                    state="readonly",
                                    width=8)
        self.key_combo.pack(side=tk.LEFT, padx=5)
        self.key_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Segunda fila de filtros
        filter_row2 = ttk.Frame(filters_frame, style="TFrame")
        filter_row2.pack(fill=tk.X, pady=5)
        
        # Filtro por fecha
        ttk.Label(filter_row2, text="Fecha:", style="Normal.TLabel").pack(side=tk.LEFT, padx=5)
        self.date_var = tk.StringVar(value="Todas")
        dates = ["Todas", "Hoy", "Esta semana", "Este mes", "Últimos 3 meses"]
        self.date_combo = ttk.Combobox(filter_row2,
                                     textvariable=self.date_var,
                                     values=dates,
                                     state="readonly",
                                     width=12)
        self.date_combo.pack(side=tk.LEFT, padx=5)
        self.date_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Filtro por acordes
        ttk.Label(filter_row2, text="Contiene acorde:", style="Normal.TLabel").pack(side=tk.LEFT, padx=5)
        self.chord_var = tk.StringVar()
        self.chord_entry = ttk.Entry(filter_row2, 
                                   textvariable=self.chord_var,
                                   width=10)
        self.chord_entry.pack(side=tk.LEFT, padx=5)
        self.chord_entry.bind('<KeyRelease>', self.apply_filters)
        
        # Botones de filtro
        filter_btn_frame = ttk.Frame(filter_row2, style="TFrame")
        filter_btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(filter_btn_frame,
                  text="🎯 Aplicar Filtros",
                  command=self.apply_filters,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(filter_btn_frame,
                  text="🗑️ Limpiar Filtros",
                  command=self.clear_filters,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=2)
        
    def create_main_content(self):
        """Crear contenido principal dividido"""
        main_paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Panel izquierdo - Lista de canciones
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=2)
        
        # Panel derecho - Vista previa/detalles
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        self.create_songs_list(left_frame)
        self.create_preview_panel(right_frame)
        
    def create_songs_list(self, parent):
        """Crear lista de canciones con treeview"""
        list_frame = ttk.LabelFrame(parent,
                                  text="📝 Lista de Canciones",
                                  padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar de la lista
        list_toolbar = ttk.Frame(list_frame, style="TFrame")
        list_toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_toolbar, 
                 text=f"Total: {len(self.songs_data)} canciones", 
                 style="Normal.TLabel").pack(side=tk.LEFT)
                 
        ttk.Label(list_toolbar,
                 text=f"Filtradas: {len(self.filtered_data)}",
                 style="Normal.TLabel").pack(side=tk.LEFT, padx=20)
        
        # Treeview para canciones
        columns = ('id', 'titulo', 'artista', 'categoria', 'tono', 'estado', 'fecha', 'acordes')
        self.songs_tree = ttk.Treeview(list_frame, 
                                     columns=columns, 
                                     show='headings',
                                     selectmode='extended',
                                     height=15)
        
        # Configurar columnas
        column_config = {
            'id': ('ID', 40),
            'titulo': ('Título', 150),
            'artista': ('Artista', 100),
            'categoria': ('Categoría', 90),
            'tono': ('Tono', 50),
            'estado': ('Estado', 80),
            'fecha': ('Fecha', 80),
            'acordes': ('Acordes', 100)
        }
        
        for col, (text, width) in column_config.items():
            self.songs_tree.heading(col, text=text)
            self.songs_tree.column(col, width=width)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, 
                                  orient=tk.VERTICAL, 
                                  command=self.songs_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame,
                                  orient=tk.HORIZONTAL,
                                  command=self.songs_tree.xview)
        self.songs_tree.configure(yscrollcommand=v_scrollbar.set,
                                xscrollcommand=h_scrollbar.set)
        
        # Empaquetar
        self.songs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind eventos
        self.songs_tree.bind('<<TreeviewSelect>>', self.on_song_select)
        self.songs_tree.bind('<Double-1>', self.on_song_double_click)
        
    def create_preview_panel(self, parent):
        """Crear panel de vista previa y detalles"""
        # Notebook para múltiples pestañas
        self.preview_notebook = ttk.Notebook(parent)
        self.preview_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de vista previa
        preview_frame = ttk.Frame(self.preview_notebook)
        self.preview_notebook.add(preview_frame, text="👁️ Vista Previa")
        
        self.preview_text = tk.Text(preview_frame, 
                                  wrap=tk.WORD, 
                                  font=('Arial', 10),
                                  height=15)
        preview_scrollbar = ttk.Scrollbar(preview_frame, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pestaña de detalles
        details_frame = ttk.Frame(self.preview_notebook)
        self.preview_notebook.add(details_frame, text="📋 Detalles")
        
        self.create_details_panel(details_frame)
        
        # Pestaña de metadatos
        metadata_frame = ttk.Frame(self.preview_notebook)
        self.preview_notebook.add(metadata_frame, text="🎵 Metadatos")
        
        self.create_metadata_panel(metadata_frame)
        
    def create_details_panel(self, parent):
        """Crear panel de detalles de canción"""
        details_text = tk.Text(parent, wrap=tk.WORD, font=('Arial', 9), height=15)
        details_scrollbar = ttk.Scrollbar(parent, command=details_text.yview)
        details_text.configure(yscrollcommand=details_scrollbar.set)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.details_text = details_text
        
    def create_metadata_panel(self, parent):
        """Crear panel de metadatos"""
        metadata_text = tk.Text(parent, wrap=tk.WORD, font=('Courier New', 9), height=15)
        metadata_scrollbar = ttk.Scrollbar(parent, command=metadata_text.yview)
        metadata_text.configure(yscrollcommand=metadata_scrollbar.set)
        
        metadata_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        metadata_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.metadata_text = metadata_text
        
    def create_toolbar(self):
        """Crear barra de herramientas inferior"""
        toolbar_frame = ttk.Frame(self.main_frame, style="TFrame")
        toolbar_frame.pack(fill=tk.X, pady=10)
        
        # Botones de acción masiva
        bulk_actions = [
            ("✏️ Editar Seleccionadas", self.edit_selected, "Primary.TButton"),
            ("🎹 Transponer", self.transpose_selected, "Info.TButton"),
            ("✅ Aprobar", self.approve_selected, "Success.TButton"),
            ("🗑️ Eliminar", self.delete_selected, "Danger.TButton"),
            ("📄 Exportar PDF", self.export_pdf, "Warning.TButton")
        ]
        
        for text, command, style in bulk_actions:
            ttk.Button(toolbar_frame,
                      text=text,
                      command=command,
                      style=style).pack(side=tk.LEFT, padx=2)
        
    def load_sample_data(self):
        """Cargar datos de ejemplo"""
        self.songs_data = [
            {
                'id': 1, 'titulo': 'Aleluya', 'artista': 'Comunidad', 
                'categoria': 'Alabanza', 'tono': 'G', 'estado': 'Aprobado',
                'fecha': '2024-01-10', 'acordes': 'G,C,D,Em',
                'contenido': '[G]Aleluya, ale[C]luya...',
                'bpm': 72, 'duracion': '3:45'
            },
            {
                'id': 2, 'titulo': 'Santo', 'artista': 'Traditional', 
                'categoria': 'Adoración', 'tono': 'C', 'estado': 'Aprobado',
                'fecha': '2024-01-08', 'acordes': 'C,F,G,Am',
                'contenido': 'Santo, [C]santo, [G]santo...',
                'bpm': 60, 'duracion': '4:20'
            },
            {
                'id': 3, 'titulo': 'Ven Espíritu', 'artista': 'Marcos Witt', 
                'categoria': 'Adoración', 'tono': 'D', 'estado': 'Pendiente',
                'fecha': '2024-01-15', 'acordes': 'D,G,A,Bm',
                'contenido': 'Ven [D]Espíritu...',
                'bpm': 80, 'duracion': '5:10'
            },
            {
                'id': 4, 'titulo': 'Cordero de Dios', 'artista': 'Comunidad', 
                'categoria': 'Cuaresma', 'tono': 'Am', 'estado': 'En revisión',
                'fecha': '2024-01-12', 'acordes': 'Am,Dm,E,G',
                'contenido': 'Cor[Am]dero de [Dm]Dios...',
                'bpm': 65, 'duracion': '3:30'
            },
            {
                'id': 5, 'titulo': 'Noche de Paz', 'artista': 'Traditional', 
                'categoria': 'Navidad', 'tono': 'F', 'estado': 'Aprobado',
                'fecha': '2023-12-20', 'acordes': 'F,Bb,C,Dm',
                'contenido': 'Noche de [F]paz...',
                'bpm': 70, 'duracion': '4:00'
            }
        ]
        
        self.filtered_data = self.songs_data.copy()
        self.populate_songs_list()
        
    def populate_songs_list(self):
        """Llenar la lista de canciones"""
        # Limpiar lista actual
        for item in self.songs_tree.get_children():
            self.songs_tree.delete(item)
            
        # Agregar canciones filtradas
        for song in self.filtered_data:
            self.songs_tree.insert('', tk.END, values=(
                song['id'],
                song['titulo'],
                song['artista'],
                song['categoria'],
                song['tono'],
                song['estado'],
                song['fecha'],
                song['acordes']
            ))
            
    def on_search_change(self, event=None):
        """Cuando cambia la búsqueda"""
        self.apply_filters()
        
    def apply_filters(self, event=None):
        """Aplicar todos los filtros"""
        search_term = self.search_var.get().lower()
        category = self.category_var.get()
        status = self.status_var.get()
        key = self.key_var.get()
        date_filter = self.date_var.get()
        chord_filter = self.chord_var.get().upper()
        
        self.filtered_data = []
        
        for song in self.songs_data:
            # Filtro de búsqueda
            if search_term and search_term not in song['titulo'].lower() and search_term not in song['artista'].lower():
                continue
                
            # Filtro de categoría
            if category != "Todas" and song['categoria'] != category:
                continue
                
            # Filtro de estado
            if status != "Todos" and song['estado'] != status:
                continue
                
            # Filtro de tono
            if key != "Todos" and song['tono'] != key:
                continue
                
            # Filtro de acordes
            if chord_filter and chord_filter not in song['acordes']:
                continue
                
            # Filtro de fecha
            if date_filter != "Todas":
                song_date = datetime.strptime(song['fecha'], '%Y-%m-%d')
                today = datetime.now()
                
                if date_filter == "Hoy" and song_date.date() != today.date():
                    continue
                elif date_filter == "Esta semana" and song_date < today - timedelta(days=today.weekday()):
                    continue
                elif date_filter == "Este mes" and song_date.month != today.month:
                    continue
                elif date_filter == "Últimos 3 meses" and song_date < today - timedelta(days=90):
                    continue
            
            self.filtered_data.append(song)
            
        self.populate_songs_list()
        
    def clear_filters(self):
        """Limpiar todos los filtros"""
        self.search_var.set("")
        self.category_var.set("Todas")
        self.status_var.set("Todos")
        self.key_var.set("Todos")
        self.date_var.set("Todas")
        self.chord_var.set("")
        self.apply_filters()
        
    def on_song_select(self, event):
        """Cuando se selecciona una canción"""
        selection = self.songs_tree.selection()
        if selection:
            item = selection[0]
            values = self.songs_tree.item(item, 'values')
            song_id = int(values[0])
            
            # Encontrar canción completa
            song = next((s for s in self.filtered_data if s['id'] == song_id), None)
            if song:
                self.show_song_preview(song)
                
    def on_song_double_click(self, event):
        """Doble click para editar canción"""
        selection = self.songs_tree.selection()
        if selection:
            self.edit_selected()
        
    def show_song_preview(self, song):
        """Mostrar vista previa de la canción"""
        # Vista previa
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, song.get('contenido', 'Sin contenido'))
        self.preview_text.config(state=tk.DISABLED)
        
        # Detalles
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        details = f"""Título: {song['titulo']}
Artista: {song['artista']}
Categoría: {song['categoria']}
Tono: {song['tono']}
Estado: {song['estado']}
Fecha: {song['fecha']}
BPM: {song.get('bpm', 'N/A')}
Duración: {song.get('duracion', 'N/A')}
Acordes: {song['acordes']}

Última modificación: {song['fecha']}
"""
        self.details_text.insert(1.0, details)
        self.details_text.config(state=tk.DISABLED)
        
        # Metadatos
        self.metadata_text.config(state=tk.NORMAL)
        self.metadata_text.delete(1.0, tk.END)
        
        metadata = f"""ID: {song['id']}
Título: {song['titulo']}
Artista: {song['artista']}
Categoría: {song['categoria']}
Tono Original: {song['tono']}
Estado: {song['estado']}
Fecha Creación: {song['fecha']}
BPM: {song.get('bpm', 'N/A')}
Duración Estimada: {song.get('duracion', 'N/A')}
Acordes Utilizados: {song['acordes']}

Estructura:
- Tipo: Canción litúrgica
- Secciones: VERSO, CORO
- Complejidad: Baja
"""
        self.metadata_text.insert(1.0, metadata)
        self.metadata_text.config(state=tk.DISABLED)
        
    def refresh_data(self):
        """Refrescar datos"""
        self.load_sample_data()
        messagebox.showinfo("Actualizar", "Datos actualizados correctamente")
        
    def export_data(self):
        """Exportar datos"""
        messagebox.showinfo("Exportar", "Funcionalidad de exportación en desarrollo")
        
    def show_stats(self):
        """Mostrar estadísticas"""
        stats = f"""📊 Estadísticas del Contenido

Total Canciones: {len(self.songs_data)}
- Aprobadas: {len([s for s in self.songs_data if s['estado'] == 'Aprobado'])}
- Pendientes: {len([s for s in self.songs_data if s['estado'] == 'Pendiente'])}
- En revisión: {len([s for s in self.songs_data if s['estado'] == 'En revisión'])}

Por Categoría:
{self.get_category_stats()}

Tonos Más Usados:
{self.get_key_stats()}
"""
        messagebox.showinfo("Estadísticas", stats)
        
    def get_category_stats(self):
        """Obtener estadísticas por categoría"""
        categories = {}
        for song in self.songs_data:
            cat = song['categoria']
            categories[cat] = categories.get(cat, 0) + 1
            
        stats = ""
        for cat, count in categories.items():
            stats += f"- {cat}: {count} canciones\n"
        return stats
        
    def get_key_stats(self):
        """Obtener estadísticas por tono"""
        keys = {}
        for song in self.songs_data:
            key = song['tono']
            keys[key] = keys.get(key, 0) + 1
            
        stats = ""
        for key, count in sorted(keys.items(), key=lambda x: x[1], reverse=True)[:5]:
            stats += f"- {key}: {count} canciones\n"
        return stats
        
    def edit_selected(self):
        """Editar canción seleccionada"""
        selection = self.songs_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona al menos una canción")
            return
            
        if len(selection) > 1:
            messagebox.showinfo("Editar Múltiple", f"Editando {len(selection)} canciones seleccionadas")
        else:
            messagebox.showinfo("Editar", "Abriendo editor para canción seleccionada")
            
    def transpose_selected(self):
        """Transponer canciones seleccionadas"""
        selection = self.songs_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona al menos una canción")
            return
            
        messagebox.showinfo("Transponer", f"Transponiendo {len(selection)} canciones")
        
    def approve_selected(self):
        """Aprobar canciones seleccionadas"""
        selection = self.songs_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona al menos una canción")
            return
            
        if messagebox.askyesno("Aprobar", f"¿Aprobar {len(selection)} canciones seleccionadas?"):
            messagebox.showinfo("Éxito", "Canciones aprobadas correctamente")
        
    def delete_selected(self):
        """Eliminar canciones seleccionadas"""
        selection = self.songs_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona al menos una canción")
            return
            
        if messagebox.askyesno("Eliminar", f"¿Eliminar {len(selection)} canciones seleccionadas?"):
            messagebox.showinfo("Éxito", "Canciones eliminadas correctamente")
            
    def export_pdf(self):
        """Exportar a PDF"""
        selection = self.songs_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona al menos una canción")
            return
            
        messagebox.showinfo("Exportar PDF", f"Exportando {len(selection)} canciones a PDF")