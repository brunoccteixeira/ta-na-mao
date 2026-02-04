'use client';

/**
 * AlertCard - Renders alert/notification messages
 */

import { AlertData } from '../../api/chatClient';
import { useState } from 'react';

interface Props {
  data: AlertData;
  onDismiss?: () => void;
}

const ALERT_CONFIG = {
  success: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    icon: '✅',
    iconBg: 'bg-emerald-500',
    titleColor: 'text-emerald-400',
  },
  warning: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    icon: '⚠️',
    iconBg: 'bg-amber-500',
    titleColor: 'text-amber-400',
  },
  error: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    icon: '❌',
    iconBg: 'bg-red-500',
    titleColor: 'text-red-400',
  },
  info: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    icon: 'ℹ️',
    iconBg: 'bg-blue-500',
    titleColor: 'text-blue-400',
  },
};

export default function AlertCard({ data, onDismiss }: Props) {
  const [dismissed, setDismissed] = useState(false);
  const config = ALERT_CONFIG[data.type];

  if (dismissed) return null;

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };

  return (
    <div className={`rounded-xl border overflow-hidden ${config.bg} ${config.border}`}>
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className={`w-8 h-8 rounded-full ${config.iconBg} flex items-center justify-center flex-shrink-0`}>
            <span className="text-sm">{config.icon}</span>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <h4 className={`font-medium ${config.titleColor}`}>
              {data.title}
            </h4>
            <p className="text-sm text-slate-300 mt-1">
              {data.message}
            </p>
          </div>

          {/* Dismiss button */}
          {data.dismissable && (
            <button
              onClick={handleDismiss}
              className="flex-shrink-0 text-slate-500 hover:text-slate-300 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
