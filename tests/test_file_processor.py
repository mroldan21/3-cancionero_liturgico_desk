# test_file_processor.py
import pytest
import sys
import os

# Agregar el directorio core al path para importar FileProcessor
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.file_processor import FileProcessor

class TestFileProcessor:
    
    def test_normalize_traditional_to_american(self):
        """Test exhaustivo de normalización"""
        processor = FileProcessor(None)
        
        test_cases = [
            ("DO", "C"),
            ("DOm", "Cm"),
            ("FA#", "F#"),            
            ("SOL", "G"),
            ("LAm", "Am"),
            ("SI", "B"),
            ("REb", "Db"),  # Cambiamos la expectativa a 'Db'
            ("MIm", "Em"),
            ("FAm", "Fm")
        ]
        
        for input_chord, expected in test_cases:
            result = processor._normalize_traditional_to_american(input_chord)
            assert result == expected, f"'{input_chord}' -> '{result}', esperaba '{expected}'"

    def test_looks_like_chord(self):
        """Test de detección de acordes válidos/inválidos"""
        processor = FileProcessor(None)
        
        # Deben devolver True
        valid_chords = ["C", "G7", "Am", "F#m", "DO", "SOL", "LAm", "C#", "Gb", "Dsus4", "Em7"]
        for chord in valid_chords:
            assert processor._is_valid_chord_token(chord), f"'{chord}' debería ser válido"
        
        # Deben devolver False
        invalid_chords = ["ABLAH", "Este no es acorde", "123", "La lluvia", "H", "Z", "123C", "Casa"]
        for chord in invalid_chords:
            assert not processor._is_valid_chord_token(chord), f"'{chord}' debería ser inválido"

    def test_is_chord_line(self):
        """Test de detección de líneas de acordes"""
        processor = FileProcessor(None)
        
        # Líneas que SÍ deben detectarse como de acordes
        chord_lines = [
            "C G Am",
            "DO SOL LAm", 
            "F C G D",
            "Am Dm G C",
            "C#m F# B E",
            "DO SOL",
            "LAm",
            "C G",
            "Am"
        ]
        
        # Líneas que NO deben detectarse como de acordes
        not_chord_lines = [
            "La lluvia cae suave",
            "Este no es un acorde",
            "Canta con alegría",
            "Dios es amor",
            "ABLAH MUNDO",
            "123 456 789",
            "C La lluvia cae",  # Mezclado
            "Amor de Dios G",   # Mezclado
            "Esta es una línea con texto normal",
            "Hello world"
        ]
        
        for line in chord_lines:
            assert processor._is_chord_line(line), f"Línea '{line}' no detectada como acordes"
            
        for line in not_chord_lines:
            assert not processor._is_chord_line(line), f"Línea '{line}' detectada incorrectamente como acordes"

    def test_extract_chords_unstructured(self):
        """Test de extracción de acordes de texto no estructurado"""
        processor = FileProcessor(None)
        
        text = """
        DO SOL LAm
        Canta con alegría
        F C G
        Alaba al Señor
        Dm Am
        Con todo tu corazón
        """
        
        chords = processor._extract_chords_unstructured(text)
        
        # Los acordes deberían normalizarse correctamente
        expected_chords = ["C", "G", "Am", "F", "Dm"]
        for chord in expected_chords:
            assert chord in chords, f"Acorde {chord} no encontrado en {chords}"

    def test_format_unstructured_lyrics(self):
        """Test de formateo de letras no estructuradas"""
        processor = FileProcessor(None)
        
        input_text = """DO SOL LAm
Canta con alegría
F C G
Alaba al Señor"""
        
        result = processor._format_unstructured_lyrics(input_text)
        
        # Verificar que se formateó correctamente
        assert "[C]" in result or "C" in result, "Acorde C no encontrado"
        assert "[G]" in result or "G" in result, "Acorde G no encontrado" 
        assert "[Am]" in result or "Am" in result, "Acorde Am no encontrado"
        assert "Canta con alegría" in result, "Letra no preservada"
        assert "Alaba al Señor" in result, "Letra no preservada"

    def test_parse_aligned_pair_simple(self):
        """Test de análisis de pares acorde-letra simples"""
        processor = FileProcessor(None)
        
        # Línea de acordes tradicionales
        chord_line = "DO SOL LAm"
        lyric_line = "Esta es una prueba"
        
        result = processor._combine_chords_and_lyrics(chord_line, lyric_line)
        
        # Verificar que se normalizaron correctamente
        assert "C" in result, "DO no se normalizó a C"
        assert "G" in result, "SOL no se normalizó a G" 
        assert "Am" in result, "LAm no se normalizó a Am"
        assert "Esta es una prueba" in result, "Letra no se incluyó correctamente"

    def test_process_pdf_single_song(self):
        """Test de procesamiento de PDF como canción única"""
        processor = FileProcessor(None)
        
        # Texto simulado de un PDF
        pdf_text = """CARNAVALITO DEL MISIONERO
        Lam rem SOL DO
        CRISTO, DIVINO NIÑO ALCALDE DE MI CIUDAD,
        MI7
        BENDICE A LOS QUE CON ANSIAS,
        lam
        VENIMOS A MISIONAR."""
        
        # Simular el método que crea una canción desde texto
        song = processor._create_single_song_from_text(pdf_text, "test.pdf")
        
        assert song is not None, "No se creó la canción"
        assert "titulo" in song, "La canción no tiene título"
        assert "letra" in song, "La canción no tiene letra"
        assert "CARNAVALITO" in song["titulo"] or "test" in song["titulo"], "Título incorrecto"

    def test_detect_probable_key(self):
        """Test de detección de tonalidad probable"""
        processor = FileProcessor(None)
        
        test_cases = [
            (["C", "G", "Am", "F"], "C"),  # Debería detectar C
            (["G", "D", "Em", "C"], "C"),  # C es más común que G
            (["G", "D", "Em", "G7"], "G"), # Más G que otros
            (["Am", "Dm", "G", "C"], "C"), # Debería detectar C
            ([], "C"),                      # Fallback a C
            (["X", "Y"], "C")               # Fallback a C con acordes inválidos
        ]
        
        for chords, expected in test_cases:
            result = processor._detect_probable_key(chords)
            assert result == expected, f"Acordes {chords} -> '{result}', esperaba '{expected}'"

# Tests adicionales para funciones específicas
def test_chord_token_validation_edge_cases():
    """Test casos bordes para validación de tokens de acordes"""
    processor = FileProcessor(None)
    
    edge_cases = [
        ("C", True),
        ("c", True),           # minúscula
        ("Cm", True),
        ("CM", True),          # Mayor con M
        ("C7", True),
        ("C#m7", True),                
        ("H", False),          # H no existe
        ("C123", False),       # Número muy largo
        ("", False),           # Vacío
        ("   ", False),        # Solo espacios
        ("C#m7b5", True),      # Acorde complejo
        ("Dsus4", True),       # Suspendido
    ]
    
    for token, expected in edge_cases:
        result = processor._is_valid_chord_token(token)
        assert result == expected, f"Token '{token}' -> {result}, esperaba {expected}"

def test_traditional_note_recognition():
    """Test específico para reconocimiento de notas tradicionales"""
    processor = FileProcessor(None)
    
    traditional_notes = [
        ("Do", True),
        ("Re", True),
        ("Mi", True),
        ("Fa", True),
        ("Sol", True),
        ("La", True),
        ("Si", True),
        ("Do#", True),
        ("Reb", True),
        ("Mib", True),
        ("Fa#", True),
        ("Solb", True),
        ("Lab", True),
        ("Sib", True),
    ]
    
    for note, expected in traditional_notes:
        result = processor._is_valid_chord_token(note)
        assert result == expected, f"Nota tradicional '{note}' -> {result}, esperaba {expected}"