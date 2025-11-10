"""
Tests para endpoints del sistema (health check y root).
"""

import pytest
from fastapi.testclient import TestClient


class TestSystemEndpoints:
    """Tests para endpoints del sistema"""

    def test_health_check(self, client: TestClient, test_settings):
        """Test del endpoint de health check"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data
        assert "environment" in data
        # El environment puede ser testing o development dependiendo de la configuración
        assert data["environment"] in ["testing", "development"]

    def test_root_endpoint(self, client: TestClient):
        """Test del endpoint raíz"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        assert data["docs"] == "/api/v1/docs"
        assert data["health"] == "/health"

    @pytest.mark.integration
    def test_api_docs_available(self, client: TestClient):
        """Test que la documentación de OpenAPI esté disponible"""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200

        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
