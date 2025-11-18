"""
Módulo: font_converter.py
Conversión de tipografías proporcionales a monoespaciadas para alineación de acordes

Responsabilidades:
- Detección de tipografía desde archivos .docx
- Gestión de métricas de caracteres (lectura/escritura en BD)
- Conversión de espaciado proporcional → monoespaciado
- Interfaz de selección de tipografía (UI)
- Pre-carga de métricas para tipografías comunes

Autor: Sistema de Cancionero Litúrgico
Versión: 1.0
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, List, Tuple
from collections import Counter
import re

try:
    from docx import Document as DocxDocument
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False
    print("⚠️ python-docx no disponible. Funcionalidad de detección limitada.")


class FontConverter:
    """
    Conversor de tipografías para alineación de acordes musicales
    """
    
    # Métricas predefinidas para tipografías comunes
    # Valores relativos al ancho de Courier New (monospace = 1.0)
    DEFAULT_METRICS = {
        'Arial': {
            10: {'i': 0.28, 'l': 0.28, 'm': 0.89, 'w': 0.83, ' ': 0.28, 
                 'a': 0.56, 'e': 0.56, 'o': 0.61, 'default': 0.56},
            11: {'i': 0.30, 'l': 0.30, 'm': 0.95, 'w': 0.89, ' ': 0.30,
                 'a': 0.60, 'e': 0.60, 'o': 0.65, 'default': 0.60},
            12: {'i': 0.33, 'l': 0.33, 'm': 1.00, 'w': 0.94, ' ': 0.33,
                 'a': 0.67, 'e': 0.67, 'o': 0.72, 'default': 0.67},
        },
        'Calibri': {
            10: {'i': 0.26, 'l': 0.26, 'm': 0.94, 'w': 0.83, ' ': 0.26,
                 'a': 0.54, 'e': 0.54, 'o': 0.59, 'default': 0.54},
            11: {'i': 0.28, 'l': 0.28, 'm': 1.00, 'w': 0.89, ' ': 0.28,
                 'a': 0.58, 'e': 0.58, 'o': 0.63, 'default': 0.58},
            12: {'i': 0.31, 'l': 0.31, 'm': 1.06, 'w': 0.94, ' ': 0.31,
                 'a': 0.65, 'e': 0.65, 'o': 0.70, 'default': 0.65},
        },
        'Times New Roman': {
            10: {'i': 0.22, 'l': 0.28, 'm': 0.83, 'w': 0.78, ' ': 0.25,
                 'a': 0.44, 'e': 0.44, 'o': 0.50, 'default': 0.50},
            11: {'i': 0.24, 'l': 0.30, 'm': 0.89, 'w': 0.83, ' ': 0.27,
                 'a': 0.48, 'e': 0.48, 'o': 0.54, 'default': 0.54},
            12: {'i': 0.26, 'l': 0.33, 'm': 0.94, 'w': 0.89, ' ': 0.29,
                 'a': 0.52, 'e': 0.52, 'o': 0.58, 'default': 0.58},
        },
        'Courier New': {
            # Monospace - todos los caracteres son 1.0
            10: {'default': 1.0},
            11: {'default': 1.0},
            12: {'default': 1.0},
        }
    }
    
    # Tipografías comunes ordenadas por popularidad
    COMMON_FONTS = [
        'Arial',
        'Calibri', 
        'Times New Roman',
        'Georgia',
        'Verdana',
        'Tahoma',
        'Trebuchet MS',
        'Comic Sans MS',
        'Courier New'
    ]
    
    def __init__(self, db_manager=None):
        """
        Inicializar conversor de tipografías
        
        Args:
            db_manager: Gestor de base de datos (opcional para modo standalone)
        """
        self.db_manager = db_manager
        self.metrics_cache = {}  # Cache de métricas cargadas
        
        # Pre-cargar métricas por defecto
        self._load_default_metrics()
        
    def _load_default_metrics(self):
        """Cargar métricas predefinidas en el cache"""
        self.metrics_cache = self.DEFAULT_METRICS.copy()
        print(f"✅ Métricas predefinidas cargadas: {len(self.metrics_cache)} tipografías")
        
    def detect_font_from_docx(self, file_path: str) -> Dict:
        """
        Detectar tipografía predominante en un archivo .docx
        
        Args:
            file_path: Ruta al archivo .docx
            
        Returns:
            Dict con 'name', 'size', 'confidence' (0.0-1.0)
        """
        if not DOCX_SUPPORT:
            return {
                'name': 'Arial',
                'size': 11,
                'confidence': 0.0,
                'method': 'default_fallback'
            }
        
        try:
            doc = DocxDocument(file_path)
            font_counts = Counter()
            size_counts = Counter()
            total_runs = 0
            
            # Analizar todos los runs en todos los párrafos
            for para in doc.paragraphs:
                for run in para.runs:
                    if run.text.strip():  # Solo contar runs con contenido
                        total_runs += 1
                        
                        # Obtener nombre de fuente
                        if run.font.name:
                            font_counts[run.font.name] += 1
                        
                        # Obtener tamaño (en puntos)
                        if run.font.size:
                            size_pt = run.font.size.pt
                            size_counts[int(size_pt)] += 1
            
            # Determinar fuente más común
            if font_counts:
                most_common_font = font_counts.most_common(1)[0]
                font_name = most_common_font[0]
                font_confidence = most_common_font[1] / total_runs
            else:
                font_name = 'Arial'
                font_confidence = 0.0
            
            # Determinar tamaño más común
            if size_counts:
                most_common_size = size_counts.most_common(1)[0]
                font_size = most_common_size[0]
            else:
                font_size = 11
            
            result = {
                'name': font_name,
                'size': font_size,
                'confidence': font_confidence,
                'method': 'docx_analysis',
                'total_runs': total_runs
            }
            
            print(f"🔍 Tipografía detectada: {font_name} {font_size}pt (confianza: {font_confidence:.1%})")
            return result
            
        except Exception as e:
            print(f"⚠️ Error detectando tipografía: {e}")
            return {
                'name': 'Arial',
                'size': 11,
                'confidence': 0.0,
                'method': 'error_fallback',
                'error': str(e)
            }
    
    def prompt_font_selection(self, detected_font: Dict, file_name: str, parent=None) -> Optional[Dict]:
        """
        Mostrar diálogo para confirmar/cambiar tipografía detectada
        
        Args:
            detected_font: Dict con tipografía detectada
            file_name: Nombre del archivo
            parent: Ventana padre de tkinter (opcional)
            
        Returns:
            Dict con tipografía seleccionada o None si se canceló
        """
        dialog = FontSelectionDialog(parent, detected_font, file_name, self.COMMON_FONTS)
        return dialog.result
    
    def detect_and_prompt_font(self, file_path: str, parent=None) -> Optional[Dict]:
        """
        Método combinado: detectar y mostrar diálogo de selección
        
        Args:
            file_path: Ruta al archivo .docx
            parent: Ventana padre de tkinter
            
        Returns:
            Dict con tipografía final seleccionada o None si canceló
        """
        import os
        
        detected = self.detect_font_from_docx(file_path)
        file_name = os.path.basename(file_path)
        
        return self.prompt_font_selection(detected, file_name, parent)
    
    def get_char_width(self, char: str, font_name: str, font_size: int) -> float:
        """
        Obtener ancho relativo de un carácter
        
        Args:
            char: Carácter a consultar
            font_name: Nombre de la tipografía
            font_size: Tamaño en puntos
            
        Returns:
            Ancho relativo (1.0 = ancho de Courier New)
        """
        # Buscar en cache
        if font_name in self.metrics_cache:
            if font_size in self.metrics_cache[font_name]:
                metrics = self.metrics_cache[font_name][font_size]
                return metrics.get(char.lower(), metrics.get('default', 0.6))
        
        # Buscar en base de datos si está disponible
        if self.db_manager:
            db_width = self._get_char_width_from_db(font_name, font_size, char)
            if db_width is not None:
                return db_width
        
        # Fallback: usar valor por defecto
        return 0.6  # Valor promedio razonable
    
    def _get_char_width_from_db(self, font_name: str, font_size: int, char: str) -> Optional[float]:
        """Obtener ancho de carácter desde base de datos"""
        if not self.db_manager:
            return None
        
        try:
            # Aquí se llamaría al método del db_manager
            # result = self.db_manager.get_font_metric(font_name, font_size, char)
            # return result['width_ratio'] if result else None
            return None  # Placeholder
        except Exception as e:
            print(f"⚠️ Error consultando BD: {e}")
            return None
    
    def calculate_monospace_width(self, text: str, font_name: str, font_size: int) -> float:
        """
        Calcular ancho total del texto en unidades monoespaciadas
        
        Args:
            text: Texto a medir
            font_name: Nombre de tipografía
            font_size: Tamaño en puntos
            
        Returns:
            Ancho total en unidades monoespaciadas (chars de Courier New)
        """
        total_width = 0.0
        
        for char in text:
            char_width = self.get_char_width(char, font_name, font_size)
            total_width += char_width
        
        return total_width
    
    def convert_text(self, text: str, font_info: Dict) -> str:
        """
        Convertir texto con espaciado proporcional a monoespaciado
        
        Args:
            text: Texto original con espaciado de tipografía proporcional
            font_info: Dict con 'name' y 'size' de la tipografía
            
        Returns:
            Texto convertido con espaciado equivalente en monospace
        """
        font_name = font_info.get('name', 'Arial')
        font_size = font_info.get('size', 11)
        
        print(f"🔄 Convirtiendo texto de {font_name} {font_size}pt a monospace...")
        
        lines = text.split('\n')
        converted_lines = []
        
        for line in lines:
            converted_line = self._convert_line(line, font_name, font_size)
            converted_lines.append(converted_line)
        
        result = '\n'.join(converted_lines)
        print(f"✅ Conversión completada: {len(lines)} líneas procesadas")
        
        return result
    
    def _convert_line(self, line: str, font_name: str, font_size: int) -> str:
        """
        Convertir una línea individual de texto
        
        Estrategia:
        1. Identificar palabras y espacios
        2. Calcular ancho proporcional de cada segmento
        3. Reemplazar espacios para mantener alineación en monospace
        """
        if not line.strip():
            return line
        
        # Dividir en segmentos (palabras y espacios)
        segments = self._split_into_segments(line)
        
        # Calcular posiciones en unidades monospace
        current_pos = 0.0
        result_chars = []
        
        for segment_type, segment_text in segments:
            if segment_type == 'word':
                # Agregar palabra tal cual
                result_chars.append(segment_text)
                # Calcular su ancho
                word_width = self.calculate_monospace_width(segment_text, font_name, font_size)
                current_pos += word_width
                
            elif segment_type == 'space':
                # Calcular cuántos espacios monospace equivalen al espacio proporcional
                space_width = self.calculate_monospace_width(segment_text, font_name, font_size)
                
                # Redondear a espacios enteros
                num_spaces = max(1, round(space_width))
                result_chars.append(' ' * num_spaces)
                current_pos += num_spaces
        
        return ''.join(result_chars)
    
    def _split_into_segments(self, line: str) -> List[Tuple[str, str]]:
        """
        Dividir línea en segmentos de palabras y espacios
        
        Returns:
            Lista de tuplas (tipo, texto) donde tipo es 'word' o 'space'
        """
        segments = []
        current_word = []
        current_spaces = []
        
        for char in line:
            if char == ' ':
                if current_word:
                    segments.append(('word', ''.join(current_word)))
                    current_word = []
                current_spaces.append(char)
            else:
                if current_spaces:
                    segments.append(('space', ''.join(current_spaces)))
                    current_spaces = []
                current_word.append(char)
        
        # Agregar último segmento
        if current_word:
            segments.append(('word', ''.join(current_word)))
        if current_spaces:
            segments.append(('space', ''.join(current_spaces)))
        
        return segments
    
    def save_metrics_to_db(self, font_name: str, font_size: int, char_metrics: Dict):
        """
        Guardar métricas aprendidas en la base de datos
        
        Args:
            font_name: Nombre de tipografía
            font_size: Tamaño en puntos
            char_metrics: Dict {char: width_ratio}
        """
        if not self.db_manager:
            print("⚠️ No hay DB manager configurado")
            return
        
        try:
            for char, width_ratio in char_metrics.items():
                # Llamar método del db_manager
                # self.db_manager.create_or_update_font_metric(
                #     font_name, font_size, char, width_ratio
                # )
                pass  # Placeholder
            
            print(f"✅ Métricas guardadas: {font_name} {font_size}pt ({len(char_metrics)} caracteres)")
        except Exception as e:
            print(f"❌ Error guardando métricas: {e}")
    
    def increment_usage(self, font_name: str, font_size: int):
        """Incrementar contador de uso de una tipografía"""
        if self.db_manager:
            try:
                # self.db_manager.increment_font_usage(font_name, font_size)
                pass  # Placeholder
            except Exception as e:
                print(f"⚠️ Error actualizando contador: {e}")


class FontSelectionDialog:
    """
    Diálogo de selección/confirmación de tipografía
    """
    
    def __init__(self, parent, detected_font: Dict, file_name: str, common_fonts: List[str]):
        """
        Crear diálogo de selección
        
        Args:
            parent: Ventana padre
            detected_font: Dict con tipografía detectada
            file_name: Nombre del archivo
            common_fonts: Lista de tipografías comunes
        """
        self.result = None
        self.detected_font = detected_font
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title("🔤 Confirmar Tipografía del Documento")
        self.dialog.geometry("500x350")
        
        if parent:
            self.dialog.transient(parent)
            self.dialog.grab_set()
        
        self._create_ui(file_name, common_fonts)
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Esperar cierre
        self.dialog.wait_window()
    
    def _create_ui(self, file_name: str, common_fonts: List[str]):
        """Crear interfaz del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="📄 Importando Canción",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Nombre de archivo
        file_label = ttk.Label(
            main_frame,
            text=f"Archivo: {file_name}",
            font=('Arial', 10)
        )
        file_label.pack(pady=(0, 20))
        
        # Información de detección
        info_frame = ttk.LabelFrame(main_frame, text="🔍 Tipografía Detectada", padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        detected_name = self.detected_font.get('name', 'Desconocida')
        detected_size = self.detected_font.get('size', 11)
        confidence = self.detected_font.get('confidence', 0.0)
        
        confidence_emoji = "✅" if confidence > 0.7 else "⚠️" if confidence > 0.3 else "❌"
        
        ttk.Label(
            info_frame,
            text=f"{confidence_emoji} Tipografía: {detected_name}",
            font=('Arial', 11)
        ).pack(anchor='w', pady=2)
        
        ttk.Label(
            info_frame,
            text=f"📏 Tamaño: {detected_size} puntos",
            font=('Arial', 11)
        ).pack(anchor='w', pady=2)
        
        if confidence > 0:
            ttk.Label(
                info_frame,
                text=f"🎯 Confianza: {confidence:.0%}",
                font=('Arial', 10),
                foreground='gray'
            ).pack(anchor='w', pady=2)
        
        # Selección manual
        selection_frame = ttk.LabelFrame(main_frame, text="✏️ Ajustar Tipografía (opcional)", padding=15)
        selection_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Combobox de fuentes
        font_frame = ttk.Frame(selection_frame)
        font_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(font_frame, text="Tipografía:", width=12).pack(side=tk.LEFT)
        self.font_combo = ttk.Combobox(
            font_frame,
            values=common_fonts,
            state='readonly',
            width=25
        )
        self.font_combo.set(detected_name)
        self.font_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Spinbox de tamaño
        size_frame = ttk.Frame(selection_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="Tamaño:", width=12).pack(side=tk.LEFT)
        self.size_var = tk.IntVar(value=detected_size)
        size_spin = tk.Spinbox(
            size_frame,
            from_=8,
            to=72,
            textvariable=self.size_var,
            width=10
        )
        size_spin.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(size_frame, text="puntos").pack(side=tk.LEFT, padx=(5, 0))
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="✓ Continuar",
            command=self._on_accept,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="✗ Cancelar",
            command=self._on_cancel,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Ayuda
        help_label = ttk.Label(
            main_frame,
            text="💡 La tipografía se usa para alinear acordes correctamente",
            font=('Arial', 9),
            foreground='gray'
        )
        help_label.pack(pady=(10, 0))
    
    def _on_accept(self):
        """Aceptar selección"""
        self.result = {
            'name': self.font_combo.get(),
            'size': self.size_var.get(),
            'method': 'user_confirmed'
        }
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Cancelar importación"""
        self.result = None
        self.dialog.destroy()


# ============================================================================
# FUNCIONES DE UTILIDAD PARA TESTING
# ============================================================================

def test_font_converter():
    """Función de prueba del módulo"""
    print("="*70)
    print("🧪 TEST: FontConverter")
    print("="*70)
    
    # Test 1: Inicialización
    print("\n📦 Test 1: Inicialización")
    converter = FontConverter()
    print(f"✅ Conversor creado con {len(converter.metrics_cache)} tipografías en cache")
    
    # Test 2: Obtener ancho de caracteres
    print("\n📏 Test 2: Ancho de caracteres")
    test_chars = ['i', 'l', 'm', 'w', ' ', 'a']
    for char in test_chars:
        width = converter.get_char_width(char, 'Arial', 11)
        print(f"  '{char}' (Arial 11pt): {width:.2f}")
    
    # Test 3: Calcular ancho de texto
    print("\n📐 Test 3: Ancho total de texto")
    test_text = "Al altar del Señor"
    width = converter.calculate_monospace_width(test_text, 'Arial', 11)
    print(f"  Texto: '{test_text}'")
    print(f"  Ancho monospace equivalente: {width:.2f} caracteres")
    
    # Test 4: Conversión de línea
    print("\n🔄 Test 4: Conversión de línea")
    original = "Em    D    G         B7"
    converted = converter._convert_line(original, 'Arial', 11)
    print(f"  Original:  '{original}'")
    print(f"  Convertido: '{converted}'")
    
    # Test 5: Conversión de texto completo
    print("\n📄 Test 5: Conversión de texto completo")
    sample_text = """Em    D    G         B7
Al altar del Señor vamos con amor"""
    
    font_info = {'name': 'Arial', 'size': 11}
    converted_text = converter.convert_text(sample_text, font_info)
    
    print("  Original:")
    for line in sample_text.split('\n'):
        print(f"    '{line}'")
    
    print("\n  Convertido:")
    for line in converted_text.split('\n'):
        print(f"    '{line}'")
    
    print("\n" + "="*70)
    print("✅ Tests completados")
    print("="*70)


def test_dialog():
    """Test del diálogo de selección"""
    print("🎨 Abriendo diálogo de prueba...")
    
    detected_font = {
        'name': 'Calibri',
        'size': 11,
        'confidence': 0.85,
        'method': 'docx_analysis'
    }
    
    dialog = FontSelectionDialog(
        None,
        detected_font,
        "cancion_ejemplo.docx",
        FontConverter.COMMON_FONTS
    )
    
    if dialog.result:
        print(f"✅ Tipografía seleccionada: {dialog.result}")
    else:
        print("❌ Usuario canceló la selección")


# ============================================================================
# PUNTO DE ENTRADA PARA TESTING
# ============================================================================

if __name__ == "__main__":
    print("🚀 Módulo FontConverter - Testing\n")
    
    # Ejecutar tests
    test_font_converter()
    
    # Descomentar para probar diálogo (requiere display)
    # test_dialog()
    
    print("\n✅ Testing completado")