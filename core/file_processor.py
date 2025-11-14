# ==============================================================================
# PARTE 1: REEMPLAZAR LÍNEAS 1-120 (imports y constantes globales)
# ==============================================================================

import os
import tempfile
import logging
from typing import Dict, List, Optional, Tuple
import threading
from datetime import datetime
import re
import json

# ==============================================================================
# CONSTANTES GLOBALES - DEFINICIÓN ÚNICA Y CONSOLIDADA
# ==============================================================================

# Regex MEJORADO: Captura acordes americanos Y tradicionales
CHORD_TOKEN_RE = re.compile(
    r'''
    (?:                                    # Grupo no capturante
        (?:SOL|DO|RE|MI|FA|LA|SI)          # Acordes tradicionales (3 o 2 letras)
        (?:[#b♯♭])?                         # Alteración opcional
        (?:m|M|maj|min|dim|aug|sus|add)?   # Calidad opcional
        \d*                                # Números opcionales (7, 9, etc.)
        (?:/(?:SOL|DO|RE|MI|FA|LA|SI|[A-G])[#b]?)?  # Bajo opcional
    |                                      # O
        [A-G]                              # Acordes americanos (nota raíz)
        (?:[#b♯♭])?                        # Alteración opcional
        (?:m|M|maj|min|dim|aug|sus|add)?   # Calidad opcional
        \d*                                # Números opcionales
        (?:/[A-G][#b]?)?                   # Bajo opcional
    )
    ''',
    re.IGNORECASE | re.VERBOSE
)

# Mapeo completo (ordenado para greedy matching)
TRAD_TO_AMERICAN = {
    # 3 letras primero
    "SOL": "G", "SOLb": "Gb", "SOL#": "G#", "SOLm": "Gm",
    # 2 letras
    "DO": "C", "DOb": "Cb", "DO#": "C#", "DOm": "Cm",
    "RE": "D", "REb": "Db", "RE#": "D#", "REm": "Dm",
    "MI": "E", "MIb": "Eb", "MI#": "E#", "MIm": "Em",
    "FA": "F", "FAb": "Fb", "FA#": "F#", "FAm": "Fm",
    "LA": "A", "LAb": "Ab", "LA#": "A#", "LAm": "Am",
    "SI": "B", "SIb": "Bb", "SI#": "B#", "SIm": "Bm",
}

TRAD_ROOTS = ["SOL", "DO", "RE", "MI", "FA", "LA", "SI"]

# Regex de validación
ANGLO_CHORD_RE = re.compile(
    r'^[A-G](?:[#♯b♭]?)(?:m|M|maj|min|sus|dim|aug|add|\d+)?(?:.*)?$',
    re.IGNORECASE
)


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
    def __init__(self, db_manager=None, *args, **kwargs):        
        """
        db_manager opcional para facilitar testing. En producción pasá el manager real.
        """
        self.db_manager = db_manager
        self.logger = kwargs.get('logger') if 'logger' in kwargs else None
        #self.logger = logging.getLogger(__name__)
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
    
# ==============================================================================
# PARTE 2: FUNCIONES DE NORMALIZACIÓN ACTUALIZADAS (usar constantes globales)
# ==============================================================================

    def _normalize_traditional_to_american(self, chord: str) -> str:
        """
        Normalizar acordes tradicionales (DO, RE, MI...) a americana (C, D, E...)
        Preserva sufijos completos y capitalización correcta (Cm, C7, Cmaj7)
        """
        if not chord:
            return chord
        
        # NO convertir todo a mayúsculas aún, preservar case original
        chord = chord.strip()
        chord_upper = chord.upper()
        
        # 1. Intentar coincidencia exacta en el diccionario
        if chord_upper in TRAD_TO_AMERICAN:
            return TRAD_TO_AMERICAN[chord_upper]
        
        # 2. Buscar prefijos tradicionales (más largos primero: SOL antes que SI)
        for trad_root in TRAD_ROOTS:
            if chord_upper.startswith(trad_root):
                # Extraer sufijo completo (todo después de la raíz)
                suffix_upper = chord_upper[len(trad_root):]
                american_root = TRAD_TO_AMERICAN[trad_root]
                
                # Normalizar sufijo preservando case correcto
                if suffix_upper:
                    # 'm' o 'M' al inicio -> acorde menor (usar 'm' minúscula)
                    if suffix_upper[0] == 'M' and not suffix_upper.startswith('MAJ'):
                        suffix = 'm' + suffix_upper[1:].lower()
                    # 'maj' o 'MAJ' -> usar 'maj' minúscula
                    elif suffix_upper.startswith('MAJ'):
                        suffix = 'maj' + suffix_upper[3:].lower()
                    # 'min' o 'MIN' -> usar 'min' minúscula
                    elif suffix_upper.startswith('MIN'):
                        suffix = 'min' + suffix_upper[3:].lower()
                    # Otros sufijos (números, #, b) -> lowercase
                    else:
                        suffix = suffix_upper.lower()
                else:
                    suffix = ''
                
                return american_root + suffix
        
        # 3. Si no es tradicional, devolver con capitalización estándar
        # Primera letra mayúscula, resto minúscula (C, Dm, F#)
        if len(chord_upper) > 0 and chord_upper[0] in 'ABCDEFG':
            return chord_upper[0] + chord_upper[1:].lower()
        
        return chord_upper
    
    def _looks_like_chord(self, token: str) -> bool:
        """
        Determinar si un token parece ser un acorde musical
        (Usa _is_valid_chord_token internamente para consistencia)
        """
        if not token or not token.strip():
            return False
            
        token = token.strip().strip("(),.;:")
        
        # Si tiene barra, verificar solo la parte izquierda (acorde/bajo)
        if "/" in token:
            left_part = token.split("/", 1)[0]
            return self._looks_like_chord(left_part)
        
        # Usar la validación consolidada
        return self._is_valid_chord_token(token)
    
    def _normalize_traditional_chord(self, token: str) -> str:
        """
        Alias de _normalize_traditional_to_american para compatibilidad
        """
        return self._normalize_traditional_to_american(token)
    
    def _is_chord_line(self, line: str) -> bool:
        """
        Determinar si una línea contiene SOLO acordes (sin texto)
        Lógica estricta: acordes y texto son mutuamente excluyentes
        """
        line = line.strip()
        if not line or len(line) < 2:
            return False
        
        # Líneas muy largas son letra
        if len(line) > 80:
            return False
        
        # Dividir en tokens
        tokens = [t for t in line.split() if t.strip()]
        if not tokens:
            return False
        
        # CRÍTICO: Verificar CADA token
        chord_count = 0
        text_count = 0
        
        for token in tokens:
            # Limpiar puntuación
            clean_token = token.strip(",.;:!?()[]{}\"'")
            
            if self._is_valid_chord_token(clean_token):
                chord_count += 1
            else:
                # Si NO es acorde, verificar si es texto real
                # Palabras de 3+ letras que no son acordes = TEXTO
                if len(clean_token) >= 3:
                    text_count += 1
        
        # REGLA ESTRICTA: Si hay aunque sea 1 palabra de texto, NO es línea de acordes
        if text_count > 0:
            return False
        
        # Debe tener al menos 1 acorde válido
        return chord_count > 0

    def _is_valid_chord_token(self, token: str) -> bool:
        """
        Determinar si un token es un acorde válido.
        Aplica primero patrones positivos, luego heurísticas de rechazo.
        """
        token = token.strip()
        if not token or len(token) > 10:
            return False
        
        token_upper = token.upper()
        
        # 1. Validar acordes americanos (A-G)
        if ANGLO_CHORD_RE.match(token):
            return True
        
        # 2. Validar acordes tradicionales (DO, RE, MI, FA, SOL, LA, SI)
        for trad_root in TRAD_ROOTS:
            if token_upper.startswith(trad_root):
                suffix = token_upper[len(trad_root):]
                if not suffix or re.match(r'^[#b♯♭]?[mM]?(aj|in|im)?\d*$', suffix):
                    return True
        
        # 3. HEURÍSTICA: Palabras >6 letras raramente son acordes
        #    (excepto casos como "Cmaj7" que ya pasaron el filtro 1)
        if len(token) > 6:
            return False
        
        # 4. Rechazar palabras comunes conocidas (reducida, solo ambiguas)
        non_chords = {
            'ESTA', 'ES', 'PARA', 'QUE', 'CON', 'POR', 'SEÑOR', 'DIOS',
            'JESUS', 'CRISTO', 'MARIA', 'SANTO', 'LUZ', 'AMOR', 'VIDA'
        }
        
        if token_upper in non_chords:
            return False
        
        return False
    

# ==============================================================================
# PARTE 3: FUNCIONES DE PROCESAMIENTO DE ARCHIVOS ACTUALIZADAS
# ==============================================================================

    def _process_single_file(self, file_path: str, options: Dict) -> Dict:
        """Procesar un solo archivo según su tipo"""
        print("")
        print("*************************************************")
        print(" ✅ Iniciando procesamiento de archivo...")
        print(f"Procesando archivo: {file_path}")
        print("*************************************************")
        print("")
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            print("Procesando archivo PDF...")
            return self.process_pdf_file(file_path, options)
        
        elif file_ext in ('.docx', '.doc') and DOCX_SUPPORT:
            print("📌 Procesando archivo DOCX...")
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
                'error': f'Tipo de archivo no soportado: {file_ext}'
            }
        
    def _process_docx_file(self, file_path: str, options: Dict) -> Dict:
        """Procesar archivo Word (.docx) extrayendo párrafos como texto"""
        print("Procesando archivo DOCX...(_process_docx_file)")
        try:
            self._update_progress("Extrayendo texto desde Word...", 10)
            print("Extrayendo texto desde Word...(_process_docx_file)")
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
         
    def _create_single_song_from_text(self, text: str, file_path: str) -> Dict:
        """Crear una sola canción desde el texto completo, formateada para tipografía monoespaciada."""
        print("✅  Creando canción desde texto completo...(_create_single_song_from_text)")
        lines = text.split('\n')
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Título según tu lógica actual
        title = self._extract_title_from_text(lines, file_name)
        print(f"📄 Título extraído: {title}")

        # Reconstruir el texto con acordes alineados
        formatted_song = self._reconstruct_fixedwidth_song(text)
        print("📄 Letra formateada creada. con (_reconstruct_fixedwidth_song)")
        print(formatted_song)

        # Detectar tonalidad
        probable_key = self._detect_tonality_from_text(formatted_song)
        print(f"📄 Tonalidad probable detectada: {probable_key}")

        return {
            'titulo': title,
            'artista': 'Desconocido',
            'letra': formatted_song.strip(),  # texto ya listo para renderizado monospace
            'tono_original': probable_key,
            'acordes': '',  # los acordes ya están embebidos en la letra
            'estado': 'pendiente',
            'categoria_id': 1,
            'notas': f"Importado desde DOCX: {os.path.basename(file_path)}"
        }
        
    def _reconstruct_fixedwidth_song(self, text: str, tabsize: int = 4) -> str:
        """
        Reconstruye texto de canción con acordes alineados en fuente monoespaciada.
        Detecta pares (línea de acordes, línea de letra) y los reensambla.
        """
        print("✅ ✅ Reconstruyendo canción en formato monoespaciado...(_reconstruct_fixedwidth_song)")
        def normalize_tabs(s: str) -> str:
            return s.replace('\t', ' ' * tabsize)
        

        lines = [normalize_tabs(l.rstrip()) for l in text.splitlines()]
        output_lines = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            if not line.strip():
                output_lines.append("")  # línea vacía
                i += 1
                continue

            # Si la línea es de acordes y hay una siguiente con letra
            if self._is_chord_line(line) and i + 1 < n and not self._is_chord_line(lines[i + 1]):                
                print("📌 Línea de acordes detectada:")

                chord_line_raw = line
                print(f"  Acordes: {chord_line_raw}")
                lyric_line_raw = lines[i+1]
                print(f"  Letra:   {lyric_line_raw}")

                # normaliza tabs si hiciste afuera
                chord_aligned, lyric_padded = self.align_chord_over_lyric(chord_line_raw, lyric_line_raw)
                print(f"  Acordes alineados: {chord_aligned}")
                print(f"  Letra ajustada:    {lyric_padded}")

                output_lines.append(chord_aligned)
                output_lines.append(lyric_padded)
                i += 2

            else:
                # Solo línea de texto (sin acordes encima)
                print("❌ Línea de letra sin acordes:")
                print(f"  Letra: {line}")
                output_lines.append(line)
                i += 1

        # Unir líneas resultantes con salto de línea
        print("✅ ✅ Reconstrucción completada.")
        print("\n".join(output_lines))
        
        return "\n".join(output_lines)

    def align_chord_over_lyric(self, chord_line: str, lyric_line: str, tabsize: int = 4) -> (str, str):
        """
        Reposiciona acordes normalizándolos y manteniéndolos separados
        """
        print("✅ Alineando acordes sobre letra... (align_chord_over_lyric)")
        max_len = max(len(chord_line), len(lyric_line))
        chord = chord_line.ljust(max_len)
        lyric = lyric_line.ljust(max_len)
        chord_out = list(" " * max_len)

        for m in CHORD_TOKEN_RE.finditer(chord_line):
            token = m.group(0)
            
            # ✅ NORMALIZAR ACORDE
            token_normalized = self._normalize_traditional_chord(token)
            
            start = m.start()
            end = m.end()
            center = int(round((start + end - 1) / 2.0))

            # Buscar target en lyric
            target = None
            if center < len(lyric) and lyric[center] != " ":
                target = center
            else:
                max_search = max(end - start, 6)
                for d in range(1, max_search + 1):
                    left = center - d
                    right = center + d
                    if left >= 0 and left < len(lyric) and lyric[left] != " ":
                        target = left
                        break
                    if right >= 0 and right < len(lyric) and lyric[right] != " ":
                        target = right
                        break
                if target is None:
                    target = min(center, len(lyric)-1)

            # Calcular posición con token normalizado
            left_pos = target - (len(token_normalized) // 2)
            left_pos = max(0, min(left_pos, max_len - len(token_normalized)))

            # Resolver conflictos
            conflict_shift = 0
            while True:
                conflict = False
                for j in range(len(token_normalized)):
                    if chord_out[left_pos + j + conflict_shift] != " ":
                        conflict = True
                        break
                if not conflict:
                    break
                conflict_shift += 1
                if left_pos + conflict_shift + len(token_normalized) > max_len:
                    found_left = False
                    for shift_left in range(1, len(token_normalized)+1):
                        lp = left_pos - shift_left
                        if lp < 0:
                            break
                        ok = True
                        for j in range(len(token_normalized)):
                            if chord_out[lp + j] != " ":
                                ok = False
                                break
                        if ok:
                            left_pos = lp
                            conflict_shift = 0
                            found_left = True
                            break
                    if not found_left:
                        break
            left_pos += conflict_shift

            # ✅ ESCRIBIR TOKEN NORMALIZADO
            for j, ch in enumerate(token_normalized):
                pos = left_pos + j
                if 0 <= pos < max_len:
                    chord_out[pos] = ch

        chord_aligned = "".join(chord_out).rstrip()
        lyric_padded = lyric.rstrip()
        return chord_aligned, lyric_padded

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


    """ 
    *****************************************************************************************
    *****************************************************************************************
        BLOQUE DE FUNCIONES DE ALINEACION POR ESPACIOS SUPERPUESTOS EN CARACTERES 
    *****************************************************************************************
    *****************************************************************************************
    """

    def _extract_chords_unstructured(self, text: str) -> List[str]:
        """Extraer acordes de formato no estructurado (líneas separadas)"""
        lines = text.split('\n')
        chords = []
        
        for line in lines:
            line = line.strip()
            if self._is_chord_line(line):
                # Extraer tokens que son acordes válidos
                tokens = line.split()
                for token in tokens:
                    if self._is_valid_chord_token(token):
                        # Normalizar a notación americana
                        normalized_chord = self._normalize_traditional_to_american(token)
                        # Asegurar que los acordes menores tengan 'm' minúscula
                        if normalized_chord.endswith('M') and len(normalized_chord) > 1:
                            normalized_chord = normalized_chord[:-1] + 'm'
                        if normalized_chord not in chords:
                            chords.append(normalized_chord)
        
        return chords    

    def _convert_single_chord(self, chord: str) -> str:
        """
        Convierte un solo acorde tradicional a americano.
        Ej: DO -> C, DOm -> Cm, FA# -> F#, SOLm7 -> Gm7
        """
        chord = chord.strip().upper()

        # Patrón: raíz (letras), accidental opcional (#/b), resto (m, 7, sus4...)
        m = re.match(r'^(DO|RE|MI|FA|SOL|LA|SI)([#B]?)(.*)$', chord, re.IGNORECASE)
        if m:
            root, accidental, rest = m.groups()
            base = self.TRAD_TO_AMERICAN.get(root.upper(), root)
            return f"{base}{accidental}{rest}"

        # Si no es tradicional, devolvemos tal cual (p. ej. C#m)
        return chord
        
    def parse_aligned_pair(self, chord_line: str, lyric_line: str):
        """
        Parsear par alineado de acordes y letra
        
        Args:
            chord_line: Línea con acordes
            lyric_line: Línea con letra
            
        Returns:
            Diccionario con texto y acordes normalizados
        """
        # Normalizar tabs a espacios
        chord_line = chord_line.replace("\t", "    ")
        lyric_line = lyric_line.replace("\t", "    ")
        
        # Ajustar longitudes
        max_len = max(len(chord_line), len(lyric_line))
        chord_line = chord_line.ljust(max_len)
        lyric_line = lyric_line.ljust(max_len)
        
        # Encontrar tokens de acordes
        tokens = self._find_chord_tokens_in_line(chord_line)
        chords = []
        
        for token in tokens:
            token_text = token['text'].strip()
            
            if not self._looks_like_chord(token_text):
                continue
                
            start, end = token['start'], token['end']
            char_index = self._map_token_to_lyric_index(start, end, lyric_line)
            
            # Normalizar acorde
            chord_normalized = self._normalize_traditional_chord(token_text)
            
            chords.append({
                "chord": chord_normalized,
                "original": token_text,
                "char_index": char_index,
                "col_start": start,
                "col_end": end
            })
        
        return {
            "text": lyric_line.rstrip(), 
            "chords": chords
        }

    def _map_traditional_root(self, root: str) -> str:
        """
        Convierte raíz tradicional (Do, Re, Mi...) a anglosajona (C, D, E...).
        Si ya es anglosajona la devuelve en mayúscula.
        """
        if not root:
            return root
        r = root.strip().upper()
        # Normalizar SOL -> SOL (en mapping existe)
        return _TRAD_TO_ANG.get(r, r)  # si no está en el mapping, devuelve la misma (A-G)

    def _pad_to_same_length(self, a: str, b: str):
        la, lb = len(a), len(b)
        if la < lb:
            a = a + " " * (lb - la)
        elif lb < la:
            b = b + " " * (la - lb)
        return a, b

    def _map_token_to_lyric_index(self, start: int, end: int, lyric_line: str) -> int:
        """
        Mapear posición de token a índice en línea de letra
        
        Args:
            start: Posición inicial del token
            end: Posición final del token  
            lyric_line: Línea de letra
            
        Returns:
            Índice en la línea de letra
        """
        center_col = (start + end - 1) / 2.0
        
        if center_col < 0:
            return 0
        if center_col >= len(lyric_line):
            return len(lyric_line) - 1 if len(lyric_line) > 0 else 0
            
        return int(round(center_col))

    def _extract_chord_lyric_pairs(self, lines: List[str]) -> List[Dict]:
        """
        Recorre las líneas detectando pares (línea de acordes seguida de línea de letra).
        Estrategia simple y robusta:
        - Si una línea es detectada como línea de acordes (_is_chord_line), se intenta emparejar con la siguiente línea no-vacía.
        - Si no hay una línea de acordes consecutiva, se omite.
        Devuelve lista de dicts parseados (parse_aligned_pair output) y también líneas sueltas sin acordes si no hay par.
        """
        pairs = []
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i].rstrip("\n")
            if not line.strip():
                i += 1
                continue
            # usa tu función _is_chord_line si existe, si no, heurística propia:
            is_chord = False
            if hasattr(self, "_is_chord_line") and callable(getattr(self, "_is_chord_line")):
                is_chord = self._is_chord_line(line)
            else:
                # heurística fallback: muchas tokens cortas y mayúsculas o presencia de #/b
                tokens = [tok for tok in re.split(r'\s+', line) if tok]
                short_tokens = sum(1 for tok in tokens if len(tok) <= 5)
                if short_tokens >= max(1, len(tokens)//2) or any(ch in line for ch in ['#', 'b', '♯', '♭', '/']):
                    is_chord = True

            if is_chord and i + 1 < n:
                next_line = lines[i+1]
                # empareja chord_line (line) con lyric_line (next_line)
                parsed = self.parse_aligned_pair(self, line, next_line)
                parsed['line_index'] = i+1  # índice de la línea de letra en el conjunto original
                pairs.append(parsed)
                i += 2
                continue
            else:
                # No es línea de acordes, pero puede ser una línea de letra sola
                # guardamos como línea sin acordes
                pairs.append({"text": line.rstrip(), "chords": [], "line_index": i})
                i += 1
        return pairs    
           
    
    def _extract_chords_unstructured(self, text: str) -> List[str]:
        """Extraer acordes de formato no estructurado (líneas separadas)"""
        lines = text.split('\n')
        chords = []
        
        for line in lines:
            line = line.strip()
            if self._is_chord_line(line):
                # Extraer tokens que son acordes válidos
                tokens = line.split()
                for token in tokens:
                    if self._is_valid_chord_token(token):
                        # Normalizar a notación americana
                        normalized_chord = self._normalize_traditional_to_american(token)
                        # Asegurar que los acordes menores tengan 'm' minúscula
                        if normalized_chord.endswith('M') and len(normalized_chord) > 1:
                            normalized_chord = normalized_chord[:-1] + 'm'
                        if normalized_chord not in chords:
                            chords.append(normalized_chord)
        
        return chords    
    
    def _format_unstructured_lyrics(self, text: str) -> str:
        """Formatear letra en formato no estructurado preservando espaciado"""
        lines = text.split('\n')
        formatted_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                formatted_lines.append("")
                i += 1
                continue
                
            # Detectar si es línea de acordes
            if self._is_chord_line(line):
                chord_line = line
                lyric_line = ""
                
                # Buscar línea de letra siguiente (no vacía, no acordes, no sección)
                j = i + 1
                while j < len(lines) and not lyric_line:
                    next_line = lines[j].strip()
                    if (next_line and 
                        not self._is_chord_line(next_line) and 
                        not self._is_section_line(next_line)):
                        lyric_line = next_line
                    j += 1
                
                if lyric_line:
                    # Combinar preservando el espaciado original
                    formatted_line = self._combine_chords_with_spacing(chord_line, lyric_line)
                    formatted_lines.append(formatted_line)
                    i = j  # Saltar las líneas procesadas
                else:
                    # Solo acordes
                    formatted_lines.append(chord_line)
                    i += 1
            else:
                # Línea normal
                formatted_lines.append(line)
                i += 1
        
        return '\n'.join(formatted_lines)
    
    def _combine_chords_with_spacing(self, chord_line: str, lyric_line: str) -> str:
        """Combinar acordes con letra preservando espaciado"""
        if not lyric_line:
            return chord_line
        
        # Extraer acordes válidos con sus posiciones
        chords_with_positions = []
        tokens = chord_line.split()
        
        for token in tokens:
            if self._is_valid_chord_token(token):
                normalized = self._normalize_traditional_to_american(token)
                chords_with_positions.append(normalized)
        
        if not chords_with_positions:
            return lyric_line
        
        # Para simplificar, poner acordes al inicio por ahora
        # En una versión avanzada, se alinearían sobre la letra
        chords_str = ' '.join([f"[{chord}]" for chord in chords_with_positions])
        return f"{chords_str} {lyric_line}"

    """
    *****************************************************************************************
    *****************************************************************************************
        FIN BLOQUE DE FUNCIONES DE ALINEACION POR ESPACIOS SUPERPUESTOS EN CARACTERES 
    *****************************************************************************************
    *****************************************************************************************
    """

    def _process_with_pdfplumber(self, file_path: str, options: Dict) -> Dict:
        """Procesar PDF preservando mejor la estructura espacial"""
        self._update_progress("Extrayendo texto completo del PDF...", 30)
        print("Extrayendo texto completo del PDF...")
        
        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"Extrayendo texto de {total_pages} páginas...")
                self._update_progress(f"Extrayendo texto de {total_pages} páginas...", 40)
                
                # Extraer TODO el texto preservando estructura
                full_text = ""
                for page_num, page in enumerate(pdf.pages):
                    # Usar extracción con layout preservation
                    text = self._extract_text_preserving_layout(page)
                    full_text += text + "\n\n"  # Doble salto entre páginas
                    
                    progress = 40 + (page_num / total_pages) * 40
                    self._update_progress(f"Página {page_num + 1}/{total_pages}", progress)
                    print(f"Página {page_num + 1}/{total_pages}")
                
                # Limpiar y normalizar el texto
                cleaned_text = self._clean_extracted_text(full_text)
                
                # Crear UNA sola canción con todo el contenido
                song = self._create_single_song_from_text(cleaned_text, file_path)
                print("Contenido de la canción creado")
                songs_found = [song] if song else []
                    
        except Exception as e:
            self.logger.error(f"Error con pdfplumber: {e}")
            return {'success': False, 'error': f'Error pdfplumber: {str(e)}'}
            
        return {
            'success': True,
            'file_type': 'pdf',
            'total_pages': total_pages,
            'songs_found': songs_found,
            'extracted_text': full_text,
            'cleaned_text': cleaned_text,
            'processed_with': 'pdfplumber_improved'
        }

    def _extract_text_preserving_layout(self, page) -> str:
        """Extraer texto preservando la estructura layout del PDF"""
        text = ""
        
        # Método 1: Extracción simple (fallback)
        simple_text = page.extract_text() or ""
        
        # Método 2: Extracción por palabras con coordenadas (más preciso)
        try:
            words = page.extract_words(
                keep_blank_chars=False, 
                use_text_flow=True,
                extra_attrs=["x0", "top", "x1", "bottom"]  # Agregar atributos necesarios
            )
            if words:
                # Ordenar palabras por posición (top, luego left)
                words_sorted = sorted(words, key=lambda x: (x.get('top', 0), x.get('x0', 0)))
                
                # Reconstruir texto manteniendo estructura
                lines = {}
                for word in words_sorted:
                    line_key = int(word.get('top', 0))  # Agrupar por línea aproximada
                    if line_key not in lines:
                        lines[line_key] = []
                    lines[line_key].append(word.get('text', ''))
                
                # Construir texto línea por línea
                text_lines = []
                for line_key in sorted(lines.keys()):
                    line_text = ' '.join(lines[line_key])
                    text_lines.append(line_text)
                
                text = '\n'.join(text_lines)
            else:
                text = simple_text
        except Exception as e:
            print(f"⚠️ Error en extracción avanzada, usando método simple: {e}")
            text = simple_text
        
        return text

    def _clean_extracted_text(self, text: str) -> str:
        """Limpiar y normalizar texto extraído del PDF"""
        if not text:
            return ""
        
        # 1. Normalizar saltos de línea
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 2. Unir líneas muy cortas (probablemente fragmentadas)
            if (len(line) < 30 and 
                cleaned_lines and 
                len(cleaned_lines[-1]) < 50):
                cleaned_lines[-1] += " " + line
            else:
                cleaned_lines.append(line)
        
        # 3. Unir estrofas lógicas (líneas que parecen versos)
        final_lines = []
        i = 0
        while i < len(cleaned_lines):
            current_line = cleaned_lines[i]
            
            # Si es una línea corta y la siguiente también, unirlas
            if (i + 1 < len(cleaned_lines) and
                len(current_line) < 40 and
                len(cleaned_lines[i + 1]) < 40 and
                not self._looks_like_chord_line(current_line) and
                not self._looks_like_chord_line(cleaned_lines[i + 1])):
                
                # Unir líneas consecutivas cortas
                joined_line = current_line + " " + cleaned_lines[i + 1]
                final_lines.append(joined_line)
                i += 2
            else:
                final_lines.append(current_line)
                i += 1
        
        return '\n'.join(final_lines)

    def _looks_like_chord_line(self, line: str) -> bool:
        """Determinar si una línea parece ser de acordes - SIEMPRE RETORNA FALSE"""
        # Desactivado: no diferenciamos líneas de acordes
        return False

    
    def _detect_tonality_from_text(self, text: str) -> str:
        """Detección simplificada de tonalidad (opcional)"""
        # Buscar indicios de tonalidad en el texto
        lines = text.split('\n')
        
        for line in lines[:10]:  # Buscar en primeras líneas
            line_upper = line.upper()
            
            # Buscar patrones comunes de tonalidad
            if ' TONO: ' in line_upper or ' TONALIDAD: ' in line_upper:
                for key in ['DO', 'RE', 'MI', 'FA', 'SOL', 'LA', 'SI', 'C', 'D', 'E', 'F', 'G', 'A', 'B']:
                    if key in line_upper:
                        return key
            
            # Buscar acordes comunes al inicio
            common_keys = {
                'C': ['DO', 'C'],
                'G': ['SOL', 'G'], 
                'D': ['RE', 'D'],
                'A': ['LA', 'A'],
                'E': ['MI', 'E'],
                'F': ['FA', 'F']
            }
            
            for key, indicators in common_keys.items():
                if any(indicator in line_upper for indicator in indicators):
                    return key
        
        return 'C'  # Tonalidad por defecto
        
    def _is_section_line(self, line: str) -> bool:
        """Determinar si una línea es una sección (como estrofa, coro)"""
        line_upper = line.upper()
        section_indicators = [
            'VERSO', 'CORO', 'ESTRIBILLO', 'INTRO', 'OUTRO', 'PUENTE',
            'ESTROFA', 'CODA', 'FINAL'
        ]
        
        return (line_upper in section_indicators or
                any(indicator in line_upper for indicator in section_indicators))

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
            
    def _contains_chords(self, line: str) -> bool:
        """Determinar si una línea contiene acordes - SIEMPRE RETORNA FALSE"""
        # Desactivado: no procesamos acordes automáticamente
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
                
    def _detect_probable_key(self, chords: List[str]) -> str:
        """Detectar tonalidad probable basada en acordes - Versión mejorada"""
        if not chords:
            return 'C'
        
        # Conteo de acordes por nota base
        chord_count = {}
        for chord in chords:
            # Extraer la nota base (primera letra)
            if chord and chord[0].upper() in 'CDEFGAB':
                base_note = chord[0].upper()
                chord_count[base_note] = chord_count.get(base_note, 0) + 1
        
        # Si no hay acordes válidos, fallback a C
        if not chord_count:
            return 'C'
        
        # Tonalidades más comunes en música cristiana (orden de probabilidad)
        # C es la más común, luego G, luego D, etc.
        common_keys = ['C', 'G', 'D', 'A', 'F', 'E', 'Bb', 'Eb', 'Am', 'Dm', 'Em']
        
        # Buscar la tonalidad más probable basada en frecuencia y orden común
        most_common_note = max(chord_count.items(), key=lambda x: x[1])[0]
        
        # Priorizar C sobre G si están cerca en frecuencia
        c_count = chord_count.get('C', 0)
        g_count = chord_count.get('G', 0)
        
        # Si C y G tienen conteos similares, priorizar C
        if c_count > 0 and (c_count >= g_count or (c_count == g_count and most_common_note == 'C')):
            return 'C'
        elif g_count > 0:
            return 'G'
        
        # Si no hay C o G claros, usar el más común
        return most_common_note
        
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


    def _find_chord_tokens_in_line(self, chord_line: str) -> List[Dict]:
        """
        Encontrar tokens de acordes en una línea usando regex global.
        
        Args:
            chord_line: Línea con acordes
            
        Returns:
            Lista de dicts con 'text', 'start', 'end' para cada token
        """
        tokens = []
        
        for match in CHORD_TOKEN_RE.finditer(chord_line):
            token_text = match.group(0).strip()
            
            if token_text and self._is_valid_chord_token(token_text):
                tokens.append({
                    'text': token_text,
                    'start': match.start(),
                    'end': match.end()
                })
        
        return tokens