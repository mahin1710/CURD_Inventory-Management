"""
StockMaster - Root Application Entry Point
Forwards requests to backend.main:app for flexibility and convenience.
"""
from backend.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
