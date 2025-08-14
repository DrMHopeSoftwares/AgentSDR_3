#!/usr/bin/env python3
"""
Test dashboard functionality directly
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def test_dashboard_data():
    """Test getting dashboard data directly"""
    print("🔍 Testing Dashboard Data")
    print("=" * 40)
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    try:
        supabase = create_client(supabase_url, service_key)
        
        # Get admin user
        admin_user = supabase.table('users').select('*').eq('email', 'admin@agentsdr.com').execute()
        if not admin_user.data:
            print("❌ Admin user not found")
            return False
        
        user_id = admin_user.data[0]['id']
        user_email = admin_user.data[0]['email']
        is_super_admin = admin_user.data[0].get('is_super_admin', False)
        
        print(f"👤 User: {user_email}")
        print(f"🔑 ID: {user_id}")
        print(f"👑 Super Admin: {is_super_admin}")
        
        # Get user's organization memberships
        print(f"\n🔍 Getting organization memberships...")
        memberships = supabase.table('organization_members').select('org_id, role').eq('user_id', user_id).execute()
        print(f"📊 Found {len(memberships.data)} memberships")
        
        # Get organization details
        org_details = []
        for membership in memberships.data:
            print(f"🔍 Processing membership: {membership}")
            
            org_response = supabase.table('organizations').select('*').eq('id', membership['org_id']).execute()
            if org_response.data:
                org_data = org_response.data[0]
                org_details.append({
                    'org': org_data,
                    'role': membership['role']
                })
                print(f"✅ Added org: {org_data['name']} (role: {membership['role']})")
            else:
                print(f"❌ Organization not found: {membership['org_id']}")
        
        print(f"\n📋 Final Dashboard Data:")
        print(f"   Organizations: {len(org_details)}")
        for org_detail in org_details:
            org = org_detail['org']
            role = org_detail['role']
            print(f"   - {org['name']} ({org['slug']}) as {role}")
        
        # Test template data structure
        print(f"\n🧪 Template Data Structure:")
        template_data = {
            'organizations': org_details,
            'recent_records': [],
            'current_user': {
                'email': user_email,
                'is_super_admin': is_super_admin
            }
        }
        
        print(f"   organizations count: {len(template_data['organizations'])}")
        print(f"   recent_records count: {len(template_data['recent_records'])}")
        print(f"   user email: {template_data['current_user']['email']}")
        print(f"   is_super_admin: {template_data['current_user']['is_super_admin']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_dashboard_data()
