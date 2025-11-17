import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from datetime import datetime

class Editor:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_song = None
        self.songs_pending_review = []
        self.current_song_index = -1
        self.chord_pattern = re.compile(r'\[([A-G][#b]?[0-9]*(?:m|maj|min|dim|aug)?[0-9]*(?:\/[A-G][#b]?)?)\]')
        self.loading_song = False
        self.categories = []
        self.selected_categories = []
        
        # Variables para tempo y capo
        self.tempo_var = tk.IntVar(value=0)
        self.capo_var = tk.IntVar(value=0)
        
        # NUEVO: Variables para filtros de estado
        self.filter_pendiente = tk.BooleanVar(value=True)
        self.filter_borrador = tk.BooleanVar(value=True)
        self.filter_aprobado = tk.BooleanVar(value=False)
        self.filter_inactivo = tk.BooleanVar(value=False)

        # Inicializar UI de manera segura
        try:
            self.setup_ui()
            self.parent.after(100, self.load_pending_songs)
        except Exception as e:
            print(f"Error inicializando editor: {e}")
            self.setup_basic_ui()

        self.load_categories()

    def setup_basic_ui(self):
        """Configurar UI básica en caso de error"""
        error_frame = ttk.Frame(self.parent, style="TFrame")
        error_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(error_frame, 
                text="❌ Error cargando el editor", 
                style="Header.TLabel").pack(pady=20)
        
        ttk.Label(error_frame, 
                text="Reinicia la aplicación o contacta al soporte",
                style="Normal.TLabel").pack(pady=10)
        
        ttk.Button(error_frame,
                text="🔄 Recargar",
                command=self.reload_editor,
                style="Primary.TButton").pack(pady=10)

    def reload_editor(self):
        """Recargar el editor"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            self.setup_ui()
            self.load_pending_songs()
        except Exception as e:
            print(f"Error recargando editor: {e}")

    def load_pending_songs(self):
        """Cargar canciones según los filtros de estado seleccionados"""
        try:
            print("🔄 Cargando canciones con filtros de estado...")
            
            # Determinar qué estados buscar según los filtros activos
            estados_activos = []
            if self.filter_pendiente.get():
                estados_activos.append('pendiente')
            if self.filter_borrador.get():
                estados_activos.append('borrador')
            if self.filter_aprobado.get():
                estados_activos.append('aprobado')
            if self.filter_inactivo.get():
                estados_activos.append('inactivo')
            
            if not estados_activos:
                print("⚠️ No hay filtros de estado seleccionados")
                self.songs_pending_review = []
                self._load_songs_into_editor([])
                return
            
            # Obtener canciones para cada estado activo
            all_canciones = []
            for estado in estados_activos:
                filters = {'estado': estado}
                canciones = self.app.database.get_canciones(filters)
                all_canciones.extend(canciones)
            
            print(f"📝 Se encontraron {len(all_canciones)} canciones con filtros: {estados_activos}")
            
            self._load_songs_into_editor(all_canciones)
                
        except Exception as e:
            print(f"❌ Error cargando canciones: {e}")
            messagebox.showerror("Error", f"Error cargando canciones: {e}")

    def load_from_import(self):
        """Cargar específicamente las últimas canciones importadas"""
        try:
            print("🔄 Cargando canciones desde importación...")
            
            filters = {
                'estado': 'pendiente', 
                'fuente': 'importacion_pdf',
                'fecha_creacion': datetime.now().strftime('%Y-%m-%d')
            }
            
            canciones = self.app.database.get_canciones(filters)
            
            if canciones:
                print(f"📝 Se encontraron {len(canciones)} canciones importadas")
                self.songs_pending_review = canciones
                self.current_song_index = 0
                self.update_songs_list()
                self.load_song(0)
            else:
                print("ℹ️ No hay canciones pendientes de importación")
                messagebox.showinfo("Importación", "No hay canciones pendientes de importación")
                
        except Exception as e:
            print(f"❌ Error cargando canciones importadas: {e}")
            messagebox.showerror("Error", f"Error cargando canciones importadas: {e}")

    def _load_songs_into_editor(self, songs, from_import=False):
        """Método común para cargar canciones en el editor"""
        if songs:
            self.songs_pending_review = songs
            self.current_song_index = 0
            
            self.update_songs_list()
            self.update_song_counter()
            
            if from_import:
                print(f"🎵 Cargando primera canción importada")
                self.load_song(0)
            else:
                if self.songs_pending_review:
                    print(f"🎵 Cargando canción índice {self.current_song_index}")
                    self.load_song(0)
                else:
                    print("ℹ️ No hay canciones para revisar")
                    self.clear_editor()

    def setup_ui(self):
        """Configurar interfaz del editor mejorado"""
        print("🔄 Iniciando setup_ui del editor...")
        
        try:
            self.main_frame = ttk.Frame(self.parent, style="TFrame")
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            self.create_header()
            print("✅ Header creado")
            
            self.create_main_panels()
            print("✅ Paneles principales creados")
            
            self.create_tools_panel()
            print("✅ Panel de herramientas creado")
            
            print("✅ Setup_ui completado exitosamente")
            
        except Exception as e:
            print(f"❌ Error en setup_ui: {e}")
            raise
        
    def create_header(self):
        """Crear header con navegación de canciones"""
        header_frame = ttk.Frame(self.main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title_frame = ttk.Frame(header_frame, style="TFrame")
        title_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, 
                               text="✏️ Editor - Revisión de Canciones", 
                               style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Navegación
        nav_frame = ttk.Frame(header_frame, style="TFrame")
        nav_frame.pack(side=tk.RIGHT)
        
        # Contador
        self.song_counter = ttk.Label(nav_frame, 
                                     text="0/0 Canciones",
                                     style="Secondary.TLabel")
        self.song_counter.pack(side=tk.LEFT, padx=10)
        
        # Botones de navegación
        nav_buttons_frame = ttk.Frame(nav_frame, style="TFrame")
        nav_buttons_frame.pack(side=tk.LEFT)
        
        ttk.Button(nav_buttons_frame,
                  text="◀ Anterior",
                  command=self.previous_song,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(nav_buttons_frame,
                  text="Siguiente ▶",
                  command=self.next_song,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
        
    def create_main_panels(self):
        """Crear paneles principales divididos"""
        paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=10)
        
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        right_frame = ttk.Frame(paned_window)  
        paned_window.add(right_frame, weight=2)
        
        self.create_songs_list_panel(left_frame)
        self.create_editor_panel(right_frame)
        
    def create_songs_list_panel(self, parent):
        """Crear panel con lista de canciones y filtros"""
        list_frame = ttk.LabelFrame(parent,
                                  text="📋 Lista de Canciones",
                                  padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # NUEVO: Panel de filtros por estado
        self.create_filters_panel(list_frame)
        
        # Toolbar de lista
        list_toolbar = ttk.Frame(list_frame, style="TFrame")
        list_toolbar.pack(fill=tk.X, pady=(10, 10))
        
        ttk.Button(list_toolbar,
                  text="🔄 Actualizar Lista",
                  command=self.load_pending_songs,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(list_toolbar,
                  text="📥 Desde Importación",
                  command=self.load_from_import,
                  style="Success.TButton").pack(side=tk.LEFT, padx=2)
        
        # Lista de canciones con colores
        columns = ('titulo', 'artista', 'estado', 'fuente')
        self.songs_tree = ttk.Treeview(list_frame, 
                                     columns=columns, 
                                     show='headings',
                                     height=15)
        
        # Configurar columnas
        self.songs_tree.heading('titulo', text='Título')
        self.songs_tree.heading('artista', text='Artista')
        self.songs_tree.heading('estado', text='Estado')
        self.songs_tree.heading('fuente', text='Fuente')
        
        self.songs_tree.column('titulo', width=150)
        self.songs_tree.column('artista', width=100)
        self.songs_tree.column('estado', width=80)
        self.songs_tree.column('fuente', width=80)
        
        # NUEVO: Configurar tags de colores para estados
        self.songs_tree.tag_configure('pendiente', background='#FFF9C4')  # Amarillo claro
        self.songs_tree.tag_configure('borrador', background='#BBDEFB')   # Azul claro
        self.songs_tree.tag_configure('aprobado', background='#C8E6C9')   # Verde claro
        self.songs_tree.tag_configure('inactivo', background='#E0E0E0')   # Gris claro
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, 
                                orient=tk.VERTICAL, 
                                command=self.songs_tree.yview)
        self.songs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.songs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selección
        self.parent.after(100, lambda: self.songs_tree.bind('<<TreeviewSelect>>', self.on_song_select))

    def create_filters_panel(self, parent):
        """NUEVO: Crear panel de filtros por estado"""
        filters_frame = ttk.LabelFrame(parent, text="🔍 Filtrar por Estado", padding=10)
        filters_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para los checkboxes en una fila
        checks_frame = ttk.Frame(filters_frame, style="TFrame")
        checks_frame.pack(fill=tk.X)
        
        # Checkboxes para cada estado con colores indicativos
        filters_config = [
            (self.filter_pendiente, "🟡 Pendiente", "#FFF9C4"),
            (self.filter_borrador, "🔵 Borrador", "#BBDEFB"),
            (self.filter_aprobado, "🟢 Aprobado", "#C8E6C9"),
            (self.filter_inactivo, "⚫ Inactivo", "#E0E0E0")
        ]
        
        for i, (var, text, color) in enumerate(filters_config):
            # Frame para cada checkbox con su color
            check_container = ttk.Frame(checks_frame, style="TFrame")
            check_container.pack(side=tk.LEFT, padx=5)
            
            # Indicador de color
            color_label = tk.Label(check_container, text="  ", bg=color, relief=tk.SOLID, borderwidth=1)
            color_label.pack(side=tk.LEFT, padx=(0, 3))
            
            # Checkbox
            check = ttk.Checkbutton(check_container, 
                                   text=text, 
                                   variable=var,
                                   command=self.on_filter_change)
            check.pack(side=tk.LEFT)
        
        # Botón para aplicar filtros
        btn_frame = ttk.Frame(filters_frame, style="TFrame")
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame,
                  text="✓ Aplicar Filtros",
                  command=self.load_pending_songs,
                  style="Primary.TButton").pack(side=tk.LEFT)
        
        ttk.Button(btn_frame,
                  text="↺ Limpiar Filtros",
                  command=self.clear_filters,
                  style="Info.TButton").pack(side=tk.LEFT, padx=5)

    def on_filter_change(self):
        """Callback cuando cambia un filtro"""
        # Auto-actualizar la lista cuando cambia un filtro
        # Esto es opcional, puedes comentarlo si prefieres solo actualizar con el botón
        # self.load_pending_songs()
        pass

    def clear_filters(self):
        """Limpiar todos los filtros"""
        self.filter_pendiente.set(True)
        self.filter_borrador.set(True)
        self.filter_aprobado.set(False)
        self.filter_inactivo.set(False)
        self.load_pending_songs()
        
    def create_editor_panel(self, parent):
        """Crear panel del editor"""
        editor_frame = ttk.LabelFrame(parent,
                                    text="📝 Editor de Canción", 
                                    padding=15)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_quick_metadata(editor_frame)
        self.create_text_editor(editor_frame)
        self.create_action_buttons(editor_frame)
        
    def create_quick_metadata(self, parent):
        """Crear sección de metadatos rápidos"""
        meta_frame = ttk.Frame(parent, style="TFrame")
        meta_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        ttk.Label(meta_frame, text="Título:", style="Normal.TLabel").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = ttk.Entry(meta_frame, width=30)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=(10, 20))
        
        # Artista
        ttk.Label(meta_frame, text="Artista:", style="Normal.TLabel").grid(row=0, column=2, sticky="w", pady=2)
        self.artist_entry = ttk.Entry(meta_frame, width=25)
        self.artist_entry.grid(row=0, column=3, sticky="ew", pady=2, padx=(10, 0))
        
        # Tono
        ttk.Label(meta_frame, text="Tono:", style="Normal.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        self.key_combo = ttk.Combobox(meta_frame,
                                    values=["C", "Cm", "D", "Dm", "E", "Em", "F", "Fm", "G", "Gm", "A", "Am", "B", "Bm"],
                                    width=8)
        self.key_combo.set("C")
        self.key_combo.grid(row=1, column=1, sticky="w", pady=2, padx=(10, 20))
        
        # Categorías (múltiples)
        ttk.Label(meta_frame, text="Categorías:", style="Normal.TLabel").grid(row=1, column=2, sticky="w", pady=2)
        categories_btn_frame = ttk.Frame(meta_frame, style="TFrame")
        categories_btn_frame.grid(row=1, column=3, sticky="w", pady=2, padx=(10, 0))

        self.categories_label = ttk.Label(categories_btn_frame, 
                                        text="Ninguna seleccionada",
                                        style="Normal.TLabel",
                                        relief=tk.SUNKEN,
                                        padding=3)
        self.categories_label.pack(side=tk.LEFT)

        ttk.Button(categories_btn_frame,
                text="✎ Editar",
                command=self.edit_categories,
                style="Info.TButton").pack(side=tk.LEFT, padx=(5, 0))

        # Tempo y Capo
        ttk.Label(meta_frame, text="Tempo (BPM):", style="Normal.TLabel").grid(row=2, column=0, sticky="w", pady=2)
        self.tempo_spin = tk.Spinbox(meta_frame, from_=40, to=300, textvariable=self.tempo_var, width=8)
        self.tempo_spin.grid(row=2, column=1, sticky="w", pady=2, padx=(10, 20))

        ttk.Label(meta_frame, text="Capo:", style="Normal.TLabel").grid(row=2, column=2, sticky="w", pady=2)
        self.capo_spin = tk.Spinbox(meta_frame, from_=0, to=12, textvariable=self.capo_var, width=8)
        self.capo_spin.grid(row=2, column=3, sticky="w", pady=2, padx=(10, 0))

        meta_frame.columnconfigure(1, weight=1)
        meta_frame.columnconfigure(3, weight=1)
        
    def create_text_editor(self, parent):
        """Crear área de edición de texto"""
        # Toolbar del editor
        editor_toolbar = ttk.Frame(parent, style="TFrame")
        editor_toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Botones de formato
        format_buttons = [
            ("🎼 Insertar Acorde", self.insert_chord),
            ("📋 Estrofa", lambda: self.insert_section("VERSO")),
            ("🎵 Coro", lambda: self.insert_section("CORO")),
            ("📄 Puente", lambda: self.insert_section("PUENTE")),
            ("🎹 Transponer", self.show_transpose_dialog)
        ]
        
        for text, command in format_buttons:
            ttk.Button(editor_toolbar,
                      text=text,
                      command=command,
                      style="Info.TButton").pack(side=tk.LEFT, padx=2)
        
        # Área de texto principal
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_editor = scrolledtext.ScrolledText(text_frame,
                                                   wrap=tk.WORD,
                                                   font=('Courier New', 11),
                                                   undo=True,
                                                   maxundo=-1)
        
        # Tags para sintaxis
        self.text_editor.tag_configure("chord", foreground="blue", font=('Courier New', 11, 'bold'))
        self.text_editor.tag_configure("section", foreground="darkgreen", font=('Courier New', 11, 'bold'))
        
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # Bind eventos
        self.text_editor.bind('<KeyRelease>', self.on_text_change)
        
    def create_action_buttons(self, parent):
        """Crear botones de acción para la canción"""
        action_frame = ttk.Frame(parent, style="TFrame")
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame,
                  text="💾 Guardar Borrador",
                  command=self.save_draft,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(action_frame,
                  text="✅ Aprobar y Publicar",
                  command=self.approve_and_publish,
                  style="Success.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(action_frame,
                  text="🗑️ Descartar",
                  command=self.discard_song,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(action_frame,
                  text="🔍 Validar",
                  command=self.validate_song,
                  style="Info.TButton").pack(side=tk.RIGHT, padx=2)
        
    def create_tools_panel(self):
        """Crear panel de herramientas adicionales"""
        tools_frame = ttk.LabelFrame(self.main_frame,
                                   text="🛠️ Herramientas",
                                   padding=15)
        tools_frame.pack(fill=tk.X, pady=10)
        
        notebook = ttk.Notebook(tools_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de acordes
        chords_frame = ttk.Frame(notebook)
        notebook.add(chords_frame, text="🎵 Acordes")
        self.create_chords_tab(chords_frame)
        
        # Pestaña de validación
        validate_frame = ttk.Frame(notebook)
        notebook.add(validate_frame, text="✅ Validación")
        self.create_validation_tab(validate_frame)
        
    def create_chords_tab(self, parent):
        """Crear pestaña de gestión de acordes"""
        chords_list_frame = ttk.LabelFrame(parent, text="Acordes en la Canción", padding=10)
        chords_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.chords_listbox = tk.Listbox(chords_list_frame, height=6)
        chords_scrollbar = ttk.Scrollbar(chords_list_frame, command=self.chords_listbox.yview)
        self.chords_listbox.configure(yscrollcommand=chords_scrollbar.set)
        
        self.chords_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chords_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        chords_btn_frame = ttk.Frame(parent, style="TFrame")
        chords_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(chords_btn_frame,
                  text="🔄 Actualizar Acordes",
                  command=self.update_chords_list,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
        
    def create_validation_tab(self, parent):
        """Crear pestaña de validación"""
        self.validation_tree = ttk.Treeview(parent, columns=('tipo', 'mensaje', 'linea'), show='headings', height=6)
        self.validation_tree.heading('tipo', text='Tipo')
        self.validation_tree.heading('mensaje', text='Mensaje')
        self.validation_tree.heading('linea', text='Línea')
        
        self.validation_tree.column('tipo', width=80)
        self.validation_tree.column('mensaje', width=250)
        self.validation_tree.column('linea', width=60)
        
        validation_scrollbar = ttk.Scrollbar(parent, command=self.validation_tree.yview)
        self.validation_tree.configure(yscrollcommand=validation_scrollbar.set)
        
        self.validation_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        validation_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    
    def edit_categories(self):
        """Abrir diálogo para seleccionar múltiples categorías"""
        cat_dialog = tk.Toplevel(self.parent)
        cat_dialog.title("Seleccionar Categorías")
        cat_dialog.geometry("400x500")
        cat_dialog.transient(self.parent)
        cat_dialog.grab_set()
        
        ttk.Label(cat_dialog, 
                text="Selecciona una o más categorías:",
                style="Normal.TLabel").pack(pady=10, padx=10)
        
        # Frame con scrollbar para checkboxes
        canvas_frame = ttk.Frame(cat_dialog)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Crear checkboxes para cada categoría
        cat_vars = {}
        for cat in self.categories:
            var = tk.BooleanVar(value=(cat in self.selected_categories))
            cat_vars[cat] = var
            ttk.Checkbutton(scrollable_frame,
                        text=cat,
                        variable=var).pack(anchor="w", padx=10, pady=2)
        
        def save_selection():
            self.selected_categories = [cat for cat, var in cat_vars.items() if var.get()]
            self.update_categories_label()
            cat_dialog.destroy()
        
        # Botones
        btn_frame = ttk.Frame(cat_dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame,
                text="✓ Guardar",
                command=save_selection,
                style="Success.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame,
                text="✗ Cancelar",
                command=cat_dialog.destroy,
                style="Danger.TButton").pack(side=tk.LEFT, padx=5)

    def update_categories_label(self):
        """Actualizar el label de categorías seleccionadas"""
        if self.selected_categories:
            text = ", ".join(self.selected_categories)
            if len(text) > 30:
                text = text[:27] + "..."
        else:
            text = "Ninguna seleccionada"
        self.categories_label.config(text=text)
        
    def update_songs_list(self):
        """Actualizar lista de canciones en el treeview con colores por estado"""
        # Limpiar lista actual
        for item in self.songs_tree.get_children():
            self.songs_tree.delete(item)
            
        # Agregar canciones con tags de color según estado
        for song in self.songs_pending_review:
            estado = song.get('estado', 'pendiente')
            self.songs_tree.insert('', tk.END, 
                                  values=(
                                      song.get('titulo', 'Sin título'),
                                      song.get('artista', song.get('autor', 'Desconocido')),
                                      estado,
                                      song.get('fuente', 'BD')
                                  ),
                                  tags=(estado,))  # Aplicar tag según estado
            
    def update_song_counter(self):
        """Actualizar contador de canciones"""
        total = len(self.songs_pending_review)
        current = self.current_song_index + 1 if self.current_song_index >= 0 else 0
        
        # Contar por estado
        estados_count = {}
        for song in self.songs_pending_review:
            estado = song.get('estado', 'pendiente')
            estados_count[estado] = estados_count.get(estado, 0) + 1
        
        # Crear texto con desglose
        counter_text = f"{current}/{total} Canciones"
        if estados_count:
            desglose = ", ".join([f"{count} {estado}" for estado, count in estados_count.items()])
            counter_text += f" ({desglose})"
        
        self.song_counter.config(text=counter_text)
        
    def load_song(self, index):
        """Cargar canción en el editor"""
        if hasattr(self, 'loading_song') and self.loading_song:
            print("⏸️ load_song ya en ejecución, ignorando...")
            return
            
        print(f"🔄 Cargando canción en índice {index}")
        self.loading_song = True
        
        try:
            if 0 <= index < len(self.songs_pending_review):
                self.current_song_index = index
                self.current_song = self.songs_pending_review[index]
                
                print(f"🎵 Canción cargada: {self.current_song.get('titulo', 'Sin título')}")
                
                # Actualizar interfaz
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, self.current_song.get('titulo', ''))
                
                self.artist_entry.delete(0, tk.END)
                self.artist_entry.insert(0, self.current_song.get('autor', ''))
                
                self.key_combo.set(self.current_song.get('tonalidad_original', 'C'))
                
                # Cargar categorías de la canción (puede ser string o lista)
                song_categories = self.current_song.get('categorias', [])
                if isinstance(song_categories, str):
                    song_categories = [cat.strip() for cat in song_categories.split(',') if cat.strip()]
                self.selected_categories = song_categories
                self.update_categories_label()
                
                try:
                    self.tempo_var.set(int(self.current_song.get('tempo_bpm', 0) or 0))
                except Exception:
                    self.tempo_var.set(0)
                try:
                    self.capo_var.set(int(self.current_song.get('posicion_capo', 0) or 0))
                except Exception:
                    self.capo_var.set(0)
                
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, self.current_song.get('letra_con_acordes', ''))
                
                self.highlight_syntax()
                self.update_chords_list()
                self.update_song_counter()
                
                # Seleccionar en la lista
                items = self.songs_tree.get_children()
                if items and index < len(items):
                    self.songs_tree.unbind('<<TreeviewSelect>>')
                    self.songs_tree.selection_set(items[index])
                    self.songs_tree.focus(items[index])
                    self.parent.after(100, self._rebind_treeview)
                    
                print("✅ Canción cargada exitosamente en el editor")
            else:
                print(f"❌ Índice {index} fuera de rango. Total canciones: {len(self.songs_pending_review)}")
                
        except Exception as e:
            print(f"❌ Error en load_song: {e}")
        finally:
            self.loading_song = False

    def _rebind_treeview(self):
        """Re-vincular evento del treeview después de cargar canción"""
        self.songs_tree.bind('<<TreeviewSelect>>', self.on_song_select)
        print("🔗 Treeview re-vinculado")

    def on_song_select(self, event):
        """Cuando se selecciona una canción en la lista"""
        if hasattr(self, 'loading_song') and self.loading_song:
            print("⏸️ Ignorando selección durante carga...")
            return
            
        selection = self.songs_tree.selection()
        if selection:
            index = self.songs_tree.index(selection[0])
            print(f"🎯 Usuario seleccionó canción en índice {index}")
            self.load_song(index)
            
    def previous_song(self):
        """Cargar canción anterior"""
        if self.current_song_index > 0:
            self.load_song(self.current_song_index - 1)
            
    def next_song(self):
        """Cargar siguiente canción"""
        if self.current_song_index < len(self.songs_pending_review) - 1:
            self.load_song(self.current_song_index + 1)
            
    def load_imported_songs(self, songs):
        """Cargar canciones desde el módulo de importación"""
        if songs:
            self.songs_pending_review = songs
            self.update_songs_list()
            self.load_song(0)
            self.update_song_counter()
            print(f"📥 Cargadas {len(songs)} canciones importadas")
        else:
            print("❌ No hay canciones para cargar")
            
    def load_categories(self):
        """Cargar categorías desde la BD"""
        try:
            print("📂 Cargando categorías...")
            categories = self.app.database.get_categorias()
            if categories:
                self.categories = [cat.get('nombre', '') for cat in categories if cat.get('nombre')]
                print(f"✅ Categorías cargadas: {self.categories}")
                
                if hasattr(self, 'category_combo'):
                    self.category_combo['values'] = self.categories
                    if self.categories:
                        self.category_combo.set(self.categories[0])
            else:
                print("⚠️ No se encontraron categorías")
                self.categories = ["General"]
        except Exception as e:
            print(f"❌ Error cargando categorías: {e}")
            self.categories = ["General"]

    def insert_chord(self):
        """Insertar marcador de acorde"""
        chord_dialog = tk.Toplevel(self.parent)
        chord_dialog.title("Insertar Acorde")
        chord_dialog.geometry("300x150")
        chord_dialog.transient(self.parent)
        chord_dialog.grab_set()
        
        ttk.Label(chord_dialog, text="Acorde:", style="Normal.TLabel").pack(pady=10)
        
        chord_entry = ttk.Entry(chord_dialog, font=('Arial', 12))
        chord_entry.pack(pady=5, padx=20, fill=tk.X)
        chord_entry.focus()
        
        def insert_and_close():
            chord = chord_entry.get().strip()
            if chord:
                self.text_editor.insert(tk.INSERT, f"[{chord}]")
            chord_dialog.destroy()
            
        chord_entry.bind('<Return>', lambda e: insert_and_close())
        
        btn_frame = ttk.Frame(chord_dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Insertar", command=insert_and_close, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=chord_dialog.destroy, style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        
    def insert_section(self, section_type):
        """Insertar sección de canción"""
        sections = {
            "VERSO": "VERSO",
            "CORO": "CORO", 
            "PUENTE": "PUENTE",
            "INTRO": "INTRO",
            "OUTRO": "OUTRO"
        }
        
        section_text = f"\n[{sections.get(section_type, section_type)}]\n"
        self.text_editor.insert(tk.INSERT, section_text)
        
    def on_text_change(self, event=None):
        """Cuando cambia el texto del editor"""
        self.highlight_syntax()
        
    def highlight_syntax(self):
        """Resaltar sintaxis de acordes y secciones"""
        for tag in ["chord", "section"]:
            self.text_editor.tag_remove(tag, "1.0", tk.END)
            
        text = self.text_editor.get(1.0, tk.END)
        
        # Resaltar acordes
        for match in self.chord_pattern.finditer(text):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add("chord", start, end)
            
        # Resaltar secciones
        section_pattern = re.compile(r'\[(VERSO|CORO|PUENTE|INTRO|OUTRO)(?:\s+\d+)?\]', re.IGNORECASE)
        for match in section_pattern.finditer(text):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add("section", start, end)
            
    def update_chords_list(self):
        """Actualizar lista de acordes utilizados"""
        if not self.chords_listbox:
            return
            
        self.chords_listbox.delete(0, tk.END)
        text = self.text_editor.get(1.0, tk.END)
        
        chords_found = set()
        for match in self.chord_pattern.finditer(text):
            chord = match.group(1)
            chords_found.add(chord)
            
        for chord in sorted(chords_found):
            self.chords_listbox.insert(tk.END, chord)
            
    def show_transpose_dialog(self):
        """Mostrar diálogo de transposición"""
        messagebox.showinfo("Transponer", "Funcionalidad de transposición en desarrollo")
        
    def validate_song(self):
        """Validar canción actual"""
        self.run_validation()
        
    def run_validation(self):
        """Ejecutar validación de la canción"""
        for item in self.validation_tree.get_children():
            self.validation_tree.delete(item)
            
        titulo = self.title_entry.get().strip()
        letra = self.text_editor.get(1.0, tk.END).strip()
        
        validations = []
        
        if not titulo:
            validations.append(('Error', 'El título es requerido', 0))
            
        if not letra or len(letra) < 10:
            validations.append(('Advertencia', 'La letra parece muy corta', 0))
            
        if '[' not in letra or ']' not in letra:
            validations.append(('Advertencia', 'No se detectaron acordes o secciones', 0))
            
        for tipo, mensaje, linea in validations:
            self.validation_tree.insert('', tk.END, values=(tipo, mensaje, linea))
            
    def save_draft(self):
        """Guardar como borrador"""
        if not self.current_song:
            messagebox.showwarning("Advertencia", "No hay canción seleccionada")
            return
            
        try:
            print("\n🔍 DEBUG - Guardando borrador:")
            print(f"ID: {self.current_song.get('id')}")
            print(f"Estado actual: {self.current_song.get('estado')}")
            
            update_data = {
                'id': str(self.current_song.get('id')),
                'titulo': self.title_entry.get().strip(),
                'autor': self.artist_entry.get().strip(),
                'letra_con_acordes': self.text_editor.get(1.0, tk.END).strip(),
                'tonalidad_original': self.key_combo.get(),
                'estado': 'borrador',
                'tempo_bpm': int(self.tempo_var.get() or 0),
                'posicion_capo': int(self.capo_var.get() or 0),
                'categoria_ids': self.get_categoria_ids(self.selected_categories),  # NUEVA LÍNEA
                'version': self.current_song.get('version', 1)
            }
            
            print("\n📤 DEBUG - Datos a enviar:")
            for key, value in update_data.items():
                print(f"{key}: {value}")
                
            result = self.app.database.update_cancion(
                update_data['id'], 
                update_data
            )
            
            print("\n📥 DEBUG - Respuesta del servidor:")
            print(f"Success: {result.get('success')}")
            print(f"Error: {result.get('error')}")
            
            if result.get('success'):
                messagebox.showinfo("Éxito", "Canción guardada como borrador")
                # Actualizar el estado local
                self.current_song['estado'] = 'borrador'
                self.update_songs_list()
            else:
                messagebox.showerror("Error", "Error al guardar la canción")
                
        except Exception as e:
            print(f"\n❌ DEBUG - Error en save_draft:")
            print(f"Tipo de error: {type(e)}")
            print(f"Detalles del error: {str(e)}")
            messagebox.showerror("Error", f"Error guardando borrador: {e}")
    
    def get_categoria_ids(self, categoria_nombres):
        """Convertir nombres de categorías a IDs"""
        ids = []
        for nombre in categoria_nombres:
            for cat in self.app.database.get_categorias():
                if cat.get('nombre') == nombre:
                    ids.append(cat.get('id'))
                    break
        return ids

    def approve_and_publish(self):
        """Aprobar y publicar canción"""
        if not self.current_song:
            messagebox.showwarning("Advertencia", "No hay canción seleccionada")
            return
            
        # Validar antes de publicar
        self.validate_song()
        validations = self.validation_tree.get_children()
        
        if validations:
            if not messagebox.askyesno("Advertencia", 
                                     "Hay validaciones pendientes. ¿Continuar con la publicación?"):
                return
        
        try:
            print("\n🔍 DEBUG - Datos originales de la canción:")
            print(f"ID: {self.current_song.get('id')}")
            print(f"Estado actual: {self.current_song.get('estado')}")
            print(f"Versión actual: {self.current_song.get('version')}")

            update_data = {
                'id': str(self.current_song.get('id')),
                'titulo': self.title_entry.get().strip(),
                'autor': self.artist_entry.get().strip(),
                'letra_con_acordes': self.text_editor.get(1.0, tk.END).strip(),
                'tonalidad_original': self.key_combo.get(),
                'estado': 'aprobado',
                'tempo_bpm': int(self.tempo_var.get() or 0),
                'posicion_capo': int(self.capo_var.get() or 0),
                'version': int(self.current_song.get('version', 1)) + 1,
                'categoria_ids': self.get_categoria_ids(self.selected_categories)  # NUEVA LÍNEA
            }
            
            print("\n📤 DEBUG - Datos a enviar al servidor:")
            for key, value in update_data.items():
                print(f"{key}: {value}")

            print(f"\n🌐 DEBUG - Llamando a update_cancion con ID: {update_data['id']}")
            
            result = self.app.database.update_cancion(
                update_data['id'], 
                update_data
            )
            
            print(f"\n📥 DEBUG - Respuesta del servidor:")
            print(f"Success: {result.get('success')}")
            print(f"Error: {result.get('error')}")
            print(f"Datos devueltos: {result}")

            if result.get('success'):
                messagebox.showinfo("Éxito", "Canción aprobada y publicada")
                # Remover de la lista si el filtro de aprobados está desactivado
                if not self.filter_aprobado.get():
                    if self.current_song_index < len(self.songs_pending_review):
                        self.songs_pending_review.pop(self.current_song_index)
                        self.update_songs_list()
                        if self.songs_pending_review:
                            next_index = min(self.current_song_index, len(self.songs_pending_review) - 1)
                            self.load_song(next_index)
                        else:
                            self.clear_editor()
                else:
                    # Si el filtro está activo, actualizar el estado local
                    self.current_song['estado'] = 'aprobado'
                    self.update_songs_list()
            else:
                messagebox.showerror("Error", "Error al publicar la canción")
                
        except Exception as e:
            print(f"\n❌ DEBUG - Error en approve_and_publish: {e}")
            print(f"Tipo de error: {type(e)}")
            print(f"Detalles del error: {str(e)}")
            messagebox.showerror("Error", f"Error publicando canción: {e}")
            
    def discard_song(self):
        """Descartar canción (soft delete)"""
        if not self.current_song:
            return
            
        if messagebox.askyesno("Confirmar", "¿Estás seguro de descartar esta canción?"):
            try:
                result = self.app.database.update_cancion(
                    self.current_song['id'], 
                    {'estado': 'inactivo'}
                )
                
                if result.get('success'):
                    messagebox.showinfo("Éxito", "Canción descartada")
                    # Remover de la lista si el filtro de inactivos está desactivado
                    if not self.filter_inactivo.get():
                        self.songs_pending_review.pop(self.current_song_index)
                    else:
                        self.current_song['estado'] = 'inactivo'
                    self.update_songs_list()
                    if self.songs_pending_review:
                        next_index = min(self.current_song_index, len(self.songs_pending_review) - 1)
                        self.load_song(next_index)
                    else:
                        self.clear_editor()
                else:
                    messagebox.showerror("Error", "Error al descartar la canción")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error descartando canción: {e}")
                
    def clear_editor(self):
        """Limpiar editor"""
        self.title_entry.delete(0, tk.END)
        self.artist_entry.delete(0, tk.END)
        self.key_combo.set('C')
        self.selected_categories = []
        self.update_categories_label()
        self.text_editor.delete(1.0, tk.END)
        self.current_song = None
        self.current_song_index = -1
        self.update_song_counter()
        if hasattr(self, 'chords_listbox'):
            self.chords_listbox.delete(0, tk.END)
        if hasattr(self, 'validation_tree'):
            for item in self.validation_tree.get_children():
                self.validation_tree.delete(item)