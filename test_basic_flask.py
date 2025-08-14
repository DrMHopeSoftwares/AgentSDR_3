#!/usr/bin/env python3
"""
Test basic Flask app functionality
"""
import requests

def test_basic_flask():
    """Test basic Flask app endpoints"""
    
    print("Testing basic Flask app...")
    
    try:
        # Test home page
        response = requests.get("http://127.0.0.1:5000/", timeout=10)
        print(f"Home page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Basic Flask app is working")
        else:
            print(f"❌ Home page returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing Flask app: {e}")

if __name__ == "__main__":
    test_basic_flask()
