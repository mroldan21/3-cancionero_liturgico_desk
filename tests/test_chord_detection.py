"""
Test específico para detección de acordes tradicionales
Guardar como: tests/test_chord_detection.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.file_processor import FileProcessor

def test_is_valid_chord_token():
    """Test de validación de tokens individuales"""
    print("="*70)
    print("🔍 TEST: _is_valid_chord_token()")
    print("="*70)
    
    fp = FileProcessor()
    
    test_cases = [
        # Americanos básicos
        ("C", True, "Acorde americano básico"),
        ("Dm", True, "Acorde menor americano"),
        ("F#", True, "Acorde con sostenido"),
        ("Bb", True, "Acorde con bemol"),
        
        # Americanos complejos
        ("C7", True, "Acorde con séptima"),
        ("Gmaj7", True, "Acorde mayor con séptima"),
        ("Asus4", True, "Acorde suspendido"),
        
        # Tradicionales básicos
        ("DO", True, "Acorde tradicional básico"),
        ("REm", True, "Acorde menor tradicional"),
        ("FA#", True, "Tradicional con sostenido"),
        ("SIb", True, "Tradicional con bemol"),
        
        # Tradicionales complejos ← CRÍTICO
        ("DO7", True, "Tradicional con séptima"),
        ("SOL7", True, "SOL con séptima"),
        ("LAmaj7", True, "LA mayor con séptima"),
        ("MIm7", True, "MI menor con séptima"),
        
        # No acordes
        ("Esta", False, "Palabra común"),
        ("SEÑOR", False, "Palabra en mayúsculas"),
        ("123", False, "Solo números"),
    ]
    
    passed = 0
    failed = 0
    
    for token, expected, description in test_cases:
        result = fp._is_valid_chord_token(token)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            
        print(f"{status} '{token:10}' -> {result:5} (esperaba: {expected:5}) | {description}")
    
    print(f"\n📊 Resultados: {passed} passed, {failed} failed")
    return failed == 0


def test_is_chord_line():
    """Test de detección de líneas de acordes"""
    print("\n" + "="*70)
    print("🔍 TEST: _is_chord_line()")
    print("="*70)
    
    fp = FileProcessor()
    
    test_cases = [
        # Acordes americanos
        ("Dm                     A7", True, "Americanos con espacios"),
        ("C  G  Am  F", True, "Múltiples americanos"),
        
        # Acordes tradicionales ← CRÍTICO
        ("DO                  DO7", True, "Tradicionales con espacios"),
        ("FA              DO", True, "Dos tradicionales"),
        ("SOL7         DO", True, "SOL7 y DO"),
        ("DO  RE  MI  FA  SOL", True, "Múltiples tradicionales"),
        
        # Mixtos
        ("DO  C  FA  G", True, "Mezcla tradicional/americano"),
        
        # Letra (NO acordes)
        ("BAUTIZAME SEÑOR CON TU ESPÍRITU", False, "Letra en mayúsculas"),
        ("Esta es la luz de Cristo,", False, "Letra normal"),
        ("yo la haré brillar.", False, "Letra con acentos"),
        
        # Casos límite
        ("", False, "Línea vacía"),
        ("DO", True, "Un solo acorde"),
        ("Esta DO es", False, "Acordes mezclados con letra"),
    ]
    
    passed = 0
    failed = 0
    
    for line, expected, description in test_cases:
        result = fp._is_chord_line(line)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        display_line = line[:40] + "..." if len(line) > 40 else line
        result_label = "ACORDES" if result else "LETRA"
        expected_label = "ACORDES" if expected else "LETRA"
        
        print(f"{status} '{display_line:45}' -> {result_label:7} (esperaba: {expected_label:7}) | {description}")
    
    print(f"\n📊 Resultados: {passed} passed, {failed} failed")
    return failed == 0


def test_reconstruct_song():
    """Test de reconstrucción completa"""
    print("\n" + "="*70)
    print("🔍 TEST: _reconstruct_fixedwidth_song()")
    print("="*70)
    
    fp = FileProcessor()
    
    # Canción con ambos formatos
    test_song = """DO                  DO7
Esta es la luz de Cristo,
FA              DO
yo la haré brillar.

SOL7         DO
Brillará sin cesar."""
    
    print("\n📄 ENTRADA:")
    print(test_song)
    print("\n🔄 PROCESANDO...")
    
    result = fp._reconstruct_fixedwidth_song(test_song)
    
    print("\n📄 SALIDA:")
    print(result)
    
    # Verificaciones
    checks = [
        ("C" in result and "C7" in result, "DO/DO7 normalizados a C/C7"),
        ("F" in result, "FA normalizado a F"),
        ("G7" in result, "SOL7 normalizado a G7"),
        (result.count("\n") >= 4, "Múltiples líneas preservadas"),
    ]
    
    print("\n📊 VERIFICACIONES:")
    all_passed = True
    for passed, description in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {description}")
        if not passed:
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE DETECCIÓN DE ACORDES\n")
    
    results = []
    results.append(("_is_valid_chord_token", test_is_valid_chord_token()))
    results.append(("_is_chord_line", test_is_chord_line()))
    results.append(("_reconstruct_fixedwidth_song", test_reconstruct_song()))
    
    print("\n" + "="*70)
    print("📊 RESUMEN FINAL")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n🎉 TODOS LOS TESTS PASARON")
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON")