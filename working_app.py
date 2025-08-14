#!/usr/bin/env python3
"""
Working AgentSDR Flask app with proper authentication
"""
import os
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Supabase client
supabase_url = os.getenv('SUPABASE_URL')
service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(supabase_url, service_key)

class User(UserMixin):
    def __init__(self, id, email, display_name=None, is_super_admin=False):
        self.id = id
        self.email = email
        self.display_name = display_name
        self.is_super_admin = is_super_admin

@login_manager.user_loader
def load_user(user_id):
    try:
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        if response.data:
            user_data = response.data[0]
            return User(
                id=user_data['id'],
                email=user_data['email'],
                display_name=user_data.get('display_name'),
                is_super_admin=user_data.get('is_super_admin', False)
            )
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

# Templates
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>AgentSDR - Login</title>
<style>body{font-family:Arial;margin:40px;} .form{max-width:400px;} input{width:100%;padding:10px;margin:10px 0;} .btn{background:#007bff;color:white;padding:10px 20px;border:none;cursor:pointer;}</style>
</head>
<body>
    <h1>AgentSDR Login</h1>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <div style="color:red;margin:10px 0;">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="POST" class="form">
        <input type="email" name="email" placeholder="Email" required value="admin@agentsdr.com">
        <input type="password" name="password" placeholder="Password" required value="admin123">
        <button type="submit" class="btn">Login</button>
    </form>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>AgentSDR - Dashboard</title>
<style>
body{font-family:Arial;margin:40px;background:#f5f5f5;} 
.card{background:white;padding:20px;margin:20px 0;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);} 
.btn{background:#007bff;color:white;padding:10px 20px;text-decoration:none;border-radius:4px;display:inline-block;margin:5px;}
.btn:hover{background:#0056b3;} 
.org-card{border:1px solid #ddd;padding:15px;margin:10px 0;border-radius:5px;}
.role-admin{background:#e3f2fd;color:#1976d2;padding:2px 8px;border-radius:12px;font-size:12px;}
.role-member{background:#e8f5e8;color:#388e3c;padding:2px 8px;border-radius:12px;font-size:12px;}
</style>
</head>
<body>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
        <h1>AgentSDR Dashboard</h1>
        <div>
            <span>{{ current_user.email }}</span>
            <a href="/logout" class="btn" style="background:#dc3545;">Logout</a>
        </div>
    </div>
    
    <div class="card">
        <h2>Debug Info</h2>
        <p><strong>User:</strong> {{ current_user.email }}</p>
        <p><strong>Super Admin:</strong> {{ current_user.is_super_admin }}</p>
        <p><strong>Organizations:</strong> {{ organizations|length }}</p>
    </div>
    
    <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
            <h2>Your Organizations</h2>
            <a href="/orgs/create" class="btn">Create Organization</a>
        </div>
        
        {% if organizations %}
            {% for org_data in organizations %}
            <div class="org-card">
                <div style="display:flex;justify-content:space-between;align-items:start;">
                    <div>
                        <h3 style="margin:0 0 10px 0;">{{ org_data.org.name }}</h3>
                        <p style="margin:0;color:#666;">{{ org_data.org.slug }}</p>
                    </div>
                    <span class="role-{{ org_data.role }}">{{ org_data.role }}</span>
                </div>
                <div style="margin-top:15px;">
                    <a href="/orgs/{{ org_data.org.slug }}" class="btn">View Dashboard</a>
                    {% if org_data.role == 'admin' %}
                    <a href="/orgs/{{ org_data.org.slug }}/members" class="btn" style="background:#6c757d;">Manage</a>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div style="text-align:center;padding:40px;color:#666;">
                <h3>No Organizations</h3>
                <p>Create your first organization to get started.</p>
                <a href="/orgs/create" class="btn">Create Organization</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            # Authenticate with Supabase
            auth_response = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
            
            if auth_response.user:
                # Get user from our database
                user_response = supabase.table('users').select('*').eq('email', email).execute()
                if user_response.data:
                    user_data = user_response.data[0]
                    user = User(
                        id=user_data['id'],
                        email=user_data['email'],
                        display_name=user_data.get('display_name'),
                        is_super_admin=user_data.get('is_super_admin', False)
                    )
                    login_user(user)
                    return redirect(url_for('dashboard'))
                else:
                    flash('User profile not found.')
            else:
                flash('Invalid email or password.')
        except Exception as e:
            flash(f'Login error: {str(e)}')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get user's organizations
        memberships = supabase.table('organization_members').select('org_id, role').eq('user_id', current_user.id).execute()
        
        organizations = []
        for membership in memberships.data:
            org_response = supabase.table('organizations').select('*').eq('id', membership['org_id']).execute()
            if org_response.data:
                organizations.append({
                    'org': org_response.data[0],
                    'role': membership['role']
                })
        
        return render_template_string(DASHBOARD_TEMPLATE, organizations=organizations)
    
    except Exception as e:
        flash(f'Dashboard error: {str(e)}')
        return render_template_string(DASHBOARD_TEMPLATE, organizations=[])

@app.route('/orgs/create')
@login_required
def create_org():
    return '<h1>Create Organization</h1><p>Organization creation form would go here</p><p><a href="/dashboard">Back to Dashboard</a></p>'

if __name__ == '__main__':
    print("🚀 Starting Working AgentSDR App...")
    print("🌐 Open: http://localhost:5000")
    print("📧 Login: admin@agentsdr.com / admin123")
    print("=" * 50)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
