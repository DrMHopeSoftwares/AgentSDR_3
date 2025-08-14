#!/usr/bin/env python3
"""
Script to properly set up super admin authentication
"""
import os
import sys
import uuid
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, '.')
load_dotenv()

def create_admin_with_auth(email, password, display_name="Super Admin"):
    """Create a super admin user with proper authentication"""
    try:
        url = os.getenv('SUPABASE_URL')
        anon_key = os.getenv('SUPABASE_ANON_KEY')
        service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not anon_key or not service_key:
            print("❌ ERROR: Missing Supabase credentials in .env file")
            return False
        
        print(f"🔧 Setting up admin user: {email}")
        
        # Step 1: Create auth user using service role (bypasses email confirmation)
        print("Step 1: Creating Supabase auth user...")
        service_client = create_client(url, service_key)
        
        try:
            # Use admin API to create user
            auth_response = service_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True  # Auto-confirm email
            })
            
            if auth_response.user:
                print(f"✅ Auth user created: {auth_response.user.id}")
                auth_user_id = auth_response.user.id
            else:
                print("❌ Failed to create auth user")
                return False
                
        except Exception as auth_error:
            print(f"❌ Auth creation failed: {auth_error}")
            return False
        
        # Step 2: Create/update user in our users table
        print("Step 2: Creating user in database...")
        
        user_data = {
            'id': auth_user_id,
            'email': email,
            'display_name': display_name,
            'is_super_admin': True
        }
        
        # Try to insert, if exists then update
        try:
            response = service_client.table('users').insert(user_data).execute()
            print("✅ User created in database")
        except Exception as e:
            if "duplicate key" in str(e):
                # User exists, update it
                response = service_client.table('users').update({
                    'is_super_admin': True,
                    'display_name': display_name
                }).eq('email', email).execute()
                print("✅ User updated in database")
            else:
                print(f"❌ Database error: {e}")
                return False
        
        print(f"🎉 SUCCESS! Super admin created:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Display Name: {display_name}")
        print(f"   User ID: {auth_user_id}")
        print(f"\n🌐 You can now log in at: http://localhost:5000/login")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 AgentSDR - Super Admin Authentication Setup")
    print("=" * 50)
    
    # Check if we have proper credentials
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_SERVICE_ROLE_KEY'):
        print("❌ ERROR: Missing Supabase credentials!")
        print("Please check your .env file has:")
        print("- SUPABASE_URL")
        print("- SUPABASE_SERVICE_ROLE_KEY")
        print("- SUPABASE_ANON_KEY")
        return
    
    print("Enter details for your super admin account:")
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    display_name = input("Display Name (default: Super Admin): ").strip() or "Super Admin"
    
    if not email or not password:
        print("❌ Email and password are required!")
        return
    
    success = create_admin_with_auth(email, password, display_name)
    
    if success:
        print("\n✅ Setup complete! You can now:")
        print("1. Start the app: python app.py")
        print("2. Go to: http://localhost:5000/login")
        print("3. Log in with your credentials")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()
