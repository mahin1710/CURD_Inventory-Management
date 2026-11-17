from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
import uvicorn

from backend.database import engine, get_db, DB_FILE
from backend import models
from backend.routes import products

# Automatically create database tables during application initialization
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="StockMaster Inventory System",
    description="Backend REST API for StockMaster - Inventory Management System",
    version="1.0.0"
)

# Register Feature Routers
app.include_router(products.router)

# 1. Root Endpoint
@app.get("/", tags=["General"])
def read_root():
    return {
        "message": "Welcome to StockMaster Inventory Management System"
    }

# 2. Health & Database Status Endpoint
@app.get("/health", tags=["General"])
def get_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    return {
        "status": "healthy",
        "database": {
            "type": "SQLite",
            "file": DB_FILE,
            "connected": True,
            "tables": table_names
        }
    }

# 3. About Endpoint
@app.get("/about", tags=["General"])
def get_about():
    return {
        "application": "StockMaster Inventory Management System",
        "phase": "Phase 06: Complete Product CRUD APIs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
