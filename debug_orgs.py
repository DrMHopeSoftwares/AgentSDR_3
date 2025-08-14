#!/usr/bin/env python3
"""
Debug script to check organizations and memberships
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def debug_organizations():
    """Debug organizations and memberships"""
    print("🔍 Debugging Organizations and Memberships")
    print("=" * 50)
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    try:
        supabase = create_client(supabase_url, service_key)
        
        # Check users
        print("\n👤 USERS:")
        users = supabase.table('users').select('*').execute()
        for user in users.data:
            print(f"   - {user['email']} (ID: {user['id']}, Super Admin: {user.get('is_super_admin', False)})")
        
        # Check organizations
        print("\n🏢 ORGANIZATIONS:")
        orgs = supabase.table('organizations').select('*').execute()
        if orgs.data:
            for org in orgs.data:
                print(f"   - {org['name']} (Slug: {org['slug']}, Owner: {org['owner_user_id']})")
        else:
            print("   No organizations found!")
        
        # Check organization members
        print("\n👥 ORGANIZATION MEMBERS:")
        members = supabase.table('organization_members').select('*').execute()
        if members.data:
            for member in members.data:
                # Get user email
                user = supabase.table('users').select('email').eq('id', member['user_id']).execute()
                user_email = user.data[0]['email'] if user.data else 'Unknown'
                
                # Get org name
                org = supabase.table('organizations').select('name').eq('id', member['org_id']).execute()
                org_name = org.data[0]['name'] if org.data else 'Unknown'
                
                print(f"   - {user_email} is {member['role']} of {org_name}")
        else:
            print("   No organization members found!")
        
        # Check for admin user specifically
        print("\n🔍 ADMIN USER CHECK:")
        admin_user = supabase.table('users').select('*').eq('email', 'admin@agentsdr.com').execute()
        if admin_user.data:
            admin_id = admin_user.data[0]['id']
            print(f"   Admin user ID: {admin_id}")
            
            # Check admin's organizations
            admin_orgs = supabase.table('organization_members').select('*').eq('user_id', admin_id).execute()
            print(f"   Admin is member of {len(admin_orgs.data)} organizations:")
            for membership in admin_orgs.data:
                org = supabase.table('organizations').select('name, slug').eq('id', membership['org_id']).execute()
                if org.data:
                    print(f"     - {org.data[0]['name']} ({org.data[0]['slug']}) as {membership['role']}")
        else:
            print("   Admin user not found!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_organizations()
