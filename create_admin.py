#!/usr/bin/env python3
"""
Simple script to create a super admin user for AgentSDR
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def create_super_admin_simple():
    """Create a super admin user with a different email to avoid conflicts"""

    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not service_key:
        print("❌ Error: Missing Supabase credentials in .env file")
        return False

    # Use a different email to avoid conflicts
    admin_email = "superadmin@agentsdr.com"
    admin_password = "admin123"

    try:
        # Create Supabase client with service role key (admin access)
        supabase = create_client(supabase_url, service_key)

        print("🔧 Creating super admin user...")
        print(f"📧 Email: {admin_email}")
        print(f"🔑 Password: {admin_password}")

        # First, clear any existing users table entries
        try:
            supabase.table('users').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            print("✅ Cleared existing users table")
        except:
            pass

        # Create user in Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email": admin_email,
            "password": admin_password,
            "email_confirm": True  # Skip email confirmation
        })

        if auth_response.user:
            user_id = auth_response.user.id
            print(f"✅ Created auth user with ID: {user_id}")

            # Create user record in our users table
            user_data = {
                'id': user_id,
                'email': admin_email,
                'display_name': 'Super Admin',
                'is_super_admin': True
            }

            db_response = supabase.table('users').insert(user_data).execute()

            if db_response.data:
                print("✅ Created user profile in database")
                print("\n🎉 SUCCESS! Super admin created successfully!")
                print("\n📋 Login Details:")
                print(f"   Email: {admin_email}")
                print(f"   Password: {admin_password}")
                print(f"   URL: http://localhost:5000/auth/login")
                return True
            else:
                print("❌ Failed to create user profile in database")
                return False
        else:
            print("❌ Failed to create user in Supabase Auth")
            return False

    except Exception as e:
        print(f"❌ Error creating super admin: {e}")
        # If user already exists, try to just create the database record
        if "already been registered" in str(e):
            print("🔄 User already exists in auth, trying to create database record...")
            try:
                # Try to get the existing user
                existing_users = supabase.auth.admin.list_users()
                for user in existing_users:
                    if user.email == admin_email:
                        user_data = {
                            'id': user.id,
                            'email': admin_email,
                            'display_name': 'Super Admin',
                            'is_super_admin': True
                        }

                        # Try to insert or update
                        db_response = supabase.table('users').upsert(user_data).execute()

                        if db_response.data:
                            print("✅ Updated user profile in database")
                            print("\n🎉 SUCCESS! Super admin ready!")
                            print("\n📋 Login Details:")
                            print(f"   Email: {admin_email}")
                            print(f"   Password: {admin_password}")
                            print(f"   URL: http://localhost:5000/auth/login")
                            return True
                        break
            except Exception as e2:
                print(f"❌ Failed to handle existing user: {e2}")

        return False



if __name__ == "__main__":
    print("🚀 AgentSDR Super Admin Creator")
    print("=" * 40)

    success = create_super_admin_simple()

    if success:
        print("\n🎯 Next Steps:")
        print("1. Start the Flask app: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Click 'Login' and use the credentials above")
        sys.exit(0)
    else:
        print("\n❌ Failed to create super admin")
        sys.exit(1)
