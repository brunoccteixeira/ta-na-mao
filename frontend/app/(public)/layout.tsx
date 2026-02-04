'use client';

import { useState } from 'react';
import ChatPage from '../../src/components/Chat/ChatPage';

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [showChat, setShowChat] = useState(false);

  return (
    <div className="theme-light">
      {children}
      {/* Chat FAB */}
      <button
        onClick={() => setShowChat(true)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-emerald-500 hover:bg-emerald-400 shadow-lg shadow-emerald-500/30 flex items-center justify-center text-2xl transition-all hover:scale-110"
        title="Fale com o assistente"
        aria-label="Abrir assistente virtual"
      >
        💬
      </button>
      {showChat && <ChatPage onBack={() => setShowChat(false)} />}
    </div>
  );
}
