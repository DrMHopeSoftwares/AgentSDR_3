#!/usr/bin/env python3
"""
Test organization creation directly
"""
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def test_org_creation():
    """Test creating an organization directly"""
    print("🏢 Testing Organization Creation...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_key:
        print("❌ Missing Supabase credentials")
        return False
    
    try:
        supabase = create_client(supabase_url, service_key)
        
        # Get the admin user
        admin_user = supabase.table('users').select('*').eq('email', 'admin@agentsdr.com').execute()
        if not admin_user.data:
            print("❌ Admin user not found")
            return False
        
        user_id = admin_user.data[0]['id']
        print(f"✅ Found admin user: {user_id}")
        
        # Test organization data
        org_name = "Test Organization"
        org_slug = "test-org"
        
        # Check if organization already exists
        existing_org = supabase.table('organizations').select('id').eq('slug', org_slug).execute()
        if existing_org.data:
            print(f"🗑️ Deleting existing organization: {org_slug}")
            supabase.table('organizations').delete().eq('slug', org_slug).execute()
        
        # Create organization
        org_data = {
            'id': str(uuid.uuid4()),
            'name': org_name,
            'slug': org_slug,
            'owner_user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        print(f"🏢 Creating organization: {org_name}")
        org_response = supabase.table('organizations').insert(org_data).execute()
        
        if org_response.data:
            print("✅ Organization created successfully")
            
            # Add creator as admin member
            member_data = {
                'id': str(uuid.uuid4()),
                'org_id': org_data['id'],
                'user_id': user_id,
                'role': 'admin',
                'joined_at': datetime.utcnow().isoformat()
            }
            
            print("👤 Adding creator as organization admin...")
            member_response = supabase.table('organization_members').insert(member_data).execute()
            
            if member_response.data:
                print("✅ Organization admin membership created")
                print(f"\n🎉 SUCCESS!")
                print(f"📋 Organization Details:")
                print(f"   Name: {org_name}")
                print(f"   Slug: {org_slug}")
                print(f"   Owner: admin@agentsdr.com")
                print(f"   URL: http://localhost:5000/orgs/{org_slug}")
                return True
            else:
                print("❌ Failed to create organization membership")
                return False
        else:
            print("❌ Failed to create organization")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_schema():
    """Check if all required tables exist"""
    print("\n🔍 Checking Database Schema...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    try:
        supabase = create_client(supabase_url, service_key)
        
        # Check tables
        tables_to_check = ['users', 'organizations', 'organization_members']
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' exists and accessible")
            except Exception as e:
                print(f"❌ Table '{table}' issue: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database schema check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AgentSDR Organization Creation Test")
    print("=" * 50)
    
    if check_database_schema():
        print("\n✅ Database schema OK")
        
        if test_org_creation():
            print("\n🎯 Organization creation works!")
            print("The issue might be in the Flask app or frontend.")
        else:
            print("\n❌ Organization creation failed")
    else:
        print("\n❌ Database schema issues found")
