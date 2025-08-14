#!/usr/bin/env python3
"""
Create another super admin user
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def create_another_admin():
    """Create another super admin user"""
    print("🔧 Creating Another Super Admin...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    # Change these credentials as needed
    admin_email = input("Enter admin email: ")
    admin_password = input("Enter admin password: ")
    admin_name = input("Enter admin display name: ")
    
    try:
        supabase = create_client(supabase_url, service_key)
        
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
                'display_name': admin_name,
                'is_super_admin': True  # Make them super admin
            }
            
            db_response = supabase.table('users').insert(user_data).execute()
            
            if db_response.data:
                print("✅ Created database record")
                print("\n🎉 SUCCESS!")
                print(f"📧 Email: {admin_email}")
                print(f"🔑 Password: {admin_password}")
                print(f"👑 Role: Super Admin")
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
    print("🚀 Create Another Super Admin")
    print("=" * 40)
    
    if create_another_admin():
        print("\n🎯 Admin user created successfully!")
        print("They can now login at: http://localhost:5000/auth/login")
    else:
        print("\n❌ Failed to create admin user")
