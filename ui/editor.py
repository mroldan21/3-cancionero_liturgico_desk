import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re

class Editor:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_song = None
        self.chord_pattern = re.compile(r'\[([A-G][#b]?[0-9]*(?:m|maj|min|dim|aug)?[0-9]*(?:\/[A-G][#b]?)?)\]')
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz del editor avanzado"""
        self.main_frame = ttk.Frame(self.parent, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ttk.Frame(self.main_frame, style="TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, 
                               text="✏️ Editor Avanzado", 
                               style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Botones de canción
        song_btn_frame = ttk.Frame(title_frame, style="TFrame")
        song_btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(song_btn_frame,
                  text="📝 Nueva Canción",
                  command=self.new_song,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(song_btn_frame,
                  text="📂 Cargar Canción", 
                  command=self.load_song,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
        
        # Panel principal dividido
        self.create_main_panels()
        
        # Panel de herramientas
        self.create_tools_panel()
        
    def create_main_panels(self):
        """Crear paneles principales divididos"""
        # Panel dividido horizontal
        paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Panel izquierdo - Metadatos
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Panel derecho - Editor de texto
        right_frame = ttk.Frame(paned_window)  
        paned_window.add(right_frame, weight=2)
        
        # Configurar paneles
        self.create_metadata_panel(left_frame)
        self.create_editor_panel(right_frame)
        
    def create_metadata_panel(self, parent):
        """Crear panel de metadatos"""
        metadata_frame = ttk.LabelFrame(parent,
                                      text="📋 Metadatos de la Canción",
                                      padding=15)
        metadata_frame.pack(fill=tk.BOTH, expand=True)
        
        # Formulario de metadatos
        form_frame = ttk.Frame(metadata_frame)
        form_frame.pack(fill=tk.X, pady=5)
        
        # Título
        ttk.Label(form_frame, text="Título:", style="Normal.TLabel").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = ttk.Entry(form_frame, width=30)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        # Artista
        ttk.Label(form_frame, text="Artista:", style="Normal.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        self.artist_entry = ttk.Entry(form_frame, width=30)
        self.artist_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        # Categoría
        ttk.Label(form_frame, text="Categoría:", style="Normal.TLabel").grid(row=2, column=0, sticky="w", pady=2)
        self.category_combo = ttk.Combobox(form_frame, 
                                         values=["Alabanza", "Adoración", "Cuaresma", "Navidad", "Comunión", "General"])
        self.category_combo.grid(row=2, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        # Tono original
        ttk.Label(form_frame, text="Tono Original:", style="Normal.TLabel").grid(row=3, column=0, sticky="w", pady=2)
        self.key_combo = ttk.Combobox(form_frame,
                                    values=["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])
        self.key_combo.grid(row=3, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        # BPM
        ttk.Label(form_frame, text="BPM:", style="Normal.TLabel").grid(row=4, column=0, sticky="w", pady=2)
        bpm_frame = ttk.Frame(form_frame)
        bpm_frame.grid(row=4, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        self.bpm_entry = ttk.Entry(bpm_frame, width=8)
        self.bpm_entry.pack(side=tk.LEFT)
        ttk.Label(bpm_frame, text="ppm", style="Small.TLabel").pack(side=tk.LEFT, padx=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Separador
        ttk.Separator(metadata_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Acordes utilizados
        chords_frame = ttk.LabelFrame(metadata_frame,
                                    text="🎵 Acordes en la Canción",
                                    padding=10)
        chords_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chords_listbox = tk.Listbox(chords_frame, height=8)
        chords_scrollbar = ttk.Scrollbar(chords_frame, command=self.chords_listbox.yview)
        self.chords_listbox.configure(yscrollcommand=chords_scrollbar.set)
        
        self.chords_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chords_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de metadatos
        meta_btn_frame = ttk.Frame(metadata_frame)
        meta_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(meta_btn_frame,
                  text="💾 Guardar",
                  command=self.save_song,
                  style="Success.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(meta_btn_frame,
                  text="🔄 Actualizar Acordes",
                  command=self.update_chords_list,
                  style="Info.TButton").pack(side=tk.LEFT, padx=2)
        
    def create_editor_panel(self, parent):
        """Crear panel del editor de texto"""
        editor_frame = ttk.LabelFrame(parent,
                                    text="📝 Editor de Letra y Acordes", 
                                    padding=15)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar del editor
        editor_toolbar = ttk.Frame(editor_frame)
        editor_toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Botones de formato
        format_buttons = [
            ("🎼 Insertar Acorde", self.insert_chord),
            ("📋 Estrofa", lambda: self.insert_section("VERSO")),
            ("🎵 Coro", lambda: self.insert_section("CORO")),
            ("📄 Puente", lambda: self.insert_section("PUENTE")),
            ("🎹 Transponer", self.show_transpose_dialog),
            ("🔍 Validar", self.validate_song)
        ]
        
        for text, command in format_buttons:
            ttk.Button(editor_toolbar,
                      text=text,
                      command=command,
                      style="Info.TButton").pack(side=tk.LEFT, padx=2)
        
        # Área de texto principal
        text_frame = ttk.Frame(editor_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_editor = scrolledtext.ScrolledText(text_frame,
                                                   wrap=tk.WORD,
                                                   font=('Courier New', 11),
                                                   undo=True,
                                                   maxundo=-1)
        
        # Configurar tags para sintaxis highlight
        self.text_editor.tag_configure("chord", foreground="blue", font=('Courier New', 11, 'bold'))
        self.text_editor.tag_configure("section", foreground="darkgreen", font=('Courier New', 11, 'bold'))
        self.text_editor.tag_configure("comment", foreground="gray", font=('Courier New', 10, 'italic'))
        
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # Bind eventos para real-time processing
        self.text_editor.bind('<KeyRelease>', self.on_text_change)
        
        # Contador de líneas
        self.line_count_label = ttk.Label(editor_frame, 
                                        text="Líneas: 0 | Caracteres: 0",
                                        style="Small.TLabel")
        self.line_count_label.pack(anchor="w")
        
    def create_tools_panel(self):
        """Crear panel de herramientas adicionales"""
        tools_frame = ttk.LabelFrame(self.main_frame,
                                   text="🛠️ Herramientas Avanzadas",
                                   padding=15)
        tools_frame.pack(fill=tk.X, pady=10)
        
        # Pestañas para diferentes herramientas
        notebook = ttk.Notebook(tools_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de transposición
        transpose_frame = ttk.Frame(notebook)
        notebook.add(transpose_frame, text="🎹 Transposición")
        
        self.create_transpose_tab(transpose_frame)
        
        # Pestaña de validación
        validate_frame = ttk.Frame(notebook)
        notebook.add(validate_frame, text="✅ Validación")
        
        self.create_validation_tab(validate_frame)
        
        # Pestaña de previsualización
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="👁️ Previsualización")
        
        self.create_preview_tab(preview_frame)
        
    def create_transpose_tab(self, parent):
        """Crear pestaña de transposición"""
        ttk.Label(parent, text="Transponer acordes:", style="Normal.TLabel").pack(anchor="w", pady=5)
        
        # Selector de semitonos
        semitones_frame = ttk.Frame(parent)
        semitones_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(semitones_frame, text="Semitonos:", style="Small.TLabel").pack(side=tk.LEFT)
        self.semitones_var = tk.IntVar(value=0)
        
        ttk.Scale(semitones_frame, 
                 from_=-12, to=12, 
                 variable=self.semitones_var,
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
                 
        ttk.Label(semitones_frame, 
                 textvariable=self.semitones_var,
                 style="Small.TLabel").pack(side=tk.LEFT)
        
        # Info de transposición
        self.transpose_info = ttk.Label(parent, 
                                      text="Original: - → Nuevo: -",
                                      style="Secondary.TLabel")
        self.transpose_info.pack(anchor="w", pady=5)
        
        # Botones de transposición
        transpose_btn_frame = ttk.Frame(parent)
        transpose_btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(transpose_btn_frame,
                  text="🎼 Transponer",
                  command=self.transpose_chords,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(transpose_btn_frame,
                  text="🔄 Reiniciar",
                  command=self.reset_transposition,
                  style="Info.TButton").pack(side=tk.LEFT, padx=2)
        
    def create_validation_tab(self, parent):
        """Crear pestaña de validación"""
        # Lista de validaciones
        self.validation_tree = ttk.Treeview(parent, columns=('tipo', 'mensaje', 'linea'), show='headings', height=8)
        self.validation_tree.heading('tipo', text='Tipo')
        self.validation_tree.heading('mensaje', text='Mensaje')
        self.validation_tree.heading('linea', text='Línea')
        
        self.validation_tree.column('tipo', width=80)
        self.validation_tree.column('mensaje', width=300)
        self.validation_tree.column('linea', width=60)
        
        validation_scrollbar = ttk.Scrollbar(parent, command=self.validation_tree.yview)
        self.validation_tree.configure(yscrollcommand=validation_scrollbar.set)
        
        self.validation_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        validation_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de validación
        validate_btn_frame = ttk.Frame(parent)
        validate_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(validate_btn_frame,
                  text="🔍 Ejecutar Validación",
                  command=self.run_validation,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(validate_btn_frame,
                  text="🗑️ Limpiar",
                  command=self.clear_validation,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=2)
        
    def create_preview_tab(self, parent):
        """Crear pestaña de previsualización"""
        self.preview_text = scrolledtext.ScrolledText(parent,
                                                    wrap=tk.WORD,
                                                    font=('Arial', 10),
                                                    state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        preview_btn_frame = ttk.Frame(parent)
        preview_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(preview_btn_frame,
                  text="🔄 Actualizar Vista Previa",
                  command=self.update_preview,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
        
    def new_song(self):
        """Crear nueva canción"""
        if self.current_song and self.text_editor.edit_modified():
            if not messagebox.askyesno("Guardar", "¿Guardar cambios antes de crear nueva canción?"):
                return
                
        self.current_song = {
            'title': '',
            'artist': '',
            'category': '',
            'key': 'C',
            'bpm': '',
            'content': ''
        }
        
        self.clear_editor()
        self.title_entry.focus()
        
    def load_song(self):
        """Cargar canción existente"""
        # Placeholder - simular carga de canción
        sample_song = {
            'title': 'Aleluya',
            'artist': 'Comunidad',
            'category': 'Alabanza', 
            'key': 'G',
            'bpm': '72',
            'content': """[INTRO]
[G]Aleluya, ale[C]luya, ale[G]luya

[VERSO 1]
[G]Te alabamos Señor,
[C]Con todo nuestro [G]ser
[D]Tu amor nos da la [C]vida
[G]Y nos hace [D]ven[G]cer

[CORO]
[G]Aleluya, ale[C]luya
[G]Cantamos con a[D]mor
[G]Aleluya, ale[C]luya
[G]A nuestro Salva[D]dor[G]"""
        }
        
        self.current_song = sample_song
        self.populate_editor()
        
    def clear_editor(self):
        """Limpiar editor"""
        self.title_entry.delete(0, tk.END)
        self.artist_entry.delete(0, tk.END)
        self.category_combo.set('')
        self.key_combo.set('C')
        self.bpm_entry.delete(0, tk.END)
        self.text_editor.delete(1.0, tk.END)
        self.chords_listbox.delete(0, tk.END)
        self.text_editor.edit_modified(False)
        
    def populate_editor(self):
        """Llenar editor con datos de canción"""
        if not self.current_song:
            return
            
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, self.current_song.get('title', ''))
        
        self.artist_entry.delete(0, tk.END)
        self.artist_entry.insert(0, self.current_song.get('artist', ''))
        
        self.category_combo.set(self.current_song.get('category', ''))
        self.key_combo.set(self.current_song.get('key', 'C'))
        self.bpm_entry.delete(0, tk.END)
        self.bpm_entry.insert(0, self.current_song.get('bpm', ''))
        
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, self.current_song.get('content', ''))
        
        self.update_chords_list()
        self.highlight_syntax()
        self.update_line_count()
        self.text_editor.edit_modified(False)
        
    def insert_chord(self):
        """Insertar marcador de acorde"""
        chord_dialog = tk.Toplevel(self.parent)
        chord_dialog.title("Insertar Acorde")
        chord_dialog.geometry("300x200")
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
        self.update_line_count()
        self.highlight_syntax()
        
    def update_line_count(self):
        """Actualizar contador de líneas y caracteres"""
        text = self.text_editor.get(1.0, tk.END)
        lines = text.count('\n')
        chars = len(text.replace('\n', ''))
        self.line_count_label.config(text=f"Líneas: {lines} | Caracteres: {chars}")
        
    def highlight_syntax(self):
        """Resaltar sintaxis de acordes y secciones"""
        # Limpiar tags anteriores
        for tag in ["chord", "section", "comment"]:
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
        # Ya está integrado en las herramientas
        pass
        
    def validate_song(self):
        """Validar canción"""
        self.run_validation()
        
    def transpose_chords(self):
        """Transponer acordes"""
        # Placeholder - implementar lógica de transposición
        messagebox.showinfo("Transponer", "Funcionalidad de transposición en desarrollo")
        
    def reset_transposition(self):
        """Reiniciar transposición"""
        self.semitones_var.set(0)
        
    def run_validation(self):
        """Ejecutar validación"""
        # Limpiar validaciones anteriores
        for item in self.validation_tree.get_children():
            self.validation_tree.delete(item)
            
        text = self.text_editor.get(1.0, tk.END)
        lines = text.split('\n')
        
        # Validaciones básicas
        validations = []
        
        # Verificar título
        if not self.title_entry.get().strip():
            validations.append(('Error', 'Falta título de la canción', 0))
            
        # Verificar estructura básica
        has_sections = any(line.strip().startswith('[') and line.strip().endswith(']') for line in lines)
        if not has_sections:
            validations.append(('Advertencia', 'No se detectaron secciones (VERSO, CORO, etc.)', 0))
            
        # Verificar acordes
        has_chords = bool(self.chord_pattern.search(text))
        if not has_chords:
            validations.append(('Advertencia', 'No se detectaron acordes musicales', 0))
            
        # Agregar validaciones al treeview
        for tipo, mensaje, linea in validations:
            self.validation_tree.insert('', tk.END, values=(tipo, mensaje, linea))
            
    def clear_validation(self):
        """Limpiar validaciones"""
        for item in self.validation_tree.get_children():
            self.validation_tree.delete(item)
            
    def update_preview(self):
        """Actualizar vista previa"""
        text = self.text_editor.get(1.0, tk.END)
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, text)
        self.preview_text.config(state=tk.DISABLED)
        
    def save_song(self):
        """Guardar canción"""
        if not self.title_entry.get().strip():
            messagebox.showerror("Error", "El título es obligatorio")
            return
            
        # Simular guardado
        messagebox.showinfo("Guardar", "Canción guardada correctamente")
        self.text_editor.edit_modified(False)