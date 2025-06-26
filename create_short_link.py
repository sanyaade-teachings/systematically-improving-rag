#!/usr/bin/env python3
import os
import sys
import dub

def create_feedback_short_link(api_key=None):
    """Create a short link for the feedback form using Dub API."""
    
    # Get API key from environment or parameter
    token = api_key or os.environ.get('DUB_API_KEY')
    
    if not token:
        print("Error: DUB_API_KEY not found. Please set the environment variable or pass as argument.")
        print("Usage: python create_short_link.py [API_KEY]")
        return None
    
    # Initialize Dub client
    d = dub.Dub(token=token)
    
    # Original feedback form URL - Cohort 3
    feedback_url = "https://maven.com/applied-llms/rag-playbook/3/forms/4be1a9"
    
    try:
        # Upsert short link (create or update if exists)
        res = d.links.upsert(request={
            "url": feedback_url,
            "external_id": "rag-cohort-3-feedback"
        })
        
        print(f"Short link: {res.short_link}")
        print(f"QR code URL: {res.qr_code}")
        
        return {
            "short_link": res.short_link,
            "qr_code": res.qr_code
        }
        
    except Exception as e:
        print(f"Error creating short link: {e}")
        return {
            "short_link": feedback_url,
            "qr_code": None
        }

if __name__ == "__main__":
    api_key = sys.argv[1] if len(sys.argv) > 1 else None
    result = create_feedback_short_link(api_key)
    if result:
        print(f"\nResults:")
        print(f"Short Link: {result['short_link']}")
        if result['qr_code']:
            print(f"QR Code: {result['qr_code']}")
        else:
            print("QR Code: Not available") 