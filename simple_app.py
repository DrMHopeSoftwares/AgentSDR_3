#!/usr/bin/env python3
"""
Simple Flask app runner with minimal setup
"""
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Set Flask environment
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

try:
    from agentsdr import create_app
    
    print("🚀 Creating Flask app...")
    app = create_app()
    
    print("✅ Flask app created successfully")
    print("🌐 Starting server on http://localhost:5000")
    print("📧 Admin login: admin@agentsdr.com / admin123")
    print("=" * 50)
    
    # Run the app
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        use_reloader=False,
        threaded=True
    )
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
