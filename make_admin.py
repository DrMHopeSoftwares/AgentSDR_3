#!/usr/bin/env python3
"""
Simple script to make a user super admin
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, '.')
load_dotenv()

def make_super_admin(email):
    """Make a user super admin"""
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            print("ERROR: Missing Supabase credentials in .env file")
            return False
        
        supabase = create_client(url, key)
        
        # Check if user exists
        user_response = supabase.table('users').select('*').eq('email', email).execute()
        
        if not user_response.data:
            print(f"ERROR: User with email {email} not found!")
            print("Please create an account first through the web interface.")
            return False
        
        user = user_response.data[0]
        print(f"Found user: {user['email']}")
        
        # Update user to super admin
        update_response = supabase.table('users').update({
            'is_super_admin': True
        }).eq('id', user['id']).execute()
        
        if update_response.data:
            print(f"SUCCESS: {email} is now a Super Admin!")
            return True
        else:
            print("ERROR: Failed to update user role")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("AgentSDR - Make Super Admin")
    print("=" * 30)
    
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <email>")
        print("Example: python make_admin.py admin@example.com")
        sys.exit(1)
    
    email = sys.argv[1].strip()
    
    if not email:
        print("ERROR: Email address is required")
        sys.exit(1)
    
    success = make_super_admin(email)
    
    if success:
        print(f"\n{email} is now a super admin!")
        print("You can now log in and access admin features.")
    else:
        print("\nFailed to create super admin. Please check the errors above.")