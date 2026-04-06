#!/usr/bin/env python3
"""Detailed debug to check what's being sent and received"""
import asyncio
import httpx
import json
from dotenv import load_dotenv
from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper

load_dotenv()

async def detailed_request_debug():
    """Make request with full debugging"""
    print("=" * 80)
    print("DETAILED REQUEST DEBUGGING")
    print("=" * 80)
    
    settings = PegaSettings.from_env()
    token_helper = PegaTokenHelper(settings)
    
    token = await token_helper.get_valid_token()
    
    # Try the current endpoint
    print("\n1. CURRENT ENDPOINT:")
    url = f"{settings.pega_application_api_base}/cases"
    print(f"   URL: {url}")
    
    payload = {"caseTypeID": settings.allowed_case_type_id}
    
    print(f"\n2. REQUEST DETAILS:")
    print(f"   Method: POST")
    print(f"   URL: {url}")
    print(f"   Headers:")
    print(f"     Authorization: Bearer [TOKEN]")
    print(f"     Accept: application/json")
    print(f"     Content-Type: application/json")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30,
            follow_redirects=False
        )
        
        print(f"\n3. RESPONSE:")
        print(f"   Status: {response.status_code} {response.reason_phrase}")
        print(f"   Headers:")
        for k, v in response.headers.items():
            if k.lower() != 'set-cookie':
                print(f"     {k}: {v[:100] if len(v) > 100 else v}")
        print(f"   Body: {response.text if response.text else '(empty)'}")
    
    print(f"\n4. DIAGNOSED ISSUE:")
    print(f"   The 303 response with empty body suggests:")
    print(f"   - The endpoint exists but might not be the right one for case creation")
    print(f"   - Or the API requires different parameters")
    print(f"   - Or the payload structure is still incorrect")
    
    print(f"\n5. WHAT TO VERIFY:")
    print(f"   1. Is the endpoint correct? Ask your Pega admin")
    print(f"   2. What does a working case creation request look like?")
    print(f"   3. Check Pega API documentation for the exact endpoint")
    print(f"\nCurrent endpoint: {url}")

if __name__ == "__main__":
    asyncio.run(detailed_request_debug())
