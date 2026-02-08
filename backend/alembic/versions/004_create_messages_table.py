"""
Alembic migration: Create Messages table
T010: Database schema - Message table creation

Creates messages table for storing user and assistant messages within conversations.
User isolation: Every message tied to user_id with indexes.
Immutable design: No updates after creation.

Schema:
- id: UUID primary key
- conversation_id: UUID FK to conversations.id (cascade delete, indexed)
- user_id: String(36) indexed for user isolation
- role: Enum-like String ('user' or 'assistant') with CHECK constraint
- content: String(4096) for message text
- tool_calls: JSONB null for tool invocation data
- tokens_used: Integer null for token tracking
- created_at: DateTime with UTC default (indexed for ordering)

Indexes:
- conversation_id: For history loading
- user_id: For user isolation verification
- created_at: For chronological ordering
- (conversation_id, created_at): Composite for efficient history queries
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    """Create messages table with indexes and constraints"""
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.String(4096), nullable=False),
        sa.Column('tool_calls', postgresql.JSON(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='ck_messages_role'),
    )

    # Indexes for query performance
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_user_id', 'messages', ['user_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])
    op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])


def downgrade() -> None:
    """Drop messages table"""
    op.drop_table('messages')
