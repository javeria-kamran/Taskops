"""
Alembic migration: Enhance Tasks table for Phase III
T009: Database Foundation - Task model updates

Adds or updates task table fields:
- completed: Boolean flag for task completion
- priority: Task priority level (high, medium, low)
- due_date: Optional due date for task
- created_at: Timestamp
- updated_at: Timestamp

Used by:
- T028: add_task MCP tool
- T029: list_tasks MCP tool
- T030: complete_task MCP tool
"""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    """Add Phase III fields to tasks table."""
    # Check if columns already exist before adding them
    # This allows idempotent migrations

    inspector = op.get_context().dialect.inspector
    if inspector and inspector.get_columns('tasks'):
        existing_columns = {col['name'] for col in inspector.get_columns('tasks')}
    else:
        existing_columns = set()

    # Add completed field if not present
    if 'completed' not in existing_columns:
        op.add_column('tasks', sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'))

    # Add priority field if not present
    if 'priority' not in existing_columns:
        op.add_column('tasks', sa.Column('priority', sa.String(20), nullable=False, server_default='medium'))

    # Add due_date field if not present
    if 'due_date' not in existing_columns:
        op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))

    # Add created_at with index if not present
    if 'created_at' not in existing_columns:
        op.add_column('tasks', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        op.create_index('ix_tasks_created_at', 'tasks', ['created_at'])

    # Add updated_at if not present
    if 'updated_at' not in existing_columns:
        op.add_column('tasks', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))


def downgrade() -> None:
    """Remove Phase III fields from tasks table."""
    # Note: Cannot safely downgrade without data loss
    # In production, this would require a more careful migration strategy
    op.drop_column('tasks', 'completed')
    op.drop_column('tasks', 'priority')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'created_at')
    op.drop_column('tasks', 'updated_at')
