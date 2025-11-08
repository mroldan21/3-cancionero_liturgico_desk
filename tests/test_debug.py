# test_debug.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.file_processor import FileProcessor

def debug_normalization():
    """Test específico de normalización de acordes tradicionales"""
    processor = FileProcessor(None)
    
    test_cases = [
        ("DO", "C"),
        ("FA", "F"), 
        ("SOL", "G"),
        ("DO7", "C7"),
        ("SOL7", "G7"),
        ("LAm", "Am"),
        ("SIm", "Bm")
    ]
    
    print("🔍 TEST: Normalización de acordes tradicionales")
    for input_chord, expected in test_cases:
        result = processor._normalize_traditional_to_american(input_chord)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_chord}' -> '{result}' (esperaba: '{expected}')")

def debug_chord_detection():
    """Test específico de detección de líneas de acordes"""
    processor = FileProcessor(None)
    
    test_lines = [
        "Dm                     A7",      # Debería ser línea de acordes
        "BAUTIZAME SEÑOR CON TU ESPÍRITU", # No debería ser línea de acordes
        "DO                  DO7",        # Debería ser línea de acordes  
        "FA              DO",             # Debería ser línea de acordes
        "Esta es la luz de Cristo",       # No debería ser línea de acordes
    ]
    
    print("\n🔍 TEST: Detección de líneas de acordes")
    for line in test_lines:
        result = processor._is_chord_line(line)
        print(f"  '{line[:30]}...' -> {'🎵 ACORDES' if result else '📝 TEXTO'}")

def debug_formatting():
    """Test específico de formateo"""
    processor = FileProcessor(None)
    
    # Simular el texto problemático
    test_text = """DO                  DO7
Esta es la luz de Cristo,
FA              DO
yo la haré brillar."""
    
    print("\n🔍 TEST: Formateo de texto")
    print("ENTRADA:")
    print(test_text)
    print("\nSALIDA:")
    result = processor._format_unstructured_lyrics(test_text)
    print(result)

def debug_specific_cases():
    """Test de casos específicos del problema"""
    processor = FileProcessor(None)
    
    print("\n🔍 TEST: Casos específicos problemáticos")
    
    # Caso 1: DO debería convertirse a C
    result1 = processor._normalize_traditional_to_american("DO")
    print(f"  DO -> {result1} (debería ser: C)")
    
    # Caso 2: DO7 debería convertirse a C7  
    result2 = processor._normalize_traditional_to_american("DO7")
    print(f"  DO7 -> {result2} (debería ser: C7)")
    
    # Caso 3: Verificar si "DO DO7" se detecta como línea de acordes
    result3 = processor._is_chord_line("DO DO7")
    print(f"  'DO DO7' es línea de acordes: {result3}")

if __name__ == "__main__":
    print("🚀 INICIANDO DEPURACIÓN")
    debug_normalization()
    debug_chord_detection() 
    debug_formatting()
    debug_specific_cases()