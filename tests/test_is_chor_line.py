import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.file_processor import FileProcessor

# Test de diagnóstico
fp = FileProcessor()

test_lines = [
    "DO                  DO7",
    "FA              DO", 
    "SOL7         DO",
]

for line in test_lines:
    tokens = line.split()
    print(f"\nLínea: '{line}'")
    print(f"Tokens: {tokens}")
    
    for token in tokens:
        valid = fp._is_valid_chord_token(token)
        print(f"  '{token}' -> {valid}")
    
    is_chord = fp._is_chord_line(line)
    print(f"  Resultado _is_chord_line: {is_chord}")