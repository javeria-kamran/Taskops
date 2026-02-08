# Frontend JWT Security Implementation Guide

## ⚠️ Current Status Assessment

**Backend JWT Security**: ✅ Complete (T043)
**Frontend JWT Security**: ⏳ Needs Implementation

The frontend framework is configured (Next.js + ChatKit) but we need to add secure JWT handling. Here's the comprehensive implementation guide:

---

## Frontend JWT Security Best Practices

### 1. Token Storage Strategy

#### ❌ NOT Recommended
```typescript
// DON'T: Store in localStorage (vulnerable to XSS)
localStorage.setItem('token', jwtToken);

// DON'T: Store in sessionStorage (still XSS vulnerable)
sessionStorage.setItem('token', jwtToken);

// DON'T: Store in cookies without flags
document.cookie = "token=" + token;
```

#### ✅ RECOMMENDED: HttpOnly Cookies
```typescript
// DO: Let backend set HttpOnly, Secure, SameSite cookies
// Backend sends: Set-Cookie: token=...; HttpOnly; Secure; SameSite=Strict; Path=/

// Frontend automatically includes cookie with requests (no code needed)
// CORS credentials must be enabled:
fetch('https://api.example.com/api/user/chat', {
  method: 'POST',
  credentials: 'include',  // Include cookies in request
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(request)
})
```

#### ✅ ALTERNATIVE: Memory Storage (For SPA)
```typescript
// Store in memory (lost on page refresh - acceptable for many apps)
let authToken: string | null = null;

export function setToken(token: string) {
  authToken = token;
}

export function getToken(): string | null {
  return authToken;
}

export function clearToken() {
  authToken = null;
}
```

### 2. Token Transmission (Recommended)

```typescript
// ✅ ALWAYS use Authorization header with Bearer scheme
const response = await fetch('https://api.example.com/api/user/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ message })
});

// NEVER put in URL or body:
// ❌ https://api.example.com/api/user/chat?token=...
// ❌ { "token": "...", "message": "..." }
```

### 3. XSS Protection (Token Theft Prevention)

```typescript
// ✅ Input Sanitization (prevent script injection)
import DOMPurify from 'dompurify';

function sanitizeUserInput(input: string): string {
  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS: [],  // No HTML allowed
    ALLOWED_ATTR: []
  });
}

// Usage in chat
const sanitizedMessage = sanitizeUserInput(userMessage);
await sendMessage(sanitizedMessage);

// ✅ Content Security Policy (prevent XSS attacks)
// Add to next.config.js:
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-inline' https://cdn.openai.com;
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self' data:;
      connect-src 'self' https://api.example.com https://api.openai.com;
    `.replace(/\n/g, '')
  }
];
```

### 4. HTTPS Enforcement (Always)

```typescript
// ✅ Environment-based URL configuration
export const getApiUrl = () => {
  const env = process.env.NEXT_PUBLIC_ENVIRONMENT || 'production';

  if (env === 'production') {
    if (!window.location.protocol.startsWith('https')) {
      window.location.href = 'https://' + window.location.host;
    }
    return 'https://api.example.com';
  }

  if (env === 'staging') {
    return 'https://api-staging.example.com';
  }

  return 'http://localhost:8000';  // Dev only
};

// Fetch with HTTPS validation
const apiUrl = getApiUrl();
if (process.env.NODE_ENV === 'production' && !apiUrl.startsWith('https')) {
  throw new Error('Production API must use HTTPS');
}
```

### 5. CSRF Protection (If Using Cookies)

```typescript
// ✅ SameSite cookie attribute (backend sets this)
// Set-Cookie: token=...; SameSite=Strict; ...

// ✅ Double-Submit Cookie (if not using SameSite)
// 1. Backend sends CSRF token in cookie
// 2. Frontend sends CSRF token in X-CSRF-Token header

export async function sendMessage(message: string) {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  return fetch('https://api.example.com/api/user/chat', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRF-Token': csrfToken || '',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  });
}
```

---

## Secure Implementation Example

### `frontend/app/chat/utils/authClient.ts`
```typescript
/**
 * Secure Auth Client
 * Handles JWT token management and requests with proper security headers
 */

interface AuthConfig {
  apiUrl: string;
  tokenKey: string;
  secureCookies: boolean;
}

class AuthClient {
  private token: string | null = null;  // Memory storage
  private config: AuthConfig;

  constructor(config: AuthConfig) {
    this.config = config;
    // Try to recover token from session (if using cookies)
    if (config.secureCookies) {
      // Backend will send token via HttpOnly cookie
      // No need to manage here
    }
  }

  /**
   * Set authentication token (from login response)
   * Only store in memory - not localStorage
   */
  setToken(token: string): void {
    // Validate token format
    if (!this.isValidJWT(token)) {
      throw new Error('Invalid JWT token format');
    }
    this.token = token;
  }

  /**
   * Get current token
   * Returns null if not authenticated
   */
  getToken(): string | null {
    return this.token;
  }

  /**
   * Check if token is expired
   */
  isTokenExpired(): boolean {
    if (!this.token) return true;

    try {
      const payload = JSON.parse(atob(this.token.split('.')[1]));
      const expirationTime = payload.exp * 1000;  // Convert to ms
      return Date.now() > expirationTime;
    } catch {
      return true;  // Invalid token, treat as expired
    }
  }

  /**
   * Clear token on logout
   */
  clearToken(): void {
    this.token = null;
  }

  /**
   * Make authenticated request to API
   */
  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Check token validity before request
    if (!this.token) {
      throw new Error('Not authenticated');
    }

    if (this.isTokenExpired()) {
      this.clearToken();
      throw new Error('Token expired, please login again');
    }

    // Validate HTTPS in production
    const url = new URL(endpoint, this.config.apiUrl);
    if (process.env.NODE_ENV === 'production' && url.protocol !== 'https:') {
      throw new Error('Production requests must use HTTPS');
    }

    const response = await fetch(url.toString(), {
      ...options,
      credentials: this.config.secureCookies ? 'include' : 'omit',
      headers: {
        ...options.headers,
        'Content-Type': 'application/json',
        ...(this.config.secureCookies ? {} : {
          'Authorization': `Bearer ${this.token}`
        })
      }
    });

    // Handle authentication errors
    if (response.status === 401) {
      this.clearToken();
      // Redirect to login
      window.location.href = '/login';
      throw new Error('Unauthorized - please login again');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  }

  /**
   * Validate JWT format
   */
  private isValidJWT(token: string): boolean {
    try {
      const parts = token.split('.');
      return parts.length === 3 &&
        this.isBase64Url(parts[0]) &&
        this.isBase64Url(parts[1]) &&
        this.isBase64Url(parts[2]);
    } catch {
      return false;
    }
  }

  /**
   * Check if string is valid Base64URL
   */
  private isBase64Url(str: string): boolean {
    try {
      atob(str.replace(/-/g, '+').replace(/_/g, '/'));
      return true;
    } catch {
      return false;
    }
  }
}

export default AuthClient;
```

### `frontend/app/chat/hooks/useChat.ts` (Secure Version)
```typescript
import { useState, useCallback } from 'react';
import AuthClient from '../utils/authClient';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const authClient = new AuthClient({
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  tokenKey: 'auth_token',
  secureCookies: process.env.NODE_ENV === 'production'
});

export function useChat(userId: string, conversationId?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (message: string) => {
    try {
      setError(null);
      setLoading(true);

      // ✅ Sanitize user input
      const sanitized = sanitizeMessage(message);
      if (!sanitized) {
        throw new Error('Message cannot be empty');
      }

      // ✅ Check authentication before sending
      if (!authClient.getToken()) {
        throw new Error('Not authenticated - please login');
      }

      // ✅ Make authenticated request with Bearer token
      const response = await authClient.request<{
        conversation_id: string;
        response: string;
        tool_calls_executed: number;
      }>(
        `/api/${userId}/chat`,
        {
          method: 'POST',
          body: JSON.stringify({
            conversation_id: conversationId,
            message: sanitized
          })
        }
      );

      // Update conversation ID if this was first message
      if (!conversationId && response.conversation_id) {
        // Update parent component with new conversation ID
      }

      // Add user message
      setMessages(prev => [...prev, {
        role: 'user',
        content: sanitized
      }]);

      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.response
      }]);

    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      console.error('Chat error:', message);
    } finally {
      setLoading(false);
    }
  }, [userId, conversationId]);

  return { messages, loading, error, sendMessage };
}

/**
 * Sanitize user input to prevent XSS
 */
function sanitizeMessage(message: string): string {
  if (!message || typeof message !== 'string') {
    return '';
  }

  return message
    .trim()  // Remove whitespace
    .slice(0, 4096)  // Max length
    .replace(/[<>]/g, '')  // Remove angle brackets
    .replace(/javascript:/gi, '')  // Remove javascript: protocol
    .replace(/on\w+\s*=/gi, '');  // Remove event handlers
}
```

---

## Security Checklist for Frontend

- [ ] **Token Storage**: Using memory or HttpOnly cookies (NOT localStorage/sessionStorage)
- [ ] **HTTPS**: Enforced in production (validate protocol)
- [ ] **Authorization Header**: Using Bearer scheme, never in URL
- [ ] **XSS Protection**: Input sanitization + CSP headers
- [ ] **Token Expiration**: Check before each request, redirect to login if expired
- [ ] **CSRF Protection**: SameSite cookie or CSRF token header
- [ ] **Error Handling**: No token leakage in error messages
- [ ] **Logout**: Clear token on logout, invalidate session
- [ ] **Cross-Site Tracking**: SameSite=Strict on cookies
- [ ] **Secure Defaults**: Fail closed, not open

---

## Environment-Specific Configuration

### Development (`.env.development.local`)
```
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SECURE_COOKIES=false
```

### Staging (`.env.staging`)
```
NEXT_PUBLIC_ENVIRONMENT=staging
NEXT_PUBLIC_API_URL=https://api-staging.example.com
NEXT_PUBLIC_SECURE_COOKIES=true
```

### Production (`.env.production`)
```
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_SECURE_COOKIES=true
# HTTPS enforced - no HTTP fallback
```

---

## Summary: Is It Safe?

### Current Status
| Aspect | Status | Risk |
|--------|--------|------|
| Backend JWT validation | ✅ Implemented | Low |
| Input sanitization | ✅ Implemented | Low |
| Authorization checks | ✅ Implemented | Low |
| HTTPS enforcement | ⏳ Config ready | Medium |
| Frontend token storage | ⏳ Needs impl. | **High** |
| XSS protection | ⏳ Partial | **High** |
| CSRF protection | ⏳ Depends on cookies | Medium |

### Recommendation

**Implement the secure patterns above before production deployment:**

1. **Use HttpOnly cookies** (preferred, backend sets them)
   - Backend sends JWT in HttpOnly, Secure, SameSite cookie
   - Frontend automatically includes with requests
   - No JavaScript access to token (XSS safe)

2. **OR use memory storage** (alternative for SPA)
   - Store token in memory variable (lost on refresh)
   - Implement refresh token flow for persistence
   - Higher XSS risk if attacker can inject scripts

3. **Always use HTTPS** in production
   - Validate protocol before API calls
   - CSP headers to prevent injection
   - Secure flag on cookies

4. **Sanitize all inputs**
   - Client-side: Prevent DOM-based XSS
   - Server-side: Already implemented (T044)
   - Defense in depth

**Bottom Line**: The backend is secure (T043-T046). Frontend needs the implementation patterns above to be fully secure. The security threat vector is primarily XSS leading to token theft on the frontend.

