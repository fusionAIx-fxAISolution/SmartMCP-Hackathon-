#!/usr/bin/env python3
"""Debug Pega API case creation in detail"""
import asyncio
import httpx
from dotenv import load_dotenv
from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper
import json

load_dotenv()

async def debug_case_creation():
    """Debug case creation with detailed logging"""
    print("=" * 80)
    print("DETAILED PEGA CASE CREATION DEBUG")
    print("=" * 80)
    
    settings = PegaSettings.from_env()
    token_helper = PegaTokenHelper(settings)
    
    # Get token
    print("\n1. Getting OAuth token...")
    token = await token_helper.get_valid_token()
    print(f"✓ Token obtained: {token[:60]}...")
    
    # Prepare request
    print("\n2. Preparing request...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "caseTypeID": settings.allowed_case_type_id,
        "processID": settings.allowed_create_process_id,
        "content": {
            "Description": "Debug test case",
            "Priority": "High",
            "Title": "Debug Test"
        }
    }
    
    url = f"{settings.pega_application_api_base}/cases"
    
    print(f"   URL: {url}")
    print(f"   Case Type ID: {settings.allowed_case_type_id}")
    print(f"   Process ID: {settings.allowed_create_process_id}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    # Make request without following redirects
    print("\n3. Sending POST request (no redirect follow)...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=30,
                follow_redirects=False
            )
            
            print(f"\n4. Response:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Status Text: {response.reason_phrase}")
            print(f"\n   Response Headers:")
            for key, value in response.headers.items():
                if key.lower() != 'set-cookie':
                    print(f"     {key}: {value}")
            
            print(f"\n   Response Body:")
            body = response.text
            print(f"     Length: {len(body)} bytes")
            if body:
                print(f"     Content: {body[:500]}")
            else:
                print(f"     (empty)")
            
            # Check for error indicators
            print(f"\n5. Analysis:")
            if response.status_code in [303, 200, 201]:
                print(f"   ⚠ Response suggests success, but actual case may not be created")
                print(f"   This could indicate:")
                print(f"     - Wrong API endpoint (even though it returns a response)")
                print(f"     - Missing required fields in payload")
                print(f"     - Authentication issue (token valid but no permission)")
                print(f"     - IP whitelisting blocking the operation")
            
            if response.status_code >= 400:
                print(f"   ✗ Error response received")
                
            # Check location header
            if 'location' in response.headers:
                location = response.headers['location']
                print(f"   Location header: {location}")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_case_creation())
