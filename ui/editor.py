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

        # Inicializar UI de manera segura
        try:
            self.setup_ui()
            # Cargar canciones después de que la UI esté lista
            self.parent.after(100, self.load_pending_songs)
        except Exception as e:
            print(f"Error inicializando editor: {e}")
            # Mostrar interfaz básica de error
            self.setup_basic_ui()

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
        """Cargar canciones pendientes de revisión desde la BD"""
        try:
            print("🔄 Cargando canciones pendientes desde BD...")
            
            # Obtener canciones con estado "pendiente"
            filters = {'estado': 'pendiente'}
            canciones = self.app.database.get_canciones(filters)
            
            print(f"📝 Se encontraron {len(canciones)} canciones pendientes")
            
            self.songs_pending_review = canciones
            self.current_song_index = 0 if canciones else -1
            
            self.update_songs_list()
            self.update_song_counter()
            
            # Cargar primera canción si existe
            if self.songs_pending_review:
                print(f"🎵 Cargando canción índice {self.current_song_index}")
                self.load_song(0)
            else:
                print("ℹ️ No hay canciones pendientes para revisar")
                self.clear_editor()
                
        except Exception as e:
            print(f"❌ Error cargando canciones pendientes: {e}")
            messagebox.showerror("Error", f"Error cargando canciones: {e}")
        
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
                                    values=["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
                                    width=8)
        self.key_combo.set("C")
        self.key_combo.grid(row=1, column=1, sticky="w", pady=2, padx=(10, 20))
        
        # Categoría
        ttk.Label(meta_frame, text="Categoría:", style="Normal.TLabel").grid(row=1, column=2, sticky="w", pady=2)
        self.category_combo = ttk.Combobox(meta_frame, 
                                         values=["Alabanza", "Adoración", "Cuaresma", "Navidad", "Comunión", "General"],
                                         width=12)
        self.category_combo.grid(row=1, column=3, sticky="w", pady=2, padx=(10, 0))
        
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
        if self.loading_song:  # ← EVITAR RECURSIÓN
            return
            
        print(f"🔄 Cargando canción en índice {index}")
        self.loading_song = True  # ← BLOQUEAR RECURSIÓN
        
        try:
            if 0 <= index < len(self.songs_pending_review):
                self.current_song_index = index
                self.current_song = self.songs_pending_review[index]
                
                print(f"🎵 Canción cargada: {self.current_song.get('titulo', 'Sin título')}")
                
                # Actualizar interfaz
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, self.current_song.get('titulo', ''))
                
                self.artist_entry.delete(0, tk.END)
                self.artist_entry.insert(0, self.current_song.get('artista', ''))
                
                self.key_combo.set(self.current_song.get('tono_original', 'C'))
                self.category_combo.set(self.current_song.get('categoria', 'General'))
                
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, self.current_song.get('letra', ''))
                
                self.highlight_syntax()
                self.update_chords_list()
                self.update_song_counter()
                
                # Seleccionar en la lista (sin disparar eventos)
                items = self.songs_tree.get_children()
                if items and index < len(items):
                    # Desvincular temporalmente el evento para evitar bucle
                    self.songs_tree.unbind('<<TreeviewSelect>>')
                    self.songs_tree.selection_set(items[index])
                    self.songs_tree.focus(items[index])
                    # Volver a vincular el evento
                    self.songs_tree.bind('<<TreeviewSelect>>', self.on_song_select)
                    
                print("✅ Canción cargada exitosamente en el editor")
            else:
                print(f"❌ Índice {index} fuera de rango. Total canciones: {len(self.songs_pending_review)}")
                
        finally:
            self.loading_song = False  # ← DESBLOQUEAR

    def on_song_select(self, event):
        """Cuando se selecciona una canción en la lista"""
        if self.loading_song:  # ← EVITAR RECURSIÓN DURANTE CARGA
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
            
    def load_from_import(self):
        """Cargar canciones desde el módulo de importación"""
        # Esto se conectará con el módulo de importación
        messagebox.showinfo("Importar", "Esta función cargará canciones recién importadas")
        
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
            # Actualizar datos de la canción
            self.current_song['titulo'] = self.title_entry.get().strip()
            self.current_song['artista'] = self.artist_entry.get().strip()
            self.current_song['letra'] = self.text_editor.get(1.0, tk.END).strip()
            self.current_song['tono_original'] = self.key_combo.get()
            self.current_song['estado'] = 'pendiente'
            
            # Guardar en BD
            result = self.app.database.update_cancion(
                self.current_song['id'], 
                self.current_song
            )
            
            if result.get('success'):
                messagebox.showinfo("Éxito", "Canción guardada como borrador")
            else:
                messagebox.showerror("Error", "Error al guardar la canción")
                
        except Exception as e:
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
            # Actualizar datos
            self.current_song['titulo'] = self.title_entry.get().strip()
            self.current_song['artista'] = self.artist_entry.get().strip()
            self.current_song['letra'] = self.text_editor.get(1.0, tk.END).strip()
            self.current_song['tono_original'] = self.key_combo.get()
            self.current_song['estado'] = 'activo'  # Cambiar estado a activo
            
            # Guardar en BD
            result = self.app.database.update_cancion(
                self.current_song['id'], 
                self.current_song
            )
            
            if result.get('success'):
                messagebox.showinfo("Éxito", "Canción aprobada y publicada")
                # Remover de la lista de pendientes y recargar
                self.songs_pending_review.pop(self.current_song_index)
                self.load_pending_songs()
            else:
                messagebox.showerror("Error", "Error al publicar la canción")
                
        except Exception as e:
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