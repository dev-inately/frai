"""
Main FastAPI application for the AI Contract Generator.
"""
import time
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from loguru import logger
import uvicorn
import asyncio

from app.config import settings
from app.models import (
    ContractGenerationRequest, ContractGenerationResponse, 
    ContractRetrievalRequest, ContractRetrievalResponse,
    ContractListResponse, DatabaseStatsResponse,
    ErrorResponse, HealthCheckResponse, BusinessContext, ContractType, ContractSection
)
from app.contract_engine import ContractEngine
from app.ai_client import AIClient
from app.database import db_manager

# Configure logging
logger.add("logs/app.log", rotation="1 day", retention="7 days", level=settings.log_level)

# Initialize FastAPI app
app = FastAPI(
    title="AI Contract Generator API",
    description="AI-powered contract generation with real-time streaming",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Initialize services
contract_engine = ContractEngine()
ai_client = AIClient()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred",
            details={"exception": str(exc)}
        ).dict()
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information."""
    return """
    <html>
        <head>
            <title>AI Contract Generator API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { font-weight: bold; color: #007bff; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 AI Contract Generator API</h1>
                <p>Welcome to the AI Contract Generator API. This service generates professional legal contracts using AI.</p>
                
                <h2>Available Endpoints:</h2>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/health</code> - Health check
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/api/contract-types</code> - Available contract types
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <code>/api/generate-contract</code> - Generate contract (streaming + save)
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <code>/api/generate-contract-full</code> - Retrieve contract by ID
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <code>/api/download-contract</code> - Download contract by ID
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/api/contracts</code> - List all contracts
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/api/contracts/stats</code> - Database statistics
                </div>
                
                <div class="endpoint">
                    <span class="method">DELETE</span> <code>/api/contracts/{id}</code> - Delete contract by ID
                </div>
                
                <h2>Documentation:</h2>
                <ul>
                    <li><a href="/docs">Interactive API Docs (Swagger UI)</a></li>
                    <li><a href="/redoc">ReDoc Documentation</a></li>
                </ul>
                
                <h2>Quick Start:</h2>
                <p>Send a POST request to <code>/api/generate-contract</code> with your business context to start generating contracts! The contract will be saved and you can retrieve it later using the returned contract ID.</p>
            </div>
        </body>
    </html>
    """


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check AI services health
        ai_health = await ai_client.health_check()
        
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            services={
                "api": "healthy",
                "ai_services": ai_health
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/api/contract-types")
async def get_contract_types():
    """Get available contract types."""
    try:
        contract_types = await contract_engine.get_contract_types()
        return {"contract_types": contract_types}
    except Exception as e:
        logger.error(f"Error getting contract types: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contract types")


@app.post("/api/generate-contract")
async def generate_contract_stream(req_context: Request, request: ContractGenerationRequest):
    """
    Generate contract with real-time streaming and save to database.
    
    This endpoint streams the contract generation process, providing
    real-time feedback as the AI generates each section, and saves
    the complete contract to the database.
    """
    try:
        request.contract_type = ContractType.TERMS_OF_SERVICE # hardcoded for ease
        request.language = "en" # hardcoded for ease
        logger.info(f"Starting contract generation for type: {request.contract_type}")
        # Generate contract ID for this request
        contract_id = str(uuid.uuid4())
        
        # Start streaming the contract generation
        async def generate_stream() -> AsyncGenerator[str, None]:
            try:
                content_chunks = []
                

                # Stream the generation
                async for chunk in ai_client.generate_contract_stream(
                    business_context=request.business_context
                ):
                    if await req_context.is_disconnected():
                        logger.info("Client disconnected 1, setting abort signal")
                        break
                    content_chunks.append(chunk)
                    yield f"data: {chunk}\n\n"
                
                # Combine all chunks and save to database
                full_content = ''.join(content_chunks)
                
                # Parse sections and generate HTML
                sections = contract_engine._parse_content_to_sections(full_content)
                html_content = contract_engine._generate_html(
                    request.contract_type,
                    contract_id,
                    sections,
                )
                
                if content_chunks:
                    # Save to database
                    await db_manager.save_contract(
                        contract_id=contract_id,
                        request=request,
                        contract_type=request.contract_type,
                        html_content=html_content,
                        raw_content=full_content,
                        sections=sections,
                        total_sections=len(sections),
                        estimated_pages=contract_engine._estimate_pages(sections),
                        generation_time=0,  # Will be calculated in the engine
                        model_used=ai_client.model
                    )
                # Send completion signal with contract ID
                yield f"[END_OF_DOC={contract_id}"
                
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                yield f"data: Error: {str(e)}\n\n"
            finally:
                pass
                # disconnection_task.cancel()
                # try:
                #     await disconnection_task
                # except asyncio.CancelledError:
                #     pass
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in contract generation stream: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Contract generation failed: {str(e)}")


@app.post("/api/generate-contract-full", response_model=ContractRetrievalResponse)
async def generate_contract_full(request: ContractRetrievalRequest):
    """
    Retrieve complete contract by ID.
    
    This endpoint retrieves a previously generated contract from the database
    and returns it as a complete response with metadata.
    """
    try:
        logger.info(f"Retrieving contract with ID: {request.contract_id}")
        
        # Retrieve the contract from database
        contract_data = await db_manager.get_contract_by_id(request.contract_id)
        
        if not contract_data:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        print("Contract data is", contract_data.get("sections", "bla"))
        # Convert to response model
        response = ContractRetrievalResponse(
            contract_id=contract_data["id"],
            contract_type=contract_data["contract_type"],
            business_context=BusinessContext(**contract_data["business_context"]),
            sections=[ContractSection(**section) for section in contract_data["sections"]],
            total_sections=contract_data["total_sections"],
            estimated_pages=contract_data["estimated_pages"],
            generation_time=contract_data["generation_time"],
            model_used=contract_data["model_used"],
            created_at=contract_data["created_at"],
            updated_at=contract_data["updated_at"]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Contract retrieval failed: {str(e)}")


@app.post("/api/download-contract")
async def download_contract(request: ContractRetrievalRequest):
    """
    Download contract by ID as HTML file.
    
    This endpoint retrieves a previously generated contract from the database
    and returns it as a downloadable HTML file with proper styling.
    """
    try:
        logger.info(f"Downloading contract with ID: {request.contract_id}")
        
        # Retrieve the contract from database
        contract_data = await db_manager.get_contract_by_id(request.contract_id)
        
        if not contract_data:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Return HTML content
        return HTMLResponse(
            content=contract_data["html_content"],
            headers={
                "Content-Disposition": f"attachment; filename=contract_{contract_data['contract_type']}_{request.contract_id[:8]}.html"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Contract download failed: {str(e)}")


@app.get("/api/contracts", response_model=ContractListResponse)
async def list_contracts(
    limit: int = 50,
    offset: int = 0,
    contract_type: Optional[str] = None
):
    """
    List generated contracts with optional filtering.
    
    This endpoint retrieves a list of previously generated contracts
    from the database with pagination and optional filtering.
    """
    try:
        logger.info(f"Listing contracts (limit: {limit}, offset: {offset}, type: {contract_type})")
        
        # Get contracts from database
        contracts_data = await db_manager.list_contracts(
            limit=limit,
            offset=offset,
        )
        
        # return {"contracts": "ok"}
        # Convert to response models
        contracts = []
        for contract_data in contracts_data:
            print("COntract id is", contract_data.get("sections", "bla"))
            contract = ContractRetrievalResponse(
                contract_id=contract_data["id"],
                contract_type=contract_data["contract_type"],
                business_context=BusinessContext(**contract_data["business_context"]),
                # sections=[ContractSection(**section) for section in contract_data["sections"]],
                total_sections=contract_data["total_sections"],
                estimated_pages=contract_data["estimated_pages"],
                generation_time=contract_data["generation_time"],
                model_used=contract_data["model_used"],
                created_at=contract_data["created_at"],
                updated_at=contract_data["updated_at"]
            )
            contracts.append(contract)
        print("length of contracts is", len(contracts))
        
        # # Get total count for pagination
        total_contracts = len(contracts_data)
        if len(contracts_data) == limit:
            # If we got a full page, there might be more
            total_contracts = offset + limit + 1  # Approximate
        
        return ContractListResponse(
            contracts=contracts,
            total=total_contracts,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing contracts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list contracts: {str(e)}")


@app.delete("/api/contracts/{contract_id}")
async def delete_contract(contract_id: str):
    """
    Delete a contract by ID.
    
    This endpoint permanently removes a contract and its sections
    from the database.
    """
    try:
        logger.info(f"Deleting contract with ID: {contract_id}")
        
        # Check if contract exists
        contract_data = await db_manager.get_contract_by_id(contract_id)
        if not contract_data:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Delete from database
        success = await db_manager.delete_contract(contract_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete contract")
        
        return {"message": "Contract deleted successfully", "contract_id": contract_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contract: {contract_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete contract: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
