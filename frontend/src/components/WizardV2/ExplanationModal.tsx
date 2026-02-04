'use client';

/**
 * ExplanationModal - Modal to explain why we ask certain questions
 *
 * Opens when user clicks "Por que perguntamos?"
 */

import { useEffect, useRef } from 'react';
import { X, HelpCircle } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  explanation: string;
  examples?: string[];
}

export default function ExplanationModal({
  isOpen,
  onClose,
  title,
  explanation,
  examples,
}: Props) {
  const modalRef = useRef<HTMLDivElement>(null);

  // Close on Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
      <div
        ref={modalRef}
        className="bg-[var(--bg-card)] rounded-2xl max-w-md w-full p-6 shadow-xl animate-slideUp"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-500/10 rounded-full flex items-center justify-center flex-shrink-0">
              <HelpCircle className="w-5 h-5 text-emerald-600" />
            </div>
            <h3 id="modal-title" className="text-lg font-semibold text-[var(--text-primary)]">
              {title}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-[var(--hover-bg)] text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
            aria-label="Fechar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="text-[var(--text-secondary)] text-sm leading-relaxed">
          <p>{explanation}</p>

          {examples && examples.length > 0 && (
            <div className="mt-4 p-3 bg-[var(--bg-primary)] rounded-xl">
              <p className="text-xs text-[var(--text-tertiary)] mb-2 font-medium">
                Exemplos de benefícios:
              </p>
              <ul className="space-y-1">
                {examples.map((example, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full flex-shrink-0" />
                    <span className="text-[var(--text-secondary)]">{example}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <button
          onClick={onClose}
          className="mt-6 w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-medium rounded-xl transition-colors"
        >
          Entendi
        </button>
      </div>
    </div>
  );
}

// Helper component: "Por que perguntamos?" button
interface WhyButtonProps {
  onClick: () => void;
  className?: string;
}

export function WhyButton({ onClick, className = '' }: WhyButtonProps) {
  return (
    <button
      onClick={onClick}
      type="button"
      className={`flex items-center gap-1.5 text-xs text-emerald-600 hover:text-emerald-700 transition-colors ${className}`}
    >
      <HelpCircle className="w-3.5 h-3.5" />
      <span>Por que perguntamos?</span>
    </button>
  );
}
