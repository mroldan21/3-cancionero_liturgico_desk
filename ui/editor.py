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
        self.categories = []  # Add categories list
        # Nuevo: controles numéricos para tempo y capo
        self.tempo_var = tk.IntVar(value=0)
        self.capo_var = tk.IntVar(value=0)

        # Inicializar UI de manera segura
        try:
            self.setup_ui()
            # Cargar canciones después de que la UI esté lista
            self.parent.after(100, self.load_pending_songs)
        except Exception as e:
            print(f"Error inicializando editor: {e}")
            # Mostrar interfaz básica de error
            self.setup_basic_ui()

        self.load_categories()  # Load categories after init

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
            # Limpiar y recrear
            for widget in self.parent.winfo_children():
                widget.destroy()
            self.setup_ui()
            self.load_pending_songs()
        except Exception as e:
            print(f"Error recargando editor: {e}")

    def load_pending_songs(self):
        """Cargar todas las canciones pendientes de revisión desde la BD"""
        try:
            print("🔄 Cargando canciones pendientes desde BD...")
            
            # Obtener todas las canciones con estado "pendiente"
            filters = {'estado': 'pendiente'}
            canciones = self.app.database.get_canciones(filters)
            
            print(f"📝 Se encontraron {len(canciones)} canciones pendientes")
            
            self._load_songs_into_editor(canciones)
                
        except Exception as e:
            print(f"❌ Error cargando canciones pendientes: {e}")
            messagebox.showerror("Error", f"Error cargando canciones: {e}")

    def load_from_import(self):
        """Cargar específicamente las últimas canciones importadas"""
        try:
            print("🔄 Cargando canciones desde importación...")
            
            # Obtener solo las canciones recién importadas que no han sido revisadas
            filters = {
                'estado': 'pendiente', 
                'fuente': 'importacion_pdf',
                'fecha_creacion': datetime.now().strftime('%Y-%m-%d')  # Solo de hoy
            }
            
            canciones = self.app.database.get_canciones(filters)
            
            if canciones:
                print(f"📝 Se encontraron {len(canciones)} canciones importadas")
                # Reemplazar lista actual con las canciones importadas
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
                # Si viene de importación, cargar la primera canción
                print(f"🎵 Cargando primera canción importada")
                self.load_song(0)
            else:
                # Si es carga general, verificar si hay canciones
                if self.songs_pending_review:
                    print(f"🎵 Cargando canción índice {self.current_song_index}")
                    self.load_song(0)
                else:
                    print("ℹ️ No hay canciones pendientes para revisar")
                    self.clear_editor()

    def setup_ui(self):
        """Configurar interfaz del editor mejorado"""
        print("🔄 Iniciando setup_ui del editor...")
        
        try:
            self.main_frame = ttk.Frame(self.parent, style="TFrame")
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Título y controles
            self.create_header()
            print("✅ Header creado")
            
            # Panel principal dividido
            self.create_main_panels()
            print("✅ Paneles principales creados")
            
            # Panel de herramientas
            self.create_tools_panel()
            print("✅ Panel de herramientas creado")
            
            print("✅ Setup_ui completado exitosamente")
            
        except Exception as e:
            print(f"❌ Error en setup_ui: {e}")
            raise
        
    def create_header(self):
        """Crear header con navegación de canciones pendientes"""
        header_frame = ttk.Frame(self.main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title_frame = ttk.Frame(header_frame, style="TFrame")
        title_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, 
                               text="✏️ Editor - Revisión de Canciones", 
                               style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Navegación de canciones pendientes
        nav_frame = ttk.Frame(header_frame, style="TFrame")
        nav_frame.pack(side=tk.RIGHT)
        
        # Contador de canciones pendientes
        self.song_counter = ttk.Label(nav_frame, 
                                     text="0/0 Pendientes",
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
        # Panel dividido horizontal
        paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Panel izquierdo - Lista de canciones pendientes
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Panel derecho - Editor
        right_frame = ttk.Frame(paned_window)  
        paned_window.add(right_frame, weight=2)
        
        # Configurar paneles
        self.create_songs_list_panel(left_frame)
        self.create_editor_panel(right_frame)
        
    def create_songs_list_panel(self, parent):
        """Crear panel con lista de canciones pendientes"""
        list_frame = ttk.LabelFrame(parent,
                                  text="📋 Canciones Pendientes de Revisión",
                                  padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar de lista
        list_toolbar = ttk.Frame(list_frame, style="TFrame")
        list_toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(list_toolbar,
                  text="🔄 Actualizar Lista",
                  command=self.load_pending_songs,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(list_toolbar,
                  text="📥 Cargar desde Importación",
                  command=self.load_from_import,
                  style="Success.TButton").pack(side=tk.LEFT, padx=2)
        
        # Lista de canciones
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
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, 
                                orient=tk.VERTICAL, 
                                command=self.songs_tree.yview)
        self.songs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.songs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selección
        self.parent.after(100, lambda: self.songs_tree.bind('<<TreeviewSelect>>', self.on_song_select))
        
    def create_editor_panel(self, parent):
        """Crear panel del editor"""
        editor_frame = ttk.LabelFrame(parent,
                                    text="📝 Editor de Canción", 
                                    padding=15)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Metadatos rápidos
        self.create_quick_metadata(editor_frame)
        
        # Editor de texto
        self.create_text_editor(editor_frame)
        
        # Botones de acción
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
        
        # Categoría
        ttk.Label(meta_frame, text="Categoría:", style="Normal.TLabel").grid(row=1, column=2, sticky="w", pady=2)
        self.category_combo = ttk.Combobox(meta_frame, 
                                         values=self.categories or ["General"],
                                         width=12)
        self.category_combo.grid(row=1, column=3, sticky="w", pady=2, padx=(10, 0))
        
        # Set default value
        if self.categories:
            self.category_combo.set(self.categories[0])
        else:
            self.category_combo.set("General")

        # Tempo (BPM) y Posición de Capo (int) - nuevos controles
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
        
        # Configurar tags para sintaxis highlight
        self.text_editor.tag_configure("chord", foreground="blue", font=('Courier New', 11, 'bold'))
        self.text_editor.tag_configure("section", foreground="darkgreen", font=('Courier New', 11, 'bold'))
        
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # Bind eventos para real-time processing
        self.text_editor.bind('<KeyRelease>', self.on_text_change)
        
    def create_action_buttons(self, parent):
        """Crear botones de acción para la canción"""
        action_frame = ttk.Frame(parent, style="TFrame")
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botones de estado
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
        
        # Pestañas para diferentes herramientas
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
        # Lista de acordes utilizados
        chords_list_frame = ttk.LabelFrame(parent, text="Acordes en la Canción", padding=10)
        chords_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.chords_listbox = tk.Listbox(chords_list_frame, height=6)
        chords_scrollbar = ttk.Scrollbar(chords_list_frame, command=self.chords_listbox.yview)
        self.chords_listbox.configure(yscrollcommand=chords_scrollbar.set)
        
        self.chords_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chords_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de acordes
        chords_btn_frame = ttk.Frame(parent, style="TFrame")
        chords_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(chords_btn_frame,
                  text="🔄 Actualizar Acordes",
                  command=self.update_chords_list,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
        
    def create_validation_tab(self, parent):
        """Crear pestaña de validación"""
        # Lista de validaciones
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
                    
    def update_songs_list(self):
        """Actualizar lista de canciones en el treeview"""
        # Limpiar lista actual
        for item in self.songs_tree.get_children():
            self.songs_tree.delete(item)
            
        # Agregar canciones pendientes
        for song in self.songs_pending_review:
            self.songs_tree.insert('', tk.END, values=(
                song.get('titulo', 'Sin título'),
                song.get('artista', 'Desconocido'),
                song.get('estado', 'pendiente'),
                song.get('fuente', 'BD')
            ))
            
    def update_song_counter(self):
        """Actualizar contador de canciones"""
        total = len(self.songs_pending_review)
        current = self.current_song_index + 1 if self.current_song_index >= 0 else 0
        self.song_counter.config(text=f"{current}/{total} Pendientes")
        
    def load_song(self, index):
        """Cargar canción en el editor"""
        if hasattr(self, 'loading_song') and self.loading_song:
            print("⏸️  load_song ya en ejecución, ignorando...")
            return
            
        print(f"🔄 Cargando canción en índice {index}")
        self.loading_song = True
        
        try:
            if 0 <= index < len(self.songs_pending_review):
                self.current_song_index = index
                self.current_song = self.songs_pending_review[index]
                
                print(f"🎵 Canción cargada: {self.current_song.get('titulo', 'Sin título')}")
                
                # Actualizar interfaz mapeando campos
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, self.current_song.get('titulo', ''))
                
                self.artist_entry.delete(0, tk.END)
                self.artist_entry.insert(0, self.current_song.get('autor', ''))  # Changed from 'artista'
                
                self.key_combo.set(self.current_song.get('tonalidad_original', 'C'))  # Changed from 'tono_original'
                
                # Update category if song has one, otherwise use first available
                song_category = self.current_song.get('categoria')
                if song_category and song_category in self.categories:
                    self.category_combo.set(song_category)
                elif self.categories:
                    self.category_combo.set(self.categories[0])
                
                # Rellenar tempo y capo desde la canción (si existen)
                try:
                    self.tempo_var.set(int(self.current_song.get('tempo_bpm', 0) or 0))
                except Exception:
                    self.tempo_var.set(0)
                try:
                    self.capo_var.set(int(self.current_song.get('posicion_capo', 0) or 0))
                except Exception:
                    self.capo_var.set(0)
                
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, self.current_song.get('letra_con_acordes', ''))  # Changed from 'letra'
                
                self.highlight_syntax()
                self.update_chords_list()
                self.update_song_counter()
                
                # Seleccionar en la lista (sin disparar eventos)
                items = self.songs_tree.get_children()
                if items and index < len(items):
                    # Desvincular temporalmente el evento
                    self.songs_tree.unbind('<<TreeviewSelect>>')
                    self.songs_tree.selection_set(items[index])
                    self.songs_tree.focus(items[index])
                    # Re-vincular después de un delay
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
            print("⏸️  Ignorando selección durante carga...")
            return
            
        selection = self.songs_tree.selection()
        if selection:
            index = self.songs_tree.index(selection[0])
            print(f"🎯 Usuario seleccionó canción en índice {index}")
            self.load_song(index)

    def on_song_select(self, event):
        """Cuando se selecciona una canción en la lista"""
        selection = self.songs_tree.selection()
        if selection:
            index = self.songs_tree.index(selection[0])
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
            self.load_song(0)  # Cargar la primera canción
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
                
                # Actualizar combobox si existe
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

    # Métodos de edición (mantener los existentes)
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
        # Limpiar tags anteriores
        for tag in ["chord", "section"]:
            self.text_editor.tag_remove(tag, "1.0", tk.END)
            
        text = self.text_editor.get(1.0, tk.END)
        
        # Resaltar acordes [ACORDE]
        for match in self.chord_pattern.finditer(text):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add("chord", start, end)
            
        # Resaltar secciones [SECCION]
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
        # Limpiar validaciones anteriores
        for item in self.validation_tree.get_children():
            self.validation_tree.delete(item)
            
        titulo = self.title_entry.get().strip()
        letra = self.text_editor.get(1.0, tk.END).strip()
        
        validations = []
        
        # Validar título
        if not titulo:
            validations.append(('Error', 'El título es requerido', 0))
            
        # Validar letra
        if not letra or len(letra) < 10:
            validations.append(('Advertencia', 'La letra parece muy corta', 0))
            
        # Validar estructura
        if '[' not in letra or ']' not in letra:
            validations.append(('Advertencia', 'No se detectaron acordes o secciones', 0))
            
        # Agregar validaciones
        for tipo, mensaje, linea in validations:
            self.validation_tree.insert('', tk.END, values=(tipo, mensaje, linea))
            
    def save_draft(self):
        """Guardar como borrador"""
        if not self.current_song:
            messagebox.showwarning("Advertencia", "No hay canción seleccionada")
            return
            
        try:
            # Debug: Mostrar datos originales
            print("\n🔍 DEBUG - Guardando borrador:")
            print(f"ID: {self.current_song.get('id')}")
            print(f"Estado actual: {self.current_song.get('estado')}")
            
            # Actualizar datos con mapeo correcto
            update_data = {
                'id': str(self.current_song.get('id')),
                'titulo': self.title_entry.get().strip(),
                'autor': self.artist_entry.get().strip(),
                'letra_con_acordes': self.text_editor.get(1.0, tk.END).strip(),
                'tonalidad_original': self.key_combo.get(),
                'activo': 1 if self.current_song.get('estado') == 'activo' else 0,
                'tempo_bpm': int(self.tempo_var.get() or 0),
                'posicion_capo': int(self.capo_var.get() or 0),
                'version': self.current_song.get('version', 1)
            }
            
            print("\n📤 DEBUG - Datos a enviar:")
            for key, value in update_data.items():
                print(f"{key}: {value}")
                
            # Guardar en BD
            result = self.app.database.update_cancion(
                update_data['id'], 
                update_data
            )
            
            print("\n📥 DEBUG - Respuesta del servidor:")
            print(f"Success: {result.get('success')}")
            print(f"Error: {result.get('error')}")
            
            if result.get('success'):
                messagebox.showinfo("Éxito", "Canción guardada como borrador")
            else:
                messagebox.showerror("Error", "Error al guardar la canción")
                
        except Exception as e:
            print(f"\n❌ DEBUG - Error en save_draft:")
            print(f"Tipo de error: {type(e)}")
            print(f"Detalles del error: {str(e)}")
            messagebox.showerror("Error", f"Error guardando borrador: {e}")

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
            # Debug: Mostrar datos originales
            print("\n🔍 DEBUG - Datos originales de la canción:")
            print(f"ID: {self.current_song.get('id')}")
            print(f"Estado actual: {self.current_song.get('estado')}")
            print(f"Versión actual: {self.current_song.get('version')}")

            # Debug: Mostrar datos a actualizar
            update_data = {
                'id': str(self.current_song.get('id')),
                'titulo': self.title_entry.get().strip(),
                'autor': self.artist_entry.get().strip(),
                'letra_con_acordes': self.text_editor.get(1.0, tk.END).strip(),
                'tonalidad_original': self.key_combo.get(),
                'activo': 1,
                'tempo_bpm': int(self.tempo_var.get() or 0),
                'posicion_capo': int(self.capo_var.get() or 0),
                'version': int(self.current_song.get('version', 1)) + 1
            }
            
            print("\n📤 DEBUG - Datos a enviar al servidor:")
            for key, value in update_data.items():
                print(f"{key}: {value}")

            # Debug: Mostrar llamada a API
            print(f"\n🌐 DEBUG - Llamando a update_cancion con ID: {update_data['id']}")
            
            # Guardar en BD
            result = self.app.database.update_cancion(
                update_data['id'], 
                update_data
            )
            
            # Debug: Mostrar respuesta del servidor
            print(f"\n📥 DEBUG - Respuesta del servidor:")
            print(f"Success: {result.get('success')}")
            print(f"Error: {result.get('error')}")
            print(f"Datos devueltos: {result}")

            if result.get('success'):
                messagebox.showinfo("Éxito", "Canción aprobada y publicada")
                # Remover de la lista de pendientes y recargar
                self.songs_pending_review.pop(self.current_song_index)
                self.load_pending_songs()
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
                # Marcar como inactiva
                result = self.app.database.update_cancion(
                    self.current_song['id'], 
                    {'estado': 'inactivo'}
                )
                
                if result.get('success'):
                    messagebox.showinfo("Éxito", "Canción descartada")
                    self.songs_pending_review.pop(self.current_song_index)
                    self.load_pending_songs()
                else:
                    messagebox.showerror("Error", "Error al descartar la canción")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error descartando canción: {e}")
                
    def clear_editor(self):
        """Limpiar editor"""
        self.title_entry.delete(0, tk.END)
        self.artist_entry.delete(0, tk.END)
        self.key_combo.set('C')
        self.category_combo.set('')
        self.text_editor.delete(1.0, tk.END)
        if hasattr(self, 'chords_listbox'):
            self.chords_listbox.delete(0, tk.END)