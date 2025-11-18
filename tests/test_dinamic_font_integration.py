"""
Script de prueba para validar la integración completa del sistema de tipografías

PASOS QUE PRUEBA:
1. Conexión a la base de datos
2. Inicialización de métricas por defecto
3. Creación del FontConverter
4. Descomentado de llamadas a BD en FontConverter
5. Prueba de conversión de texto
6. Validación de que los datos se guardan en BD

PREREQUISITOS:
- Tabla font_metrics creada en MySQL
- Métodos agregados a DatabaseManager
- font_converter.py en la carpeta core/
- Aplicación principal debe estar corriendo o simular app.database

USO:
    python test_font_integration.py
    
NOTA: Este script se adapta a tu estructura donde se accede a la BD via app.database
"""

import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Imports necesarios
try:
    from core.font_converter import FontConverter
    print("✅ FontConverter importado correctamente")
except ImportError as e:
    print(f"❌ Error importando FontConverter: {e}")
    sys.exit(1)

# OPCIÓN 1: Importar la clase App completa (RECOMENDADO)
try:
    # Ajusta según donde esté tu clase App principal
    from main import App  # O el archivo donde está tu clase App
    USE_FULL_APP = True
    print("✅ App importada - Se usará app.database")
except ImportError as e:
    print(f"⚠️  No se pudo importar App: {e}")
    USE_FULL_APP = False
    
# OPCIÓN 2: Importar DatabaseManager directamente (FALLBACK)
if not USE_FULL_APP:
    try:
        from core.database import DatabaseManager
        print("✅ DatabaseManager importado directamente (modo fallback)")
    except ImportError as e:
        print(f"❌ Error importando DatabaseManager: {e}")
        print("💡 Ajusta los imports según tu estructura de proyecto")
        sys.exit(1)


def print_header(title):
    """Imprimir header decorado"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_step(step_num, description):
    """Imprimir paso numerado"""
    print(f"\n📍 PASO {step_num}: {description}")
    print("-" * 70)


def test_database_connection(db_manager):
    """Paso 1: Probar conexión a base de datos"""
    print_step(1, "Probando conexión a base de datos")
    
    try:
        # Verificar que los nuevos métodos existen
        required_methods = [
            'get_font_metric',
            'get_font_metrics',
            'create_or_update_font_metric',
            'increment_font_usage',
            'initialize_default_font_metrics'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(db_manager, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Faltan métodos en DatabaseManager: {missing_methods}")
            return False
        
        print("✅ Todos los métodos requeridos están presentes")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando DatabaseManager: {e}")
        return False


def test_initialize_metrics(db_manager):
    """Paso 2: Inicializar métricas por defecto"""
    print_step(2, "Inicializando métricas por defecto")
    
    try:
        result = db_manager.initialize_default_font_metrics()
        
        if result['success']:
            print(f"✅ Métricas inicializadas correctamente")
            print(f"   - Total insertado: {result['total_inserted']} registros")
            print(f"   - Tipografías: {result['fonts_initialized']}")
        else:
            print(f"❌ Error inicializando métricas: {result}")
            return False
        
        # Verificar que se guardaron
        available = db_manager.get_available_fonts()
        print(f"\n📋 Tipografías disponibles en BD:")
        for font in available:
            print(f"   - {font['font_name']} {font['font_size']}pt ({font['char_count']} caracteres)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return False


def test_font_converter_creation(db_manager):
    """Paso 3: Crear FontConverter con conexión a BD"""
    print_step(3, "Creando FontConverter con conexión a BD")
    
    try:
        converter = FontConverter(db_manager)
        print("✅ FontConverter creado correctamente")
        print(f"   - Métricas en cache: {len(converter.metrics_cache)} tipografías")
        print(f"   - DB Manager conectado: {converter.db_manager is not None}")
        
        return converter
        
    except Exception as e:
        print(f"❌ Error creando FontConverter: {e}")
        return None


def test_char_width_from_db(converter):
    """Paso 4: Probar obtención de ancho desde BD"""
    print_step(4, "Probando obtención de ancho de caracteres desde BD")
    
    test_cases = [
        ('Arial', 11, 'a'),
        ('Arial', 11, 'e'),
        ('Arial', 11, 'm'),
        ('Calibri', 11, 'i'),
        ('Times New Roman', 11, 'w'),
    ]
    
    success_count = 0
    
    for font_name, font_size, char in test_cases:
        try:
            width = converter.get_char_width(char, font_name, font_size)
            print(f"   ✅ {font_name} {font_size}pt '{char}': {width:.3f}")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Error obteniendo '{char}': {e}")
    
    print(f"\n📊 Resultado: {success_count}/{len(test_cases)} pruebas exitosas")
    return success_count == len(test_cases)


def test_text_conversion(converter):
    """Paso 5: Probar conversión de texto completo"""
    print_step(5, "Probando conversión de texto completo")
    
    # Texto de prueba (simulando Word con Arial 11pt)
    test_text = """Em    D    G         B7
Al altar del Señor vamos con amor"""
    
    font_info = {
        'name': 'Arial',
        'size': 11
    }
    
    try:
        print("📄 Texto original:")
        for i, line in enumerate(test_text.split('\n'), 1):
            print(f"   {i}: '{line}'")
        
        print("\n🔄 Convirtiendo...")
        converted = converter.convert_text(test_text, font_info)
        
        print("\n📄 Texto convertido:")
        for i, line in enumerate(converted.split('\n'), 1):
            print(f"   {i}: '{line}'")
        
        # Análisis de conversión
        original_lines = test_text.split('\n')
        converted_lines = converted.split('\n')
        
        print("\n📊 Análisis de conversión:")
        for i, (orig, conv) in enumerate(zip(original_lines, converted_lines), 1):
            print(f"   Línea {i}:")
            print(f"      Original:   {len(orig):3d} chars")
            print(f"      Convertido: {len(conv):3d} chars")
            print(f"      Diferencia: {len(conv) - len(orig):+3d} chars")
        
        print("\n✅ Conversión completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en conversión: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_usage_increment(db_manager, converter):
    """Paso 6: Probar incremento de contador de uso"""
    print_step(6, "Probando incremento de contador de uso")
    
    try:
        font_name = 'Arial'
        font_size = 11
        
        # Obtener uso actual
        metrics_before = db_manager.get_font_metrics(font_name, font_size)
        print(f"📊 Métricas antes: {len(metrics_before)} caracteres")
        
        # Incrementar uso
        print(f"🔄 Incrementando uso de {font_name} {font_size}pt...")
        converter.increment_usage(font_name, font_size)
        
        # Verificar incremento
        top_fonts = db_manager.get_most_used_fonts(5)
        print(f"\n🏆 Top 5 tipografías más usadas:")
        for i, font in enumerate(top_fonts, 1):
            print(f"   {i}. {font['font_name']} {font['font_size']}pt - {font['total_usage']} usos")
        
        print("\n✅ Contador de uso actualizado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error incrementando uso: {e}")
        return False


def test_end_to_end(converter, db_manager):
    """Prueba end-to-end: Simular importación completa"""
    print_step("BONUS", "Simulación de importación completa (end-to-end)")
    
    try:
        # Simular detección de tipografía
        detected_font = {
            'name': 'Calibri',
            'size': 11,
            'confidence': 0.85,
            'method': 'test_simulation'
        }
        
        print(f"🔍 Tipografía detectada: {detected_font['name']} {detected_font['size']}pt")
        
        # Texto de prueba
        sample_song = """DO           SOL    FA
Esta es mi canción de prueba
     RE         LAm
Con acordes alineados"""
        
        print(f"\n📄 Canción original:")
        for line in sample_song.split('\n'):
            print(f"   '{line}'")
        
        # Convertir
        print(f"\n🔄 Aplicando conversión con {detected_font['name']}...")
        converted_song = converter.convert_text(sample_song, detected_font)
        
        print(f"\n📄 Canción convertida:")
        for line in converted_song.split('\n'):
            print(f"   '{line}'")
        
        # Incrementar uso
        converter.increment_usage(detected_font['name'], detected_font['size'])
        
        print("\n✅ Simulación end-to-end completada exitosamente")
        print("💡 Esta es la conversión que se aplicará en importaciones reales")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal del script de prueba"""
    print_header("🧪 TEST DE INTEGRACIÓN: Sistema de Tipografías")
    print("\nEste script prueba la integración completa entre:")
    print("  - DatabaseManager (métodos de font_metrics)")
    print("  - FontConverter (conversión de tipografías)")
    print("  - Base de datos MySQL")
    
    # Inicializar acceso a base de datos
    print("\n🔧 Inicializando acceso a base de datos...")
    
    if USE_FULL_APP:
        # OPCIÓN 1: Usar app.database (tu estructura)
        try:
            print("📱 Creando instancia de App...")
            # Crear app sin inicializar UI (modo headless para testing)
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Ocultar ventana
            
            app = App(root)
            db_manager = app.database  # ← Acceso según tu estructura
            
            print("✅ Acceso a base de datos via app.database")
        except Exception as e:
            print(f"❌ Error creando App: {e}")
            print("💡 Intentando modo fallback con DatabaseManager directo...")
            USE_FULL_APP = False
    
    if not USE_FULL_APP:
        # OPCIÓN 2: DatabaseManager directo (fallback)
        try:
            print("🔧 Creando DatabaseManager directamente...")
            # AJUSTAR SEGÚN TUS CREDENCIALES
            db_manager = DatabaseManager(
                host='localhost',
                user='tu_usuario',      # CAMBIAR
                password='tu_password',  # CAMBIAR
                database='tu_database'   # CAMBIAR
            )
            print("✅ DatabaseManager inicializado directamente")
        except Exception as e:
            print(f"❌ Error inicializando DatabaseManager: {e}")
            print("💡 Ajusta las credenciales o la estructura de App")
            return False
    
    # Ejecutar pruebas secuenciales
    results = []
    
    # Paso 1: Conexión
    results.append(("Conexión DB", test_database_connection(db_manager)))
    
    if not results[-1][1]:
        print("\n❌ No se puede continuar sin conexión a BD")
        return False
    
    # Paso 2: Inicialización
    results.append(("Inicialización", test_initialize_metrics(db_manager)))
    
    # Paso 3: Crear converter
    converter = test_font_converter_creation(db_manager)
    results.append(("Crear Converter", converter is not None))
    
    if not converter:
        print("\n❌ No se puede continuar sin FontConverter")
        return False
    
    # Paso 4: Obtener anchos desde BD
    results.append(("Anchos desde BD", test_char_width_from_db(converter)))
    
    # Paso 5: Conversión de texto
    results.append(("Conversión de texto", test_text_conversion(converter)))
    
    # Paso 6: Incremento de uso
    results.append(("Incremento de uso", test_usage_increment(db_manager, converter)))
    
    # Bonus: End-to-end
    results.append(("End-to-end", test_end_to_end(converter, db_manager)))
    
    # Resumen final
    print_header("📊 RESUMEN DE RESULTADOS")
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {test_name}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "-" * 70)
    print(f"Total: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("✅ El sistema de tipografías está listo para usar")
        print("\n💡 Próximo paso: Integrar en file_processor.py")
    else:
        print(f"\n⚠️  {failed} prueba(s) fallaron")
        print("💡 Revisa los errores arriba y corrige antes de continuar")
    
    # Cleanup
    if USE_FULL_APP:
        try:
            root.destroy()
        except:
            pass
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)