"""
Test de depuración para file_processor.py
Agrega test específico para _normalize_traditional_to_american
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.file_processor import FileProcessor

def test_normalize_capitalization():
    """Test de capitalización correcta en normalización"""
    print("="*70)
    print("🔍 TEST: Capitalización en _normalize_traditional_to_american()")
    print("="*70)
    
    fp = FileProcessor()
    
    test_cases = [
        # Acordes menores (debe ser 'm' minúscula)
        ("DOm", "Cm", "DO menor"),
        ("REm", "Dm", "RE menor"),
        ("LAm", "Am", "LA menor"),
        ("SIm", "Bm", "SI menor"),
        
        # Con séptima menor
        ("DOm7", "Cm7", "DO menor séptima"),
        ("REm7", "Dm7", "RE menor séptima"),
        
        # Mayores con séptima (solo número)
        ("DO7", "C7", "DO séptima"),
        ("SOL7", "G7", "SOL séptima"),
        
        # Mayor explícito
        ("DOmaj7", "Cmaj7", "DO mayor séptima"),
        ("SOLmaj", "Gmaj", "SOL mayor"),
        
        # Con alteraciones
        ("DO#m", "C#m", "DO sostenido menor"),
        ("REb", "Db", "RE bemol"),
        ("FA#", "F#", "FA sostenido"),
        
        # Básicos
        ("DO", "C", "DO mayor"),
        ("RE", "D", "RE mayor"),
        ("MI", "E", "MI mayor"),
        ("FA", "F", "FA mayor"),
        ("SOL", "G", "SOL mayor"),
        ("LA", "A", "LA mayor"),
        ("SI", "B", "SI mayor"),
        
        # Americanos ya normalizados
        ("Cm", "Cm", "Ya americano menor"),
        ("C7", "C7", "Ya americano séptima"),
        ("Cmaj7", "Cmaj7", "Ya americano maj7"),
    ]
    
    passed = 0
    failed = 0
    
    for input_chord, expected, description in test_cases:
        result = fp._normalize_traditional_to_american(input_chord)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} '{input_chord:8}' -> '{result:8}' (esperaba: '{expected:8}') | {description}")
    
    print(f"\n📊 Resultados: {passed}/{len(test_cases)} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    test_normalize_capitalization()