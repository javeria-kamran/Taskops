/**
 * Domain Configuration for Open AI ChatKit
 * This file registers allowed domains with OpenAI console
 *
 * Environment variables required:
 * - NEXT_PUBLIC_ENVIRONMENT: development | staging | production
 * - NEXT_PUBLIC_OPENAI_API_KEY: OpenAI API key
 * - NEXT_PUBLIC_OPENAI_ORG_ID: OpenAI organization ID (optional)
 */

export const DOMAIN_CONFIG = {
  development: {
    frontend_domain: "http://localhost:3000",
    backend_domain: "http://localhost:8000",
    openai_allowed_domains: ["localhost:3000", "127.0.0.1:3000"],
    environment: "development"
  },
  staging: {
    frontend_domain: "https://staging.example.com",
    backend_domain: "https://api-staging.example.com",
    openai_allowed_domains: ["staging.example.com"],
    environment: "staging"
  },
  production: {
    frontend_domain: "https://app.example.com",
    backend_domain: "https://api.example.com",
    openai_allowed_domains: ["app.example.com"],
    environment: "production"
  }
};

/**
 * Get current environment configuration
 *
 * Returns: Environment-specific configuration object
 *
 * Example:
 * ```ts
 * const config = getConfig();
 * console.log(config.frontend_domain); // https://app.example.com (in production)
 * ```
 */
export const getConfig = () => {
  const env = process.env.NEXT_PUBLIC_ENVIRONMENT || "development";
  return DOMAIN_CONFIG[env as keyof typeof DOMAIN_CONFIG];
};

/**
 * OpenAI API Configuration
 *
 * Fields:
 * - api_key: OpenAI API key from environment
 * - organization_id: OpenAI organization ID (if applicable)
 * - allowed_domains: Domains registered with OpenAI console
 * - timeout_ms: Request timeout in milliseconds
 *
 * Note: These values must be registered in OpenAI console under:
 * Organization Settings > API Keys > Domain Restrictions
 */
export const OPENAI_CONFIG = {
  api_key: process.env.NEXT_PUBLIC_OPENAI_API_KEY || "",
  organization_id: process.env.NEXT_PUBLIC_OPENAI_ORG_ID || "",
  allowed_domains: getConfig().openai_allowed_domains,
  timeout_ms: 30000
};

/**
 * Backend API Configuration
 *
 * Fields:
 * - base_url: Base URL for backend API
 * - api_version: API version (v1, v2, etc.)
 * - timeout_ms: Request timeout in milliseconds
 *
 * Example:
 * ```ts
 * // In production, this would be:
 * // base_url: "https://api.example.com"
 * // api_version: "v1"
 * ```
 */
export const BACKEND_CONFIG = {
  base_url: getConfig().backend_domain,
  api_version: "v1",
  timeout_ms: 30000
};

/**
 * API Endpoints
 *
 * Define all backend API endpoints used by the frontend.
 * Use placeholder {user_id} for dynamic values that will be replaced at runtime.
 *
 * Example usage:
 * ```ts
 * const chatUrl = API_ENDPOINTS.chat.replace("{user_id}", userId);
 * // Result: https://api.example.com/api/user123/chat
 * ```
 */
export const API_ENDPOINTS = {
  // Health check endpoint
  health: `${BACKEND_CONFIG.base_url}/health`,

  // Chat endpoints
  chat: `${BACKEND_CONFIG.base_url}/api/{user_id}/chat`,
  conversations: `${BACKEND_CONFIG.base_url}/api/{user_id}/conversations`,

  // Task endpoints
  tasks: `${BACKEND_CONFIG.base_url}/api/{user_id}/tasks`,
  taskDetail: `${BACKEND_CONFIG.base_url}/api/{user_id}/tasks/{task_id}`,

  // User endpoints
  userProfile: `${BACKEND_CONFIG.base_url}/api/{user_id}/profile`,
  userSettings: `${BACKEND_CONFIG.base_url}/api/{user_id}/settings`,
};

/**
 * Validation function to ensure required environment variables are set
 *
 * Returns: boolean indicating if configuration is valid
 *
 * Example:
 * ```ts
 * if (!validateConfig()) {
 *   throw new Error("Missing required environment variables");
 * }
 * ```
 */
export const validateConfig = (): boolean => {
  const config = getConfig();

  // Check required fields
  if (!config.frontend_domain || !config.backend_domain) {
    console.error("Missing required domain configuration");
    return false;
  }

  // Check OpenAI configuration in production
  const env = process.env.NEXT_PUBLIC_ENVIRONMENT || "development";
  if (env === "production") {
    if (!OPENAI_CONFIG.api_key) {
      console.error("NEXT_PUBLIC_OPENAI_API_KEY is required in production");
      return false;
    }
  }

  return true;
};

/**
 * Helper function to build full API URL with user ID
 *
 * Args:
 * - endpoint: API endpoint template with placeholders
 * - userId: User ID to insert into URL
 * - params: Additional path parameters (task_id, etc.)
 *
 * Returns: Complete API URL
 *
 * Example:
 * ```ts
 * const url = buildApiUrl(API_ENDPOINTS.taskDetail, "user123", { task_id: "task456" });
 * // Returns: https://api.example.com/api/user123/tasks/task456
 * ```
 */
export const buildApiUrl = (
  endpoint: string,
  userId: string,
  params: Record<string, string> = {}
): string => {
  let url = endpoint.replace("{user_id}", userId);

  // Replace additional parameters
  Object.entries(params).forEach(([key, value]) => {
    url = url.replace(`{${key}}`, value);
  });

  return url;
};

/**
 * Helper function to get authorization headers
 *
 * Args:
 * - token: JWT token from authentication
 *
 * Returns: Headers object with authorization
 *
 * Example:
 * ```ts
 * const headers = getAuthHeaders(jwtToken);
 * fetch(url, { headers });
 * ```
 */
export const getAuthHeaders = (token: string): Record<string, string> => {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
    "X-API-Version": BACKEND_CONFIG.api_version,
  };
};

/**
 * Environment detection helpers
 */
export const isProduction = (): boolean => {
  return (process.env.NEXT_PUBLIC_ENVIRONMENT || "development") === "production";
};

export const isStaging = (): boolean => {
  return (process.env.NEXT_PUBLIC_ENVIRONMENT || "development") === "staging";
};

export const isDevelopment = (): boolean => {
  return (process.env.NEXT_PUBLIC_ENVIRONMENT || "development") === "development";
};
