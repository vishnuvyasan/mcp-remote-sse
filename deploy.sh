#!/bin/bash

# Deployment script for MCP Server to Cloudflare Workers

echo "Starting deployment of MCP Server to Cloudflare Workers..."

# Make sure wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "Wrangler not found. Installing..."
    npm install -g wrangler
fi

# Make sure build_worker.py is executable
chmod +x build_worker.py

# Run the build script
echo "Building the application..."
python build_worker.py

# Change to the build directory
cd build

# Install npm dependencies
echo "Installing npm dependencies..."
npm install

# Deploy to Cloudflare Workers
echo "Deploying to Cloudflare Workers..."
npx wrangler publish

echo "Deployment completed!"

# Made with Bob
