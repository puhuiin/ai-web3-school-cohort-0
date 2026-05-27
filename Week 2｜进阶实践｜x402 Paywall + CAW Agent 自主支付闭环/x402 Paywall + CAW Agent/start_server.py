#!/usr/bin/env python3
"""
x402 Paywall Server 启动脚本
"""
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    debug = os.getenv("SERVER_DEBUG", "false").lower() == "true"
    
    print(f"Starting x402 Paywall Server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"API Docs: http://localhost:{port}/docs")
    print()
    
    uvicorn.run(
        "server.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    main()