#!/usr/bin/env python3
"""
NGrok tunnel for exposing the local MCP server
"""
import sys
import logging
from pyngrok import ngrok, conf
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configure ngrok
LOCAL_PORT = 8000
# ⚠️ IMPORTANT: Replace with your actual ngrok auth token from https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTH_TOKEN = "YOUR_NGROK_AUTH_TOKEN_HERE"  # Paste your token here


def setup_ngrok_tunnel():
    """Set up and maintain ngrok tunnel"""
    
    logger.info("=" * 60)
    logger.info("NGrok Tunnel for MCP Server")
    logger.info("=" * 60)
    
    # Set auth token if provided
    if NGROK_AUTH_TOKEN:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        logger.info("✓ Auth token configured")
    else:
        logger.warning("⚠ No auth token configured - using free tier (rate limited)")
    
    try:
        # Open the tunnel
        logger.info(f"Starting ngrok tunnel on localhost:{LOCAL_PORT}...")
        public_url = ngrok.connect(LOCAL_PORT, "http")
        
        logger.info("=" * 60)
        logger.info("✓ NGrok tunnel established!")
        logger.info("=" * 60)
        logger.info(f"\nPublic URL: {public_url}")
        logger.info(f"MCP Endpoint: {public_url}/mcp")
        logger.info(f"\nLocal endpoint: http://localhost:{LOCAL_PORT}/mcp")
        logger.info("\n✓ Use the public URL in Copilot Studio")
        logger.info("=" * 60)
        
        # Keep the tunnel alive
        logger.info("\nTunnel is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(10)
            
    except KeyboardInterrupt:
        logger.info("\nShutting down tunnel...")
        ngrok.kill()
        logger.info("✓ Tunnel closed")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_ngrok_tunnel()
