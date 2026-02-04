'use client';

/**
 * ChatInterface - Main chat component with geolocation and session persistence
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import {
  ChatMessage,
  Action,
  LocationData,
  sendMessage,
  startChat,
  generateMessageId,
  executeAction,
} from '../../api/chatClient';
import { useGeolocation, formatCoordinates } from '../../hooks/useGeolocation';
import { useSessionStorage } from '../../hooks/useSessionStorage';
import MessageBubble from './MessageBubble';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Session persistence hook
  const {
    sessionId: storedSessionId,
    messages: storedMessages,
    location: _storedLocation,
    saveSession,
    clearSession,
    isRestored,
  } = useSessionStorage();

  // Geolocation hook
  const {
    position,
    loading: locationLoading,
    error: locationError,
    permissionStatus,
    requestPosition,
    isSupported: locationSupported,
  } = useGeolocation();

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Restore session from localStorage or initialize new chat
  useEffect(() => {
    if (!isRestored) return;

    if (storedSessionId && storedMessages.length > 0) {
      // Restore previous session
      setSessionId(storedSessionId);
      setMessages(storedMessages);
      setIsLoading(false);
    } else {
      // Initialize new chat
      initializeChat();
    }
  }, [isRestored, storedSessionId, storedMessages]);

  // Get current location data for API requests
  const getLocationData = useCallback((): LocationData | undefined => {
    if (position) {
      return {
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
      };
    }
    return undefined;
  }, [position]);

  const initializeChat = async () => {
    try {
      setIsLoading(true);
      const response = await startChat();
      setSessionId(response.session_id);

      // Add welcome message
      const welcomeMessage: ChatMessage = {
        id: generateMessageId(),
        role: 'assistant',
        text: response.text,
        ui_components: response.ui_components,
        suggested_actions: response.suggested_actions,
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);

      // Save to localStorage
      saveSession(response.session_id, [welcomeMessage]);
    } catch (err) {
      console.error('Failed to initialize chat:', err);
      setError('Erro ao conectar. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  // Reset chat and start new session
  const handleResetChat = async () => {
    clearSession();
    setMessages([]);
    setSessionId(null);
    await initializeChat();
  };

  const handleSendMessage = useCallback(async (text: string, imageBase64?: string) => {
    if (!text.trim() && !imageBase64) return;
    if (!sessionId) return;

    setError(null);

    // Add user message
    const userMessage: ChatMessage = {
      id: generateMessageId(),
      role: 'user',
      text: text.trim(),
      image_base64: imageBase64,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await sendMessage({
        message: text.trim(),
        session_id: sessionId,
        image_base64: imageBase64,
        location: getLocationData(),
      });

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: generateMessageId(),
        role: 'assistant',
        text: response.text,
        ui_components: response.ui_components,
        suggested_actions: response.suggested_actions,
        timestamp: new Date(),
      };

      setMessages(prev => {
        const newMessages = [...prev, assistantMessage];
        // Save session to localStorage
        saveSession(sessionId, newMessages, getLocationData());
        return newMessages;
      });
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Erro ao enviar mensagem. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, getLocationData, saveSession]);

  const handleAction = useCallback(async (action: Action) => {
    if (!sessionId) return;

    if (action.action_type === 'send_message') {
      await handleSendMessage(action.payload);
    } else if (action.action_type === 'camera') {
      fileInputRef.current?.click();
    } else {
      await executeAction(action, sessionId, handleSendMessage);
    }
  }, [sessionId, handleSendMessage]);

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Convert to base64
    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64 = e.target?.result as string;
      await handleSendMessage('Enviando imagem...', base64);
    };
    reader.readAsDataURL(file);

    // Clear input
    event.target.value = '';
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(inputValue);
  };

  const handleLocationClick = () => {
    if (position) {
      // Already have location - show info or toggle off?
      // For now, just refresh
      requestPosition();
    } else {
      requestPosition();
    }
  };

  // Location status indicator
  const getLocationStatusColor = () => {
    if (locationLoading) return 'text-amber-400 animate-pulse';
    if (position) return 'text-emerald-400';
    if (permissionStatus === 'denied') return 'text-red-400';
    return 'text-slate-500';
  };

  const getLocationTooltip = () => {
    if (locationLoading) return 'Obtendo localização...';
    if (position) return `Localização ativa: ${formatCoordinates(position.latitude, position.longitude)}`;
    if (permissionStatus === 'denied') return 'Localização bloqueada';
    if (locationError) return locationError;
    return 'Clique para compartilhar localização';
  };

  return (
    <div className="flex flex-col h-full bg-slate-900">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-slate-800 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center">
              <span className="text-xl">🤖</span>
            </div>
            <div>
              <h1 className="font-semibold text-slate-200">Tá na Mão</h1>
              <p className="text-xs text-slate-500">
                {isLoading ? 'Digitando...' : 'Online'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Location indicator */}
            {locationSupported && (
              <button
                onClick={handleLocationClick}
                disabled={locationLoading}
                className={`p-2 rounded-full transition-colors ${getLocationStatusColor()} hover:bg-slate-800`}
                title={getLocationTooltip()}
              >
                {locationLoading ? (
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                )}
              </button>
            )}

            {/* Reset chat button */}
            <button
              onClick={handleResetChat}
              disabled={isLoading}
              className="p-2 rounded-full text-slate-500 hover:text-slate-200 hover:bg-slate-800 transition-colors"
              title="Nova conversa"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>

        {/* Location banner */}
        {position && (
          <div className="mt-2 flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400">
            <span>📍</span>
            <span>Localização compartilhada</span>
            <span className="text-emerald-500/60">•</span>
            <span className="text-emerald-500/60">{formatCoordinates(position.latitude, position.longitude)}</span>
          </div>
        )}

        {/* Location error */}
        {locationError && !position && (
          <div className="mt-2 flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-xs text-amber-400">
            <span>⚠️</span>
            <span>{locationError}</span>
            <button
              onClick={requestPosition}
              className="ml-auto text-amber-300 hover:text-amber-200 underline"
            >
              Tentar novamente
            </button>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((message, index) => (
          <MessageBubble
            key={message.id}
            message={message}
            onAction={handleAction}
            isLatest={index === messages.length - 1 && message.role === 'assistant'}
          />
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-center gap-2 text-slate-500 mb-4">
            <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center">
              <span className="animate-pulse">🤖</span>
            </div>
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-slate-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 bg-slate-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 bg-slate-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4">
            <p className="text-sm text-red-400">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-xs text-red-300 hover:text-red-200 mt-1"
            >
              Fechar
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 border-t border-slate-800 p-4">
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          {/* Location button */}
          {locationSupported && !position && (
            <button
              type="button"
              onClick={handleLocationClick}
              disabled={locationLoading}
              className={`p-2 rounded-full transition-colors ${
                locationLoading
                  ? 'text-amber-400 animate-pulse'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
              title="Compartilhar localização"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          )}

          {/* Image upload button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="p-2 rounded-full text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            title="Enviar imagem"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </button>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleImageUpload}
            accept="image/*"
            className="hidden"
          />

          {/* Text input */}
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Digite sua mensagem..."
            disabled={isLoading}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-full px-4 py-2 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500 disabled:opacity-50"
          />

          {/* Send button */}
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="p-2 rounded-full bg-teal-500 text-white hover:bg-teal-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
