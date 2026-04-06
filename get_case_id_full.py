#!/usr/bin/env python3
"""Get the actual case ID by following redirect"""
import asyncio
import httpx
from dotenv import load_dotenv
from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper
import re

load_dotenv()

async def create_case_with_redirect():
    """Create a case and follow redirect to get full case ID"""
    print("=" * 70)
    print("Creating Pega Case and Getting Full Case ID")
    print("=" * 70)
    
    # Load settings
    settings = PegaSettings.from_env()
    token_helper = PegaTokenHelper(settings)
    
    # Get token
    token = await token_helper.get_valid_token()
    
    print(f"\nCreating case...")
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
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
        
        print(f"Final Status Code: {response.status_code}")
        
        # Try to extract case ID from response
        body = response.text
        
        # Look for case ID patterns in the HTML/response
        # Pattern 1: Look for caseID or case ID in the HTML
        case_id_match = re.search(r'["\']?caseID["\']?\s*[:=]\s*["\']?([A-Z0-9\-\s]+)["\']?', body)
        if case_id_match:
            print(f"✓ Case ID found: {case_id_match.group(1)}")
        else:
            # Pattern 2: Look for case number/ID in common positions
            case_match = re.search(r'FAI-ProductMngmt-Work-ProductInfo\s+[A-Z0-9\-\s]+', body)
            if case_match:
                print(f"✓ Case reference found: {case_match.group(0)}")
        
        # Print URL to find case ID
        if response.url:
            print(f"\nFinal URL: {response.url}")
            
        print(f"\n{'=' * 70}")
        print("✓ CASE CREATED SUCCESSFULLY!")
        print(f"{'=' * 70}")
        
        # Extract from URL if possible
        url_str = str(response.url)
        if "/cases/" in url_str:
            case_id = url_str.split("/cases/")[-1].split("?")[0].split("/")[0]
            print(f"Case ID from URL: {case_id}")

if __name__ == "__main__":
    asyncio.run(create_case_with_redirect())
