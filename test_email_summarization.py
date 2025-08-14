#!/usr/bin/env python3
"""
Test script for email summarization endpoint
"""
import requests
import json
import sys

def test_email_summarization():
    """Test the email summarization endpoint"""

    print("Starting email summarization test...")

    # Test data
    url = "http://127.0.0.1:5000/orgs/anas-services/agents/32fdf3b5-57af-4147-88df-71dd80991c54/emails/summarize"
    data = {
        "type": "last_24_hours",
        "count": 10
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"Testing URL: {url}")
    print(f"Sending data: {data}")

    try:
        print("Making request...")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"JSON response: {json.dumps(json_response, indent=2)}")
            except Exception as json_error:
                print(f"Response is not valid JSON: {json_error}")

    except Exception as e:
        print(f"Error making request: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Test script started")
    test_email_summarization()
    print("Test script completed")
