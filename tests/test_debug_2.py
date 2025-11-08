"""
Test de depuración para file_processor.py
Agrega test específico para align_chord_over_lyric
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.file_processor import FileProcessor

def test_normalize_traditional():
    """Test de normalización de acordes tradicionales"""
    print("🔍 TEST: Normalización de acordes tradicionales")
    
    fp = FileProcessor()
    
    test_cases = [
        ("DO", "C"),
        ("FA", "F"),
        ("SOL", "G"),
        ("DO7", "C7"),
        ("SOL7", "G7"),
        ("LAm", "Am"),
        ("SIm", "Bm"),
    ]
    
    for trad, expected in test_cases:
        result = fp._normalize_traditional_to_american(trad)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{trad}' -> '{result}' (esperaba: '{expected}')")

def test_is_chord_line():
    """Test de detección de líneas de acordes"""
    print("🔍 TEST: Detección de líneas de acordes")
    
    fp = FileProcessor()
    
    test_lines = [
        ("Dm                     A7", True),
        ("BAUTIZAME SEÑOR CON TU ESPÍRITU", False),
        ("DO                  DO7", True),
        ("FA              DO", True),
        ("Esta es la luz de Cristo,", False),
    ]
    
    for line, expected in test_lines:
        result = fp._is_chord_line(line)
        icon = "🎵 ACORDES" if result else "📝 TEXTO"
        print(f"  '{line[:30]}...' -> {icon}")

def test_format_text():
    """Test de formateo de texto con acordes"""
    print("🔍 TEST: Formateo de texto")
    
    fp = FileProcessor()
    
    input_text = """DO                  DO7
Esta es la luz de Cristo,
FA              DO
yo la haré brillar."""
    
    print("ENTRADA:")
    print(input_text)
    
    formatted = fp._reconstruct_fixedwidth_song(input_text)
    
    print("SALIDA:")
    print(formatted)

def test_specific_cases():
    """Test de casos específicos problemáticos"""
    print("🔍 TEST: Casos específicos problemáticos")
    
    fp = FileProcessor()
    
    # Test de normalización individual
    print(f"  DO -> {fp._normalize_traditional_to_american('DO')} (debería ser: C)")
    print(f"  DO7 -> {fp._normalize_traditional_to_american('DO7')} (debería ser: C7)")
    
    # Test de detección de línea de acordes
    chord_line = "DO DO7"
    is_chord = fp._is_chord_line(chord_line)
    print(f"  '{chord_line}' es línea de acordes: {is_chord}")


# ==============================================================================
# NUEVO TEST: align_chord_over_lyric
# ==============================================================================

def test_align_chord_over_lyric():
    """Test específico de alineación de acordes sobre letra"""
    print("\n" + "="*70)
    print("🔍 TEST CRÍTICO: align_chord_over_lyric")
    print("="*70)
    
    fp = FileProcessor()
    
    # Caso 1: Tokens separados normales
    print("\n📌 Caso 1: Tokens separados normales")
    chord1 = "  Dm                     A7"
    lyric1 = "BAUTIZAME SEÑOR CON TU ESPÍRITU"
    
    result_chord1, result_lyric1 = fp.align_chord_over_lyric(chord1, lyric1)
    
    print(f"Entrada chord:  '{chord1}'")
    print(f"Entrada lyric:  '{lyric1}'")
    print(f"Salida chord:   '{result_chord1}'")
    print(f"Salida lyric:   '{result_lyric1}'")
    
    # Verificación
    if "Dm" in result_chord1 and "A7" in result_chord1:
        print("✅ Acordes presentes")
    else:
        print("❌ Acordes faltantes")
    
    # Caso 2: CRÍTICO - Tokens pegados "DmD7"
    print("\n📌 Caso 2: CRÍTICO - Tokens pegados (DmD7)")
    chord2 = "                       Dm  D7"
    lyric2 = "BAUTIZAME, BAUTIZAME SEÑOR"
    
    result_chord2, result_lyric2 = fp.align_chord_over_lyric(chord2, lyric2)
    
    print(f"Entrada chord:  '{chord2}'")
    print(f"Entrada lyric:  '{lyric2}'")
    print(f"Salida chord:   '{result_chord2}'")
    print(f"Salida lyric:   '{result_lyric2}'")
    
    # Verificación crítica
    if "Dm D7" in result_chord2:
        print("✅ CORRECTO: Tokens separados con espacio 'Dm D7'")
    elif "DmD7" in result_chord2:
        print("❌ ERROR: Tokens siguen pegados 'DmD7'")
    else:
        print("⚠️  ADVERTENCIA: Resultado inesperado")
    
    # Caso 3: Acordes tradicionales
    print("\n📌 Caso 3: Acordes tradicionales (DO, SOL)")
    chord3 = "DO                  DO7"
    lyric3 = "Esta es la luz de Cristo,"
    
    result_chord3, result_lyric3 = fp.align_chord_over_lyric(chord3, lyric3)
    
    print(f"Entrada chord:  '{chord3}'")
    print(f"Entrada lyric:  '{lyric3}'")
    print(f"Salida chord:   '{result_chord3}'")
    print(f"Salida lyric:   '{result_lyric3}'")
    
    # Verificación normalización
    if "C" in result_chord3 and "C7" in result_chord3:
        print("✅ Normalización correcta: DO->C, DO7->C7")
    else:
        print("❌ ERROR en normalización")
    
    # Caso 4: Múltiples acordes juntos
    print("\n📌 Caso 4: Múltiples acordes consecutivos")
    chord4 = "FA    DO  FA    DO SOL    DO"
    lyric4 = "Brillará, brillará sin cesar."
    
    result_chord4, result_lyric4 = fp.align_chord_over_lyric(chord4, lyric4)
    
    print(f"Entrada chord:  '{chord4}'")
    print(f"Entrada lyric:  '{lyric4}'")
    print(f"Salida chord:   '{result_chord4}'")
    print(f"Salida lyric:   '{result_lyric4}'")
    
    # Contar espacios entre acordes
    acordes_salida = result_chord4.split()
    if len(acordes_salida) >= 6:
        print(f"✅ {len(acordes_salida)} acordes separados correctamente")
    else:
        print(f"❌ Solo {len(acordes_salida)} acordes (esperaba 6)")
    
    # Caso 5: Test con tabs
    print("\n📌 Caso 5: Línea con tabs")
    chord5 = "Dm\t\t\tA7"
    lyric5 = "BAUTIZAME SEÑOR CON TU ESPÍRITU"
    
    result_chord5, result_lyric5 = fp.align_chord_over_lyric(chord5, lyric5)
    
    print(f"Entrada chord:  '{chord5}' (con tabs)")
    print(f"Entrada lyric:  '{lyric5}'")
    print(f"Salida chord:   '{result_chord5}'")
    print(f"Salida lyric:   '{result_lyric5}'")
    
    if "\t" not in result_chord5:
        print("✅ Tabs convertidos a espacios")
    else:
        print("❌ Tabs aún presentes")


# ==============================================================================
# TEST DE INTEGRACIÓN COMPLETA
# ==============================================================================

def test_full_song_reconstruction():
    """Test de reconstrucción completa de canción"""
    print("\n" + "="*70)
    print("🔍 TEST DE INTEGRACIÓN: Canción completa")
    print("="*70)
    
    fp = FileProcessor()
    
    # Canción de ejemplo con ambos formatos
    song_text = """Notacion americana
  Dm                     A7
BAUTIZAME SEÑOR CON TU ESPÍRITU
                        Dm
BAUTIZAME SEÑOR CON TU ESPIRITU
  Dm                     A7
BAUTIZAME SEÑOR CON TU ESPIRITU
                       Dm  D7
BAUTIZAME, BAUTIZAME SEÑOR

Notacion tradicional
DO                  DO7
Esta es la luz de Cristo,
FA              DO
yo la haré brillar."""
    
    print("\n📄 TEXTO ORIGINAL:")
    print(song_text)
    
    reconstructed = fp._reconstruct_fixedwidth_song(song_text)
    
    print("\n📄 TEXTO RECONSTRUIDO:")
    print(reconstructed)
    
    # Verificaciones
    print("\n📊 VERIFICACIONES:")
    
    checks = [
        ("Dm D7" in reconstructed, "Tokens 'Dm D7' separados"),
        ("C" in reconstructed and "C7" in reconstructed, "Normalización DO->C, DO7->C7"),
        ("F" in reconstructed, "Normalización FA->F"),
        (reconstructed.count("\n") > 5, "Estructura con múltiples líneas"),
    ]
    
    for passed, description in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {description}")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("🚀 INICIANDO DEPURACIÓN")
    print()
    
    # Tests originales
    test_normalize_traditional()
    print()
    test_is_chord_line()
    print()
    test_format_text()
    print()
    test_specific_cases()
    
    # Nuevos tests específicos
    test_align_chord_over_lyric()
    test_full_song_reconstruction()
    
    print("\n" + "="*70)
    print("✅ DEPURACIÓN COMPLETADA")
    print("="*70)
