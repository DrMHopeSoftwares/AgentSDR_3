#!/usr/bin/env python3
"""
Debug version of Flask app with better error handling
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🚀 Starting AgentSDR Flask Application (Debug Mode)")
    print("=" * 60)
    
    # Check environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_ROLE_KEY']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"❌ {var}: Missing")
            return False
    
    try:
        # Import and create the Flask app
        from agentsdr import create_app
        
        app = create_app()
        
        # Enable debug mode and detailed error logging
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
        
        print("✅ Flask app created successfully")
        print("🌐 Starting server on http://localhost:5000")
        print("\n📋 Available Routes:")
        print("   🏠 Home: http://localhost:5000")
        print("   🔐 Login: http://localhost:5000/auth/login")
        print("   📝 Signup: http://localhost:5000/auth/signup")
        print("   🏢 Create Org: http://localhost:5000/orgs/create")
        print("\n💡 Admin Login:")
        print("   📧 Email: admin@agentsdr.com")
        print("   🔑 Password: admin123")
        print("\n" + "=" * 60)
        
        # Add error handlers
        @app.errorhandler(500)
        def internal_error(error):
            print(f"🚨 500 Error: {error}")
            return f"Internal Server Error: {error}", 500
        
        @app.errorhandler(404)
        def not_found(error):
            print(f"🚨 404 Error: {error}")
            return f"Not Found: {error}", 404
        
        @app.errorhandler(Exception)
        def handle_exception(e):
            print(f"🚨 Unhandled Exception: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {e}", 500
        
        # Start the Flask development server
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False,  # Disable reloader to avoid issues
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required packages: pip install Flask Flask-Login Flask-WTF WTForms supabase python-dotenv email-validator")
        return False
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
