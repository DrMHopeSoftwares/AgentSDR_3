from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from agentsdr.orgs import orgs_bp
from agentsdr.core.supabase_client import get_supabase, get_service_supabase
from agentsdr.core.rbac import require_org_admin, require_org_member, is_org_admin
from agentsdr.core.email import get_email_service
from agentsdr.core.models import CreateOrganizationRequest, UpdateOrganizationRequest, CreateInvitationRequest
from datetime import datetime, timedelta
import uuid
import secrets

@orgs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_organization():
    if request.method == 'POST':
        try:
            # Handle both JSON and form data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()

            current_app.logger.info(f"Creating organization with data: {data}")
            current_app.logger.info(f"Current user: {current_user.id} ({current_user.email})")

            org_request = CreateOrganizationRequest(**data)

            supabase = get_service_supabase()

            # Check if slug is unique
            existing_org = supabase.table('organizations').select('id').eq('slug', org_request.slug).execute()
            if existing_org.data:
                current_app.logger.warning(f"Organization slug already exists: {org_request.slug}")
                return jsonify({'error': 'Organization slug already exists'}), 400

            # Create organization
            org_data = {
                'id': str(uuid.uuid4()),
                'name': org_request.name,
                'slug': org_request.slug,
                'owner_user_id': current_user.id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            current_app.logger.info(f"Inserting organization data: {org_data}")
            org_response = supabase.table('organizations').insert(org_data).execute()

            if org_response.data:
                current_app.logger.info("Organization created successfully")

                # Add creator as admin
                member_data = {
                    'id': str(uuid.uuid4()),
                    'org_id': org_data['id'],
                    'user_id': current_user.id,
                    'role': 'admin',
                    'joined_at': datetime.utcnow().isoformat()
                }

                current_app.logger.info(f"Adding organization member: {member_data}")
                member_response = supabase.table('organization_members').insert(member_data).execute()

                if member_response.data:
                    current_app.logger.info("Organization member added successfully")
                    flash('Organization created successfully!', 'success')
                    return jsonify({
                        'success': True,
                        'message': 'Organization created successfully!',
                        'redirect': url_for('main.dashboard')  # Redirect to dashboard for now
                    })
                else:
                    current_app.logger.error("Failed to add organization member")
                    return jsonify({'error': 'Failed to add organization member'}), 500
            else:
                current_app.logger.error("Failed to create organization")
                return jsonify({'error': 'Failed to create organization'}), 500

        except Exception as e:
            current_app.logger.error(f"Error creating organization: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Error creating organization: {str(e)}'}), 400

    return render_template('orgs/create.html')

@orgs_bp.route('/<org_slug>/edit', methods=['GET', 'POST'])
@require_org_admin('org_slug')
def edit_organization(org_slug):
    try:
        supabase = get_supabase()

        # Get organization
        org_response = supabase.table('organizations').select('*').eq('slug', org_slug).execute()
        if not org_response.data:
            flash('Organization not found.', 'error')
            return redirect(url_for('main.dashboard'))

        organization = org_response.data[0]

        if request.method == 'POST':
            try:
                data = request.get_json()
                update_request = UpdateOrganizationRequest(**data)

                update_data = {}
                if update_request.name:
                    update_data['name'] = update_request.name
                if update_request.slug:
                    # Check if new slug is unique
                    if update_request.slug != org_slug:
                        existing_org = supabase.table('organizations').select('id').eq('slug', update_request.slug).execute()
                        if existing_org.data:
                            return jsonify({'error': 'Organization slug already exists'}), 400
                    update_data['slug'] = update_request.slug

                if update_data:
                    update_data['updated_at'] = datetime.utcnow().isoformat()
                    supabase.table('organizations').update(update_data).eq('id', organization['id']).execute()

                flash('Organization updated successfully!', 'success')
                return jsonify({'redirect': url_for('main.org_dashboard', org_slug=update_data.get('slug', org_slug))})

            except Exception as e:
                return jsonify({'error': str(e)}), 400

        return render_template('orgs/edit.html', organization=organization)

    except Exception as e:
        flash('Error loading organization.', 'error')
        return redirect(url_for('main.dashboard'))
@orgs_bp.route('/<org_slug>/manage', methods=['GET'])
@require_org_admin('org_slug')
def manage_organization(org_slug):
    """Organization admin overview page with management actions"""
    try:
        supabase = get_service_supabase()

        # Get organization
        org_response = supabase.table('organizations').select('*').eq('slug', org_slug).execute()
        if not org_response.data:
            flash('Organization not found.', 'error')
            return redirect(url_for('main.dashboard'))
        organization = org_response.data[0]

        # Counts and recent
        members_count = supabase.table('organization_members').select('id', count='exact').eq('org_id', organization['id']).execute()
        records_count = supabase.table('records').select('id', count='exact').eq('org_id', organization['id']).execute()
        invites_count = supabase.table('invitations').select('id', count='exact').eq('org_id', organization['id']).execute()

        recent_records = supabase.table('records').select('*').eq('org_id', organization['id']).order('created_at', desc=True).limit(5).execute()
        # Agents count may fail if table not yet migrated
        try:
            agents_count_resp = supabase.table('agents').select('id', count='exact').eq('org_id', organization['id']).execute()
            agents_count_val = agents_count_resp.count or 0
        except Exception:
            agents_count_val = 0

        return render_template('orgs/manage.html',
                               organization=organization,
                               members_count=members_count.count or 0,
                               records_count=records_count.count or 0,
                               invites_count=invites_count.count or 0,
                               agents_count=agents_count_val,
                               recent_records=recent_records.data or [])
    except Exception as e:
        flash('Error loading organization.', 'error')
        return redirect(url_for('main.dashboard'))


@orgs_bp.route('/<org_slug>', methods=['DELETE'])
@require_org_admin('org_slug')
def delete_organization(org_slug):
    """Delete organization and related data (admin only)."""
    try:
        supabase = get_service_supabase()
        org_resp = supabase.table('organizations').select('id').eq('slug', org_slug).execute()
        if not org_resp.data:
            return jsonify({'error': 'Organization not found'}), 404
        org_id = org_resp.data[0]['id']

        # Delete related rows first (basic cascade)
        supabase.table('organization_members').delete().eq('org_id', org_id).execute()
        supabase.table('invitations').delete().eq('org_id', org_id).execute()
        supabase.table('records').delete().eq('org_id', org_id).execute()

        # Delete organization
        supabase.table('organizations').delete().eq('id', org_id).execute()

        flash('Organization deleted successfully.', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orgs_bp.route('/<org_slug>/agents', methods=['POST'])
@require_org_admin('org_slug')
def create_agent(org_slug):
    """Create an agent for the organization. Types: email_summarizer | hubspot_data | custom"""
    try:
        # Accept JSON or form-encoded payloads robustly
        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            data = request.form.to_dict() or {}
        name = (data.get('name') or '').strip()
        agent_type = (data.get('type') or '').strip()
        if not name or not agent_type:
            return jsonify({'error': 'Name and type are required'}), 400
        if agent_type not in ['email_summarizer', 'hubspot_data', 'custom']:
            return jsonify({'error': 'Invalid agent type'}), 400

        supabase = get_service_supabase()
        # Resolve slug -> id
        org_resp = supabase.table('organizations').select('id').eq('slug', org_slug).limit(1).execute()
        if not org_resp.data:
            return jsonify({'error': 'Organization not found'}), 404
        org_id = org_resp.data[0]['id']

        # For now, store agents in records table as placeholder
        # title=name, content=JSON metadata, type='agent'
        import json, uuid
        now = datetime.utcnow().isoformat()
        agent = {
            'id': str(uuid.uuid4()),
            'org_id': org_id,
            'name': name,
            'agent_type': agent_type,
            'config': {},
            'created_by': current_user.id,
            'created_at': now,
            'updated_at': now
        }
        supabase.table('agents').insert(agent).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orgs_bp.route('/<org_slug>/agents', methods=['GET'])
@require_org_member('org_slug')
def list_agents(org_slug):
    """List agents for an organization (records tagged as agents)."""
    try:
        supabase = get_service_supabase()
        org_resp = supabase.table('organizations').select('*').eq('slug', org_slug).limit(1).execute()
        if not org_resp.data:
            flash('Organization not found.', 'error')
            return redirect(url_for('main.dashboard'))
        organization = org_resp.data[0]

        # For now: agents are records whose content JSON has agent_type
        agents_resp = supabase.table('agents').select('*').eq('org_id', organization['id']).order('created_at', desc=True).execute()
        agents = agents_resp.data or []
        return render_template('orgs/agents.html', organization=organization, agents=agents)
    except Exception as e:
        flash('Error loading agents.', 'error')
        return redirect(url_for('main.dashboard'))



@orgs_bp.route('/<org_slug>/members')
@require_org_member('org_slug')
def list_members(org_slug):
    try:
        supabase = get_supabase()
        # Get organization
        org_response = supabase.table('organizations').select('*').eq('slug', org_slug).execute()
        if not org_response.data:
            flash('Organization not found.', 'error')
            return redirect(url_for('main.dashboard'))
        organization = org_response.data[0]

        # Get members
        members_response = supabase.table('organization_members').select('user_id, role, joined_at').eq('org_id', organization['id']).execute()
        members = []
        for member in members_response.data:
            user_response = supabase.table('users').select('email, display_name').eq('id', member['user_id']).execute()
            if user_response.data:
                user_data = user_response.data[0]
                members.append({
                    'user_id': member['user_id'],
                    'email': user_data['email'],
                    'display_name': user_data.get('display_name'),
                    'role': member['role'],
                    'joined_at': member['joined_at']
                })

        return render_template('orgs/members.html', organization=organization, members=members)

    except Exception as e:
        flash('Error loading members.', 'error')
        return redirect(url_for('main.dashboard'))


@orgs_bp.route('/<org_slug>/agents/<agent_id>', methods=['PATCH'])
@require_org_admin('org_slug')
def update_agent(org_slug, agent_id):
    try:
        data = request.get_json() or {}
        updates = {}
        if 'name' in data and data['name']:
            updates['name'] = data['name']
        if not updates:
            return jsonify({'error': 'No changes provided'}), 400
        updates['updated_at'] = datetime.utcnow().isoformat()
        supabase = get_service_supabase()
        supabase.table('agents').update(updates).eq('id', agent_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orgs_bp.route('/<org_slug>/agents/<agent_id>', methods=['DELETE'])
@require_org_admin('org_slug')
def delete_agent(org_slug, agent_id):
    try:
        supabase = get_service_supabase()
        supabase.table('agents').delete().eq('id', agent_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orgs_bp.route('/<org_slug>/members/<user_id>/remove', methods=['POST'])
@require_org_admin('org_slug')
def remove_member(org_slug, user_id):
    try:
        supabase = get_supabase()

        # Get organization
        org_response = supabase.table('organizations').select('*').eq('slug', org_slug).execute()
        if not org_response.data:
            return jsonify({'error': 'Organization not found'}), 404

        organization = org_response.data[0]

        # Check if user is trying to remove themselves
        if user_id == current_user.id:
            return jsonify({'error': 'Cannot remove yourself from the organization'}), 400

        # Remove member
        supabase.table('organization_members').delete().eq('org_id', organization['id']).eq('user_id', user_id).execute()

        flash('Member removed successfully.', 'success')
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orgs_bp.route('/<org_slug>/members/<user_id>/role', methods=['POST'])
@require_org_admin('org_slug')
def update_member_role(org_slug, user_id):
    try:
        data = request.get_json()
        new_role = data.get('role')

        if new_role not in ['admin', 'member']:
            return jsonify({'error': 'Invalid role'}), 400

        supabase = get_supabase()

        # Get organization
        org_response = supabase.table('organizations').select('*').eq('slug', org_slug).execute()
        if not org_response.data:
            return jsonify({'error': 'Organization not found'}), 404

        organization = org_response.data[0]

        # Update member role
        supabase.table('organization_members').update({'role': new_role}).eq('org_id', organization['id']).eq('user_id', user_id).execute()

        flash('Member role updated successfully.', 'success')
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orgs_bp.route('/<org_slug>/invites')
@require_org_admin('org_slug')
def list_invitations(org_slug):
    try:
        supabase = get_supabase()

        # Get organization
        org_response = supabase.table('organizations').select('*').eq('slug', org_slug).execute()
        if not org_response.data:
            flash('Organization not found.', 'error')
            return redirect(url_for('main.dashboard'))

        organization = org_response.data[0]

        # Get invitations
        invitations_response = supabase.table('invitations').select('*').eq('org_id', organization['id']).order('created_at', desc=True).execute()

        return render_template('orgs/invitations.html', organization=organization, invitations=invitations_response.data)

    except Exception as e:
        flash('Error loading invitations.', 'error')
        return redirect(url_for('main.dashboard'))

@orgs_bp.route('/<org_slug>/invites', methods=['POST'])
@require_org_admin('org_slug')
def create_invitation(org_slug):
    try:
        data = request.get_json()
        invite_request = CreateInvitationRequest(**data)

        supabase = get_supabase()

        # Get organization
        org_response = supabase.table('organizations').select('*').eq('slug', org_slug).execute()
        if not org_response.data:
            return jsonify({'error': 'Organization not found'}), 404

        organization = org_response.data[0]

        # Check if user is already a member
        existing_member = supabase.table('organization_members').select('*').eq('org_id', organization['id']).eq('user_id', invite_request.email).execute()
        if existing_member.data:
            return jsonify({'error': 'User is already a member of this organization'}), 400

        # Check if invitation already exists
        existing_invite = supabase.table('invitations').select('*').eq('org_id', organization['id']).eq('email', invite_request.email).eq('accepted_at', None).execute()
        if existing_invite.data:
            return jsonify({'error': 'Invitation already sent to this email'}), 400

        # Create invitation
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=72)

        invitation_data = {
            'id': str(uuid.uuid4()),
            'org_id': organization['id'],
            'email': invite_request.email,
            'role': invite_request.role,
            'token': token,
            'expires_at': expires_at.isoformat(),
            'invited_by': current_user.id,
            'created_at': datetime.utcnow().isoformat()
        }

        invitation_response = supabase.table('invitations').insert(invitation_data).execute()

        if invitation_response.data:
            # Send invitation email
            email_sent = get_email_service().send_invitation_email(
                invite_request.email,
                organization['name'],
                invite_request.role,
                token,
                current_user.display_name or current_user.email
            )

            if email_sent:
                flash('Invitation sent successfully!', 'success')
            else:
                flash('Invitation created but email failed to send.', 'warning')

            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to create invitation'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@orgs_bp.route('/<org_slug>/invites/<invitation_id>/resend', methods=['POST'])
@require_org_admin('org_slug')
def resend_invitation(org_slug, invitation_id):
    try:
        supabase = get_supabase()

        # Get invitation
        invitation_response = supabase.table('invitations').select('*').eq('id', invitation_id).execute()
        if not invitation_response.data:
            return jsonify({'error': 'Invitation not found'}), 404

        invitation = invitation_response.data[0]

        # Get organization
        org_response = supabase.table('organizations').select('*').eq('id', invitation['org_id']).execute()
        if not org_response.data:
            return jsonify({'error': 'Organization not found'}), 404

        organization = org_response.data[0]

        # Resend invitation email
        email_sent = get_email_service().send_invitation_email(
            invitation['email'],
            organization['name'],
            invitation['role'],
            invitation['token'],
            current_user.display_name or current_user.email
        )

        if email_sent:
            flash('Invitation resent successfully!', 'success')
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to send invitation email'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@orgs_bp.route('/mine', methods=['GET'])
@login_required
def my_organizations():
    """List organizations where the current user is admin"""
    try:
        supabase = get_service_supabase()

        # Get memberships where user is admin
        memberships = supabase.table('organization_members').select('org_id, role').eq('user_id', current_user.id).eq('role', 'admin').execute()

        # Collect org details
        orgs = []
        for m in memberships.data or []:
            org_resp = supabase.table('organizations').select('id, name, slug, owner_user_id, created_at').eq('id', m['org_id']).execute()
            if org_resp.data:
                orgs.append({
                    'org': org_resp.data[0],
                    'role': m['role']
                })

        return render_template('orgs/mine.html', organizations=orgs)
    except Exception as e:
        flash(f'Failed to load organizations: {e}', 'error')
        return render_template('orgs/mine.html', organizations=[])



@orgs_bp.route('/<org_slug>/invites/<invitation_id>', methods=['DELETE'])
@require_org_admin('org_slug')
def revoke_invitation(org_slug, invitation_id):
    try:
        supabase = get_supabase()

        # Delete invitation
        supabase.table('invitations').delete().eq('id', invitation_id).execute()

        flash('Invitation revoked successfully.', 'success')
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
