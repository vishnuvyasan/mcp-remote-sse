#!/usr/bin/env python
"""
Build script for deploying FastAPI application to Cloudflare Workers.
This script packages the FastAPI application for deployment to Cloudflare Workers.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def main():
    """Main build function to prepare the application for Cloudflare Workers."""
    print("Building MCP Server for Cloudflare Workers...")
    
    # Create build directory
    build_dir = Path("./build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    
    # Copy necessary files
    print("Copying application files...")
    shutil.copytree("./app", "./build/app")
    shutil.copy("./worker.js", "./build/")
    shutil.copy("./wrangler.toml", "./build/")
    
    # Create Python adapter for Cloudflare Workers
    print("Creating Python adapter...")
    with open("./build/adapter.py", "w") as f:
        f.write("""
import json
from app.main import app
from fastapi.responses import JSONResponse

async def handle_request(request_data):
    \"\"\"Handle incoming requests from Cloudflare Workers.\"\"\"
    try:
        # Parse the request data
        method = request_data.get("method", "GET")
        path = request_data.get("path", "/")
        query_string = request_data.get("query", "")
        headers = request_data.get("headers", {})
        body = request_data.get("body", None)
        
        # Create a FastAPI compatible request
        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": method,
            "path": path,
            "query_string": query_string.encode(),
            "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        }
        
        # Process the request through FastAPI
        response = await app(scope, receive=None, send=None)
        
        # Return the response
        return {
            "status": response.status_code,
            "headers": dict(response.headers),
            "body": response.body.decode() if hasattr(response, "body") else "",
        }
    except Exception as e:
        # Handle any errors
        return {
            "status": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
""")
    
    # Create package.json for npm dependencies
    print("Creating package.json...")
    with open("./build/package.json", "w") as f:
        f.write("""
{
  "name": "mcp-server",
  "version": "1.0.0",
  "description": "MCP Server with OAuth and SSE",
  "main": "worker.js",
  "scripts": {
    "deploy": "wrangler publish"
  },
  "dependencies": {
    "fastapi-worker": "^0.1.0"
  },
  "devDependencies": {
    "wrangler": "^2.0.0"
  }
}
""")
    
    print("Build completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
