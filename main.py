from fastapi import FastAPI

# Initialize the FastAPI application
app = FastAPI(
    title="StockMaster Inventory System",
    description="Backend REST API for StockMaster - Inventory Management System",
    version="1.0.0"
)

# 1. Root Endpoint
@app.get("/")
def read_root():
    """
    Root endpoint that welcomes users to StockMaster.
    """
    return {
        "message": "Welcome to StockMaster Inventory Management System"
    }

# 2. Health Endpoint
@app.get("/health")
def get_health():
    """
    Health check endpoint to verify backend service status.
    """
    return {
        "status": "healthy"
    }

# 3. About Endpoint
@app.get("/about")
def get_about():
    """
    About endpoint providing application details and current development phase.
    """
    return {
        "application": "StockMaster Inventory Management System",
        "phase": "Phase 01: Environment Setup and First FastAPI Application",
        "version": "1.0.0"
    }
