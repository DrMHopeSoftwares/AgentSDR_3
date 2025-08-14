#!/usr/bin/env python3
"""
Simple startup script for AgentSDR Flask application
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🚀 Starting AgentSDR Flask Application")
    print("=" * 50)
    
    # Check if required environment variables are set
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_ROLE_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    print("✅ Environment variables loaded")
    print(f"📍 Supabase URL: {os.getenv('SUPABASE_URL')}")
    
    try:
        # Import and create the Flask app
        from agentsdr import create_app
        
        app = create_app()
        
        print("✅ Flask app created successfully")
        print("🌐 Starting server on http://localhost:5000")
        print("\n📋 Available Routes:")
        print("   🏠 Home: http://localhost:5000")
        print("   🔐 Login: http://localhost:5000/auth/login")
        print("   📝 Signup: http://localhost:5000/auth/signup")
        print("\n💡 To create an admin account:")
        print("   1. Go to http://localhost:5000/auth/signup")
        print("   2. Register with any email/password")
        print("   3. The first user will be automatically made super admin")
        print("\n" + "=" * 50)
        
        # Start the Flask development server
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to avoid issues
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required packages: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return False

if __name__ == "__main__":
    main()
