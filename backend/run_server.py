#!/usr/bin/env python3
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting SEO Blog Automation SaaS Server...")
    print("Server will be available at http://127.0.0.1:8000")
    print("API documentation at http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8001,
        reload=False,
        log_level="info"
    )