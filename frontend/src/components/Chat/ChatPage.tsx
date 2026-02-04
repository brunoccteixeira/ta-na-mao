'use client';

/**
 * ChatPage - Full-page chat interface
 */

import ChatInterface from './ChatInterface';

interface Props {
  onBack?: () => void;
}

export default function ChatPage({ onBack }: Props) {
  return (
    <div className="fixed inset-0 bg-slate-950 z-50 flex flex-col">
      {/* Top bar with back button */}
      {onBack && (
        <div className="flex-shrink-0 border-b border-slate-800 p-2">
          <button
            onClick={onBack}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span className="text-sm">Voltar ao Dashboard</span>
          </button>
        </div>
      )}

      {/* Chat interface */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  );
}
