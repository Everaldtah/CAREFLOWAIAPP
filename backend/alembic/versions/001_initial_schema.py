"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('plan', sa.String(50), nullable=False, server_default='basic'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('settings', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'])

    # Create clinics table
    op.create_table(
        'clinics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('npi', sa.String(20), unique=True),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('fax', sa.String(50)),
        sa.Column('address_line1', sa.String(255)),
        sa.Column('address_line2', sa.String(255)),
        sa.Column('city', sa.String(100)),
        sa.Column('state', sa.String(50)),
        sa.Column('postal_code', sa.String(20)),
        sa.Column('country', sa.String(100), server_default='USA'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('settings', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clinics.id', ondelete='SET NULL')),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(50)),
        sa.Column('role', sa.String(50), nullable=False, server_default='patient'),
        sa.Column('permissions', postgresql.ARRAY(sa.String(100)), server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('npi', sa.String(20)),
        sa.Column('specialization', sa.String(255)),
        sa.Column('license_number', sa.String(100)),
        sa.Column('api_key_hash', sa.String(255), unique=True),
        sa.Column('preferences', postgresql.JSON()),
        sa.Column('timezone', sa.String(50), server_default='America/New_York'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clinics.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mrn', sa.String(50), unique=True),
        sa.Column('first_name', sa.String(255), nullable=False),
        sa.Column('last_name', sa.String(255), nullable=False),
        sa.Column('preferred_name', sa.String(100)),
        sa.Column('date_of_birth', sa.Date()),
        sa.Column('gender', sa.String(50), nullable=False, server_default='unknown'),
        sa.Column('sex_at_birth', sa.String(50), server_default='unknown'),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('phone_type', sa.String(20)),
        sa.Column('address_line1', sa.String(255)),
        sa.Column('address_line2', sa.String(255)),
        sa.Column('city', sa.String(100)),
        sa.Column('state', sa.String(50)),
        sa.Column('postal_code', sa.String(20)),
        sa.Column('country', sa.String(100), server_default='USA'),
        sa.Column('emergency_contact_name', sa.String(255)),
        sa.Column('emergency_contact_phone', sa.String(50)),
        sa.Column('emergency_contact_relationship', sa.String(100)),
        sa.Column('blood_type', sa.String(10)),
        sa.Column('allergies', postgresql.ARRAY(sa.String())),
        sa.Column('medical_conditions', postgresql.ARRAY(sa.String())),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('no_show_count', sa.Integer(), server_default='0'),
        sa.Column('portal_enabled', sa.Boolean(), server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create appointments table
    op.create_table(
        'appointments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clinics.id', ondelete='CASCADE'), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), server_default='30'),
        sa.Column('appointment_type', sa.String(50), nullable=False, server_default='follow_up'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('chief_complaint', sa.Text()),
        sa.Column('notes', sa.Text()),
        sa.Column('fee', sa.Numeric(10, 2)),
        sa.Column('is_telehealth', sa.Boolean(), server_default='false'),
        sa.Column('telehealth_link', sa.String(500)),
        sa.Column('reminder_sent', sa.Boolean(), server_default='false'),
        sa.Column('reminder_count', sa.Integer(), server_default='0'),
        sa.Column('checked_in_at', sa.DateTime(timezone=True)),
        sa.Column('checked_in_by_id', postgresql.UUID(as_uuid=True)),
        sa.Column('cancelled_at', sa.DateTime(timezone=True)),
        sa.Column('cancelled_by_id', postgresql.UUID(as_uuid=True)),
        sa.Column('cancellation_reason', sa.Text()),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create encounters table
    op.create_table(
        'encounters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clinics.id', ondelete='CASCADE'), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('appointment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('appointments.id', ondelete='SET NULL'), unique=True),
        sa.Column('encounter_type', sa.String(50), nullable=False, server_default='office_visit'),
        sa.Column('status', sa.String(50), nullable=False, server_default='scheduled'),
        sa.Column('chief_complaint', sa.Text()),
        sa.Column('subjective', sa.Text()),
        sa.Column('objective', sa.Text()),
        sa.Column('assessment', sa.Text()),
        sa.Column('plan', sa.Text()),
        sa.Column('vitals', postgresql.JSON()),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True)),
        sa.Column('is_billable', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create notes table
    op.create_table(
        'notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('encounter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('encounters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('note_type', sa.String(50), nullable=False, server_default='soap'),
        sa.Column('content', postgresql.JSON(), nullable=False),
        sa.Column('narrative', sa.Text()),
        sa.Column('is_draft', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_signed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('signed_at', postgresql.UUID(as_uuid=True)),
        sa.Column('signed_by_id', postgresql.UUID(as_uuid=True)),
        sa.Column('is_ai_generated', sa.Boolean(), server_default='false'),
        sa.Column('ai_confidence', sa.Float()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='SET NULL')),
        sa.Column('agent_type', sa.String(100), nullable=False, server_default='general'),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('topic', sa.String(255)),
        sa.Column('context', postgresql.JSON()),
        sa.Column('escalated_at', sa.DateTime(timezone=True)),
        sa.Column('escalated_to_id', postgresql.UUID(as_uuid=True)),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('resolution', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSON()),
        sa.Column('model', sa.String(100)),
        sa.Column('tokens_used', sa.Integer()),
        sa.Column('confidence', sa.Float()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create agent_runs table
    op.create_table(
        'agent_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='SET NULL')),
        sa.Column('agent_type', sa.String(100), nullable=False),
        sa.Column('agent_version', sa.String(50), server_default='1.0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='started'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('duration_ms', sa.Integer()),
        sa.Column('input_data', postgresql.JSON()),
        sa.Column('output_data', postgresql.JSON()),
        sa.Column('model_name', sa.String(100)),
        sa.Column('model_version', sa.String(50)),
        sa.Column('tokens_input', sa.Integer()),
        sa.Column('tokens_output', sa.Integer()),
        sa.Column('total_cost', sa.Float()),
        sa.Column('error_message', sa.Text()),
        sa.Column('error_details', postgresql.JSON()),
        sa.Column('user_feedback', sa.String(20)),
        sa.Column('feedback_notes', sa.Text()),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True)),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True)),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create claims table
    op.create_table(
        'claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('encounter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('encounters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('insurance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patient_insurances.id', ondelete='SET NULL')),
        sa.Column('claim_number', sa.String(100), unique=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('date_of_service', sa.Date(), nullable=False),
        sa.Column('submission_date', sa.Date()),
        sa.Column('adjudication_date', sa.Date()),
        sa.Column('total_charge', sa.Numeric(10, 2), nullable=False),
        sa.Column('allowed_amount', sa.Numeric(10, 2)),
        sa.Column('paid_amount', sa.Numeric(10, 2)),
        sa.Column('patient_responsibility', sa.Numeric(10, 2)),
        sa.Column('payer_name', sa.String(255)),
        sa.Column('payer_id', sa.String(50)),
        sa.Column('submitted_by_id', postgresql.UUID(as_uuid=True)),
        sa.Column('submitted_via', sa.String(50)),
        sa.Column('denial_reason', sa.Text()),
        sa.Column('denial_code', sa.String(50)),
        sa.Column('internal_notes', sa.Text()),
        sa.Column('metadata', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create claim_lines table
    op.create_table(
        'claim_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('claim_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('claims.id', ondelete='CASCADE'), nullable=False),
        sa.Column('line_number', sa.Integer(), server_default='1'),
        sa.Column('procedure_code', sa.String(20), nullable=False),
        sa.Column('modifier_1', sa.String(10)),
        sa.Column('modifier_2', sa.String(10)),
        sa.Column('diagnosis_code_pointer', sa.String(20)),
        sa.Column('description', sa.String(255)),
        sa.Column('charge_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('allowed_amount', sa.Numeric(10, 2)),
        sa.Column('paid_amount', sa.Numeric(10, 2)),
        sa.Column('units', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('invoice_number', sa.String(100), unique=True, nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('invoice_date', sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column('due_date', sa.Date()),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('tax_amount', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('balance_due', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text()),
        sa.Column('internal_notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create invoice_lines table
    op.create_table(
        'invoice_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Integer(), server_default='1'),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('reference_type', sa.String(50)),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('payment_method', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('reference_number', sa.String(100)),
        sa.Column('notes', sa.Text()),
        sa.Column('processed_by_id', postgresql.UUID(as_uuid=True)),
        sa.Column('processed_at', sa.DateTime(timezone=True)),
        sa.Column('gateway_response', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create patient_insurances table
    op.create_table(
        'patient_insurances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('insurance_name', sa.String(255), nullable=False),
        sa.Column('policy_number', sa.String(100), nullable=False),
        sa.Column('group_number', sa.String(100)),
        sa.Column('member_name', sa.String(255)),
        sa.Column('member_id', sa.String(100)),
        sa.Column('payer_id', sa.String(20)),
        sa.Column('payer_name', sa.String(255)),
        sa.Column('copay', sa.Numeric(10, 2)),
        sa.Column('deductible', sa.Numeric(10, 2)),
        sa.Column('is_primary', sa.Boolean(), server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('expiration_date', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('user_email', sa.String(255)),
        sa.Column('user_role', sa.String(50)),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True)),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True)),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True)),
        sa.Column('details', postgresql.JSON()),
        sa.Column('reason', sa.Text()),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('request_id', sa.String(100)),
        sa.Column('success', sa.Boolean(), server_default='true'),
        sa.Column('error_message', sa.Text()),
        sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create integrations table
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clinics.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='inactive'),
        sa.Column('api_endpoint', sa.String(500)),
        sa.Column('api_key_encrypted', sa.String(500)),
        sa.Column('client_id', sa.String(255)),
        sa.Column('client_secret_encrypted', sa.String(500)),
        sa.Column('settings', postgresql.JSON()),
        sa.Column('last_sync_at', sa.DateTime(timezone=True)),
        sa.Column('last_sync_status', sa.String(50)),
        sa.Column('last_sync_error', sa.Text()),
        sa.Column('webhook_url', sa.String(500)),
        sa.Column('webhook_secret', sa.String(255)),
        sa.Column('capabilities', postgresql.ARRAY(sa.String())),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('integrations')
    op.drop_table('audit_logs')
    op.drop_table('patient_insurances')
    op.drop_table('payments')
    op.drop_table('invoice_lines')
    op.drop_table('invoices')
    op.drop_table('claim_lines')
    op.drop_table('claims')
    op.drop_table('agent_runs')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('notes')
    op.drop_table('encounters')
    op.drop_table('appointments')
    op.drop_table('patients')
    op.drop_table('users')
    op.drop_table('clinics')
    op.drop_table('tenants')
