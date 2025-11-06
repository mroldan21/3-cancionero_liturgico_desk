import os
import tempfile
import logging
from typing import Dict, List, Optional, Tuple
import threading
from datetime import datetime
import re

# Try to import PDF processing libraries
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("⚠️  PyPDF2 no instalado. Instala con: pip install PyPDF2")

try:
    import pdfplumber
    PDFPLUMBER_SUPPORT = True
except ImportError:
    PDFPLUMBER_SUPPORT = False
    print("⚠️  pdfplumber no instalado. Instala con: pip install pdfplumber")

try:
    import pytesseract
    from PIL import Image
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False
    print("⚠️  pytesseract/PIL no instalados. Instala con: pip install pytesseract pillow")

# Try to import python-docx for Word support
try:
    from docx import Document as DocxDocument
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False
    print("⚠️  python-docx no instalado. Instala con: pip install python-docx")

class FileProcessor:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.progress_callback = None
        
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
        
    def _update_progress(self, message, percent=None):
        """Update progress through callback"""
        if self.progress_callback:
            self.progress_callback(message, percent)
            
    def process_pdf_file(self, file_path: str, options: Dict = None) -> Dict:
        """
        Procesar archivo PDF y extraer contenido de canciones
        
        Args:
            file_path: Ruta al archivo PDF
            options: Opciones de procesamiento
            
        Returns:
            Dict con resultados del procesamiento
        """
        if not PDF_SUPPORT and not PDFPLUMBER_SUPPORT:
            return {
                'success': False,
                'error': 'Librerías PDF no disponibles. Instala PyPDF2 o pdfplumber'
            }
            
        options = options or {}
        self._update_progress(f"Procesando PDF: {os.path.basename(file_path)}", 10)
        
        try:
            # Determinar método de procesamiento
            use_pdfplumber = PDFPLUMBER_SUPPORT and options.get('use_pdfplumber', True)
            
            if use_pdfplumber and PDFPLUMBER_SUPPORT:
                return self._process_with_pdfplumber(file_path, options)
            elif PDF_SUPPORT:
                return self._process_with_pypdf2(file_path, options)
            else:
                return {
                    'success': False,
                    'error': 'No hay librerías PDF disponibles'
                }
                
        except Exception as e:
            self.logger.error(f"Error procesando PDF {file_path}: {e}")
            return {
                'success': False,
                'error': f'Error procesando PDF: {str(e)}'
            }
    
            
    # def _process_with_pdfplumber(self, file_path: str, options: Dict) -> Dict:
    #     """Procesar PDF usando pdfplumber (más avanzado)"""
    #     self._update_progress("Extrayendo texto con pdfplumber...", 30)
        
    #     songs_found = []
    #     total_pages = 0
    #     extracted_text = ""
        
    #     try:
    #         with pdfplumber.open(file_path) as pdf:
    #             total_pages = len(pdf.pages)
    #             self._update_progress(f"Analizando {total_pages} páginas...", 40)
                
    #             for page_num, page in enumerate(pdf.pages):
    #                 # Extraer texto
    #                 text = page.extract_text() or ""
    #                 extracted_text += f"\n--- Página {page_num + 1} ---\n{text}"
                    
    #                 # Progreso por página
    #                 progress = 40 + (page_num / total_pages) * 40
    #                 self._update_progress(f"Procesando página {page_num + 1}/{total_pages}", progress)
                    
    #                 # Si hay texto, intentar identificar canciones
    #                 if text.strip():
    #                     page_songs = self._analyze_text_for_songs(text, page_num + 1)
    #                     songs_found.extend(page_songs)
                        
    #     except Exception as e:
    #         self.logger.error(f"Error con pdfplumber: {e}")
    #         return {
    #             'success': False,
    #             'error': f'Error pdfplumber: {str(e)}'
    #         }
            
    #     return {
    #         'success': True,
    #         'file_type': 'pdf',
    #         'total_pages': total_pages,
    #         'songs_found': songs_found,
    #         'extracted_text': extracted_text,
    #         'processed_with': 'pdfplumber'
    #     }

    def _process_with_pdfplumber(self, file_path: str, options: Dict) -> Dict:
        """Procesar PDF como UNA sola canción por archivo"""
        self._update_progress("Extrayendo texto completo del PDF...", 30)
        print ("2. Extrayendo texto completo del PDF...")
        
        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                print (f"2.1 Extrayendo texto de {total_pages} páginas...")
                self._update_progress(f"Extrayendo texto de {total_pages} páginas...", 40)
                
                # Extraer TODO el texto como una sola canción, preservando espacios
                full_text = ""
                for page_num, page in enumerate(pdf.pages):
                    # Reconstruir texto preservando espacios aplicando gaps entre caracteres
                    page_text = self._reconstruct_text_from_page(page)
                    full_text += page_text + "\n"
                    
                    progress = 40 + (page_num / total_pages) * 40
                    self._update_progress(f"Página {page_num + 1}/{total_pages}", progress)
                    print (f"2.2 Página {page_num + 1}/{total_pages}")
                
                # Crear UNA sola canción con todo el contenido
                song = self._create_single_song_from_text(full_text, file_path)
                print ("2.3 Creado contenido de la canción: ", song)
                songs_found = [song] if song else []
                
        except Exception as e:
            self.logger.error(f"Error con pdfplumber: {e}")
            return {'success': False, 'error': f'Error pdfplumber: {str(e)}'}
            
        return {
            'success': True,
            'file_type': 'pdf',
            'total_pages': total_pages,
            'songs_found': songs_found,  # Solo UNA canción
            'extracted_text': full_text,
            'processed_with': 'pdfplumber'
        }

    def _reconstruct_text_from_page(self, page) -> str:
        """
        Reconstruir texto de una página usando page.chars para preservar
        espacios proporcionales. Agrupa caracteres por línea (y0) y calcula
        gaps entre caracteres para insertar espacios.
        """
        try:
            chars = page.chars
            if not chars:
                return page.extract_text() or ""

            # Agrupar por línea aproximando y0 (usar redondeo)
            lines_map = {}
            for ch in chars:
                # redondear y0 a 1 decimal para agrupar caracteres en la misma línea
                y_key = round(float(ch.get('top', ch.get('y0', 0))), 1)
                lines_map.setdefault(y_key, []).append(ch)

            # Ordenar líneas por coordenada vertical (de arriba hacia abajo)
            sorted_lines = [lines_map[k] for k in sorted(lines_map.keys(), reverse=False)]
            page_lines = []

            for line_chars in sorted_lines:
                # Ordenar caracteres por x0 (izquierda a derecha)
                line_chars_sorted = sorted(line_chars, key=lambda c: float(c.get('x0', 0)))
                # Calcular ancho medio de carácter para referencia (mediana robusta)
                widths = [float(c.get('x1', 0)) - float(c.get('x0', 0)) for c in line_chars_sorted if float(c.get('x1', 0)) - float(c.get('x0', 0)) > 0]
                if widths:
                    widths_sorted = sorted(widths)
                    m = len(widths_sorted) // 2
                    if len(widths_sorted) % 2 == 1:
                        avg_w = widths_sorted[m]
                    else:
                        avg_w = (widths_sorted[m - 1] + widths_sorted[m]) / 2.0
                    # evitar valores extremos
                    avg_w = max(2.0, min(avg_w, 40.0))
                else:
                    avg_w = 5.0

                # Construir la línea insertando espacios proporcionalmente al gap
                line_builder = ""
                prev_x1 = None
                for ch in line_chars_sorted:
                    x0 = float(ch.get('x0', 0))
                    x1 = float(ch.get('x1', 0))
                    txt = ch.get('text', '')

                    if prev_x1 is None:
                        # primer carácter, añadir texto directamente (respetando su texto, puede ser espacio)
                        line_builder += txt
                    else:
                        gap = x0 - prev_x1
                        # Si el propio carácter es un espacio real, respetarlo
                        if txt.isspace():
                            line_builder += txt
                        else:
                            # Umbrales más conservadores para reducir espacios (ajustados por tipografía)
                            # gap <= 0.12*avg_w -> sin espacio
                            # 0.12*avg_w < gap <= 0.35*avg_w -> 1 non-breaking space
                            # gap > 0.35*avg_w -> múltiplos reducidos de non-breaking spaces
                            if gap <= 0.12 * avg_w:
                                line_builder += txt
                            elif gap <= 0.35 * avg_w:
                                line_builder += "\u00A0" + txt
                            else:
                                # reducir la cantidad de espacios usando divisor mayor (1.8*avg_w)
                                spaces = max(1, int(gap / (1.8 * avg_w)))
                                line_builder += ("\u00A0" * spaces) + txt

                    prev_x1 = x1

                # Append the reconstructed line (preserve trailing spaces if any)
                page_lines.append(line_builder.rstrip("\n"))

            # Unir líneas con salto de línea
            return "\n".join(page_lines)
        except Exception as e:
            self.logger.error(f"Error reconstruyendo página: {e}")
            # Fallback al extract_text convencional
            return page.extract_text() or ""

    def _create_single_song_from_text(self, text: str, file_path: str) -> Dict:
        """Crear una sola canción desde el texto completo del PDF"""
        lines = text.split('\n')
        
        # Usar el nombre del archivo como título por defecto
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Buscar título real en las primeras líneas
        title = self._extract_title_from_text(lines, file_name)
        
        # Detectar formato de la canción
        if self._has_structured_format(text):
            # Formato estructurado: con [ACORDES] y [SECCIONES]
            all_chords = self._extract_chords_structured(text)
            formatted_lyrics = self._format_structured_lyrics(text)
        else:
            # Formato no estructurado: acordes en líneas separadas
            all_chords = self._extract_chords_unstructured(text)
            formatted_lyrics = self._format_unstructured_lyrics(text)
        
        probable_key = self._detect_probable_key(all_chords)
        
        return {
            'titulo': title,
            'artista': 'Desconocido',
            'letra': formatted_lyrics.strip(),
            'tono_original': probable_key,
            'acordes': ','.join(all_chords),
            'estado': 'pendiente',
            'categoria_id': 1,
            'notas': f"Importado desde PDF: {os.path.basename(file_path)}"
        }

    def _has_structured_format(self, text: str) -> bool:
        """Detectar si la canción usa formato estructurado con corchetes"""
        # Si encuentra patrones [ACORDE] o [SECCIÓN], es estructurado
        return bool(re.search(r'\[[A-G][#b]?\]|\[(VERSO|CORO|ESTRIBILLO)\]', text, re.IGNORECASE))

    def _extract_chords_structured(self, text: str) -> List[str]:
        """Extraer acordes de formato estructurado [Acorde]"""
        chords = re.findall(r'\[([A-G][#b]?[0-9]*(?:m|maj|min|dim|aug)?[0-9]*)\]', text, re.IGNORECASE)
        return list(set(chords))

    def _extract_chords_unstructured(self, text: str) -> List[str]:
        """Extraer acordes de formato no estructurado (líneas separadas)"""
        lines = text.split('\n')
        chords = []
        
        # Patrón para acordes musicales
        chord_pattern = r'\b([A-G][#b]?(?:m|maj|min|dim|aug)?[0-9]*)\b'
        
        for line in lines:
            line = line.strip()
            # Si la línea parece ser solo acordes (pocas palabras, muchos acordes)
            if (len(line.split()) <= 3 and 
                re.search(chord_pattern, line, re.IGNORECASE) and
                len(line) < 30):
                
                found_chords = re.findall(chord_pattern, line, re.IGNORECASE)
                chords.extend(found_chords)
        
        return list(set(chords))

    def _format_structured_lyrics(self, text: str) -> str:
        """Formatear letra en formato estructurado (ya está bien formateada)"""
        return text

    def _format_unstructured_lyrics(self, text: str) -> str:
        """Formatear letra en formato no estructurado para mejor visualización"""
        lines = text.split('\n')
        formatted_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            # Detectar si es línea de acordes
            if self._is_chord_line(line):
                chord_line = line
                lyric_line = ""
                
                # Buscar línea de letra siguiente
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if (next_line and 
                        not self._is_chord_line(next_line) and 
                        not self._is_section_line(next_line)):
                        lyric_line = next_line
                        i += 1  # Saltar la línea de letra ya que la procesamos
                
                # Formatear como línea estructurada
                formatted_line = self._combine_chords_and_lyrics(chord_line, lyric_line)
                formatted_lines.append(formatted_line)
                
            # Detectar secciones (líneas en mayúsculas o con patrones)
            elif self._is_section_line(line):
                formatted_lines.append(f"\n[{line}]")
                
            # Línea de letra normal
            else:
                formatted_lines.append(line)
                
            i += 1
        
        return '\n'.join(formatted_lines)

    def _is_chord_line(self, line: str) -> bool:
        """Determinar si una línea es principalmente acordes"""
        if not line.strip():
            return False
            
        # Contar acordes en la línea
        chord_pattern = r'\b([A-G][#b]?(?:m|maj|min|dim|aug)?[0-9]*)\b'
        chords = re.findall(chord_pattern, line, re.IGNORECASE)
        
        # Si tiene acordes y es una línea corta, probablemente es línea de acordes
        return (len(chords) > 0 and 
                len(line.split()) <= 4 and 
                len(line) < 50)

    def _is_section_line(self, line: str) -> bool:
        """Determinar si una línea es una sección (como estrofa, coro)"""
        line_upper = line.upper()
        section_indicators = [
            'VERSO', 'CORO', 'ESTRIBILLO', 'INTRO', 'OUTRO', 'PUENTE',
            'ESTROFA', 'CODA', 'FINAL'
        ]
        
        return (line_upper in section_indicators or
                any(indicator in line_upper for indicator in section_indicators))

    def _combine_chords_and_lyrics(self, chord_line: str, lyric_line: str) -> str:
        """Combinar línea de acordes con línea de letra en formato estructurado"""
        if not lyric_line:
            return chord_line  # Devolver solo los acordes si no hay letra
        
        # Extraer acordes de la línea
        chord_pattern = r'\b([A-G][#b]?(?:m|maj|min|dim|aug)?[0-9]*)\b'
        chords = re.findall(chord_pattern, chord_line, re.IGNORECASE)
        
        if not chords:
            return lyric_line
        
        # Posicionar acordes sobre la letra (simplificado)
        # En una implementación real, esto sería más sofisticado
        result = lyric_line
        for chord in chords:
            # Agregar acorde al inicio como [Acorde]
            result = f"[{chord}] {result}"
        
        return result

    # def _extract_title_from_text(self, lines: List[str], default_title: str) -> str:
    #     """Extraer título de las primeras líneas del texto"""
    #     for i, line in enumerate(lines[:5]):  # Buscar en primeras 5 líneas
    #         line = line.strip()
    #         if (len(line) > 3 and len(line) < 50 and 
    #             not self._is_song_section(line) and
    #             not self._contains_chords(line)):
    #             return line
    #     return default_title
  
    def _process_with_pypdf2(self, file_path: str, options: Dict) -> Dict:
        """Procesar PDF usando PyPDF2 (básico)"""
        self._update_progress("Extrayendo texto con PyPDF2...", 30)
        
        songs_found = []
        extracted_text = ""
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                self._update_progress(f"Analizando {total_pages} páginas...", 40)
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text() or ""
                    extracted_text += f"\n--- Página {page_num + 1} ---\n{text}"
                    
                    # Progreso por página
                    progress = 40 + (page_num / total_pages) * 40
                    self._update_progress(f"Procesando página {page_num + 1}/{total_pages}", progress)
                    
                    # Analizar texto en busca de canciones
                    if text.strip():
                        page_songs = self._analyze_text_for_songs(text, page_num + 1)
                        songs_found.extend(page_songs)
                        
        except Exception as e:
            self.logger.error(f"Error con PyPDF2: {e}")
            return {
                'success': False,
                'error': f'Error PyPDF2: {str(e)}'
            }
            
        return {
            'success': True,
            'file_type': 'pdf',
            'total_pages': total_pages,
            'songs_found': songs_found,
            'extracted_text': extracted_text,
            'processed_with': 'pypdf2'
        }
        
    # def _analyze_text_for_songs(self, text: str, page_num: int) -> List[Dict]:
    #     """
    #     Analizar texto extraído para identificar canciones
        
    #     Args:
    #         text: Texto a analizar
    #         page_num: Número de página
            
    #     Returns:
    #         Lista de canciones identificadas
    #     """
    #     songs = []
    #     lines = text.split('\n')
        
    #     # Patrones para identificar canciones
    #     current_song = None
    #     current_section = None
    #     content_lines = []
        
    #     for i, line in enumerate(lines):
    #         line = line.strip()
    #         if not line:
    #             continue
                
    #         # Detectar título de canción (líneas en mayúsculas o con patrones)
    #         if self._is_song_title(line, lines, i):
    #             # Guardar canción anterior si existe
    #             if current_song and content_lines:
    #                 current_song['content'] = '\n'.join(content_lines)
    #                 current_song = self._finalize_song(current_song)
    #                 if current_song:
    #                     songs.append(current_song)
                
    #             # Nueva canción
    #             current_song = {
    #                 'titulo': line,
    #                 'artista': 'Desconocido',
    #                 'letra': '',
    #                 'content_lines': [],
    #                 'page': page_num,
    #                 'line_start': i + 1,
    #                 'sections': [],
    #                 'acordes_detectados': []
    #             }
    #             content_lines = [line]
    #             current_section = 'INICIO'
                
    #         # Detectar secciones musicales
    #         elif self._is_song_section(line):
    #             if current_song:
    #                 section_name = self._extract_section_name(line)
    #                 current_song['sections'].append(section_name)
    #                 content_lines.append(f"\n[{section_name}]")
    #                 current_section = section_name
    #             else:
    #                 content_lines.append(line)
                    
    #         # Detectar acordes
    #         elif self._contains_chords(line):
    #             if current_song:
    #                 chords = self._extract_chords(line)
    #                 current_song['acordes_detectados'].extend(chords)
    #                 # Formatear línea con acordes
    #                 formatted_line = self._format_chord_line(line)
    #                 content_lines.append(formatted_line)
    #             else:
    #                 content_lines.append(line)
                    
    #         # Línea de letra normal
    #         else:
    #             content_lines.append(line)
                
    #     # Procesar última canción
    #     if current_song and content_lines:
    #         current_song['content'] = '\n'.join(content_lines)
    #         current_song = self._finalize_song(current_song)
    #         if current_song:
    #             songs.append(current_song)
                
    #     return songs
    
    def _analyze_text_for_songs(self, text: str, page_num: int) -> List[Dict]:
        """NO USAR - Cada PDF es una sola canción"""
        return []  # Retornar lista vacía, el procesamiento se hace en _create_single_song_from_text

    def _is_song_title(self, line: str, all_lines: List[str], current_index: int) -> bool:
        """Determinar si una línea es un título de canción"""
        # Líneas muy cortas probablemente no son títulos
        if len(line) < 3 or len(line) > 100:
            return False
            
        # Patrones que indican título
        title_indicators = [
            line.isupper(),  # Todo en mayúsculas
            any(keyword in line.lower() for keyword in [
                'canción', 'cancion', 'himno', 'salmo', 'coro', 'aleluya',
                'santo', 'gloria', 'padre', 'jesús', 'jesus', 'maría', 'maria'
            ]),
            # Línea seguida de espacio en blanco o sección
            current_index + 1 < len(all_lines) and 
            (not all_lines[current_index + 1].strip() or 
             self._is_song_section(all_lines[current_index + 1]))
        ]
        
        return any(title_indicators)
        
    def _is_song_section(self, line: str) -> bool:
        """Determinar si una línea es una sección musical"""
        section_indicators = [
            line.upper() in ['INTRO', 'VERSO', 'CORO', 'ESTRIBILLO', 'PUENTE', 'FINAL', 'CODA'],
            line.startswith('[') and line.endswith(']'),
            any(keyword in line.upper() for keyword in [
                'VERSO', 'CORO', 'ESTROFA', 'PUENTE', 'INTRODUCCIÓN'
            ])
        ]
        return any(section_indicators)
        
    def _extract_section_name(self, line: str) -> str:
        """Extraer nombre de sección de una línea"""
        if line.startswith('[') and line.endswith(']'):
            return line[1:-1].strip()
        return line.upper()
        
    def _contains_chords(self, line: str) -> bool:
        """Determinar si una línea contiene acordes"""
        # Patrón básico de acordes: [A], [Cm], [G7], etc.
        chord_patterns = [
            r'\[[A-G][#b]?[0-9]*(m|maj|min|dim|aug)?[0-9]*\]',
            r'\b[A-G][#b]?(m|maj|min|dim|aug)?[0-9]*\b'
        ]
        import re
        for pattern in chord_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
        
    def _extract_chords(self, line: str) -> List[str]:
        """Extraer acordes de una línea"""
        import re
        chords = []
        # Buscar acordes entre corchetes
        bracket_chords = re.findall(r'\[([A-G][#b]?[0-9]*(?:m|maj|min|dim|aug)?[0-9]*)\]', line, re.IGNORECASE)
        chords.extend(bracket_chords)
        
        # Buscar acordes sueltos
        loose_chords = re.findall(r'\b([A-G][#b]?(?:m|maj|min|dim|aug)?[0-9]*)\b', line, re.IGNORECASE)
        chords.extend(loose_chords)
        
        return list(set(chords))  # Remover duplicados
        
    def _format_chord_line(self, line: str) -> str:
        """Formatear línea con acordes para formato estándar"""
        import re
        # Convertir acordes sueltos a formato entre corchetes
        formatted = re.sub(
            r'\b([A-G][#b]?(?:m|maj|min|dim|aug)?[0-9]*)\b', 
            r'[\1]', 
            line
        )
        return formatted
        
    def _finalize_song(self, song_data: Dict) -> Optional[Dict]:
        """Finalizar y validar datos de canción"""
        if not song_data.get('titulo') or not song_data.get('content'):
            return None
            
        # Extraer acordes únicos
        all_chords = []
        for chord in song_data.get('acordes_detectados', []):
            if chord not in all_chords:
                all_chords.append(chord)
                
        # Determinar tonalidad probable
        probable_key = self._detect_probable_key(all_chords)
        
        return {
            'titulo': song_data['titulo'],
            'artista': song_data.get('artista', 'Desconocido'),
            'letra': song_data['content'],
            'tono_original': probable_key,
            'acordes': ','.join(all_chords),
            'pagina': song_data.get('page', 1),
            'secciones': song_data.get('sections', []),
            'estado': 'pendiente',
            'categoria_id': 1,  # Categoría por defecto
            'notas': f"Importado desde PDF. Página {song_data.get('page', 1)}"
        }
        
    def _detect_probable_key(self, chords: List[str]) -> str:
        """Detectar tonalidad probable basada en acordes"""
        if not chords:
            return 'C'
            
        # Conteo de acordes (simplificado)
        chord_count = {}
        for chord in chords:
            base_chord = chord[0]  # Solo la nota base
            chord_count[base_chord] = chord_count.get(base_chord, 0) + 1
            
        # Tonalidades más comunes en música cristiana
        common_keys = ['C', 'G', 'D', 'A', 'F']
        for key in common_keys:
            if key in chord_count:
                return key
                
        # Fallback al acorde más común
        if chord_count:
            return max(chord_count.items(), key=lambda x: x[1])[0]
            
        return 'C'
        
    def process_files_batch(self, file_paths: List[str], options: Dict = None) -> Dict:
        """
        Procesar múltiples archivos (versión simplificada sin threads)
        """
        options = options or {}
        results = {
            'total_files': len(file_paths),
            'processed_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'total_songs_found': 0,
            'file_results': []
        }
        
        for i, file_path in enumerate(file_paths):
            self._update_progress(f"Procesando archivo {i+1}/{len(file_paths)}", 
                                (i / len(file_paths)) * 100)
            
            # Procesar según tipo de archivo (pdf, docx, txt...)
            file_result = self._process_single_file(file_path, options)
            results['file_results'].append(file_result)
            results['processed_files'] += 1
            
            if file_result['success']:
                results['successful_files'] += 1
                results['total_songs_found'] += len(file_result.get('songs_found', []))
            else:
                results['failed_files'] += 1
                    
        self._update_progress("Procesamiento completado", 100)
        return results    
    def _process_single_file(self, file_path: str, options: Dict) -> Dict:
        """Procesar un solo archivo según su tipo"""
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.pdf':
            return self.process_pdf_file(file_path, options)
        elif file_ext in ('.docx', '.doc') and DOCX_SUPPORT:
            return self._process_docx_file(file_path, options)
        elif file_ext == '.txt':
            # Simple text file: read and create song
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                song = self._create_single_song_from_text(text, file_path)
                return {
                    'success': True,
                    'file_type': 'txt',
                    'total_pages': 1,
                    'songs_found': [song] if song else [],
                    'extracted_text': text,
                    'processed_with': 'txt'
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        else:
            return {
                'success': False,
                'error': f'Tipo de archivo no soportado o dependencia faltante: {file_ext}'
            }
    
    def save_songs_to_database(self, songs: List[Dict]) -> Dict:
        """
        Guardar canciones procesadas en la base de datos
        
        Args:
            songs: Lista de canciones a guardar
            
        Returns:
            Dict con resultados del guardado
        """
        results = {
            'total_songs': len(songs),
            'saved_songs': 0,
            'failed_songs': 0,
            'errors': []
        }
        
        for i, song in enumerate(songs):
            try:
                self._update_progress(f"Guardando canción {i+1}/{len(songs)}", 
                                    (i / len(songs)) * 100)
                
                # Preparar datos para la BD
                song_data = {
                    'titulo': song['titulo'],
                    'artista': song['artista'],
                    'letra': song['letra'],
                    'tono_original': song.get('tono_original', 'C'),
                    'bpm': song.get('bpm'),
                    'categoria_id': song.get('categoria_id', 1),
                    'estado': 'pendiente',
                    'notas': song.get('notas', 'Importado desde PDF')
                }
                
                # Guardar en BD
                result = self.db_manager.create_cancion(song_data)
                if result.get('success'):
                    results['saved_songs'] += 1
                else:
                    results['failed_songs'] += 1
                    results['errors'].append({
                        'song': song['titulo'],
                        'error': result.get('error', 'Error desconocido')
                    })
                    
            except Exception as e:
                results['failed_songs'] += 1
                results['errors'].append({
                    'song': song.get('titulo', 'Desconocido'),
                    'error': str(e)
                })
                
        self._update_progress("Guardado completado", 100)
        return results
    
    def _extract_title_from_text(self, lines: List[str], default_title: str) -> str:
        """Extraer título de las primeras líneas del texto"""
        
        # 1. Iterar sobre las primeras líneas (donde el título suele estar)
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if not line:
                continue
                
            # Saltarse líneas muy cortas o de un solo carácter que suelen ser acordes
            # o referencias de página no detectadas.
            if len(line) < 3:
                continue
                
            # Saltar líneas que son acordes (usando el método existente)
            # Esto debería filtrar "Lam", "rem", "SOL", "DO" en tu ejemplo.
            if self._is_chord_line(line):
                continue
                
            # Saltar líneas que son secciones (usando el método existente)
            if self._is_section_line(line):
                continue
                
            # Líneas entre 3 y 50 caracteres son candidatas a título
            if 3 <= len(line) <= 50:
                
                # 2. **PRIORIDAD MÁXIMA:** Si está entre comillas (formato explícito)
                if (line.startswith('"') and line.endswith('"')) or \
                (line.startswith('«') and line.endswith('»')) or \
                (line.startswith("'") and line.endswith("'")):
                    # Devuelve el título sin las comillas
                    return line[1:-1].strip()
                
                # 3. **ALTA PRIORIDAD:** Títulos en MAYÚSCULAS o con el formato de título habitual
                # - Si no contiene acordes
                # - Y tiene más de una palabra (para evitar acordes largos como "M17" o "MI7")
                # - O está completamente en MAYÚSCULAS (como "CARNAVALITO DEL MISIONERO")
                
                # El cambio clave es: ¡Permitir títulos en MAYÚSCULAS!
                
                # **Aseguramos que no sean acordes:**
                if not self._contains_chords(line):
                    
                    # **Si es un título completamente en MAYÚSCULAS y pasa el filtro de acordes, lo retornamos.**
                    if line.isupper():
                        return line
                    
                    # **Si es un título en formato normal (no todo mayúsculas), también lo retornamos.**
                    # Esta es tu condición original, pero ahora permite las mayúsculas antes.
                    if not line.isupper():
                        return line
                
        # 4. Si no se encuentra un título, retorna el valor por defecto
        print ("Titulo retornado: ", default_title)
        return default_title

    def _process_docx_file(self, file_path: str, options: Dict) -> Dict:
        """Procesar archivo Word (.docx) extrayendo párrafos como texto"""
        try:
            self._update_progress("Extrayendo texto desde Word...", 10)
            doc = DocxDocument(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text is not None]
            full_text = "\n".join(paragraphs)
            # Crear una "canción" única con el contenido
            song = self._create_single_song_from_text(full_text, file_path)
            return {
                'success': True,
                'file_type': 'docx',
                'total_pages': 1,
                'songs_found': [song] if song else [],
                'extracted_text': full_text,
                'processed_with': 'docx'
            }
        except Exception as e:
            self.logger.error(f"Error procesando DOCX {file_path}: {e}")
            return {'success': False, 'error': f'Error docx: {str(e)}'}