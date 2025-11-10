"""
Test de diagnóstico de _reconstruct_fixedwidth_song
Guardar como: tests/test_reconstruct_debug.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.file_processor import FileProcessor

def test_reconstruct_step_by_step():
    """Test paso a paso de la reconstrucción"""
    print("="*70)
    print("🔍 TEST: _reconstruct_fixedwidth_song() - PASO A PASO")
    print("="*70)
    
    fp = FileProcessor()
    
    # Caso simple
    test_song = """DO                  DO7
Esta es la luz de Cristo,
FA              DO
yo la haré brillar."""
    
    print("\n📄 ENTRADA:")
    print(test_song)
    print("\n" + "="*70)
    
    # Simular el proceso interno
    lines = [l.rstrip() for l in test_song.splitlines()]
    
    print("\n🔍 ANÁLISIS LÍNEA POR LÍNEA:")
    for i, line in enumerate(lines):
        print(f"\n[Línea {i}]: '{line}'")
        
        # Verificar si es línea vacía
        if not line.strip():
            print("  ↳ Línea vacía")
            continue
        
        # Verificar si es línea de acordes
        is_chord = fp._is_chord_line(line)
        print(f"  ↳ _is_chord_line(): {is_chord}")
        
        # Si es línea de acordes, verificar la siguiente
        if is_chord and i + 1 < len(lines):
            next_line = lines[i + 1]
            next_is_chord = fp._is_chord_line(next_line)
            print(f"  ↳ Siguiente línea: '{next_line}'")
            print(f"  ↳ Siguiente es acorde: {next_is_chord}")
            
            if not next_is_chord:
                print(f"  ✅ EMPAREJAMIENTO DETECTADO")
                print(f"     Acordes: {line}")
                print(f"     Letra:   {next_line}")
    
    print("\n" + "="*70)
    print("🔄 EJECUTANDO _reconstruct_fixedwidth_song()...")
    print("="*70)
    
    result = fp._reconstruct_fixedwidth_song(test_song)
    
    print("\n📄 SALIDA:")
    print(result)
    
    print("\n" + "="*70)
    print("📊 VERIFICACIÓN DE NORMALIZACIÓN:")
    print("="*70)
    
    checks = [
        ("DO" not in result or result.count("DO") < test_song.count("DO"), 
         "DO normalizado (reducido o eliminado)"),
        ("C" in result, "C presente (normalización de DO)"),
        ("C7" in result, "C7 presente (normalización de DO7)"),
        ("FA" not in result or result.count("FA") < test_song.count("FA"),
         "FA normalizado (reducido o eliminado)"),
        ("F" in result, "F presente (normalización de FA)"),
    ]
    
    for passed, description in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {description}")


def test_align_chord_over_lyric_direct():
    """Test directo de align_chord_over_lyric"""
    print("\n" + "="*70)
    print("🔍 TEST: align_chord_over_lyric() - DIRECTO")
    print("="*70)
    
    fp = FileProcessor()
    
    test_cases = [
        ("DO                  DO7", "Esta es la luz de Cristo,"),
        ("FA              DO", "yo la haré brillar."),
        ("SOL7         DO", "Brillará sin cesar."),
    ]
    
    for chord_line, lyric_line in test_cases:
        print(f"\n📌 Entrada:")
        print(f"   Acordes: '{chord_line}'")
        print(f"   Letra:   '{lyric_line}'")
        
        chord_aligned, lyric_padded = fp.align_chord_over_lyric(chord_line, lyric_line)
        
        print(f"📤 Salida:")
        print(f"   Acordes: '{chord_aligned}'")
        print(f"   Letra:   '{lyric_padded}'")
        
        # Verificar normalización
        if "DO" in chord_line:
            has_c = "C" in chord_aligned
            print(f"   {'✅' if has_c else '❌'} Normalización DO→C: {has_c}")
        
        if "FA" in chord_line:
            has_f = "F" in chord_aligned
            print(f"   {'✅' if has_f else '❌'} Normalización FA→F: {has_f}")
        
        if "SOL" in chord_line:
            has_g = "G" in chord_aligned
            print(f"   {'✅' if has_g else '❌'} Normalización SOL→G: {has_g}")


if __name__ == "__main__":
    print("🚀 INICIANDO DIAGNÓSTICO DE RECONSTRUCCIÓN\n")
    
    test_reconstruct_step_by_step()
    test_align_chord_over_lyric_direct()
    
    print("\n" + "="*70)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("="*70)