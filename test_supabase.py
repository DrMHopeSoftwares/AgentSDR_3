#!/usr/bin/env python3
"""
Test Supabase connection and create admin user
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def test_connection():
    """Test Supabase connection"""
    print("🔧 Testing Supabase Connection...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_key:
        print("❌ Missing Supabase credentials")
        return False
    
    try:
        # Create client
        supabase = create_client(supabase_url, service_key)
        
        # Test connection by listing users
        print("📋 Testing auth connection...")
        users = supabase.auth.admin.list_users()
        print(f"✅ Found {len(users)} users in auth")
        
        # Test database connection
        print("📋 Testing database connection...")
        result = supabase.table('users').select('*').execute()
        print(f"✅ Found {len(result.data)} users in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_admin_user():
    """Create admin user directly"""
    print("\n🔧 Creating Admin User...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    admin_email = "admin@agentsdr.com"
    admin_password = "admin123"
    
    try:
        supabase = create_client(supabase_url, service_key)
        
        # Clear existing users first
        print("🗑️ Clearing existing users...")
        existing_users = supabase.auth.admin.list_users()
        for user in existing_users:
            try:
                supabase.auth.admin.delete_user(user.id)
                print(f"   ✅ Deleted {user.email}")
            except:
                pass
        
        # Clear database users
        supabase.table('users').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("✅ Cleared database users")
        
        # Create new admin user
        print(f"👤 Creating admin user: {admin_email}")
        auth_response = supabase.auth.admin.create_user({
            "email": admin_email,
            "password": admin_password,
            "email_confirm": True
        })
        
        if auth_response.user:
            user_id = auth_response.user.id
            print(f"✅ Created auth user: {user_id}")
            
            # Create database record
            user_data = {
                'id': user_id,
                'email': admin_email,
                'display_name': 'Super Admin',
                'is_super_admin': True
            }
            
            db_response = supabase.table('users').insert(user_data).execute()
            
            if db_response.data:
                print("✅ Created database record")
                print("\n🎉 SUCCESS!")
                print(f"📧 Email: {admin_email}")
                print(f"🔑 Password: {admin_password}")
                return True
            else:
                print("❌ Failed to create database record")
                return False
        else:
            print("❌ Failed to create auth user")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AgentSDR Supabase Test & Setup")
    print("=" * 40)
    
    if test_connection():
        print("\n✅ Supabase connection successful!")
        
        if create_admin_user():
            print("\n🎯 Next Steps:")
            print("1. Start Flask app: python app.py")
            print("2. Go to: http://localhost:5000/auth/login")
            print("3. Login with admin@agentsdr.com / admin123")
        else:
            print("\n❌ Failed to create admin user")
    else:
        print("\n❌ Supabase connection failed")
