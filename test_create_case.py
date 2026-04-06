#!/usr/bin/env python3
"""Test the pega_create_case tool"""
from __future__ import annotations

import asyncio
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper
from app.pega_client import PegaCaseClient
from app.tools.PegaCreateCase import register_pega_create_case_tool
from mcp.server.fastmcp import FastMCP


async def test_create_case():
    """Test creating a Pega case"""
    print("=" * 60)
    print("Testing pega_create_case tool")
    print("=" * 60)
    
    # Load settings
    print("\n1. Loading settings from environment...")
    try:
        settings = PegaSettings.from_env()
        print(f"✓ Settings loaded successfully")
        print(f"  - Pega Base URL: {settings.pega_base_url}")
        print(f"  - Application API: {settings.pega_application_api_base}")
        print(f"  - Case Type ID: {settings.allowed_case_type_id}")
        print(f"  - Process ID: {settings.allowed_create_process_id}")
    except Exception as e:
        print(f"✗ Failed to load settings: {e}")
        return
    
    # Initialize clients
    print("\n2. Initializing Pega clients...")
    try:
        token_helper = PegaTokenHelper(settings)
        pega_client = PegaCaseClient(settings, token_helper)
        print("✓ Clients initialized")
    except Exception as e:
        print(f"✗ Failed to initialize clients: {e}")
        return
    
    # Test token retrieval
    print("\n3. Testing token retrieval...")
    try:
        token = await token_helper.get_valid_token()
        print(f"✓ Token retrieved successfully")
        print(f"  - Token length: {len(token)} characters")
    except Exception as e:
        print(f"✗ Failed to get token: {e}")
        return
    
    # Test case creation
    print("\n4. Testing case creation...")
    try:
        # Pega API only requires caseTypeID
        payload = {
            "caseTypeID": settings.allowed_case_type_id,
        }
        
        print(f"  - Payload: {payload}")
        
        result = await pega_client.create_case(
            payload=payload,
            view_type="none",
            page_name=None,
            origin_channel=settings.default_origin_channel,
        )
        
        print(f"✓ Case created successfully!")
        print(f"  - Response: {result}")
        
        if isinstance(result, dict) and "ID" in result:
            print(f"  - Case ID: {result['ID']}")
        
    except Exception as e:
        print(f"✗ Failed to create case: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_create_case())
