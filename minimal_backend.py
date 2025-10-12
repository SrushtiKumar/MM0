#!/usr/bin/env python3
"""Minimal backend to test API issues"""

from fastapi import FastAPI
from datetime import datetime
import uvicorn

app = FastAPI()

@app.get("/api/status")
async def simple_status():
    """Simple status endpoint"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)