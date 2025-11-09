#!/bin/bash
# Quick script to start ngrok for the Excel-Agent server
# Usage: ./start_ngrok.sh [port]
# Default port is 5050

PORT=${1:-5050}

echo "🚀 Starting ngrok tunnel on port $PORT..."
ngrok http --host-header=rewrite $PORT

