# Database Schema: Phase III - Chatbot Tables

## Overview

**Phase**: III - AI Chatbot
**Priority**: P0 (Critical)
**Dependencies**: `schema.md` (Phase II)

This document specifies the new database tables required for Phase III chatbot functionality. These tables extend the existing Phase II schema to support conversation persistence.

## Schema Extensions

### New Tables

Phase III adds 2 new tables:
1. **conversations** - Stores conversation metadata
2. **messages** - Stores individual messages in conversations

### Existing Tables (No Changes)

These Phase II tables remain unchanged:
- **users** - User accounts (from Better Auth)
- **sessions** - Active sessions (from Better Auth)
- **accounts** - OAuth accounts (from Better Auth)
- **tasks** - User tasks

## Table: conversations

**Purpose**: Track individual chat conversations between users and the AI agent

### Schema Definition

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_conversations_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
```

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )
    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True
    )
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        nullable=True
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

### Field Descriptions

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique conversation identifier |
| user_id | VARCHAR(255) | NOT NULL, FK → users.id | Owner of the conversation |
| title | VARCHAR(200) | NULL | Optional conversation title (e.g., "Shopping list planning") |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When conversation was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp |

### Business Rules

1. **Automatic Title**: Title can be auto-generated from first message (optional feature)
2. **Updated At**: Automatically updated when new message is added
3. **Cascade Delete**: When user is deleted, all conversations are deleted
4. **User Isolation**: Users can only access their own conversations

### Example Records

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_abc123",
  "title": "Task planning for today",
  "created_at": "2024-12-28T10:30:00Z",
  "updated_at": "2024-12-28T10:35:00Z"
}
```

## Table: messages

**Purpose**: Store individual messages within conversations

### Schema Definition

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE,

    CONSTRAINT check_role CHECK (role IN ('user', 'assistant'))
);

-- Indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at ASC);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at ASC);
```

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True
    )
    role: str = Field(
        nullable=False,
        max_length=20
    )
    content: str = Field(
        nullable=False,
        sa_column=Column("content", sa_type=Text)
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

### Field Descriptions

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique message identifier |
| conversation_id | UUID | NOT NULL, FK → conversations.id | Parent conversation |
| role | VARCHAR(20) | NOT NULL, CHECK IN ('user', 'assistant') | Message sender |
| content | TEXT | NOT NULL | Message content |
| metadata | JSONB | NULL | Additional data (tools_used, etc.) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When message was sent |

### Message Roles

- **user**: Message from the user
- **assistant**: Message from the AI agent

### Metadata Format

The `metadata` field stores additional information:

**For user messages**:
```json
{
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

**For assistant messages**:
```json
{
  "tools_used": ["add_task", "list_tasks"],
  "model": "gpt-4",
  "processing_time_ms": 1234
}
```

### Example Records

**User Message**:
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440001",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "user",
  "content": "Add task to buy groceries",
  "metadata": {},
  "created_at": "2024-12-28T10:30:00Z"
}
```

**Assistant Message**:
```json
{
  "id": "750e8400-e29b-41d4-a716-446655440002",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "assistant",
  "content": "✅ I've created a new task: 'Buy groceries' (Task #15)",
  "metadata": {
    "tools_used": ["add_task"],
    "processing_time_ms": 1200
  },
  "created_at": "2024-12-28T10:30:02Z"
}
```

## Relationships

### Entity Relationship Diagram

```
users (Phase II)
  ↓ 1:N
conversations (Phase III)
  ↓ 1:N
messages (Phase III)
```

### Foreign Key Constraints

1. **conversations.user_id → users.id**
   - ON DELETE CASCADE (delete all conversations when user is deleted)

2. **messages.conversation_id → conversations.id**
   - ON DELETE CASCADE (delete all messages when conversation is deleted)

## Migration Scripts

### Migration: Create Phase III Tables

```python
"""Add conversations and messages tables

Revision ID: 003_phase3_chatbot
Revises: 002_phase2_web
Create Date: 2024-12-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003_phase3_chatbot'
down_revision = '002_phase2_web'
branch_labels = None
depends_on = None

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for conversations
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_created_at', 'conversations', ['created_at'], postgresql_ops={'created_at': 'DESC'})

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('uuid_generate_v4()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_role')
    )

    # Create indexes for messages
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'], postgresql_ops={'created_at': 'ASC'})
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])

def downgrade():
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_index('idx_messages_created_at', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    op.drop_index('idx_conversations_created_at', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
```

### Running Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Add conversations and messages tables"

# Apply migration
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

## Database Queries

### Common Queries

**Create new conversation**:
```sql
INSERT INTO conversations (user_id)
VALUES ('user_abc123')
RETURNING *;
```

**Find user's conversations**:
```sql
SELECT * FROM conversations
WHERE user_id = 'user_abc123'
ORDER BY updated_at DESC
LIMIT 20;
```

**Get conversation with messages**:
```sql
SELECT
    c.id AS conversation_id,
    c.title,
    c.created_at AS conversation_created_at,
    m.id AS message_id,
    m.role,
    m.content,
    m.created_at AS message_created_at
FROM conversations c
LEFT JOIN messages m ON m.conversation_id = c.id
WHERE c.id = '550e8400-e29b-41d4-a716-446655440000'
  AND c.user_id = 'user_abc123'
ORDER BY m.created_at ASC;
```

**Add message to conversation**:
```sql
INSERT INTO messages (conversation_id, role, content, metadata)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'user',
    'Add task to buy groceries',
    '{}'::jsonb
)
RETURNING *;
```

**Update conversation timestamp**:
```sql
UPDATE conversations
SET updated_at = NOW()
WHERE id = '550e8400-e29b-41d4-a716-446655440000';
```

**Get recent messages (for context loading)**:
```sql
SELECT role, content, created_at
FROM messages
WHERE conversation_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY created_at ASC
LIMIT 50;
```

## Performance Considerations

### Indexes

All critical queries are covered by indexes:

1. **idx_conversations_user_id**: Fast lookup of user's conversations
2. **idx_conversations_created_at**: Efficient ordering by recency
3. **idx_messages_conversation_id**: Fast message lookup by conversation
4. **idx_messages_created_at**: Efficient ordering of messages
5. **idx_messages_conversation_created**: Composite index for combined queries

### Query Optimization

**Load messages efficiently**:
```python
# ✅ GOOD: Limit message history
messages = db.query(Message).filter(
    Message.conversation_id == conversation_id
).order_by(Message.created_at.asc()).limit(50).all()

# ❌ BAD: Load all messages (could be thousands)
messages = db.query(Message).filter(
    Message.conversation_id == conversation_id
).all()
```

### Storage Estimates

**Assumptions**:
- Average message: 200 characters
- Average conversation: 20 messages
- 1000 active users
- Each user has 5 conversations

**Calculations**:
- Messages: 1000 users × 5 conversations × 20 messages = 100,000 rows
- Message size: 200 chars × 100,000 = 20 MB (content only)
- With metadata + timestamps: ~50 MB
- Conversations: 1000 users × 5 = 5,000 rows (~1 MB)

**Total Phase III storage**: ~50 MB (very manageable)

## Data Retention

### Optional: Cleanup Old Conversations

```sql
-- Delete conversations older than 90 days with no activity
DELETE FROM conversations
WHERE updated_at < NOW() - INTERVAL '90 days';
-- Messages will be cascade deleted
```

### Optional: Archive Strategy

For long-term storage:

```sql
-- Create archive table
CREATE TABLE messages_archive (LIKE messages INCLUDING ALL);

-- Move old messages to archive
INSERT INTO messages_archive
SELECT * FROM messages
WHERE created_at < NOW() - INTERVAL '1 year';

DELETE FROM messages
WHERE created_at < NOW() - INTERVAL '1 year';
```

## Security Considerations

### User Isolation

**CRITICAL**: Always filter conversations by user_id:

```python
# ✅ SECURE
conversation = db.query(Conversation).filter(
    Conversation.id == conversation_id,
    Conversation.user_id == user_id  # REQUIRED
).first()

# ❌ INSECURE
conversation = db.query(Conversation).filter(
    Conversation.id == conversation_id
).first()
```

### SQL Injection Prevention

- Always use ORM (SQLModel) - never raw SQL
- Use parameterized queries if raw SQL is necessary
- Validate UUIDs before queries

### Data Privacy

- Messages may contain sensitive information
- Implement encryption at rest (database level)
- Regularly audit access logs
- Comply with GDPR/privacy regulations

## Testing

### Seed Data for Testing

```python
# Create test conversation
conversation = Conversation(
    user_id="test_user_123",
    title="Test conversation"
)
db.add(conversation)
db.commit()

# Add messages
messages = [
    Message(
        conversation_id=conversation.id,
        role="user",
        content="Add task to buy milk"
    ),
    Message(
        conversation_id=conversation.id,
        role="assistant",
        content="✅ Created task 'Buy milk'"
    ),
]
for msg in messages:
    db.add(msg)
db.commit()
```

### Test Queries

```python
def test_conversation_creation():
    conversation = Conversation(user_id="user_123")
    db.add(conversation)
    db.commit()
    assert conversation.id is not None

def test_message_cascade_delete():
    # Create conversation with messages
    conversation = create_test_conversation_with_messages()
    conversation_id = conversation.id

    # Delete conversation
    db.delete(conversation)
    db.commit()

    # Verify messages are deleted
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).all()
    assert len(messages) == 0
```

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial Phase III database schema specification |
