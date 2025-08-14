# AgentSDR Architecture

## Overview

AgentSDR is a multi-tenant Flask application built with modern web technologies and enterprise-grade security. The architecture follows a modular blueprint pattern with clear separation of concerns.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│                 │    │                 │    │                 │
│ • Jinja2        │◄──►│ • Flask         │◄──►│ • Supabase      │
│ • Tailwind CSS  │    │ • Blueprints    │    │ • PostgreSQL    │
│ • Alpine.js     │    │ • RBAC          │    │ • RLS Policies  │
│ • HTMX          │    │ • Rate Limiting │    │ • GoTrue Auth   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Application Structure

### Core Components

#### 1. Flask Application Factory (`agentsdr/__init__.py`)
- Centralized app configuration
- Extension initialization
- Blueprint registration
- User loader for Flask-Login

#### 2. Authentication Module (`agentsdr/auth/`)
- **routes.py**: Login, signup, logout, invitation acceptance
- **models.py**: User model with Flask-Login integration
- **forms.py**: WTForms for validation

#### 3. Core Utilities (`agentsdr/core/`)
- **supabase_client.py**: Supabase client management
- **rbac.py**: Role-based access control decorators
- **models.py**: Pydantic models for validation
- **email.py**: Email service for invitations

#### 4. Organization Management (`agentsdr/orgs/`)
- Organization CRUD operations
- Member management
- Invitation system
- Role assignment

#### 5. Records Module (`agentsdr/records/`)
- Example domain data management
- Organization-scoped CRUD operations
- Demonstrates multi-tenant data access

#### 6. Admin Module (`agentsdr/admin/`)
- Super admin functionality
- Platform-wide analytics
- User and organization management

## Database Architecture

### Schema Design

```sql
-- Core entities with relationships
users (id, email, display_name, is_super_admin, created_at, updated_at)
  │
  ├── organizations (id, name, slug, owner_user_id, created_at, updated_at)
  │     │
  │     ├── organization_members (org_id, user_id, role, joined_at)
  │     ├── invitations (org_id, email, role, token, expires_at, invited_by)
  │     └── records (org_id, title, content, created_by, created_at, updated_at)
  │
  └── organization_members (user_id, org_id, role, joined_at)
```

### Row Level Security (RLS)

All tables implement RLS policies ensuring:

1. **Data Isolation**: Users can only access data from their organizations
2. **Role-Based Access**: Different permissions based on user roles
3. **Super Admin Bypass**: Super admins can access all data
4. **Secure Invitations**: Token-based invitation system with expiry

### Key Policies

```sql
-- Example: Records table policies
CREATE POLICY "Users can view records from their organizations" ON public.records
    FOR SELECT USING (public.is_org_member(org_id) OR public.is_super_admin());

CREATE POLICY "Users can create records in their organizations" ON public.records
    FOR INSERT WITH CHECK (public.is_org_member(org_id) OR public.is_super_admin());
```

## Security Architecture

### Authentication Flow

1. **User Login**: Supabase GoTrue authentication
2. **Session Management**: Flask-Login with secure cookies
3. **Token Storage**: Supabase tokens stored in Flask session
4. **Auto-refresh**: Automatic token refresh handling

### Authorization System

```python
# Decorator-based authorization
@require_super_admin
def admin_only_function():
    pass

@require_org_admin('org_slug')
def org_admin_function(org_slug):
    pass

@require_org_member('org_slug')
def org_member_function(org_slug):
    pass
```

### Security Features

- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **Rate Limiting**: Flask-Limiter with configurable limits
- **Secure Cookies**: HTTP-only, secure, same-site cookies
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: Parameterized queries via Supabase
- **XSS Protection**: Jinja2 auto-escaping

## Multi-Tenancy Implementation

### Data Isolation Strategy

1. **Organization-Scoped Queries**: All data queries include org_id filter
2. **RLS Policies**: Database-level enforcement of data boundaries
3. **URL-Based Context**: Organization context from URL parameters
4. **Session State**: Current organization stored in session

### Organization Context

```python
# URL pattern: /org/<org_slug>/records
@require_org_member('org_slug')
def list_records(org_slug):
    # org_slug parameter provides context
    # RLS policies ensure data isolation
    records = supabase.table('records').eq('org_id', org_id).execute()
```

## Frontend Architecture

### Template Structure

```
templates/
├── layout.html              # Base template with navigation
├── main/                    # Main application pages
│   ├── index.html          # Landing page
│   └── dashboard.html      # User dashboard
├── auth/                    # Authentication pages
│   ├── login.html          # Login form
│   ├── signup.html         # Signup form
│   └── accept_invitation.html
├── orgs/                    # Organization management
├── records/                 # Records management
└── admin/                   # Admin interface
```

### UI Components

- **Responsive Design**: Mobile-first with Tailwind CSS
- **Interactive Elements**: Alpine.js for client-side interactions
- **AJAX Requests**: HTMX for dynamic content updates
- **Toast Notifications**: JavaScript-based notification system
- **Modal Dialogs**: Alpine.js modal components

### CSS Architecture

```css
/* Component-based CSS with Tailwind */
.btn-primary {
    @apply bg-primary-600 text-white hover:bg-primary-700;
}

.card {
    @apply bg-white rounded-lg shadow-sm border border-secondary-200;
}
```

## API Design

### RESTful Endpoints

```
Authentication:
POST /auth/login
POST /auth/signup
GET  /auth/logout
GET  /invite/accept?token=<token>

Organizations:
GET    /orgs/create
POST   /orgs/create
GET    /orgs/<slug>/edit
POST   /orgs/<slug>/edit
GET    /orgs/<slug>/members
POST   /orgs/<slug>/members/<id>/remove
GET    /orgs/<slug>/invites
POST   /orgs/<slug>/invites

Records:
GET    /records/<org_slug>
POST   /records/<org_slug>/create
GET    /records/<org_slug>/<id>
POST   /records/<org_slug>/<id>/edit
DELETE /records/<org_slug>/<id>

Admin:
GET    /admin/dashboard
GET    /admin/organizations
GET    /admin/users
```

### Request/Response Patterns

```python
# JSON API responses
{
    "success": True,
    "data": {...},
    "error": None
}

# Error responses
{
    "success": False,
    "error": "Error message",
    "data": None
}
```

## Deployment Architecture

### Development Environment

```
┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   Tailwind CSS  │
│   (Port 5000)   │    │   (Watch Mode)  │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┼───► Browser
                                 │
                    ┌─────────────┴─────────────┐
                    │        Supabase           │
                    │   (Remote Database)       │
                    └───────────────────────────┘
```

### Production Environment

```
┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   CDN           │
│   (Nginx)       │    │   (Static Files)│
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│   WSGI Server   │
│   (Gunicorn)    │
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   Supabase      │
│   (Container)   │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘
```

### Docker Configuration

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
```

## Performance Considerations

### Database Optimization

- **Indexes**: Strategic indexes on frequently queried columns
- **RLS Efficiency**: Optimized RLS policies for minimal overhead
- **Connection Pooling**: Supabase handles connection management
- **Query Optimization**: Efficient queries with proper joins

### Caching Strategy

- **Session Storage**: Redis for session data
- **Static Assets**: CDN for CSS/JS files
- **Database Caching**: Supabase query caching
- **Application Caching**: In-memory caching for frequently accessed data

### Scalability

- **Horizontal Scaling**: Stateless application design
- **Database Scaling**: Supabase handles database scaling
- **CDN Integration**: Global content delivery
- **Load Balancing**: Multiple application instances

## Monitoring and Logging

### Application Monitoring

- **Error Tracking**: Structured error logging
- **Performance Metrics**: Request timing and database query metrics
- **User Analytics**: Usage patterns and feature adoption
- **Security Monitoring**: Failed login attempts and suspicious activity

### Database Monitoring

- **Query Performance**: Slow query identification
- **Connection Usage**: Database connection monitoring
- **Storage Metrics**: Database size and growth tracking
- **RLS Policy Performance**: Policy execution metrics

## Testing Strategy

### Test Types

1. **Unit Tests**: Individual function testing
2. **Integration Tests**: API endpoint testing
3. **Database Tests**: RLS policy verification
4. **Security Tests**: Authentication and authorization testing
5. **UI Tests**: Frontend component testing

### Test Coverage

- **Backend**: >85% code coverage target
- **Critical Paths**: 100% coverage for auth and RBAC
- **Database**: RLS policy testing
- **Security**: Penetration testing for common vulnerabilities

## Future Enhancements

### Planned Features

1. **API Versioning**: RESTful API with versioning
2. **Real-time Updates**: WebSocket integration
3. **Advanced Analytics**: Business intelligence dashboard
4. **Mobile App**: React Native mobile application
5. **Microservices**: Service decomposition for scale

### Technical Debt

1. **Database Migrations**: Automated migration system
2. **API Documentation**: OpenAPI/Swagger documentation
3. **Monitoring**: Advanced observability tools
4. **CI/CD**: Automated testing and deployment pipeline

---

This architecture provides a solid foundation for a scalable, secure, and maintainable multi-tenant application.
