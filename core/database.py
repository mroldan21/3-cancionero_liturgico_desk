import requests
import json
from typing import Dict, List, Optional, Any
import logging

class DatabaseManager:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Realizar petición a la API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=data, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, json=data, headers=headers)
            else:
                raise ValueError(f"Método no soportado: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error en petición {method} {url}: {e}")
            return {'success': False, 'error': str(e)}
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decodificando JSON: {e}")
            return {'success': False, 'error': 'Respuesta JSON inválida'}

    # ===== CANCIONES =====
    def get_canciones(self, filters: Dict = None) -> List[Dict]:
        """Obtener lista de canciones"""
        endpoint = "canciones.php"
        result = self._make_request(endpoint, 'GET', filters)
        return result.get('data', []) if result.get('success') else []


    def get_cancion(self, cancion_id: int) -> Optional[Dict]:
        """Obtener una canción por ID"""
        endpoint = f"canciones.php?id={cancion_id}"
        result = self._make_request(endpoint)
        return result.get('data') if result.get('success') else None

    def create_cancion(self, cancion_data: Dict) -> Dict:
        """Crear nueva canción"""
        endpoint = "canciones.php"
        return self._make_request(endpoint, 'POST', cancion_data)

    def update_cancion(self, cancion_id: int, cancion_data: Dict) -> Dict:
        """Actualizar canción existente"""
        endpoint = f"canciones.php?id={cancion_id}"
        return self._make_request(endpoint, 'PUT', cancion_data)

    def delete_cancion(self, cancion_id: int) -> Dict:
        """Eliminar canción"""
        endpoint = f"canciones.php?id={cancion_id}"
        return self._make_request(endpoint, 'DELETE')

    # ===== USUARIOS =====
    def get_usuarios(self) -> List[Dict]:
        """Obtener lista de usuarios"""
        endpoint = "usuarios.php"
        result = self._make_request(endpoint)
        return result.get('data', []) if result.get('success') else []

    def get_usuario(self, usuario_id: int) -> Optional[Dict]:
        """Obtener usuario por ID"""
        endpoint = f"usuarios.php?id={usuario_id}"
        result = self._make_request(endpoint)
        return result.get('data') if result.get('success') else None

    def create_usuario(self, usuario_data: Dict) -> Dict:
        """Crear nuevo usuario"""
        endpoint = "usuarios.php"
        return self._make_request(endpoint, 'POST', usuario_data)

    def update_usuario(self, usuario_id: int, usuario_data: Dict) -> Dict:
        """Actualizar usuario"""
        endpoint = f"usuarios.php?id={usuario_id}"
        return self._make_request(endpoint, 'PUT', usuario_data)

    def delete_usuario(self, usuario_id: int) -> Dict:
        """Eliminar usuario"""
        endpoint = f"usuarios.php?id={usuario_id}"
        return self._make_request(endpoint, 'DELETE')

    # ===== CATEGORÍAS =====
    def get_categorias(self) -> List[Dict]:
        """Obtener categorías"""
        endpoint = "categorias.php"
        result = self._make_request(endpoint)
        return result.get('data', []) if result.get('success') else []

    # ===== ESTADÍSTICAS =====
    # def get_estadisticas(self) -> Dict:
    #     """Obtener estadísticas del sistema"""
    #     endpoint = "estadisticas.php"
    #     result = self._make_request(endpoint)
    #     return result.get('data', {}) if result.get('success') else {}
    
    # En core/database.py, comenta o modifica el método get_estadisticas:

    def get_estadisticas(self) -> Dict:
        """Obtener estadísticas del sistema"""
        try:
            # Si el endpoint no existe, calcular estadísticas localmente
            canciones = self.get_canciones()
            categorias = self.get_categorias()
            
            return {
                'total_canciones': len(canciones),
                'total_categorias': len(categorias),
                'canciones_pendientes': len([c for c in canciones if c.get('estado') == 'pendiente']),
                'canciones_activas': len([c for c in canciones if c.get('estado') == 'activo']),
                'ultima_actualizacion': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
        
        # Opcional: si quieres intentar el endpoint primero
        # endpoint = "estadisticas.php"
        # result = self._make_request(endpoint)
        # return result.get('data', {}) if result.get('success') else {}

    # ===== BACKUPS =====
    def create_backup(self, tipo: str = 'completo') -> Dict:
        """Crear backup"""
        endpoint = "backup.php"
        return self._make_request(endpoint, 'POST', {'tipo': tipo})

    def get_backups(self) -> List[Dict]:
        """Obtener lista de backups"""
        endpoint = "backup.php"
        result = self._make_request(endpoint)
        return result.get('data', []) if result.get('success') else []

    def restore_backup(self, backup_id: int) -> Dict:
        """Restaurar backup"""
        endpoint = f"backup.php?id={backup_id}"
        return self._make_request(endpoint, 'POST')

    # ===== LOGS =====
    def get_logs(self, filters: Dict = None) -> List[Dict]:
        """Obtener logs del sistema"""
        endpoint = "logs.php"
        result = self._make_request(endpoint, 'GET', filters)
        return result.get('data', []) if result.get('success') else []

    def clear_logs(self) -> Dict:
        """Limpiar logs"""
        endpoint = "logs.php"
        return self._make_request(endpoint, 'DELETE')

    # ===== SISTEMA =====
    def get_configuracion(self) -> Dict:
        """Obtener configuración del sistema"""
        endpoint = "configuracion.php"
        result = self._make_request(endpoint)
        return result.get('data', {}) if result.get('success') else {}

    def update_configuracion(self, config_data: Dict) -> Dict:
        """Actualizar configuración del sistema"""
        endpoint = "configuracion.php"
        return self._make_request(endpoint, 'PUT', config_data)

    # ===== SINCRONIZACIÓN =====
    def sincronizar(self) -> Dict:
        """Sincronizar datos"""
        endpoint = "sincronizar.php"
        return self._make_request(endpoint, 'POST')

    def test_connection(self) -> bool:
        """Probar conexión con la API"""
        try:
            endpoint = "test.php"
            result = self._make_request(endpoint)
            return result.get('success', False)
        except:
            return False
        
    # ============================================================================
    # MÉTODOS PARA AGREGAR A DatabaseManager en database.py
    # ============================================================================

    # ===== FONT METRICS =====

    def get_font_metric(self, font_name: str, font_size: int, char: str) -> Optional[Dict]:
        """
        Obtener métrica de un carácter específico
        
        Args:
            font_name: Nombre de la tipografía (ej: 'Arial')
            font_size: Tamaño en puntos (ej: 11)
            char: Carácter a consultar (ej: 'a')
            
        Returns:
            Dict con los datos o None si no existe
        """
        endpoint = "font_metrics.php"
        params = {
            'action': 'get',
            'font_name': font_name,
            'font_size': font_size,
            'char': char
        }
        result = self._make_request(endpoint, 'GET', params)
        return result.get('data') if result.get('success') else None


    def get_font_metrics(self, font_name: str, font_size: int) -> Dict:
        """
        Obtener todas las métricas para una tipografía específica
        
        Args:
            font_name: Nombre de la tipografía
            font_size: Tamaño en puntos
            
        Returns:
            Dict {caracter: width_ratio} o {} si no hay métricas
        """
        endpoint = "font_metrics.php"
        params = {
            'action': 'list',
            'font_name': font_name,
            'font_size': font_size
        }
        result = self._make_request(endpoint, 'GET', params)
        return result.get('data', {}) if result.get('success') else {}


    def create_or_update_font_metric(self, font_name: str, font_size: int, 
                                    char: str, width_ratio: float) -> Dict:
        """
        Crear o actualizar métrica de un carácter
        
        Args:
            font_name: Nombre de la tipografía
            font_size: Tamaño en puntos
            char: Carácter
            width_ratio: Ancho relativo (float)
            
        Returns:
            Dict {'success': bool, 'message': str, 'data': dict}
        """
        endpoint = "font_metrics.php"
        data = {
            'action': 'create',
            'font_name': font_name,
            'font_size': font_size,
            'char': char,
            'width_ratio': width_ratio
        }
        return self._make_request(endpoint, 'POST', data)


    def bulk_create_font_metrics(self, font_name: str, font_size: int, 
                                char_metrics: Dict[str, float]) -> Dict:
        """
        Crear o actualizar múltiples métricas de una vez
        
        Args:
            font_name: Nombre de la tipografía
            font_size: Tamaño en puntos
            char_metrics: Dict {caracter: width_ratio}
            
        Returns:
            Dict {'success': bool, 'message': str, 'data': dict}
        """
        endpoint = "font_metrics.php"
        data = {
            'action': 'bulk',
            'font_name': font_name,
            'font_size': font_size,
            'metrics': char_metrics
        }
        return self._make_request(endpoint, 'POST', data)


    def increment_font_usage(self, font_name: str, font_size: int) -> Dict:
        """
        Incrementar contador de uso para una tipografía
        
        Args:
            font_name: Nombre de la tipografía
            font_size: Tamaño en puntos
            
        Returns:
            Dict {'success': bool, 'message': str, 'data': dict}
        """
        endpoint = "font_metrics.php"
        data = {
            'font_name': font_name,
            'font_size': font_size
        }
        return self._make_request(endpoint, 'PUT', data)


    def get_most_used_fonts(self, limit: int = 10) -> List[Dict]:
        """
        Obtener las tipografías más utilizadas
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de dicts [{'font_name', 'font_size', 'total_usage', 'last_used'}]
        """
        endpoint = "font_metrics.php"
        params = {
            'action': 'most_used',
            'limit': limit
        }
        result = self._make_request(endpoint, 'GET', params)
        return result.get('data', []) if result.get('success') else []


    def get_available_fonts(self) -> List[Dict]:
        """
        Obtener lista de todas las tipografías disponibles
        
        Returns:
            Lista de dicts [{'font_name', 'font_size', 'char_count'}]
        """
        endpoint = "font_metrics.php"
        params = {'action': 'available_fonts'}
        result = self._make_request(endpoint, 'GET', params)
        return result.get('data', []) if result.get('success') else []


    def delete_font_metrics(self, font_name: str, font_size: int) -> Dict:
        """
        Eliminar todas las métricas de una tipografía específica
        
        Args:
            font_name: Nombre de la tipografía
            font_size: Tamaño en puntos
            
        Returns:
            Dict {'success': bool, 'message': str, 'data': dict}
        """
        endpoint = f"font_metrics.php?font_name={font_name}&font_size={font_size}"
        return self._make_request(endpoint, 'DELETE')


    def initialize_default_font_metrics(self) -> Dict:
        """
        Pre-cargar métricas por defecto para tipografías comunes
        
        Returns:
            Dict con estadísticas de la inicialización
        """
        endpoint = "font_metrics.php"
        data = {'action': 'initialize'}
        result = self._make_request(endpoint, 'POST', data)
        
        if result.get('success'):
            self.logger.info(f"✅ Métricas inicializadas: {result.get('data', {})}")
        else:
            self.logger.error(f"❌ Error inicializando métricas: {result.get('message')}")
        
        return result


# Instancia global para usar en la app
database = DatabaseManager("https://cincomasuno.ar/api_cancionero_desk")






# ============================================================================
# SCRIPT DE TESTING (agregar al final del archivo database.py)
# ============================================================================

def test_font_metrics_api():
    """
    Función de prueba para validar los métodos de font_metrics
    Ejecutar: python database.py
    """
    print("="*70)
    print("🧪 TEST: API de Font Metrics")
    print("="*70)
    
    # Crear instancia del manager
    db = DatabaseManager("https://cincomasuno.ar/api_cancionero_desk")
    
    # Test 1: Inicializar métricas por defecto
    print("\n📦 Test 1: Inicializar métricas por defecto")
    result = db.initialize_default_font_metrics()
    print(f"   Resultado: {result.get('message')}")
    if result.get('data'):
        print(f"   Datos: {result['data']}")
    
    # Test 2: Obtener métrica específica
    print("\n📏 Test 2: Obtener métrica específica")
    metric = db.get_font_metric('Arial', 11, 'a')
    if metric:
        print(f"   ✅ Métrica encontrada: {metric}")
    else:
        print(f"   ❌ Métrica no encontrada")
    
    # Test 3: Obtener todas las métricas
    print("\n📚 Test 3: Obtener todas las métricas de Arial 11pt")
    metrics = db.get_font_metrics('Arial', 11)
    print(f"   ✅ Encontradas {len(metrics)} métricas")
    if metrics:
        print(f"   Ejemplo: {list(metrics.items())[:5]}")
    
    # Test 4: Crear/actualizar métrica individual
    print("\n✏️ Test 4: Crear/actualizar métrica")
    result = db.create_or_update_font_metric('Arial', 11, 'z', 0.55)
    print(f"   Resultado: {result.get('message')}")
    
    # Test 5: Crear múltiples métricas
    print("\n📝 Test 5: Crear métricas en bulk")
    test_metrics = {'x': 0.58, 'y': 0.54, 'ñ': 0.60}
    result = db.bulk_create_font_metrics('Arial', 11, test_metrics)
    print(f"   Resultado: {result.get('message')}")
    if result.get('data'):
        print(f"   Detalles: {result['data']}")
    
    # Test 6: Incrementar uso
    print("\n📈 Test 6: Incrementar uso")
    result = db.increment_font_usage('Arial', 11)
    print(f"   Resultado: {result.get('message')}")
    
    # Test 7: Tipografías más usadas
    print("\n🏆 Test 7: Tipografías más usadas")
    top_fonts = db.get_most_used_fonts(5)
    for i, font in enumerate(top_fonts, 1):
        print(f"   {i}. {font['font_name']} {font['font_size']}pt - {font['total_usage']} usos")
    
    # Test 8: Tipografías disponibles
    print("\n📋 Test 8: Tipografías disponibles")
    available = db.get_available_fonts()
    for font in available:
        print(f"   - {font['font_name']} {font['font_size']}pt ({font['char_count']} caracteres)")
    
    print("\n" + "="*70)
    print("✅ Tests completados")
    print("="*70)


# Agregar al final del archivo database.py
if __name__ == "__main__":
    test_font_metrics_api()