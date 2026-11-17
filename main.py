from fastapi import FastAPI

# FastAPI application instance create kora hocche
app = FastAPI(
    title="CURD_Inventory Management System",
    description="Backend REST API for Inventory Management",
    version="1.0.0"
)

# Root GET Endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to CURD_Inventory Management System API",
        "status": "running"
    }
