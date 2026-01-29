/**
 * MessageBubble - Renders a chat message with optional components
 */

import { ChatMessage, Action } from '../../api/chatClient';
import { CardList } from '../Cards';
import { ActionList } from './ActionButton';

interface Props {
  message: ChatMessage;
  onAction?: (action: Action) => void;
  isLatest?: boolean;
}

export default function MessageBubble({ message, onAction, isLatest }: Props) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[85%] ${isUser ? 'order-1' : 'order-2'}`}>
        {/* Avatar */}
        {!isUser && (
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center">
              <span className="text-sm">🤖</span>
            </div>
            <span className="text-xs text-slate-500">Tá na Mão</span>
          </div>
        )}

        {/* Message content */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-teal-500 text-white rounded-tr-sm'
              : 'bg-slate-800 text-slate-200 rounded-tl-sm border border-slate-700'
          }`}
        >
          {/* Image preview if user sent an image */}
          {message.image_base64 && (
            <div className="mb-2 rounded-lg overflow-hidden">
              <img
                src={message.image_base64}
                alt="Imagem enviada"
                className="max-w-full max-h-48 object-contain"
              />
            </div>
          )}

          {/* Text content with markdown-like formatting */}
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {formatMessageText(message.text)}
          </div>
        </div>

        {/* UI Components (cards) */}
        {message.ui_components && message.ui_components.length > 0 && (
          <div className="mt-3">
            <CardList components={message.ui_components} />
          </div>
        )}

        {/* Suggested actions */}
        {isLatest && message.suggested_actions && onAction && (
          <ActionList
            actions={message.suggested_actions}
            onAction={onAction}
          />
        )}

        {/* Timestamp */}
        <div className={`mt-1 text-xs text-slate-500 ${isUser ? 'text-right' : 'text-left'}`}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
}

/**
 * Format message text with basic markdown support
 */
function formatMessageText(text: string): React.ReactNode {
  // Split by lines and process
  const lines = text.split('\n');

  return lines.map((line, i) => {
    // Bold: **text**
    let processed: React.ReactNode = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Bullet points
    if (line.startsWith('- ') || line.startsWith('• ')) {
      const content = line.substring(2);
      return (
        <div key={i} className="flex items-start gap-2">
          <span className="text-teal-400">•</span>
          <span dangerouslySetInnerHTML={{ __html: content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') }} />
        </div>
      );
    }

    // Numbered lists
    const numberedMatch = line.match(/^(\d+)\.\s(.+)$/);
    if (numberedMatch) {
      return (
        <div key={i} className="flex items-start gap-2">
          <span className="text-teal-400 font-medium">{numberedMatch[1]}.</span>
          <span dangerouslySetInnerHTML={{ __html: numberedMatch[2].replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') }} />
        </div>
      );
    }

    // Headers with emojis
    if (line.match(/^[📋💊🏪🎯✅❌⚠️ℹ️]/)) {
      return (
        <div key={i} className="font-semibold text-slate-100 mt-2 first:mt-0">
          <span dangerouslySetInnerHTML={{ __html: String(processed) }} />
        </div>
      );
    }

    // Regular line
    return (
      <span key={i}>
        <span dangerouslySetInnerHTML={{ __html: String(processed) }} />
        {i < lines.length - 1 && <br />}
      </span>
    );
  });
}

/**
 * Format timestamp
 */
function formatTime(date: Date): string {
  return new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}
