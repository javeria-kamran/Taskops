/**
 * Better Auth API route handler
 * Handles all authentication-related requests using Better Auth
 */

import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"

export const { GET, POST } = toNextJsHandler(auth)
