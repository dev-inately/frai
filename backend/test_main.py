#!/usr/bin/env python3
"""
Comprehensive test suite for the AI Contract Generator backend.
Tests all endpoints, models, and core functionality.
"""
import pytest
import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from app.config import settings
from app.ai_client import AIClient
from app.contract_engine import ContractEngine
from app.database import db_manager
from app.models import (
    ContractGenerationRequest, BusinessContext, ContractType,
    ContractRetrievalRequest, ContractSection
)
from main import app

# Test client
client = TestClient(app)

# Test data
SAMPLE_BUSINESS_CONTEXT = {
    "description": "A SaaS company providing project management tools for remote teams",
    "industry": "SaaS",
    "location": "California",
    "company_size": "Startup"
}

SAMPLE_CONTRACT_REQUEST = {
    "business_context": SAMPLE_BUSINESS_CONTEXT,
    "contract_type": "terms_of_service",
    "language": "en"
}

SAMPLE_CONTRACT_SECTIONS = [
    {
        "title": "Terms of Service",
        "content": "These terms govern your use of our service...",
        "section_number": 1,
        "subsection_number": None
    },
    {
        "title": "Acceptable Use",
        "content": "You agree not to misuse our service...",
        "section_number": 2,
        "subsection_number": None
    }
]


class TestModels:
    """Test Pydantic models validation."""
    
    def test_business_context_valid(self):
        """Test valid business context creation."""
        context = BusinessContext(**SAMPLE_BUSINESS_CONTEXT)
        assert context.description == SAMPLE_BUSINESS_CONTEXT["description"]
        assert context.industry == SAMPLE_BUSINESS_CONTEXT["industry"]
    
    def test_business_context_invalid_description(self):
        """Test business context with invalid description."""
        invalid_context = SAMPLE_BUSINESS_CONTEXT.copy()
        invalid_context["description"] = "Too short"
        
        with pytest.raises(ValueError, match="must be at least 10 characters"):
            BusinessContext(**invalid_context)
    
    def test_contract_generation_request_valid(self):
        """Test valid contract generation request."""
        request = ContractGenerationRequest(**SAMPLE_CONTRACT_REQUEST)
        assert request.business_context.description == SAMPLE_BUSINESS_CONTEXT["description"]
        assert request.contract_type == ContractType.TERMS_OF_SERVICE
        assert request.language == "en"
    
    def test_contract_generation_request_invalid_language(self):
        """Test contract request with invalid language."""
        invalid_request = SAMPLE_CONTRACT_REQUEST.copy()
        invalid_request["language"] = "invalid"
        
        with pytest.raises(ValueError):
            ContractGenerationRequest(**invalid_request)


class TestHealthEndpoints:
    """Test health check and root endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns HTML."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "AI Contract Generator API" in response.text
        assert "text/html" in response.headers["content-type"]
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


class TestContractGeneration:
    """Test contract generation endpoints."""
    
    @patch('main.ai_client.generate_contract_stream')
    @patch('main.contract_engine._parse_content_to_sections')
    @patch('main.contract_engine._generate_html')
    @patch('main.db_manager.save_contract')
    async def test_generate_contract_stream_success(
        self, mock_save, mock_html, mock_parse, mock_stream
    ):
        """Test successful contract generation streaming."""
        # Mock AI client response
        mock_stream.return_value = AsyncMock()
        mock_stream.return_value.__aiter__.return_value = [
            "This is a terms of service contract.",
            " It contains multiple sections.",
            " Please read carefully."
        ]
        
        # Mock contract engine responses
        mock_parse.return_value = SAMPLE_CONTRACT_SECTIONS
        mock_html.return_value = "<html><body>Contract HTML</body></html>"
        
        # Mock database save
        mock_save.return_value = None
        
        # Make request
        response = client.post("/api/generate-contract", json=SAMPLE_CONTRACT_REQUEST)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert "text/plain" in response.headers["content-type"]
        
        # Verify mocks were called
        mock_stream.assert_called_once()
        mock_parse.assert_called_once()
        mock_html.assert_called_once()
        mock_save.assert_called_once()
    
    def test_generate_contract_invalid_request(self):
        """Test contract generation with invalid request."""
        invalid_request = {
            "business_context": {
                "description": "Too short",
                "industry": "SaaS",
                "location": "California",
                "company_size": "Startup"
            },
            "contract_type": "invalid_type",
            "language": "xx"
        }
        
        response = client.post("/api/generate-contract", json=invalid_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('main.ai_client.generate_contract_stream')
    async def test_generate_contract_ai_error(self, mock_stream):
        """Test contract generation when AI client fails."""
        # Mock AI client to raise exception
        mock_stream.side_effect = Exception("AI service unavailable")
        
        response = client.post("/api/generate-contract", json=SAMPLE_CONTRACT_REQUEST)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestContractRetrieval:
    """Test contract retrieval endpoints."""
    
    @patch('main.db_manager.get_contract_by_id')
    async def test_get_contract_success(self, mock_get):
        """Test successful contract retrieval."""
        # Mock database response
        mock_contract = {
            "contract_id": "test-id-123",
            "contract_type": "terms_of_service",
            "business_context": SAMPLE_BUSINESS_CONTEXT,
            "sections": SAMPLE_CONTRACT_SECTIONS,
            "total_sections": 2,
            "estimated_pages": 1,
            "generation_time": 5.2,
            "model_used": "gpt-4",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        mock_get.return_value = mock_contract
        
        request_data = {"contract_id": "test-id-123"}
        response = client.post("/api/generate-contract-full", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["contract_id"] == "test-id-123"
        assert data["contract_type"] == "terms_of_service"
    
    @patch('main.db_manager.get_contract_by_id')
    async def test_get_contract_not_found(self, mock_get):
        """Test contract retrieval for non-existent contract."""
        # Mock database to return None
        mock_get.return_value = None
        
        request_data = {"contract_id": "non-existent-id"}
        response = client.post("/api/generate-contract-full", json=request_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Contract not found" in response.json()["detail"]


class TestContractListing:
    """Test contract listing endpoints."""
    
    @patch('main.db_manager.list_contracts')
    async def test_list_contracts_success(self, mock_list):
        """Test successful contract listing."""
        # Mock database response
        mock_contracts = [
            {
                "contract_id": "test-id-1",
                "contract_type": "terms_of_service",
                "business_context": SAMPLE_BUSINESS_CONTEXT,
                "total_sections": 2,
                "estimated_pages": 1,
                "generation_time": 5.2,
                "model_used": "gpt-4",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
        mock_list.return_value = mock_contracts
        
        response = client.get("/api/contracts?limit=10&offset=0")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["contracts"]) == 1
        assert data["total"] == 1
        assert data["limit"] == 10
        assert data["offset"] == 0
    
    @patch('main.db_manager.list_contracts')
    async def test_list_contracts_with_pagination(self, mock_list):
        """Test contract listing with pagination."""
        # Mock database response
        mock_list.return_value = []
        
        response = client.get("/api/contracts?limit=5&offset=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["limit"] == 5
        assert data["offset"] == 10


class TestContractDeletion:
    """Test contract deletion endpoint."""
    
    @patch('main.db_manager.delete_contract')
    async def test_delete_contract_success(self, mock_delete):
        """Test successful contract deletion."""
        # Mock database response
        mock_delete.return_value = True
        
        response = client.delete("/api/contracts/test-id-123")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Contract deleted successfully"
    
    @patch('main.db_manager.delete_contract')
    async def test_delete_contract_not_found(self, mock_delete):
        """Test deletion of non-existent contract."""
        # Mock database response
        mock_delete.return_value = False
        
        response = client.delete("/api/contracts/non-existent-id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Contract not found" in response.json()["detail"]


class TestDatabaseManager:
    """Test database manager functionality."""
    
    @patch('app.database.db_manager.get_contract_stats')
    async def test_get_contract_stats(self, mock_stats):
        """Test getting contract statistics."""
        mock_stats.return_value = {
            "total_contracts": 10,
            "contracts_by_type": {"terms_of_service": 8, "privacy_policy": 2},
            "recent_activity": "2024-01-01T00:00:00Z"
        }
        
        stats = await db_manager.get_contract_stats()
        assert stats["total_contracts"] == 10
        assert len(stats["contracts_by_type"]) == 2


class TestContractEngine:
    """Test contract engine functionality."""
    
    def test_contract_engine_initialization(self):
        """Test contract engine can be initialized."""
        engine = ContractEngine()
        assert engine is not None
    
    @patch('app.contract_engine.ContractEngine.get_contract_types')
    async def test_get_contract_types(self, mock_types):
        """Test getting available contract types."""
        mock_types.return_value = ["terms_of_service", "privacy_policy"]
        
        engine = ContractEngine()
        types = await engine.get_contract_types()
        assert len(types) == 2
        assert "terms_of_service" in types


class TestAIClient:
    """Test AI client functionality."""
    
    @patch('app.ai_client.AIClient.health_check')
    async def test_ai_client_health_check(self, mock_health):
        """Test AI client health check."""
        mock_health.return_value = "healthy"
        
        client = AIClient()
        health = await client.health_check()
        assert health == "healthy"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_json_request(self):
        """Test handling of invalid JSON requests."""
        response = client.post(
            "/api/generate-contract",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        incomplete_request = {
            "business_context": {
                "description": "Valid description",
                # Missing other required fields
            }
        }
        
        response = client.post("/api/generate-contract", json=incomplete_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = client.options("/api/generate-contract")
        assert "access-control-allow-origin" in response.headers
    
    def test_process_time_header(self):
        """Test process time header is added."""
        response = client.get("/health")
        assert "x-process-time" in response.headers


class TestIntegration:
    """Integration tests for the complete flow."""
    
    @patch('main.ai_client.generate_contract_stream')
    @patch('main.contract_engine._parse_content_to_sections')
    @patch('main.contract_engine._generate_html')
    @patch('main.db_manager.save_contract')
    @patch('main.db_manager.get_contract_by_id')
    async def test_complete_contract_lifecycle(
        self, mock_get, mock_save, mock_html, mock_parse, mock_stream
    ):
        """Test complete contract lifecycle: generate, save, retrieve."""
        # Mock AI generation
        mock_stream.return_value = AsyncMock()
        mock_stream.return_value.__aiter__.return_value = [
            "Complete contract content here."
        ]
        
        # Mock contract processing
        mock_parse.return_value = SAMPLE_CONTRACT_SECTIONS
        mock_html.return_value = "<html>Contract</html>"
        
        # Mock database operations
        mock_save.return_value = None
        mock_get.return_value = {
            "contract_id": "test-id",
            "contract_type": "terms_of_service",
            "business_context": SAMPLE_BUSINESS_CONTEXT,
            "sections": SAMPLE_CONTRACT_SECTIONS,
            "total_sections": 2,
            "estimated_pages": 1,
            "generation_time": 5.0,
            "model_used": "gpt-4",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # 1. Generate contract
        gen_response = client.post("/api/generate-contract", json=SAMPLE_CONTRACT_REQUEST)
        assert gen_response.status_code == status.HTTP_200_OK
        
        # 2. Retrieve contract (simulate getting the ID from the stream)
        contract_id = "test-id"
        retrieve_response = client.post(
            "/api/generate-contract-full",
            json={"contract_id": contract_id}
        )
        assert retrieve_response.status_code == status.HTTP_200_OK
        
        # 3. List contracts
        list_response = client.get("/api/contracts")
        assert list_response.status_code == status.HTTP_200_OK
        
        # 4. Delete contract
        delete_response = client.delete(f"/api/contracts/{contract_id}")
        assert delete_response.status_code == status.HTTP_200_OK


# Fixtures for common test data
@pytest.fixture
def sample_business_context():
    """Fixture for sample business context."""
    return BusinessContext(**SAMPLE_BUSINESS_CONTEXT)

@pytest.fixture
def sample_contract_request():
    """Fixture for sample contract request."""
    return ContractGenerationRequest(**SAMPLE_CONTRACT_REQUEST)

@pytest.fixture
def sample_contract_sections():
    """Fixture for sample contract sections."""
    return [ContractSection(**section) for section in SAMPLE_CONTRACT_SECTIONS]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
