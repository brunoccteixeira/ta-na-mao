/**
 * useSessionStorage - Hook for persisting chat session in localStorage
 *
 * Provides:
 * - Session ID persistence
 * - Message history caching
 * - Location data caching
 * - Auto-expire after 24 hours
 */

import { useState, useEffect, useCallback } from 'react';
import { ChatMessage, LocationData } from '../api/chatClient';

const STORAGE_KEY = 'tanamao_chat_session';
const SESSION_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours

interface StoredSession {
  sessionId: string;
  messages: ChatMessage[];
  location?: LocationData;
  createdAt: number;
  lastActivityAt: number;
}

interface UseSessionStorageReturn {
  sessionId: string | null;
  messages: ChatMessage[];
  location: LocationData | undefined;
  saveSession: (sessionId: string, messages: ChatMessage[], location?: LocationData) => void;
  clearSession: () => void;
  isRestored: boolean;
}

/**
 * Parse stored messages to restore Date objects
 */
function parseStoredMessages(messages: any[]): ChatMessage[] {
  return messages.map(msg => ({
    ...msg,
    timestamp: new Date(msg.timestamp),
  }));
}

/**
 * Check if session is expired
 */
function isSessionExpired(session: StoredSession): boolean {
  const now = Date.now();
  return now - session.lastActivityAt > SESSION_TTL_MS;
}

export function useSessionStorage(): UseSessionStorageReturn {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [location, setLocation] = useState<LocationData | undefined>(undefined);
  const [isRestored, setIsRestored] = useState(false);

  // Restore session on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const session: StoredSession = JSON.parse(stored);

        // Check if expired
        if (isSessionExpired(session)) {
          localStorage.removeItem(STORAGE_KEY);
          setIsRestored(true);
          return;
        }

        // Restore session
        setSessionId(session.sessionId);
        setMessages(parseStoredMessages(session.messages));
        setLocation(session.location);
      }
    } catch (error) {
      console.error('Failed to restore session from localStorage:', error);
      localStorage.removeItem(STORAGE_KEY);
    }
    setIsRestored(true);
  }, []);

  // Save session to localStorage
  const saveSession = useCallback(
    (newSessionId: string, newMessages: ChatMessage[], newLocation?: LocationData) => {
      try {
        const session: StoredSession = {
          sessionId: newSessionId,
          messages: newMessages.slice(-50), // Keep last 50 messages
          location: newLocation,
          createdAt: Date.now(),
          lastActivityAt: Date.now(),
        };

        localStorage.setItem(STORAGE_KEY, JSON.stringify(session));

        setSessionId(newSessionId);
        setMessages(newMessages);
        setLocation(newLocation);
      } catch (error) {
        console.error('Failed to save session to localStorage:', error);
      }
    },
    []
  );

  // Clear session from localStorage
  const clearSession = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      setSessionId(null);
      setMessages([]);
      setLocation(undefined);
    } catch (error) {
      console.error('Failed to clear session from localStorage:', error);
    }
  }, []);

  return {
    sessionId,
    messages,
    location,
    saveSession,
    clearSession,
    isRestored,
  };
}

/**
 * Get stored session ID without full hook (for API calls)
 */
export function getStoredSessionId(): string | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const session: StoredSession = JSON.parse(stored);
      if (!isSessionExpired(session)) {
        return session.sessionId;
      }
    }
  } catch {
    // Ignore errors
  }
  return null;
}

/**
 * Update session activity timestamp
 */
export function updateSessionActivity(): void {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const session: StoredSession = JSON.parse(stored);
      session.lastActivityAt = Date.now();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    }
  } catch {
    // Ignore errors
  }
}
