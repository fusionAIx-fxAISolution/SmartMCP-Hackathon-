#!/usr/bin/env python3
"""Debug Pega API connectivity"""
import asyncio
import httpx
from dotenv import load_dotenv
from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper

load_dotenv()

async def debug_pega_api():
    """Debug Pega API issues"""
    print("=" * 70)
    print("Pega API Debug Information")
    print("=" * 70)
    
    # Load settings
    settings = PegaSettings.from_env()
    token_helper = PegaTokenHelper(settings)
    
    # Get token
    print("\n1. Getting OAuth token...")
    try:
        token = await token_helper.get_valid_token()
        print(f"✓ Token retrieved: {token[:50]}...")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return
    
    # Test API endpoint
    print(f"\n2. Testing API endpoint...")
    print(f"   Base URL: {settings.pega_application_api_base}")
    print(f"   Full URL: {settings.pega_application_api_base}/cases")
    
    # Make actual request with detailed logging
    print(f"\n3. Making POST request to /cases...")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }
            
            payload = {
                "caseTypeID": settings.allowed_case_type_id,
                "processID": settings.allowed_create_process_id,
                "content": {
                    "Description": "Debug test",
                    "Priority": "High",
                    "Title": "Debug"
                }
            }
            
            url = f"{settings.pega_application_api_base}/cases"
            
            print(f"   URL: {url}")
            print(f"   Headers: Authorization: Bearer [TOKEN], Accept: application/json")
            print(f"   Payload: {payload}")
            
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"\n4. Response Details:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Body: {response.text[:500]}")
            
            if response.status_code == 404:
                print(f"\n⚠ 404 Not Found - Likely causes:")
                print(f"   1. Wrong API endpoint path")
                print(f"   2. API disabled on Pega instance")
                print(f"   3. IP whitelisting blocking your request")
                print(f"   4. Application not accessible via this path")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(debug_pega_api())
