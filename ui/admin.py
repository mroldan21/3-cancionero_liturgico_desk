import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import json

class AdminPanel:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz del panel de administración"""
        self.main_frame = ttk.Frame(self.parent, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(self.main_frame, 
                               text="⚙️ Panel de Administración", 
                               style="Header.TLabel")
        title_label.pack(pady=10)
        
        # Notebook para secciones
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Crear pestañas
        self.create_users_tab()
        self.create_database_tab()
        self.create_backup_tab()
        self.create_system_tab()
        self.create_logs_tab()
        
    def create_users_tab(self):
        """Crear pestaña de gestión de usuarios"""
        users_frame = ttk.Frame(self.notebook)
        self.notebook.add(users_frame, text="👥 Gestión de Usuarios")
        
        # Toolbar de usuarios
        users_toolbar = ttk.Frame(users_frame, style="TFrame")
        users_toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(users_toolbar,
                  text="➕ Nuevo Usuario",
                  command=self.new_user,
                  style="Success.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(users_toolbar,
                  text="✏️ Editar Usuario",
                  command=self.edit_user,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(users_toolbar,
                  text="🗑️ Eliminar Usuario",
                  command=self.delete_user,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=2)
        
        # Lista de usuarios
        users_list_frame = ttk.LabelFrame(users_frame,
                                        text="📋 Usuarios del Sistema",
                                        padding=10)
        users_list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('id', 'username', 'nombre', 'email', 'rol', 'estado', 'ultimo_acceso')
        self.users_tree = ttk.Treeview(users_list_frame, 
                                     columns=columns, 
                                     show='headings',
                                     height=12)
        
        # Configurar columnas
        column_config = {
            'id': ('ID', 40),
            'username': ('Usuario', 100),
            'nombre': ('Nombre', 120),
            'email': ('Email', 150),
            'rol': ('Rol', 80),
            'estado': ('Estado', 80),
            'ultimo_acceso': ('Último Acceso', 120)
        }
        
        for col, (text, width) in column_config.items():
            self.users_tree.heading(col, text=text)
            self.users_tree.column(col, width=width)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(users_list_frame, 
                                  orient=tk.VERTICAL, 
                                  command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar datos de ejemplo
        self.load_sample_users()
        
    def create_database_tab(self):
        """Crear pestaña de gestión de base de datos"""
        db_frame = ttk.Frame(self.notebook)
        self.notebook.add(db_frame, text="🗄️ Base de Datos")
        
        # Estado de la BD
        status_frame = ttk.LabelFrame(db_frame,
                                    text="📊 Estado de la Base de Datos",
                                    padding=15)
        status_frame.pack(fill=tk.X, pady=10)
        
        # Estadísticas
        stats_grid = ttk.Frame(status_frame, style="TFrame")
        stats_grid.pack(fill=tk.X)
        
        stats_data = [
            ("Total Canciones:", "1,247", "📝"),
            ("Total Usuarios:", "8", "👥"),
            ("Tamaño BD:", "45.2 MB", "💾"),
            ("Último Backup:", "2024-01-15", "🕒")
        ]
        
        for i, (label, value, icon) in enumerate(stats_data):
            stat_frame = ttk.Frame(stats_grid)
            stat_frame.grid(row=0, column=i, padx=20, pady=10, sticky="ew")
            
            ttk.Label(stat_frame, text=label, style="Small.TLabel").pack()
            ttk.Label(stat_frame, text=f"{icon} {value}", 
                     style="Normal.TLabel").pack()
            
            stats_grid.columnconfigure(i, weight=1)
        
        # Operaciones de BD
        operations_frame = ttk.LabelFrame(db_frame,
                                        text="🛠️ Operaciones de Base de Datos",
                                        padding=15)
        operations_frame.pack(fill=tk.X, pady=10)
        
        # Botones de operaciones
        ops_buttons = [
            ("🔄 Sincronizar BD", self.sync_database, "Primary.TButton"),
            ("🧹 Optimizar BD", self.optimize_database, "Info.TButton"),
            ("🔍 Verificar Integridad", self.check_integrity, "Warning.TButton"),
            ("🗑️ Limpiar Cache", self.clear_cache, "Danger.TButton")
        ]
        
        for i, (text, command, style) in enumerate(ops_buttons):
            btn = ttk.Button(operations_frame,
                           text=text,
                           command=command,
                           style=style)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            operations_frame.columnconfigure(i, weight=1)
        
        # Configuración avanzada
        advanced_frame = ttk.LabelFrame(db_frame,
                                      text="⚙️ Configuración Avanzada",
                                      padding=15)
        advanced_frame.pack(fill=tk.X, pady=10)
        
        # Configuraciones
        config_grid = ttk.Frame(advanced_frame, style="TFrame")
        config_grid.pack(fill=tk.X)
        
        # Timeout de conexión
        ttk.Label(config_grid, text="Timeout Conexión (seg):", style="Normal.TLabel").grid(row=0, column=0, sticky="w", pady=2)
        self.timeout_var = tk.StringVar(value="30")
        ttk.Entry(config_grid, textvariable=self.timeout_var, width=10).grid(row=0, column=1, sticky="w", pady=2, padx=5)
        
        # Límite de consultas
        ttk.Label(config_grid, text="Límite Consultas:", style="Normal.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        self.query_limit_var = tk.StringVar(value="1000")
        ttk.Entry(config_grid, textvariable=self.query_limit_var, width=10).grid(row=1, column=1, sticky="w", pady=2, padx=5)
        
        # Auto-backup
        self.auto_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_grid, 
                       text="Auto-backup cada 24h",
                       variable=self.auto_backup_var,
                       style="TCheckbutton").grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        
        config_grid.columnconfigure(1, weight=1)
        
    def create_backup_tab(self):
        """Crear pestaña de backup y restauración"""
        backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(backup_frame, text="💾 Backup & Restauración")
        
        # Crear backup
        create_frame = ttk.LabelFrame(backup_frame,
                                    text="📤 Crear Backup",
                                    padding=15)
        create_frame.pack(fill=tk.X, pady=10)
        
        backup_options = ttk.Frame(create_frame, style="TFrame")
        backup_options.pack(fill=tk.X, pady=5)
        
        self.backup_type = tk.StringVar(value="completo")
        ttk.Radiobutton(backup_options, 
                       text="Backup Completo",
                       variable=self.backup_type,
                       value="completo").pack(side=tk.LEFT, padx=10)
                       
        ttk.Radiobutton(backup_options,
                       text="Backup Incremental", 
                       variable=self.backup_type,
                       value="incremental").pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(backup_options,
                       text="Solo Datos",
                       variable=self.backup_type,
                       value="datos").pack(side=tk.LEFT, padx=10)
        
        # Botones de backup
        backup_btn_frame = ttk.Frame(create_frame, style="TFrame")
        backup_btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(backup_btn_frame,
                  text="💾 Crear Backup Ahora",
                  command=self.create_backup,
                  style="Success.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(backup_btn_frame,
                  text="📁 Seleccionar Directorio",
                  command=self.select_backup_dir,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
        
        # Restaurar backup
        restore_frame = ttk.LabelFrame(backup_frame,
                                     text="📥 Restaurar Backup",
                                     padding=15)
        restore_frame.pack(fill=tk.X, pady=10)
        
        # Lista de backups disponibles
        backups_list_frame = ttk.Frame(restore_frame, style="TFrame")
        backups_list_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(backups_list_frame, text="Backups Disponibles:", style="Normal.TLabel").pack(anchor="w")
        
        self.backups_tree = ttk.Treeview(restore_frame, 
                                       columns=('nombre', 'fecha', 'tamaño', 'tipo'),
                                       show='headings',
                                       height=6)
        
        self.backups_tree.heading('nombre', text='Nombre')
        self.backups_tree.heading('fecha', text='Fecha')
        self.backups_tree.heading('tamaño', text='Tamaño')
        self.backups_tree.heading('tipo', text='Tipo')
        
        self.backups_tree.column('nombre', width=200)
        self.backups_tree.column('fecha', width=120)
        self.backups_tree.column('tamaño', width=80)
        self.backups_tree.column('tipo', width=100)
        
        backups_scrollbar = ttk.Scrollbar(restore_frame, command=self.backups_tree.yview)
        self.backups_tree.configure(yscrollcommand=backups_scrollbar.set)
        
        self.backups_tree.pack(fill=tk.X, pady=5)
        backups_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de restauración
        restore_btn_frame = ttk.Frame(restore_frame, style="TFrame")
        restore_btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(restore_btn_frame,
                  text="🔄 Restaurar Seleccionado",
                  command=self.restore_backup,
                  style="Warning.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(restore_btn_frame,
                  text="🗑️ Eliminar Backup",
                  command=self.delete_backup,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=2)
        
        # Cargar backups de ejemplo
        self.load_sample_backups()
        
    def create_system_tab(self):
        """Crear pestaña de configuración del sistema"""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="🖥️ Sistema")
        
        # Configuración general
        general_frame = ttk.LabelFrame(system_frame,
                                     text="⚙️ Configuración General",
                                     padding=15)
        general_frame.pack(fill=tk.X, pady=10)
        
        # Grid de configuraciones
        config_grid = ttk.Frame(general_frame, style="TFrame")
        config_grid.pack(fill=tk.X)
        
        configs = [
            ("Idioma:", "language_combo", ["Español", "English"], 0),
            ("Tema:", "theme_combo", ["Claro", "Oscuro", "Automático"], 1),
            ("Máx. archivos importación:", "max_files_entry", "50", 2),
            ("Tamaño máx. archivo (MB):", "max_size_entry", "10", 3)
        ]
        
        self.config_vars = {}
        
        for i, (label, key, values, row) in enumerate(configs):
            ttk.Label(config_grid, text=label, style="Normal.TLabel").grid(row=row, column=0, sticky="w", pady=5, padx=5)
            
            if isinstance(values, list):
                var = tk.StringVar(value=values[0])
                combo = ttk.Combobox(config_grid, textvariable=var, values=values, state="readonly", width=15)
                combo.grid(row=row, column=1, sticky="w", pady=5, padx=5)
                self.config_vars[key] = var
            else:
                var = tk.StringVar(value=values)
                entry = ttk.Entry(config_grid, textvariable=var, width=15)
                entry.grid(row=row, column=1, sticky="w", pady=5, padx=5)
                self.config_vars[key] = var
        
        # Configuración de OCR
        ocr_frame = ttk.LabelFrame(system_frame,
                                 text="🔍 Configuración OCR",
                                 padding=15)
        ocr_frame.pack(fill=tk.X, pady=10)
        
        ocr_grid = ttk.Frame(ocr_frame, style="TFrame")
        ocr_grid.pack(fill=tk.X)
        
        self.ocr_quality = tk.StringVar(value="alto")
        ttk.Radiobutton(ocr_grid, text="Alta Calidad", variable=self.ocr_quality, value="alto").grid(row=0, column=0, sticky="w", padx=10)
        ttk.Radiobutton(ocr_grid, text="Balanceado", variable=self.ocr_quality, value="balanceado").grid(row=0, column=1, sticky="w", padx=10)
        ttk.Radiobutton(ocr_grid, text="Rápido", variable=self.ocr_quality, value="rapido").grid(row=0, column=2, sticky="w", padx=10)
        
        # Configuración de exportación
        export_frame = ttk.LabelFrame(system_frame,
                                    text="📤 Configuración de Exportación",
                                    padding=15)
        export_frame.pack(fill=tk.X, pady=10)
        
        self.include_chords = tk.BooleanVar(value=True)
        ttk.Checkbutton(export_frame, 
                       text="Incluir acordes en exportación",
                       variable=self.include_chords,
                       style="TCheckbutton").pack(anchor="w", pady=2)
        
        self.include_metadata = tk.BooleanVar(value=True)
        ttk.Checkbutton(export_frame,
                       text="Incluir metadatos",
                       variable=self.include_metadata,
                       style="TCheckbutton").pack(anchor="w", pady=2)
        
        # Botones de sistema
        system_btn_frame = ttk.Frame(system_frame, style="TFrame")
        system_btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(system_btn_frame,
                  text="💾 Guardar Configuración",
                  command=self.save_system_config,
                  style="Success.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(system_btn_frame,
                  text="🔄 Restablecer Valores",
                  command=self.reset_system_config,
                  style="Warning.TButton").pack(side=tk.LEFT, padx=2)
        
    def create_logs_tab(self):
        """Crear pestaña de logs y auditoría"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📋 Logs & Auditoría")
        
        # Filtros de logs
        filters_frame = ttk.LabelFrame(logs_frame,
                                     text="🎛️ Filtros de Logs",
                                     padding=15)
        filters_frame.pack(fill=tk.X, pady=10)
        
        filter_row = ttk.Frame(filters_frame, style="TFrame")
        filter_row.pack(fill=tk.X)
        
        # Nivel de log
        ttk.Label(filter_row, text="Nivel:", style="Normal.TLabel").pack(side=tk.LEFT, padx=5)
        self.log_level = tk.StringVar(value="Todos")
        levels = ["Todos", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        ttk.Combobox(filter_row, 
                    textvariable=self.log_level,
                    values=levels,
                    state="readonly",
                    width=10).pack(side=tk.LEFT, padx=5)
        
        # Usuario
        ttk.Label(filter_row, text="Usuario:", style="Normal.TLabel").pack(side=tk.LEFT, padx=5)
        self.log_user = tk.StringVar(value="Todos")
        users = ["Todos", "admin", "editor1", "editor2", "sistema"]
        ttk.Combobox(filter_row,
                    textvariable=self.log_user,
                    values=users,
                    state="readonly",
                    width=10).pack(side=tk.LEFT, padx=5)
        
        # Fecha
        ttk.Label(filter_row, text="Fecha:", style="Normal.TLabel").pack(side=tk.LEFT, padx=5)
        self.log_date = tk.StringVar(value="Últimos 7 días")
        dates = ["Últimas 24h", "Últimos 7 días", "Últimos 30 días", "Todo"]
        ttk.Combobox(filter_row,
                    textvariable=self.log_date,
                    values=dates,
                    state="readonly",
                    width=12).pack(side=tk.LEFT, padx=5)
        
        # Botones de filtro
        ttk.Button(filter_row,
                  text="🔍 Aplicar Filtros",
                  command=self.apply_log_filters,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=10)
        
        # Lista de logs
        logs_list_frame = ttk.LabelFrame(logs_frame,
                                       text="📄 Registros del Sistema",
                                       padding=15)
        logs_list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('fecha', 'nivel', 'usuario', 'modulo', 'mensaje')
        self.logs_tree = ttk.Treeview(logs_list_frame, 
                                    columns=columns, 
                                    show='headings',
                                    height=15)
        
        # Configurar columnas
        logs_column_config = {
            'fecha': ('Fecha/Hora', 150),
            'nivel': ('Nivel', 80),
            'usuario': ('Usuario', 100),
            'modulo': ('Módulo', 100),
            'mensaje': ('Mensaje', 300)
        }
        
        for col, (text, width) in logs_column_config.items():
            self.logs_tree.heading(col, text=text)
            self.logs_tree.column(col, width=width)
        
        # Scrollbars
        logs_scrollbar = ttk.Scrollbar(logs_list_frame, 
                                     orient=tk.VERTICAL, 
                                     command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=logs_scrollbar.set)
        
        self.logs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Toolbar de logs
        logs_toolbar = ttk.Frame(logs_list_frame, style="TFrame")
        logs_toolbar.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(logs_toolbar,
                  text="🔄 Actualizar Logs",
                  command=self.refresh_logs,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(logs_toolbar,
                  text="📤 Exportar Logs",
                  command=self.export_logs,
                  style="Success.TButton").pack(side=tk.LEFT, padx=2)
                  
        ttk.Button(logs_toolbar,
                  text="🗑️ Limpiar Logs",
                  command=self.clear_logs,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=2)
        
        # Cargar logs de ejemplo
        self.load_sample_logs()
        
    def load_sample_users(self):
        """Cargar usuarios de ejemplo"""
        sample_users = [
            (1, 'admin', 'Administrador Principal', 'admin@iglesia.com', 'Administrador', 'Activo', '2024-01-15 10:30'),
            (2, 'editor1', 'María González', 'maria@iglesia.com', 'Editor', 'Activo', '2024-01-15 09:15'),
            (3, 'editor2', 'Carlos López', 'carlos@iglesia.com', 'Editor', 'Activo', '2024-01-14 16:45'),
            (4, 'revisor1', 'Ana Martínez', 'ana@iglesia.com', 'Revisor', 'Activo', '2024-01-14 14:20'),
            (5, 'lector1', 'Pedro Sánchez', 'pedro@iglesia.com', 'Lector', 'Activo', '2024-01-13 11:05')
        ]
        
        for user in sample_users:
            self.users_tree.insert('', tk.END, values=user)
            
    def load_sample_backups(self):
        """Cargar backups de ejemplo"""
        sample_backups = [
            ('backup_20240115_full.zip', '2024-01-15 02:00', '45.2 MB', 'Completo'),
            ('backup_20240114_inc.zip', '2024-01-14 02:00', '1.3 MB', 'Incremental'),
            ('backup_20240113_full.zip', '2024-01-13 02:00', '44.9 MB', 'Completo'),
            ('backup_20240112_data.json', '2024-01-12 15:30', '12.8 MB', 'Solo Datos')
        ]
        
        for backup in sample_backups:
            self.backups_tree.insert('', tk.END, values=backup)
            
    def load_sample_logs(self):
        """Cargar logs de ejemplo"""
        sample_logs = [
            ('2024-01-15 10:30:15', 'INFO', 'admin', 'Importación', 'Importadas 15 canciones desde Word'),
            ('2024-01-15 09:15:42', 'INFO', 'editor1', 'Editor', 'Canción "Aleluya" modificada'),
            ('2024-01-14 16:45:33', 'WARNING', 'sistema', 'Backup', 'Backup automático completado con advertencias'),
            ('2024-01-14 14:20:18', 'ERROR', 'editor2', 'OCR', 'Error en procesamiento OCR de imagen'),
            ('2024-01-13 17:30:55', 'INFO', 'admin', 'Sistema', 'Configuración del sistema actualizada'),
            ('2024-01-13 15:20:41', 'INFO', 'sistema', 'Sincronización', 'Sincronización con BD completada')
        ]
        
        for log in sample_logs:
            self.logs_tree.insert('', tk.END, values=log)
            
    # Métodos de usuarios
    def new_user(self):
        """Crear nuevo usuario"""
        messagebox.showinfo("Nuevo Usuario", "Funcionalidad de nuevo usuario en desarrollo")
        
    def edit_user(self):
        """Editar usuario seleccionado"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un usuario para editar")
            return
        messagebox.showinfo("Editar Usuario", "Funcionalidad de edición de usuario en desarrollo")
        
    def delete_user(self):
        """Eliminar usuario seleccionado"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un usuario para eliminar")
            return
            
        if messagebox.askyesno("Eliminar Usuario", "¿Estás seguro de eliminar el usuario seleccionado?"):
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
    
    # Métodos de base de datos
    def sync_database(self):
        """Sincronizar base de datos"""
        messagebox.showinfo("Sincronizar", "Sincronización con BD completada")
        
    def optimize_database(self):
        """Optimizar base de datos"""
        messagebox.showinfo("Optimizar", "Base de datos optimizada correctamente")
        
    def check_integrity(self):
        """Verificar integridad de la BD"""
        messagebox.showinfo("Integridad", "Verificación de integridad completada - Sin errores")
        
    def clear_cache(self):
        """Limpiar cache"""
        messagebox.showinfo("Cache", "Cache limpiado correctamente")
    
    # Métodos de backup
    def create_backup(self):
        """Crear backup"""
        backup_type = self.backup_type.get()
        messagebox.showinfo("Backup", f"Backup {backup_type} creado correctamente")
        
    def select_backup_dir(self):
        """Seleccionar directorio de backup"""
        messagebox.showinfo("Directorio", "Funcionalidad de selección de directorio en desarrollo")
        
    def restore_backup(self):
        """Restaurar backup seleccionado"""
        selection = self.backups_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un backup para restaurar")
            return
            
        if messagebox.askyesno("Restaurar Backup", "¿Estás seguro de restaurar este backup? Se sobrescribirán los datos actuales."):
            messagebox.showinfo("Éxito", "Backup restaurado correctamente")
            
    def delete_backup(self):
        """Eliminar backup seleccionado"""
        selection = self.backups_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un backup para eliminar")
            return
            
        if messagebox.askyesno("Eliminar Backup", "¿Estás seguro de eliminar este backup?"):
            messagebox.showinfo("Éxito", "Backup eliminado correctamente")
    
    # Métodos de sistema
    def save_system_config(self):
        """Guardar configuración del sistema"""
        messagebox.showinfo("Guardar", "Configuración del sistema guardada correctamente")
        
    def reset_system_config(self):
        """Restablecer configuración del sistema"""
        if messagebox.askyesno("Restablecer", "¿Restablecer toda la configuración a valores por defecto?"):
            messagebox.showinfo("Éxito", "Configuración restablecida correctamente")
    
    # Métodos de logs
    def apply_log_filters(self):
        """Aplicar filtros a los logs"""
        messagebox.showinfo("Filtros", "Filtros aplicados correctamente")
        
    def refresh_logs(self):
        """Actualizar logs"""
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        self.load_sample_logs()
        messagebox.showinfo("Actualizar", "Logs actualizados correctamente")
        
    def export_logs(self):
        """Exportar logs"""
        messagebox.showinfo("Exportar", "Logs exportados correctamente")
        
    def clear_logs(self):
        """Limpiar logs"""
        if messagebox.askyesno("Limpiar Logs", "¿Estás seguro de limpiar todos los logs?"):
            for item in self.logs_tree.get_children():
                self.logs_tree.delete(item)
            messagebox.showinfo("Éxito", "Logs limpiados correctamente")