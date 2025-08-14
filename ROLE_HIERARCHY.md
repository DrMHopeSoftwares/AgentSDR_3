# AgentSDR Role Hierarchy System

## 🎯 Role Structure Overview

Your AgentSDR system implements a perfect 3-tier role hierarchy:

```
👑 SUPER ADMIN (Developer/Monitor)
    ↓
🔧 ORGANIZATION ADMIN (Organization Creator/Manager)
    ↓
👤 USER (Regular Member)
```

## 📋 Detailed Role Breakdown

### 👑 **SUPER ADMIN** (Developer Role)
- **Who**: You (the developer) and other system administrators
- **Access**: EVERYTHING - Full system monitoring and control
- **Permissions**:
  - ✅ Access ALL organizations (even if not a member)
  - ✅ View all users and their activities
  - ✅ Create/delete any organization
  - ✅ Promote/demote any user
  - ✅ System-wide analytics and monitoring
  - ✅ Platform configuration and settings
  - ✅ Bypass all organization-level restrictions

### 🔧 **ORGANIZATION ADMIN** (Auto-promoted when creating org)
- **Who**: Users who create organizations
- **Access**: Full control over THEIR organization(s)
- **How they become admin**: Automatically when they create an organization
- **Permissions**:
  - ✅ Manage their organization settings
  - ✅ Invite users to their organization
  - ✅ Promote/demote members within their organization
  - ✅ Create/edit/delete organization content
  - ✅ View organization analytics
  - ✅ Remove members from their organization
  - ❌ Cannot access other organizations (unless invited)
  - ❌ Cannot access system-wide features

### 👤 **USER** (Default Role)
- **Who**: Anyone who registers on AgentSDR
- **Access**: Limited to organizations they're invited to
- **Permissions**:
  - ✅ Create organizations (becomes admin of that org)
  - ✅ Join organizations via invitation
  - ✅ View/edit content in organizations they're members of
  - ✅ Basic profile management
  - ❌ Cannot invite others (unless they're org admin)
  - ❌ Cannot access organizations they're not members of

## 🔄 Role Transition Flow

### **New User Registration**:
1. User visits: `http://localhost:5000/auth/signup`
2. Fills out registration form
3. **Automatically becomes**: 👤 **USER** (regular user)
4. Gets access to dashboard with option to create organization

### **User Creates Organization**:
1. User clicks "Create Organization"
2. Fills out organization details
3. **Automatically becomes**: 🔧 **ORGANIZATION ADMIN** for that specific organization
4. Can now invite other users to their organization

### **User Gets Invited to Organization**:
1. Organization admin sends invitation
2. User accepts invitation
3. **Becomes**: 👤 **MEMBER** of that organization
4. Can access that organization's content

## 🎯 Current Implementation Status

✅ **WORKING PERFECTLY**:
- User registration creates regular users
- Organization creation auto-promotes creator to admin
- Role-based access control (RBAC) system
- Organization membership system
- Invitation system
- Super admin bypass for all restrictions

## 🔐 Access Control Examples

### **Super Admin** (`admin@agentsdr.com`):
```
✅ Can access: /admin/users (all users)
✅ Can access: /orgs/any-org-slug (any organization)
✅ Can access: /admin/analytics (system analytics)
✅ Can access: /admin/settings (platform settings)
```

### **Organization Admin** (user who created "acme-corp"):
```
✅ Can access: /orgs/acme-corp/dashboard
✅ Can access: /orgs/acme-corp/members
✅ Can access: /orgs/acme-corp/settings
❌ Cannot access: /orgs/other-company/dashboard
❌ Cannot access: /admin/users
```

### **Regular User** (member of "acme-corp"):
```
✅ Can access: /orgs/acme-corp/dashboard (read-only)
✅ Can access: /orgs/acme-corp/records (based on permissions)
❌ Cannot access: /orgs/acme-corp/settings
❌ Cannot access: /orgs/acme-corp/members/invite
```

## 🚀 How to Use the System

### **As Super Admin**:
1. Login: `admin@agentsdr.com` / `admin123`
2. Access everything, monitor all organizations
3. Create additional super admins if needed

### **For Regular Users**:
1. Register at: `http://localhost:5000/auth/signup`
2. Create organization → Become organization admin
3. Invite team members to organization

### **Organization Management**:
1. Organization creator = automatic admin
2. Admin can invite users with roles: `admin` or `member`
3. Admin can promote members to admin
4. Admin can remove members

## 📊 Database Structure

```sql
users (
  id, email, display_name, 
  is_super_admin  -- Only true for system admins
)

organizations (
  id, name, slug, 
  owner_user_id  -- Creator becomes admin
)

organization_members (
  org_id, user_id, 
  role  -- 'admin' or 'member'
)
```

## ✨ Perfect Multi-Tenant Architecture

Your system is now perfectly set up as a **multi-tenant SaaS platform** where:

- 👑 **You (Super Admin)**: Monitor everything
- 🔧 **Organization Creators**: Manage their own organizations
- 👤 **Users**: Access organizations they're invited to

This is exactly how platforms like Slack, Discord, or GitHub work!
