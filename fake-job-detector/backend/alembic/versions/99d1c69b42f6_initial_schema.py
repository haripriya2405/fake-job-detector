"""initial_schema

Revision ID: 99d1c69b42f6
Revises: 
Create Date: 2026-08-17

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from app.db.base import GUID

# revision identifiers, used by Alembic.
revision: str = '99d1c69b42f6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', GUID(), primary_key=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. analyses table
    op.create_table(
        'analyses',
        sa.Column('id', GUID(), primary_key=True, nullable=False),
        sa.Column('user_id', GUID(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('job_title', sa.String(length=255), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=False, server_default='text'),
        sa.Column('raw_content', sa.Text(), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('ml_confidence_score', sa.Float(), nullable=True),
        sa.Column('rule_penalty_score', sa.Float(), nullable=True),
        sa.Column('domain_trust_score', sa.Float(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('analysis_engine', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_analyses_id'), 'analyses', ['id'], unique=False)
    op.create_index(op.f('ix_analyses_user_id'), 'analyses', ['user_id'], unique=False)
    op.create_index(op.f('ix_analyses_job_title'), 'analyses', ['job_title'], unique=False)
    op.create_index(op.f('ix_analyses_company_name'), 'analyses', ['company_name'], unique=False)
    op.create_index(op.f('ix_analyses_risk_score'), 'analyses', ['risk_score'], unique=False)
    op.create_index(op.f('ix_analyses_risk_level'), 'analyses', ['risk_level'], unique=False)

    # 3. analysis_indicators table
    op.create_table(
        'analysis_indicators',
        sa.Column('id', GUID(), primary_key=True, nullable=False),
        sa.Column('analysis_id', GUID(), sa.ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='medium'),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('risk_weight', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_analysis_indicators_id'), 'analysis_indicators', ['id'], unique=False)
    op.create_index(op.f('ix_analysis_indicators_analysis_id'), 'analysis_indicators', ['analysis_id'], unique=False)

    # 4. url_analyses table
    op.create_table(
        'url_analyses',
        sa.Column('id', GUID(), primary_key=True, nullable=False),
        sa.Column('analysis_id', GUID(), sa.ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('whois_age_days', sa.Integer(), nullable=True),
        sa.Column('mx_record_valid', sa.Boolean(), nullable=True),
        sa.Column('is_suspicious', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('flags_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_url_analyses_id'), 'url_analyses', ['id'], unique=False)
    op.create_index(op.f('ix_url_analyses_analysis_id'), 'url_analyses', ['analysis_id'], unique=False)
    op.create_index(op.f('ix_url_analyses_domain'), 'url_analyses', ['domain'], unique=False)

    # 5. verification_results table
    op.create_table(
        'verification_results',
        sa.Column('id', GUID(), primary_key=True, nullable=False),
        sa.Column('analysis_id', GUID(), sa.ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_name', sa.String(length=255), nullable=True),
        sa.Column('domain_checked', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='unverified'),
        sa.Column('whois_age_days', sa.Integer(), nullable=True),
        sa.Column('mx_record_valid', sa.Boolean(), nullable=True),
        sa.Column('linkedin_match', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('details_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_verification_results_id'), 'verification_results', ['id'], unique=False)
    op.create_index(op.f('ix_verification_results_analysis_id'), 'verification_results', ['analysis_id'], unique=False)

    # 6. model_versions table
    op.create_table(
        'model_versions',
        sa.Column('id', GUID(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False, unique=True),
        sa.Column('algorithm', sa.String(length=100), nullable=False),
        sa.Column('training_dataset', sa.String(length=255), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('artifact_path', sa.String(length=512), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_model_versions_id'), 'model_versions', ['id'], unique=False)

    # 7. rule_versions table
    op.create_table(
        'rule_versions',
        sa.Column('id', GUID(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False, unique=True),
        sa.Column('rule_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('rules_definition_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_rule_versions_id'), 'rule_versions', ['id'], unique=False)

    # 8. audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', GUID(), primary_key=True, nullable=False),
        sa.Column('user_id', GUID(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=True),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('rule_versions')
    op.drop_table('model_versions')
    op.drop_table('verification_results')
    op.drop_table('url_analyses')
    op.drop_table('analysis_indicators')
    op.drop_table('analyses')
    op.drop_table('users')
