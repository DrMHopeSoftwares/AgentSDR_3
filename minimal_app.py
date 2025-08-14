#!/usr/bin/env python3
"""
Minimal Flask app for testing
"""
from flask import Flask, render_template_string
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key')

# Simple template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AgentSDR Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .card { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>AgentSDR Dashboard</h1>
    
    <div class="card">
        <h2>Debug Info</h2>
        <p><strong>Organizations Count:</strong> {{ organizations|length }}</p>
        <p><strong>Records Count:</strong> {{ recent_records|length }}</p>
    </div>
    
    <div class="card">
        <h2>Your Organizations</h2>
        {% if organizations %}
            {% for org_data in organizations %}
            <div style="border: 1px solid #eee; padding: 15px; margin: 10px 0;">
                <h3>{{ org_data.org.name }}</h3>
                <p><strong>Slug:</strong> {{ org_data.org.slug }}</p>
                <p><strong>Role:</strong> {{ org_data.role }}</p>
                <a href="/orgs/{{ org_data.org.slug }}" class="btn">View Dashboard</a>
            </div>
            {% endfor %}
        {% else %}
            <p>No organizations found.</p>
            <a href="/orgs/create" class="btn">Create Organization</a>
        {% endif %}
    </div>
    
    <div class="card">
        <h2>Quick Actions</h2>
        <a href="/orgs/create" class="btn">Create Organization</a>
        <a href="/auth/logout" class="btn" style="background: #dc3545;">Logout</a>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return '<h1>AgentSDR</h1><p><a href="/dashboard">Go to Dashboard</a></p><p><a href="/auth/login">Login</a></p>'

@app.route('/dashboard')
def dashboard():
    try:
        from supabase import create_client
        
        # Get dashboard data
        supabase_url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        supabase = create_client(supabase_url, service_key)
        
        # Hardcode admin user for testing
        user_id = '95b6cb15-8d04-4abd-bc99-4be4d644309f'
        
        # Get memberships
        memberships = supabase.table('organization_members').select('org_id, role').eq('user_id', user_id).execute()
        
        # Get organization details
        org_details = []
        for membership in memberships.data:
            org_response = supabase.table('organizations').select('*').eq('id', membership['org_id']).execute()
            if org_response.data:
                org_data = org_response.data[0]
                org_details.append({
                    'org': org_data,
                    'role': membership['role']
                })
        
        return render_template_string(DASHBOARD_TEMPLATE, 
                                    organizations=org_details,
                                    recent_records=[])
    
    except Exception as e:
        return f'<h1>Dashboard Error</h1><p>{str(e)}</p><pre>{str(e.__class__.__name__)}</pre>'

@app.route('/auth/login')
def login():
    return '<h1>Login</h1><p>Use: admin@agentsdr.com / admin123</p><p><a href="/dashboard">Skip to Dashboard</a></p>'

@app.route('/orgs/create')
def create_org():
    return '<h1>Create Organization</h1><p>Organization creation form would go here</p><p><a href="/dashboard">Back to Dashboard</a></p>'

if __name__ == '__main__':
    print("🚀 Starting minimal Flask app...")
    print("🌐 Open: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
