"""
Test de diagnóstico para procesar archivo DOCX completo
Archivo: Al altar del Señor.docx
Guardar como: tests/test_al_altar_docx.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.file_processor import FileProcessor

def test_process_docx_file():
    """Test completo del procesamiento de Al altar del Señor.docx"""
    print("="*70)
    print("🔍 TEST: Procesamiento de Al altar del Señor.docx")
    print("="*70)
    
    # Ruta al archivo DOCX (ajustar según tu estructura)
    file_path = "tests/Al altar del Señor.docx"
    
    # Verificar que existe el archivo
    if not os.path.exists(file_path):
        print(f"❌ ERROR: No se encuentra el archivo: {file_path}")
        print(f"   Buscando en directorio actual: {os.getcwd()}")
        
        # Buscar en directorios comunes
        possible_paths = [
            "Al altar del Señor.docx",
            "../Al altar del Señor.docx",
            "tests/test_files/Al altar del Señor.docx",
            "../tests/test_files/Al altar del Señor.docx",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                print(f"✅ Encontrado en: {file_path}")
                break
        else:
            print("\n⚠️  Por favor, coloca el archivo en alguna de estas ubicaciones:")
            for path in possible_paths:
                print(f"   - {os.path.abspath(path)}")
            return
    
    print(f"\n📄 Procesando archivo: {file_path}")
    print("="*70)
    
    # Crear procesador
    fp = FileProcessor(db_manager=None)
    
    # Opciones de procesamiento
    options = {
        'use_pdfplumber': True,
        'extract_chords': True
    }
    
    print("\n🔄 PASO 1: Procesando archivo DOCX...")
    print("-"*70)
    
    result = fp._process_docx_file(file_path, options)
    
    if not result.get('success'):
        print(f"❌ ERROR: {result.get('error')}")
        return
    
    print("✅ Archivo procesado exitosamente")
    print(f"   Tipo: {result.get('file_type')}")
    print(f"   Procesado con: {result.get('processed_with')}")
    
    # Mostrar texto extraído
    extracted_text = result.get('extracted_text', '')
    print(f"\n📄 TEXTO EXTRAÍDO ({len(extracted_text)} caracteres):")
    print("-"*70)
    print(extracted_text[:500])  # Primeros 500 caracteres
    if len(extracted_text) > 500:
        print(f"\n... ({len(extracted_text) - 500} caracteres más)")
    
    # Verificar canciones encontradas
    songs = result.get('songs_found', [])
    print(f"\n🎵 CANCIONES ENCONTRADAS: {len(songs)}")
    print("-"*70)
    
    if not songs:
        print("❌ No se encontraron canciones")
        return
    
    # Analizar primera canción
    song = songs[0]
    print(f"\n📋 CANCIÓN 1:")
    print(f"   Título: {song.get('titulo')}")
    print(f"   Artista: {song.get('artista')}")
    print(f"   Tono: {song.get('tono_original')}")
    print(f"   Estado: {song.get('estado')}")
    
    # Mostrar letra formateada
    letra = song.get('letra', '')
    print(f"\n📝 LETRA FORMATEADA ({len(letra)} caracteres):")
    print("="*70)
    print(letra)
    print("="*70)
    
    # Análisis detallado de la letra
    print("\n🔍 ANÁLISIS DE FORMATO:")
    print("-"*70)
    
    lines = letra.split('\n')
    print(f"   Total de líneas: {len(lines)}")
    
    # Contar líneas de acordes vs letra
    chord_lines = 0
    lyric_lines = 0
    empty_lines = 0
    
    for line in lines:
        if not line.strip():
            empty_lines += 1
        elif fp._is_chord_line(line):
            chord_lines += 1
        else:
            lyric_lines += 1
    
    print(f"   Líneas de acordes: {chord_lines}")
    print(f"   Líneas de letra: {lyric_lines}")
    print(f"   Líneas vacías: {empty_lines}")
    
    # Detectar pares de acorde+letra
    print(f"\n🎸 DETECCIÓN DE PARES ACORDE+LETRA:")
    print("-"*70)
    
    pares_detectados = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if fp._is_chord_line(line) and i + 1 < len(lines):
            next_line = lines[i + 1]
            if not fp._is_chord_line(next_line) and next_line.strip():
                pares_detectados += 1
                print(f"\n   Par #{pares_detectados}:")
                print(f"   Acordes: {line}")
                print(f"   Letra:   {next_line}")
                i += 2
                continue
        i += 1
    
    print(f"\n   Total de pares detectados: {pares_detectados}")
    
    # Verificar normalización de acordes
    print(f"\n🔤 VERIFICACIÓN DE NORMALIZACIÓN:")
    print("-"*70)
    
    checks = [
        ("Em" in letra, "Em presente"),
        ("D" in letra, "D presente"),
        ("G" in letra, "G presente"),
        ("B7" in letra, "B7 presente"),
        ("DO" not in letra, "DO normalizado (no presente)"),
        ("RE" not in letra, "RE normalizado (no presente)"),
        ("MI" not in letra, "MI normalizado (no presente)"),
    ]
    
    for passed, description in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {description}")
    
    # Verificar espaciado
    print(f"\n📏 VERIFICACIÓN DE ESPACIADO:")
    print("-"*70)
    
    # Buscar líneas con múltiples espacios consecutivos (indicador de alineación)
    lines_with_spacing = 0
    for line in lines:
        if '  ' in line:  # 2 o más espacios
            lines_with_spacing += 1
    
    print(f"   Líneas con espaciado múltiple: {lines_with_spacing}/{len(lines)}")
    
    if lines_with_spacing > 0:
        print(f"   ✅ Se preservó el espaciado para alineación")
    else:
        print(f"   ⚠️  No se detectó espaciado múltiple (posible problema)")
    
    # Verificar espacios no rompibles
    non_breaking_spaces = letra.count('\u00A0')
    print(f"   Espacios no rompibles (\\u00A0): {non_breaking_spaces}")
    
    if non_breaking_spaces > 0:
        print(f"   ✅ Se usaron espacios no rompibles")
    else:
        print(f"   ⚠️  No se detectaron espacios no rompibles")


def test_reconstruct_with_real_content():
    """Test de _reconstruct_fixedwidth_song con contenido real"""
    print("\n" + "="*70)
    print("🔍 TEST: _reconstruct_fixedwidth_song() con contenido real")
    print("="*70)
    
    fp = FileProcessor(db_manager=None)
    
    # Simular texto extraído del DOCX
    test_song = """Al altar del Señor
Em D     G               B7                  Em
Al altar del Señor vamos con amor
D                 G            B7                  Em
a entregar al Señor lo que Él nos dio."""
    
    print("\n📄 ENTRADA:")
    print(test_song)
    print("\n" + "="*70)
    
    print("\n🔄 Ejecutando _reconstruct_fixedwidth_song()...")
    result = fp._reconstruct_fixedwidth_song(test_song)
    
    print("\n📄 SALIDA:")
    print("="*70)
    print(result)
    print("="*70)
    
    # Verificaciones
    lines = result.split('\n')
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Líneas de entrada: {len(test_song.split(chr(10)))}")
    print(f"   Líneas de salida: {len(lines)}")
    
    # Contar acordes normalizados
    normalized_chords = sum(1 for line in lines if any(chord in line for chord in ['Em', 'D', 'G', 'B7']))
    print(f"   Líneas con acordes normalizados: {normalized_chords}")


if __name__ == "__main__":
    print("🚀 INICIANDO TEST DE Al altar del Señor.docx\n")
    
    # Test principal
    test_process_docx_file()
    
    # Test complementario
    test_reconstruct_with_real_content()
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETADO")
    print("="*70)
    print("\n💡 INSTRUCCIONES:")
    print("   1. Coloca 'Al altar del Señor.docx' en la carpeta tests/")
    print("   2. Ejecuta: python tests/test_al_altar_docx.py")
    print("   3. Revisa la salida para verificar:")
    print("      - ✅ Acordes normalizados (Em, D, G, B7)")
    print("      - ✅ Pares acorde+letra detectados")
    print("      - ✅ Espaciado preservado")
    print("      - ✅ Espacios no rompibles usados")
    print("="*70)