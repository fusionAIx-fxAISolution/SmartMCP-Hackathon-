#!/usr/bin/env python3
"""Get the case ID from Pega API response"""
import asyncio
import httpx
from dotenv import load_dotenv
from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper

load_dotenv()

async def create_case_and_get_id():
    """Create a case and extract the case ID"""
    print("=" * 70)
    print("Creating Pega Case and Retrieving Case ID")
    print("=" * 70)
    
    # Load settings
    settings = PegaSettings.from_env()
    token_helper = PegaTokenHelper(settings)
    
    # Get token
    token = await token_helper.get_valid_token()
    
    # Create case with full details
    print(f"\nCreating case...")
    
    async with httpx.AsyncClient(follow_redirects=False) as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        
        payload = {
            "caseTypeID": settings.allowed_case_type_id,
            "processID": settings.allowed_create_process_id,
            "content": {
                "Description": "Test case from MCP server",
                "Priority": "High",
                "Title": "MCP Test Case"
            }
        }
        
        url = f"{settings.pega_application_api_base}/cases"
        
        response = await client.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        # Check for Location header (redirect URL contains case info)
        if "location" in response.headers:
            location = response.headers["location"]
            print(f"Location: {location}")
            
            # Extract case ID from location
            # Usually looks like: /cases/CASEID or /path/to/CASEID
            import re
            case_id_match = re.search(r'([A-Z0-9\-]+(?:\s[A-Z0-9\-]+)?)\s*$', location)
            if case_id_match:
                case_id = case_id_match.group(1)
                print(f"\n{'=' * 70}")
                print(f"✓ CASE CREATED SUCCESSFULLY!")
                print(f"{'=' * 70}")
                print(f"Case ID: {case_id}")
                print(f"{'=' * 70}")
            else:
                print(f"Could not extract case ID from location header")
        
        print(f"\nResponse Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:200] if response.text else '(empty)'}")

if __name__ == "__main__":
    asyncio.run(create_case_and_get_id())
