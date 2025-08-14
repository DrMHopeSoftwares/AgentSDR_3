#!/usr/bin/env python3
"""
Simple Flask app runner
"""
from agentsdr import create_app

if __name__ == '__main__':
    print("🚀 Starting AgentSDR...")
    app = create_app()
    print("✅ Flask app created")
    print("🌐 Server starting on http://localhost:5000")
    print("📧 Admin: admin@agentsdr.com / admin123")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )
