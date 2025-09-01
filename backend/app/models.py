"""
Data models for the AI Contract Generator API.
"""
from typing import Optional, List, Callable
from pydantic import BaseModel, Field, validator
from enum import Enum


class ContractType(str, Enum):
    """Available contract types."""
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"


class BusinessContext(BaseModel):
    """Business context for contract generation."""
    description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Business description for contract generation"
    )
    
    @validator('description')
    def validate_description(cls, v):
        """Validate business description."""
        if len(v.strip()) < 10:
            raise ValueError('Business description must be at least 10 characters long')
        return v.strip()


class ContractGenerationRequest(BaseModel):
    """Request model for contract generation."""
    business_context: BusinessContext
    contract_type: ContractType
    language: str = Field(
        default="en",
        pattern="^[a-z]{2}$",
        description="Contract language (ISO 639-1 code)"
    )


class ContractRetrievalRequest(BaseModel):
    """Request model for retrieving existing contracts."""
    contract_id: str = Field(
        ...,
        description="The ID of the contract to retrieve"
    )


class ContractSection(BaseModel):
    """Individual contract section."""
    title: str
    content: str
    section_number: int
    subsection_number: Optional[int] = None


class ContractGenerationResponse(BaseModel):
    """Response model for contract generation."""
    contract_id: str
    contract_type: str
    sections: List[ContractSection]
    total_sections: int
    estimated_pages: int
    generation_time: float
    model_used: str


class ContractRetrievalResponse(BaseModel):
    """Response model for contract retrieval."""
    contract_id: str
    contract_type: str
    business_context: BusinessContext
    # language: str
    sections: Optional[List[ContractSection]] = None
    total_sections: int
    estimated_pages: int
    generation_time: float
    model_used: str
    created_at: str
    updated_at: str


class ContractListResponse(BaseModel):
    """Response model for listing contracts."""
    contracts: List[ContractRetrievalResponse]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[dict] = None


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str
    services: dict


class DatabaseStatsResponse(BaseModel):
    """Database statistics response."""
    total_contracts: int
    contracts_by_type: dict
    recent_contracts: int
