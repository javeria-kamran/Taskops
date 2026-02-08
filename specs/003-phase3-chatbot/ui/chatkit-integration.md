# UI Specification: OpenAI ChatKit Integration

## Overview

**Component**: OpenAI ChatKit
**Phase**: III - AI Chatbot
**Priority**: P0 (Critical)
**Dependencies**: `chat-endpoint` (Phase III), `authentication` (Phase II)

This document specifies how to integrate OpenAI ChatKit into the Next.js 16+ frontend to provide a chat interface for task management.

## What is OpenAI ChatKit?

OpenAI ChatKit is an official React component library that provides:
- Pre-built chat UI components
- Message rendering and formatting
- Typing indicators
- Error handling
- Responsive design
- Accessibility features

**Documentation**: https://platform.openai.com/docs/chatkit

## Installation

### NPM Package

```bash
cd frontend
npm install @openai/chatkit
```

### Required Dependencies

```bash
npm install @openai/chatkit react react-dom
```

ChatKit requires:
- React 18+ (Next.js 16 uses React 19 ✅)
- Next.js 14+ (we're using Next.js 16 ✅)

## Domain Allowlist Setup

### Why Domain Allowlist?

OpenAI ChatKit requires domain verification for security. You must add your domain to OpenAI's allowlist before deployment.

### Development (Localhost)

**Good news**: Localhost works without allowlist configuration! ✅

```
http://localhost:3000 ✅ No allowlist needed
http://127.0.0.1:3000 ✅ No allowlist needed
```

### Production Setup

**Before deployment**:

1. **Deploy frontend** to get production URL (e.g., `https://mytodoapp.vercel.app`)

2. **Add domain to OpenAI allowlist**:
   - Go to: https://platform.openai.com/settings/organization/security/domain-allowlist
   - Click "Add domain"
   - Enter: `mytodoapp.vercel.app` (without https://)
   - Save changes

3. **Get domain key**:
   - OpenAI provides a domain key after approval
   - Copy the key (format: `dk-xxxxxxxxxxxxx`)

4. **Set environment variable**:
   ```bash
   # frontend/.env.local
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-xxxxxxxxxxxxx
   ```

5. **Redeploy** with new environment variable

### Allowlist Status

```typescript
// Check if domain is allowed (optional)
import { checkDomainAllowlist } from '@openai/chatkit';

const isAllowed = await checkDomainAllowlist();
console.log('Domain allowed:', isAllowed);
```

## Basic Integration

### Page Setup: /chat

Create a new page for the chat interface:

**File**: `frontend/app/(app)/chat/page.tsx`

```typescript
import { ChatInterface } from '@/components/chat/ChatInterface';

export default function ChatPage() {
  return (
    <div className="h-screen flex flex-col">
      <header className="border-b p-4">
        <h1 className="text-2xl font-bold">Task Assistant</h1>
      </header>
      <main className="flex-1 overflow-hidden">
        <ChatInterface />
      </main>
    </div>
  );
}
```

### Chat Interface Component

**File**: `frontend/components/chat/ChatInterface.tsx`

```typescript
'use client';

import { useState } from 'react';
import { ChatKit, Message } from '@openai/chatkit';
import { useAuth } from '@/hooks/useAuth';

export function ChatInterface() {
  const { token } = useAuth(); // Get JWT token
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    // Add user message to UI
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);

    try {
      // Call chat endpoint
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      // Update conversation ID if new conversation
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      // Add assistant message to UI
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.message.content,
        createdAt: data.message.created_at,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Show error message
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        createdAt: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatKit
      messages={messages}
      onSendMessage={handleSendMessage}
      isLoading={isLoading}
      placeholder="Ask me to manage your tasks..."
      className="h-full"
    />
  );
}
```

## Advanced Features

### Loading Conversation History

**Load existing conversation on mount**:

```typescript
'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export function ChatInterface() {
  const searchParams = useSearchParams();
  const conversationIdParam = searchParams.get('conversation_id');

  useEffect(() => {
    if (conversationIdParam) {
      loadConversationHistory(conversationIdParam);
    }
  }, [conversationIdParam]);

  const loadConversationHistory = async (convId: string) => {
    try {
      const response = await fetch(`/api/conversations/${convId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to load conversation');

      const data = await response.json();
      setConversationId(convId);
      setMessages(data.messages.map((msg: any) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        createdAt: msg.created_at,
      })));
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  // ... rest of component
}
```

### Typing Indicator

ChatKit provides built-in typing indicators:

```typescript
<ChatKit
  messages={messages}
  onSendMessage={handleSendMessage}
  isLoading={isLoading}  // Shows "Agent is typing..." when true
  loadingMessage="Agent is thinking..."  // Custom loading message
  placeholder="Ask me to manage your tasks..."
/>
```

### Custom Message Rendering

Override default message rendering:

```typescript
import { MessageRenderer } from '@openai/chatkit';

const customMessageRenderer: MessageRenderer = (message) => {
  return (
    <div className={`message message-${message.role}`}>
      <div className="message-content">
        {message.content}
      </div>
      <div className="message-time">
        {new Date(message.createdAt).toLocaleTimeString()}
      </div>
    </div>
  );
};

<ChatKit
  messages={messages}
  messageRenderer={customMessageRenderer}
  // ... other props
/>
```

### Error Handling

Display user-friendly errors:

```typescript
const [error, setError] = useState<string | null>(null);

const handleSendMessage = async (content: string) => {
  setError(null);  // Clear previous errors

  try {
    // ... send message
  } catch (error) {
    if (error instanceof Error) {
      setError(error.message);
    } else {
      setError('An unexpected error occurred');
    }
  }
};

return (
  <div className="h-full flex flex-col">
    {error && (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    )}
    <ChatKit
      messages={messages}
      onSendMessage={handleSendMessage}
      isLoading={isLoading}
    />
  </div>
);
```

## Styling and Customization

### Theme Customization

ChatKit supports custom themes:

```typescript
import { ChatKit, ChatKitTheme } from '@openai/chatkit';

const customTheme: ChatKitTheme = {
  colors: {
    primary: '#3b82f6',      // Blue
    background: '#ffffff',
    userMessage: '#e0f2fe',
    assistantMessage: '#f1f5f9',
    text: '#1e293b',
    border: '#e2e8f0',
  },
  fonts: {
    body: 'Inter, system-ui, sans-serif',
    mono: 'Monaco, monospace',
  },
  spacing: {
    messageGap: '1rem',
    padding: '1rem',
  },
};

<ChatKit
  theme={customTheme}
  messages={messages}
  onSendMessage={handleSendMessage}
/>
```

### Tailwind CSS Integration

ChatKit works with Tailwind CSS:

```typescript
<ChatKit
  className="h-full"
  inputClassName="border-2 border-blue-500 rounded-lg p-3"
  messageClassName="shadow-sm"
  messages={messages}
  onSendMessage={handleSendMessage}
/>
```

## Layout Examples

### Full-Screen Chat

```typescript
export default function ChatPage() {
  return (
    <div className="fixed inset-0 flex flex-col">
      <header className="flex-none h-16 border-b px-6 flex items-center justify-between">
        <h1 className="text-xl font-bold">Task Assistant</h1>
        <button>New Chat</button>
      </header>
      <main className="flex-1 overflow-hidden">
        <ChatInterface />
      </main>
    </div>
  );
}
```

### Sidebar + Chat Layout

```typescript
export default function ChatPage() {
  return (
    <div className="h-screen flex">
      {/* Sidebar: Conversation list */}
      <aside className="w-64 border-r overflow-y-auto">
        <ConversationList />
      </aside>

      {/* Main: Chat interface */}
      <main className="flex-1 flex flex-col">
        <header className="border-b p-4">
          <h2>Current Conversation</h2>
        </header>
        <div className="flex-1 overflow-hidden">
          <ChatInterface />
        </div>
      </main>
    </div>
  );
}
```

## Conversation Management

### Conversation List Component

**File**: `frontend/components/chat/ConversationList.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

interface Conversation {
  id: string;
  title: string | null;
  updated_at: string;
}

export function ConversationList() {
  const { token } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const response = await fetch('/api/conversations', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to load conversations');

      const data = await response.json();
      setConversations(data.conversations);
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  return (
    <div className="p-4 space-y-2">
      <h3 className="font-semibold mb-4">Recent Conversations</h3>
      {conversations.map(conv => (
        <Link
          key={conv.id}
          href={`/chat?conversation_id=${conv.id}`}
          className="block p-3 hover:bg-gray-100 rounded"
        >
          <div className="font-medium">
            {conv.title || 'Untitled Conversation'}
          </div>
          <div className="text-sm text-gray-500">
            {new Date(conv.updated_at).toLocaleDateString()}
          </div>
        </Link>
      ))}
      <button
        onClick={() => window.location.href = '/chat'}
        className="w-full p-3 border border-dashed rounded hover:bg-gray-50"
      >
        + New Conversation
      </button>
    </div>
  );
}
```

## Authentication Integration

### Protected Chat Route

**File**: `frontend/app/(app)/chat/layout.tsx`

```typescript
import { redirect } from 'next/navigation';
import { getServerSession } from '@/lib/auth';

export default async function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getServerSession();

  if (!session) {
    redirect('/signin?callbackUrl=/chat');
  }

  return <>{children}</>;
}
```

### Token Management

```typescript
'use client';

import { useSession } from 'next-auth/react';

export function ChatInterface() {
  const { data: session } = useSession();
  const token = session?.user?.token;

  if (!token) {
    return <div>Please sign in to use the chat</div>;
  }

  // ... rest of component
}
```

## Mobile Responsiveness

### Responsive Layout

```typescript
export default function ChatPage() {
  return (
    <div className="h-screen flex flex-col md:flex-row">
      {/* Sidebar: Hidden on mobile, visible on desktop */}
      <aside className="hidden md:block md:w-64 border-r">
        <ConversationList />
      </aside>

      {/* Main chat: Full width on mobile */}
      <main className="flex-1 flex flex-col">
        <header className="border-b p-4 flex items-center justify-between">
          <button className="md:hidden">☰</button>
          <h1 className="text-lg md:text-xl font-bold">Task Assistant</h1>
        </header>
        <div className="flex-1 overflow-hidden">
          <ChatInterface />
        </div>
      </main>
    </div>
  );
}
```

### Mobile Optimizations

```typescript
<ChatKit
  messages={messages}
  onSendMessage={handleSendMessage}
  // Mobile-specific props
  isMobile={window.innerWidth < 768}
  inputPosition="bottom"  // Keep input at bottom on mobile
  autoFocus={false}  // Don't auto-focus on mobile (prevents keyboard)
/>
```

## Accessibility

ChatKit includes built-in accessibility features:

- **Keyboard navigation**: Tab, Enter, Escape
- **Screen reader support**: ARIA labels and roles
- **High contrast mode**: Respects user preferences
- **Focus management**: Proper focus trapping

### Additional Accessibility

```typescript
<ChatKit
  messages={messages}
  onSendMessage={handleSendMessage}
  // Accessibility props
  ariaLabel="Task management chat"
  ariaLiveRegion="polite"  // Announce new messages
  inputAriaLabel="Type your message"
/>
```

## Performance Optimization

### Message Virtualization

For conversations with many messages:

```typescript
import { ChatKit, VirtualizedMessages } from '@openai/chatkit';

<ChatKit
  messages={messages}
  onSendMessage={handleSendMessage}
  // Enable virtualization for 100+ messages
  enableVirtualization={messages.length > 100}
  virtualizedWindowSize={50}  // Render 50 messages at a time
/>
```

### Lazy Loading History

```typescript
const [hasMore, setHasMore] = useState(true);
const [offset, setOffset] = useState(0);

const loadMoreMessages = async () => {
  // Load older messages with pagination
  const response = await fetch(
    `/api/conversations/${conversationId}/messages?offset=${offset}&limit=20`
  );
  const data = await response.json();

  setMessages(prev => [...data.messages, ...prev]);
  setOffset(prev => prev + 20);
  setHasMore(data.has_more);
};

<ChatKit
  messages={messages}
  onSendMessage={handleSendMessage}
  onScrollTop={loadMoreMessages}  // Load more when scrolled to top
  hasMoreMessages={hasMore}
/>
```

## Testing

### Component Testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInterface } from '@/components/chat/ChatInterface';

describe('ChatInterface', () => {
  it('sends message when form is submitted', async () => {
    render(<ChatInterface />);

    const input = screen.getByPlaceholderText(/ask me/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Add task to buy milk' } });
    fireEvent.click(sendButton);

    // Verify message appears in UI
    expect(await screen.findByText('Add task to buy milk')).toBeInTheDocument();
  });

  it('displays assistant response', async () => {
    // Mock fetch
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          message: { content: '✅ Created task' }
        }),
      })
    ) as jest.Mock;

    render(<ChatInterface />);

    // Send message
    const input = screen.getByPlaceholderText(/ask me/i);
    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.submit(input);

    // Verify response
    expect(await screen.findByText('✅ Created task')).toBeInTheDocument();
  });
});
```

## Environment Variables

**File**: `frontend/.env.local`

```bash
# Development (optional, localhost works without it)
# NEXT_PUBLIC_OPENAI_DOMAIN_KEY=

# Production (required)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-xxxxxxxxxxxxx

# API endpoint (if different from default)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Common Issues

**1. "Domain not allowed" error in production**
- Solution: Add domain to OpenAI allowlist and set `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`

**2. Messages not appearing**
- Check: Network tab for failed API requests
- Verify: JWT token is valid and included in headers
- Check: CORS configuration on backend

**3. Typing indicator stuck**
- Ensure: `isLoading` state is set to false after response
- Check: Error handling catches all exceptions

**4. Conversation not persisting**
- Verify: `conversation_id` is stored and passed to subsequent messages
- Check: Database has conversation record

## File Structure

```
frontend/
├── app/
│   └── (app)/
│       └── chat/
│           ├── layout.tsx           # Protected route wrapper
│           └── page.tsx              # Main chat page
├── components/
│   └── chat/
│       ├── ChatInterface.tsx         # Main chat component
│       ├── ConversationList.tsx      # Sidebar conversation list
│       └── MessageRenderer.tsx       # Custom message rendering (optional)
├── hooks/
│   └── useChat.ts                    # Chat logic hook (optional)
└── .env.local                        # Environment variables
```

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial ChatKit integration specification |
