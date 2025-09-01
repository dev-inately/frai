"""
Database models and storage layer for the AI Contract Generator.
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import os
from loguru import logger

from .models import ContractGenerationRequest, ContractSection


class DatabaseManager:
    """Manages SQLite database operations for contract storage."""
    
    def __init__(self, db_path: str = "contracts.db"):
        """Initialize database manager."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create contracts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contracts (
                    id TEXT PRIMARY KEY,
                    contract_type TEXT NOT NULL,
                    business_context TEXT NOT NULL,
                    language TEXT NOT NULL,
                    html_content TEXT NOT NULL,
                    raw_content TEXT NOT NULL,
                    total_sections INTEGER NOT NULL,
                    estimated_pages INTEGER NOT NULL,
                    generation_time REAL NOT NULL,
                    model_used TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create contract sections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contract_sections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    section_number INTEGER NOT NULL,
                    subsection_number INTEGER,
                    FOREIGN KEY (contract_id) REFERENCES contracts (id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    async def save_contract(
        self,
        contract_id: str,
        request: ContractGenerationRequest,
        contract_type: str,
        html_content: str,
        raw_content: str,
        sections: List[ContractSection],
        total_sections: int,
        estimated_pages: int,
        generation_time: float,
        model_used: str
    ) -> bool:
        """Save a generated contract to the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Insert contract
                cursor.execute("""
                    INSERT INTO contracts (
                        id, contract_type, business_context,
                        language, html_content, raw_content,
                        total_sections, estimated_pages, generation_time, model_used
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    contract_id,
                    contract_type,
                    json.dumps(request.business_context.dict()),
                    request.language or "en",
                    html_content,
                    raw_content,
                    total_sections,
                    estimated_pages,
                    generation_time,
                    model_used
                ))
                
                # Insert contract sections
                for section in sections:
                    cursor.execute("""
                        INSERT INTO contract_sections (
                            contract_id, title, content, section_number, subsection_number
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        contract_id,
                        section.title,
                        section.content,
                        section.section_number,
                        section.subsection_number
                    ))
                
                conn.commit()
                logger.info(f"Contract {contract_id} saved to database")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save contract {contract_id}: {str(e)}")
            return False
    
    async def get_contract_by_id(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a contract by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get contract
                cursor.execute("""
                    SELECT * FROM contracts WHERE id = ?
                """, (contract_id,))
                
                contract_row = cursor.fetchone()
                if not contract_row:
                    return None
                
                # Get contract sections
                cursor.execute("""
                    SELECT * FROM contract_sections 
                    WHERE contract_id = ? 
                    ORDER BY section_number, subsection_number
                """, (contract_id,))
                
                sections = []
                for section_row in cursor.fetchall():
                    sections.append({
                        "title": section_row["title"],
                        "content": section_row["content"],
                        "section_number": section_row["section_number"],
                        "subsection_number": section_row["subsection_number"]
                    })
                
                # Convert to dictionary
                contract = dict(contract_row)
                contract["business_context"] = json.loads(contract["business_context"])
                contract["sections"] = sections
                
                return contract
                
        except Exception as e:
            logger.error(f"Failed to retrieve contract {contract_id}: {str(e)}")
            return None
    
    async def list_contracts(
        self, 
        limit: int = 50, 
        offset: int = 0,
        contract_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List contracts with optional filtering."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM contracts"
                params = []
                
                if contract_type:
                    query += " WHERE contract_type = ?"
                    params.append(contract_type)
                
                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                
                contracts = []
                for row in cursor.fetchall():
                    contract = dict(row)
                    contract["business_context"] = json.loads(contract["business_context"])
                    contracts.append(contract)
                
                return contracts
                
        except Exception as e:
            logger.error(f"Failed to list contracts: {str(e)}")
            return []
    
    async def delete_contract(self, contract_id: str) -> bool:
        """Delete a contract by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete sections first (foreign key constraint)
                cursor.execute("DELETE FROM contract_sections WHERE contract_id = ?", (contract_id,))
                
                # Delete contract
                cursor.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
                
                conn.commit()
                logger.info(f"Contract {contract_id} deleted from database")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete contract {contract_id}: {str(e)}")
            return False
    
    async def get_contract_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total contracts
                cursor.execute("SELECT COUNT(*) FROM contracts")
                total_contracts = cursor.fetchone()[0]
                
                # Contracts by type
                cursor.execute("""
                    SELECT contract_type, COUNT(*) 
                    FROM contracts 
                    GROUP BY contract_type
                """)
                contracts_by_type = dict(cursor.fetchall())
                
                # Recent contracts
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM contracts 
                    WHERE created_at >= datetime('now', '-7 days')
                """)
                recent_contracts = cursor.fetchone()[0]
                
                return {
                    "total_contracts": total_contracts,
                    "contracts_by_type": contracts_by_type,
                    "recent_contracts": recent_contracts
                }
                
        except Exception as e:
            logger.error(f"Failed to get contract stats: {str(e)}")
            return {}


# Global database manager instance
db_manager = DatabaseManager()
