"""initial

Revision ID: 20260211_0001
Revises:
Create Date: 2026-02-11
"""
from alembic import op
import sqlalchemy as sa

revision = '20260211_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('groups', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('name', sa.String(120), nullable=False), sa.Column('description', sa.String(255)))
    op.create_unique_constraint('uq_groups_name', 'groups', ['name'])

    op.create_table('permissions', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('name', sa.String(120), nullable=False))
    op.create_unique_constraint('uq_permissions_name', 'permissions', ['name'])
    op.create_index('ix_permissions_name', 'permissions', ['name'])

    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('must_reset_password', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('failed_logins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table('group_members', sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id'), primary_key=True), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), primary_key=True))
    op.create_table('group_permissions', sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id'), primary_key=True), sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permissions.id'), primary_key=True))

    op.create_table('password_reset_tokens', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False), sa.Column('token', sa.String(255), nullable=False), sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False), sa.Column('used_at', sa.DateTime(timezone=True)))
    op.create_unique_constraint('uq_prt_token', 'password_reset_tokens', ['token'])
    op.create_index('ix_prt_token', 'password_reset_tokens', ['token'])

    op.create_table('email_verification_tokens', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False), sa.Column('token', sa.String(255), nullable=False), sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False), sa.Column('used_at', sa.DateTime(timezone=True)))
    op.create_unique_constraint('uq_evt_token', 'email_verification_tokens', ['token'])
    op.create_index('ix_evt_token', 'email_verification_tokens', ['token'])

    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('actor_user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('event_type', sa.String(120), nullable=False),
        sa.Column('target_type', sa.String(120), nullable=False),
        sa.Column('target_id', sa.String(120)),
        sa.Column('details', sa.JSON()),
        sa.Column('request_id', sa.String(64)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_audit_logs_event_type', 'audit_logs', ['event_type'])
    op.create_index('ix_audit_logs_request_id', 'audit_logs', ['request_id'])


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('email_verification_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_table('group_permissions')
    op.drop_table('group_members')
    op.drop_table('users')
    op.drop_table('permissions')
    op.drop_table('groups')
