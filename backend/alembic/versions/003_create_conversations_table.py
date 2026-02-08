"""
Alembic migration: Create Conversations table
T010: Database schema - Conversation table creation

Creates conversations table for grouping messages into logical chat sessions.
User isolation: Every conversation tied to user_id with indexes.

Schema:
- id: UUID primary key
- user_id: String(36) FK to users.id (indexed)
- title: String(256) with default
- created_at: DateTime with UTC default
- updated_at: DateTime with UTC default (indexed for recency)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    """Create conversations table with indexes"""
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(256), nullable=False, server_default='New Conversation'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Indexes for user isolation and recency sorting
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_updated_at', 'conversations', ['updated_at'])


def downgrade() -> None:
    """Drop conversations table"""
    op.drop_table('conversations')
