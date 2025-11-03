#!/usr/bin/env python3
"""
Run the enhanced backend on port 8001
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_app:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )