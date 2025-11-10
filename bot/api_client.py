"""
Cliente HTTP para comunicarse con el backend API
"""
import httpx
from typing import Optional, Dict, Any
from bot.config import config


class APIClient:
    """Cliente para hacer llamadas al backend API"""

    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.timeout = 30.0

    async def get(self, endpoint: str, params: Optional[Dict] = None, token: Optional[str] = None) -> Dict[Any, Any]:
        """Realiza una petición GET"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    async def post(self, endpoint: str, data: Dict, token: Optional[str] = None) -> Dict[Any, Any]:
        """Realiza una petición POST"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    # Métodos específicos para cada endpoint

    async def login(self, username: str, password: str) -> Dict[Any, Any]:
        """Login en el sistema"""
        data = {"username": username, "password": password}
        return await self.post("/auth/login", data)

    async def get_proyectos(self, token: str, page: int = 1) -> Dict[Any, Any]:
        """Obtiene lista de proyectos"""
        return await self.get("/proyectos", params={"page": page, "page_size": 10}, token=token)

    async def get_proyecto_by_codigo(self, codigo: str, token: str) -> Optional[Dict[Any, Any]]:
        """Obtiene un proyecto por código"""
        try:
            return await self.get(f"/proyectos/codigo/{codigo}", token=token)
        except httpx.HTTPStatusError:
            return None

    async def get_tareas(
        self,
        token: str,
        proyecto_id: Optional[str] = None,
        estado: Optional[str] = None,
        page: int = 1
    ) -> Dict[Any, Any]:
        """Obtiene lista de tareas"""
        params = {"page": page, "page_size": 10}
        if proyecto_id:
            params["proyecto_id"] = proyecto_id
        if estado:
            params["estado"] = estado
        return await self.get("/tareas", params=params, token=token)

    async def get_mis_tareas(self, token: str) -> Dict[Any, Any]:
        """Obtiene las tareas asignadas al usuario actual"""
        return await self.get("/tareas/mis-tareas", token=token)

    async def get_tareas_hoy(self, token: str) -> list:
        """Obtiene las tareas que vencen hoy"""
        response = await self.get("/tareas/hoy", token=token)
        return response if isinstance(response, list) else []


# Instancia global del cliente API
api_client = APIClient()
