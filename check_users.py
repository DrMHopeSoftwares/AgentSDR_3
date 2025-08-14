#!/usr/bin/env python3
"""
Simple script to check current users and hierarchy
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, '.')
load_dotenv()

def main():
    try:
        # Create Supabase client directly
        url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not url or not service_key:
            print("ERROR: Missing Supabase credentials in .env file")
            return

        supabase = create_client(url, service_key)
        
        # Get all users
        users_response = supabase.table('users').select('id, email, display_name, is_super_admin, created_at').execute()

        if users_response.data:
            print('👥 **Current Users in Database:**')
            print('-' * 80)
            for user in users_response.data:
                role_icon = '👑' if user.get('is_super_admin') else '👤'
                display_name = user.get('display_name', 'N/A')
                print(f'{role_icon} {user["email"]} ({display_name}) - Super Admin: {user.get("is_super_admin", False)}')
        else:
            print('No users found in the database.')
            
        # Get organizations
        orgs_response = supabase.table('organizations').select('*').execute()
        if orgs_response.data:
            print('\n🏢 **Organizations:**')
            print('-' * 80)
            for org in orgs_response.data:
                print(f'• {org["name"]} ({org["slug"]}) - Owner: {org["owner_user_id"]}')
                
        # Get organization members with user details
        members_response = supabase.table('organization_members').select('*, users(email)').execute()
        if members_response.data:
            print('\n👥 **Organization Members:**')
            print('-' * 80)
            for member in members_response.data:
                user_email = member.get('users', {}).get('email', 'Unknown') if member.get('users') else 'Unknown'
                print(f'• {user_email} - Role: {member["role"]} in Org: {member["org_id"]}')
                
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
