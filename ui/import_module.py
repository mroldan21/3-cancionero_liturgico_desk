import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import time
from core.file_processor import FileProcessor

class ImportModule:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.selected_files = []
        self.processing = False
        self.imported_songs = []  # Add storage for imported songs

        # Inicializar procesador de archivos
        self.file_processor = FileProcessor(app.database)
        self.file_processor.set_progress_callback(self.on_processing_progress)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz de importación mejorada"""
        self.main_frame = ttk.Frame(self.parent, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(self.main_frame, 
                               text="📥 Importación Masiva", 
                               style="Header.TLabel")
        title_label.pack(pady=10)
        
        # Panel de configuración
        self.create_config_panel()
        
        # Lista de archivos
        self.create_files_panel()
        
        # Panel de vista previa
        self.create_preview_panel()
        
        # Botones de acción
        self.create_action_buttons()

    def on_processing_progress(self, message, percent=None):
        """Callback para actualizar progreso del procesamiento"""
        if percent is not None:
            self.progress_var.set(percent)
        self.progress_label.config(text=message)
        self.parent.update()

    # Modificar el método process_files_thread:
    def process_files_thread(self):
        """Procesar archivos en hilo separado"""
        print("1.1 Procesando archivos en hilo separado...")

        total_files = len(self.selected_files)

        # Configurar opciones de procesamiento
        options = {
            'use_pdfplumber': True,
            'auto_detect_structure': self.auto_detect.get(),
            'extract_chords': self.auto_chords.get()
        }

        # Procesar archivos
        print("1.2 Procesando archivos...")
        results = self.file_processor.process_files_batch(
            [f['path'] for f in self.selected_files],
            options
        )
 
         # Guardar canciones encontradas como pendientes
        all_songs = []
        for idx, file_result in enumerate(results['file_results']):
            if file_result['success']:
                found = file_result.get('songs_found', [])
                if found:
                    all_songs.extend(found)
                else:
                    # Marcar archivo sin canciones
                    if idx < len(self.selected_files):
                        self.update_file_status(self.selected_files[idx]['name'], 'ℹ️ Sin canciones')
            else:
                if idx < len(self.selected_files):
                    self.update_file_status(self.selected_files[idx]['name'], '❌ Error')
        
        if all_songs:
            # Guardar en BD con estado "pendiente"
            for song in all_songs:
                song['estado'] = 'pendiente'  # Marcar como pendiente de revisión
                song['fuente'] = 'importacion_pdf'
            
            save_results = self.file_processor.save_songs_to_database(all_songs)
            
            # Después de guardar las canciones, cambiar el mensaje:
            if save_results['saved_songs'] > 0:
                if messagebox.askyesno("Procesamiento Completado", 
                                    f"Se importaron {save_results['saved_songs']} canciones (una por archivo). ¿Quieres revisarlas en el editor ahora?"):
                    self.app.show_editor()
        else:
            # Actualizar UI indicando que no se encontraron canciones
            self.progress_var.set(100)
            self.update_progress_label("ℹ️ No se encontraron canciones para procesar")
            messagebox.showinfo("Procesamiento Completado", "No se encontraron canciones para procesar")
        
        self.processing = False
    
        # Actualizar estado de archivos   
        #  # Enviar canciones encontradas al editor
        #  print("1.3 Guardando canciones encontradas...")
        #  songs_found = []
        #  for file_result in results['file_results']:
        #      if file_result['success'] and file_result.get('songs_found'):
        #          songs_found.extend(file_result['songs_found'])
 
        #  if songs_found:
        #      for song_data in songs_found:
        #          # Usar root.after para llamar a la UI desde el hilo principal
        #          self.app.root.after(0, self.app.show_editor, song_data)
        #  else:
        #      self.app.root.after(0, lambda: messagebox.showinfo("Procesamiento Completado", "No se encontraron canciones en los archivos procesados."))
 
        #  self.processing = False

    def create_config_panel(self):
        """Crear panel de configuración expandido"""
        config_frame = ttk.LabelFrame(self.main_frame,
                                    text="⚙️ Configuración de Importación",
                                    padding=15)
        config_frame.pack(fill=tk.X, pady=10)
        
        # Tipo de importación
        source_frame = ttk.Frame(config_frame)
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="Tipo de Origen:", style="Normal.TLabel").pack(side=tk.LEFT)
        
        #self.source_type = tk.StringVar(value="document")
        self.source_type = tk.StringVar(value="pdf")

        source_types = [
            ("📄 PDF (Una canción por archivo)", "pdf"),
            ("🖼️ Imágenes (OCR)", "image"), 
            ("📝 Texto Plano", "text")
        ]
        
        for i, (text, value) in enumerate(source_types):
            ttk.Radiobutton(source_frame, 
                          text=text, 
                          variable=self.source_type,
                          value=value,
                          command=self.on_source_change).pack(side=tk.LEFT, padx=15)
        
        # Opciones de procesamiento
        process_frame = ttk.Frame(config_frame)
        process_frame.pack(fill=tk.X, pady=10)
        
        self.auto_detect = tk.BooleanVar(value=True)
        ttk.Checkbutton(process_frame, 
                       text="Detección automática de estructura",
                       variable=self.auto_detect,
                       style="TCheckbutton").pack(side=tk.LEFT, padx=10)
        
        self.auto_chords = tk.BooleanVar(value=True)
        ttk.Checkbutton(process_frame,
                       text="Identificación automática de acordes",
                       variable=self.auto_chords,
                       style="TCheckbutton").pack(side=tk.LEFT, padx=10)
        
        self.auto_categories = tk.BooleanVar(value=True)
        ttk.Checkbutton(process_frame,
                       text="Sugerir categorías",
                       variable=self.auto_categories,
                       style="TCheckbutton").pack(side=tk.LEFT, padx=10)
        
        # Opciones específicas por tipo
        self.specific_options_frame = ttk.Frame(config_frame)
        self.specific_options_frame.pack(fill=tk.X, pady=5)
        self.update_specific_options()
        
    def on_source_change(self):
        """Actualizar opciones cuando cambia el tipo de origen"""
        self.update_specific_options()
        
    def update_specific_options(self):
        """Actualizar opciones específicas según el tipo seleccionado"""
        # Limpiar frame
        for widget in self.specific_options_frame.winfo_children():
            widget.destroy()
            
        source_type = self.source_type.get()
        
        if source_type == "image":
            # Opciones para OCR
            ttk.Label(self.specific_options_frame, 
                     text="Configuración OCR:", 
                     style="Small.TLabel").pack(side=tk.LEFT)
            
            self.ocr_quality = tk.StringVar(value="high")
            ttk.Radiobutton(self.specific_options_frame,
                          text="Alta calidad",
                          variable=self.ocr_quality,
                          value="high").pack(side=tk.LEFT, padx=10)
                          
            ttk.Radiobutton(self.specific_options_frame,
                          text="Rápido", 
                          variable=self.ocr_quality,
                          value="fast").pack(side=tk.LEFT, padx=10)
                          
        elif source_type == "web":
            # Opciones para web scraping
            web_frame = ttk.Frame(self.specific_options_frame)
            web_frame.pack(fill=tk.X)
            
            ttk.Label(web_frame, text="URLs (una por línea):", style="Small.TLabel").pack(anchor="w")
            
            self.url_text = tk.Text(web_frame, height=3, width=50)
            self.url_text.pack(fill=tk.X, pady=5)
            
            url_btn_frame = ttk.Frame(web_frame)
            url_btn_frame.pack(fill=tk.X)
            
            ttk.Button(url_btn_frame,
                      text="➕ Agregar URLs",
                      command=self.add_urls,
                      style="Info.TButton").pack(side=tk.LEFT, padx=2)
                      
            ttk.Button(url_btn_frame, 
                      text="🗑️ Limpiar URLs",
                      command=self.clear_urls,
                      style="Danger.TButton").pack(side=tk.LEFT, padx=2)
        
    def create_files_panel(self):
        """Crear panel de lista de archivos mejorado"""
        files_frame = ttk.LabelFrame(self.main_frame,
                                   text="📁 Archivos Seleccionados",
                                   padding=15)
        files_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Toolbar de archivos
        toolbar = ttk.Frame(files_frame)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, 
                  text="➕ Agregar Archivos",
                  command=self.add_files,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(toolbar,
                  text="➕ Agregar Carpeta", 
                  command=self.add_folder,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(toolbar,
                  text="🗑️ Limpiar Lista",
                  command=self.clear_files,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(toolbar,
                  text="👁️ Vista Previa",
                  command=self.preview_selected_file,
                  style="Info.TButton").pack(side=tk.RIGHT, padx=2)
        
        # Lista de archivos con más detalles
        columns = ('nombre', 'tipo', 'tamaño', 'ruta', 'estado')
        self.files_tree = ttk.Treeview(files_frame, 
                                     columns=columns, 
                                     show='headings',
                                     height=3)
        
        # Configurar columnas
        self.files_tree.heading('nombre', text='Nombre Archivo')
        self.files_tree.heading('tipo', text='Tipo')
        self.files_tree.heading('tamaño', text='Tamaño') 
        self.files_tree.heading('ruta', text='Ruta')
        self.files_tree.heading('estado', text='Estado')
        
        self.files_tree.column('nombre', width=200)
        self.files_tree.column('tipo', width=80)
        self.files_tree.column('tamaño', width=80)
        self.files_tree.column('ruta', width=250)
        self.files_tree.column('estado', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(files_frame, 
                                orient=tk.VERTICAL, 
                                command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=scrollbar.set)
        
        self.files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selección
        self.files_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
    def create_preview_panel(self):
        """Crear panel de vista previa"""
        self.preview_frame = ttk.LabelFrame(self.main_frame,
                                          text="👁️ Vista Previa",
                                          padding=15)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Área de vista previa
        self.preview_text = tk.Text(self.preview_frame, 
                                  height=7, 
                                  wrap=tk.WORD,
                                  font=('Courier', 10))
        
        preview_scrollbar = ttk.Scrollbar(self.preview_frame, 
                                        command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Estado inicial
        self.preview_text.insert(tk.END, "Selecciona un archivo para ver la vista previa...")
        self.preview_text.config(state=tk.DISABLED)
        
    def create_action_buttons(self):
        """Crear botones de acción mejorados"""
        action_frame = ttk.Frame(self.main_frame, style="TFrame")
        action_frame.pack(fill=tk.X, pady=10)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(action_frame, 
                                          variable=self.progress_var,
                                          maximum=100,
                                          style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Contador de progreso
        self.progress_label = ttk.Label(action_frame, 
                                      text="Listo para procesar",
                                      style="Secondary.TLabel")
        self.progress_label.pack(anchor="w")
        
        # Botones
        btn_frame = ttk.Frame(action_frame, style="TFrame")
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame,
                  text="🔄 Procesar Archivos",
                  command=self.start_processing,
                  style="Success.TButton").pack(side=tk.RIGHT, padx=5)
                  
        ttk.Button(btn_frame,
                  text="📤 Exportar Resultados", 
                  command=self.export_results,
                  style="Primary.TButton").pack(side=tk.RIGHT, padx=5)
                  
        ttk.Button(btn_frame,
                  text="❌ Cancelar",
                  command=self.cancel_import,
                  style="Danger.TButton").pack(side=tk.RIGHT, padx=5)
                  
    def add_files(self):
        """Agregar archivos a la lista"""
        file_types = self.get_file_types()
        
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos para importar",
            filetypes=file_types
        )
        
        self.add_files_to_list(files)
        
    def add_folder(self):
        """Agregar todos los archivos de una carpeta"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder:
            file_types = self.get_file_extensions()
            all_files = []
            
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in file_types):
                        all_files.append(os.path.join(root, file))
            
            self.add_files_to_list(all_files)
            
    def get_file_types(self):
        """Obtener tipos de archivo según fuente seleccionada"""
        source_type = self.source_type.get()
        
        if source_type == "document":
            return [("Documentos", "*.docx *.pdf"), ("Todos los archivos", "*.*")]
        elif source_type == "image":
            return [("Imágenes", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp"), ("Todos los archivos", "*.*")]
        elif source_type == "text":
            return [("Texto", "*.txt"), ("Todos los archivos", "*.*")]
        else:
            return [("Todos los archivos", "*.*")]
            
    def get_file_extensions(self):
        """Obtener extensiones de archivo"""
        source_type = self.source_type.get()
        
        if source_type == "document":
            return ['.docx', '.pdf']
        elif source_type == "image":
            return ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']
        elif source_type == "text":
            return ['.txt']
        else:
            return []
        
    def add_files_to_list(self, files):
        """Agregar lista de archivos al treeview"""
        for file_path in files:
            if any(f['path'] == file_path for f in self.selected_files):
                continue  # Evitar duplicados
                
            file_name = os.path.basename(file_path)
            file_type = self.get_file_type(file_path)
            file_size = self.get_file_size(file_path)
            file_folder = os.path.dirname(file_path)
            
            self.selected_files.append({
                'path': file_path,
                'name': file_name,
                'type': file_type,
                'size': file_size,
                'folder': file_folder,
                'status': 'Pendiente'
            })
            
            self.files_tree.insert('', tk.END, values=(
                file_name, file_type, file_size, file_folder, 'Pendiente'
            ))
            
        self.update_progress_label()
        
    def get_file_type(self, file_path):
        """Obtener tipo de archivo"""
        ext = os.path.splitext(file_path)[1].lower()
        type_map = {
            '.docx': 'Word',
            '.pdf': 'PDF', 
            '.jpg': 'Imagen', '.jpeg': 'Imagen', '.png': 'Imagen',
            '.tiff': 'Imagen', '.tif': 'Imagen', '.bmp': 'Imagen',
            '.txt': 'Texto'
        }
        return type_map.get(ext, 'Desconocido')
    
    def get_file_size(self, file_path):
        """Obtener tamaño de archivo legible"""
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "N/A"
    
    def clear_files(self):
        """Limpiar lista de archivos"""
        if self.selected_files:
            if messagebox.askyesno("Confirmar", "¿Estás seguro de limpiar la lista de archivos?"):
                self.selected_files.clear()
                for item in self.files_tree.get_children():
                    self.files_tree.delete(item)
                self.update_progress_label()
                self.clear_preview()
    
    def on_file_select(self, event):
        """Cuando se selecciona un archivo en la lista"""
        selection = self.files_tree.selection()
        if selection:
            item = selection[0]
            values = self.files_tree.item(item, 'values')
            file_name = values[0]
            
            # Encontrar archivo en la lista
            file_info = next((f for f in self.selected_files if f['name'] == file_name), None)
            if file_info:
                self.show_preview(file_info)
    
    def show_preview(self, file_info):
        """Mostrar vista previa del archivo"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        try:
            if file_info['type'] in ['Word', 'PDF', 'Imagen']:
                self.preview_text.insert(tk.END, f"📄 {file_info['name']}\n")
                self.preview_text.insert(tk.END, f"📁 {file_info['folder']}\n")
                self.preview_text.insert(tk.END, f"📊 {file_info['size']}\n")
                self.preview_text.insert(tk.END, f"🎵 Tipo: {file_info['type']}\n\n")
                self.preview_text.insert(tk.END, "Vista previa disponible después del procesamiento...")
            else:
                # Para archivos de texto, mostrar contenido
                with open(file_info['path'], 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Primeros 1000 caracteres
                    self.preview_text.insert(tk.END, content)
                    
        except Exception as e:
            self.preview_text.insert(tk.END, f"Error al cargar vista previa: {str(e)}")
            
        self.preview_text.config(state=tk.DISABLED)
    
    def clear_preview(self):
        """Limpiar vista previa"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "Selecciona un archivo para ver la vista previa...")
        self.preview_text.config(state=tk.DISABLED)
    
    def preview_selected_file(self):
        """Vista previa del archivo seleccionado"""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "No hay archivo seleccionado")
            return
            
        self.on_file_select(None)
    
    def add_urls(self):
        """Agregar URLs para web scraping"""
        # Placeholder - implementar diálogo para URLs
        messagebox.showinfo("URLs", "Funcionalidad de URLs en desarrollo")
    
    def clear_urls(self):
        """Limpiar URLs"""
        if hasattr(self, 'url_text'):
            self.url_text.delete(1.0, tk.END)
    
    def start_processing(self):
        """Iniciar procesamiento de archivos (sin threads)"""
        if not self.selected_files:
            messagebox.showwarning("Advertencia", "No hay archivos para procesar")
            return
            
        if self.processing:
            messagebox.showwarning("Advertencia", "Procesamiento ya en curso")
            return
            
        self.processing = True
        self.progress_var.set(0)
        self.update_progress_label()
        
        # Procesar directamente (sin thread)
        print ("===============================================================")
        print ("✅ Iniciando procesamiento directo de archivos...")
        print ("===============================================================")
        self.process_files_direct()

    def process_files_direct(self):
        """Procesar archivos directamente en el hilo principal"""
        try:
            total_files = len(self.selected_files)
            
            # Configurar opciones de procesamiento
            options = {
                'use_pdfplumber': True,
                'auto_detect_structure': self.auto_detect.get(),
                'extract_chords': self.auto_chords.get()
            }
            
            # Procesar cada archivo individualmente
            all_songs = []
            
            for i, file_info in enumerate(self.selected_files):
                file_path = file_info['path']
                
                # Actualizar progreso
                progress = (i / total_files) * 100
                self.progress_var.set(progress)
                self.update_progress_label(f"Procesando: {os.path.basename(file_path)} ({i+1}/{total_files})")
                
                # Procesar archivo individual
                file_result = self.file_processor._process_single_file(file_path, options)
                print ("===============================================================")
                print ("✅ ✅ Archivo procesado: ✅ ✅ ")
                print ("===============================================================")
                print(f"Resultado procesamiento {file_info['name']}: {file_result}")
                print ("===============================================================")
                                
                if file_result['success']:
                    songs_found = file_result.get('songs_found', [])
                    print(f"Canciones encontradas en {file_info['name']}: {len(songs_found)}")

                    if songs_found:
                        all_songs.extend(songs_found)
                        print(f"✅ Canciones agregadas de {file_info['name']}")

                        # Actualizar estado en treeview
                        self.update_file_status(file_info['name'], '✅ Completado')
                    else:
                        # No se encontraron canciones en este archivo
                        self.update_file_status(file_info['name'], 'ℹ️ Sin canciones')
                else:
                    self.update_file_status(file_info['name'], '❌ Error')
                    print(f"Error procesando {file_info['name']}: {file_result.get('error')}")
                
                # Pequeña pausa para que la UI se aktualice
                self.parent.update()
            
            # Guardar canciones encontradas
            if all_songs:
                # Preparar canciones
                for song in all_songs:
                    song['estado'] = 'pendiente'
                    song['fuente'] = 'importacion_pdf'
                
                # Guardar en BD y almacenar localmente
                print("Guardando canciones encontradas en la base de datos...")
                print(f"Número total de canciones a guardar: {len(all_songs)}")
                print(f"Primeras canciones: {all_songs[:3]}")  # Mostrar primeras 3 canciones para depuración
                print(f"contenido de la primera canción: {all_songs[0]}")  # Mostrar contenido de la primera canción
                
                save_results = self.file_processor.save_songs_to_database(all_songs)
                self.imported_songs = all_songs  # Guardar referencia local
                
                # Actualizar progreso
                self.progress_var.set(100)
                self.update_progress_label(f"✅ {len(all_songs)} canciones encontradas")
                
                if messagebox.askyesno("Procesamiento Completado", 
                                    f"Se encontraron {len(all_songs)} canciones. ¿Quieres revisarlas en el editor ahora?"):
                    # Primero mostrar el editor
                    self.app.show_editor()
                    # Luego intentar navegar con un pequeño delay
                    self.parent.after(100, lambda: self._navigate_to_editor(0))
            else:
                # Indicar que no se encontraron canciones para procesar
                self.progress_var.set(100)
                self.update_progress_label("ℹ️ No se encontraron canciones para procesar")
                messagebox.showinfo("Procesamiento Completado", "No se encontraron canciones para procesar")
            
            self.processing = False
        except Exception as e:
            self.processing = False
            messagebox.showerror("Error", f"Ocurrió un error durante el procesamiento: {e}")
            print(f"Error en process_files_direct: {e}")

    def _navigate_to_editor(self, retry_count=0):
        """Navegar al editor con las canciones importadas de forma segura"""
        MAX_RETRIES = 1  # Límite de reintentos
        try:
            if hasattr(self.app, 'editor') and self.app.editor:
                # Recargar categorías primero
                self.app.editor.load_categories()
                # Luego cargar las canciones importadas
                self.app.editor.load_imported_songs(self.imported_songs)
                print("✅ Navegación al editor completada")
            else:
                if retry_count < MAX_RETRIES:
                    print(f"⚠️ Editor no disponible, reintento {retry_count + 1}/{MAX_RETRIES}")
                    self.parent.after(500, lambda: self._navigate_to_editor(retry_count + 1))
                else:
                    print("❌ No se pudo acceder al editor después de varios intentos")
                    messagebox.showerror("Error", 
                        "No se pudo abrir el editor después de varios intentos.\n"
                        "Las canciones fueron guardadas y podrás acceder a ellas más tarde.")
        except Exception as e:
            print(f"❌ Error navegando al editor: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el editor: {e}")
        
    def update_file_status(self, file_name, status):
        """Actualizar estado de un archivo en el treeview"""
        for item in self.files_tree.get_children():
            values = self.files_tree.item(item, 'values')
            if values[0] == file_name:
                new_values = list(values)
                new_values[4] = status
                self.files_tree.item(item, values=new_values)
                break
    
    def update_progress_label(self, text=None):
        """Actualizar etiqueta de progreso"""
        if text is None:
            text = f"Archivos listos: {len(self.selected_files)}"
        self.progress_label.config(text=text)
    
    def export_results(self):
        """Exportar resultados del procesamiento"""
        if not any(f.get('status') == '✅ Completado' for f in self.selected_files):
            messagebox.showwarning("Advertencia", "No hay archivos procesados para exportar")
            return
            
        # Simular exportación
        messagebox.showinfo("Exportar", "Funcionalidad de exportación en desarrollo")



        """Cancelar importación y volver al dashboard"""    
    
    def cancel_import(self):
        if self.processing:
            if messagebox.askyesno("Confirmar", "¿Estás seguro de cancelar el procesamiento?"):
                self.processing = False
        self.app.show_dashboard()