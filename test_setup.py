#!/usr/bin/env python3
"""
Quick test script to verify AgentSDR setup
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_env_config():
    """Test environment configuration"""
    print("🔧 Testing Environment Configuration")
    print("=" * 50)
    
    # Check Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon = os.getenv('SUPABASE_ANON_KEY')
    supabase_service = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    print(f"SUPABASE_URL: {'✅ Configured' if supabase_url and 'your-project' not in supabase_url else '❌ Not configured'}")
    print(f"SUPABASE_ANON_KEY: {'✅ Configured' if supabase_anon and 'your-anon' not in supabase_anon else '❌ Not configured'}")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'✅ Configured' if supabase_service and 'your-service' not in supabase_service else '❌ Not configured'}")
    
    # Check Flask config
    flask_secret = os.getenv('FLASK_SECRET_KEY')
    print(f"FLASK_SECRET_KEY: {'✅ Configured' if flask_secret and 'your-super-secret' not in flask_secret else '❌ Not configured'}")
    
    print()
    
    if 'your-project' in supabase_url or 'your-anon' in supabase_anon:
        print("❌ **CRITICAL: Supabase credentials not configured!**")
        print("Please update your .env file with your actual Supabase credentials.")
        return False
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("📦 Testing Module Imports")
    print("=" * 50)
    
    try:
        import flask
        print("✅ Flask")
    except ImportError as e:
        print(f"❌ Flask: {e}")
        return False
    
    try:
        import supabase
        print("✅ Supabase")
    except ImportError as e:
        print(f"❌ Supabase: {e}")
        return False
    
    try:
        from agentsdr import create_app
        print("✅ AgentSDR App")
    except ImportError as e:
        print(f"❌ AgentSDR App: {e}")
        return False
    
    print()
    return True

def main():
    print("🧪 AgentSDR Setup Test")
    print("=" * 50)
    
    env_ok = test_env_config()
    imports_ok = test_imports()
    
    print("📋 **Summary:**")
    if env_ok and imports_ok:
        print("✅ All tests passed! Your setup looks good.")
        print("\n🚀 **Next Steps:**")
        print("1. Set up database schema in Supabase SQL Editor")
        print("2. Start the app: python app.py")
        print("3. Create an account at http://localhost:5000")
        print("4. Set yourself as super admin: python scripts/setup_super_admin.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        if not env_ok:
            print("\n🔧 **Fix Environment:**")
            print("1. Update .env file with real Supabase credentials")
            print("2. Get credentials from Supabase Dashboard > Project Settings > API")
        if not imports_ok:
            print("\n🔧 **Fix Dependencies:**")
            print("1. Run: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
