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
    def get_estadisticas(self) -> Dict:
        """Obtener estadísticas del sistema"""
        endpoint = "estadisticas.php"
        result = self._make_request(endpoint)
        return result.get('data', {}) if result.get('success') else {}

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
        
# Instancia global para usar en la app
database = DatabaseManager("https://cincomasuno.ar/api_cancionero_desk")