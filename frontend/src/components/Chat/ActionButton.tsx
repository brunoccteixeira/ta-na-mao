/**
 * ActionButton - Renders a suggested action button
 */

import { Action } from '../../api/chatClient';

interface Props {
  action: Action;
  onClick: () => void;
  disabled?: boolean;
}

const ACTION_ICONS: Record<string, string> = {
  send_message: '💬',
  open_url: '🔗',
  call_phone: '📞',
  open_whatsapp: '💬',
  share: '📤',
  camera: '📷',
  open_map: '🗺️',
};

export default function ActionButton({ action, onClick, disabled }: Props) {
  const icon = action.icon || ACTION_ICONS[action.action_type] || '▶️';

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        inline-flex items-center gap-2 px-4 py-2 rounded-full
        text-sm font-medium transition-all
        ${action.primary
          ? 'bg-teal-500 text-white hover:bg-teal-400 shadow-lg shadow-teal-500/25'
          : 'bg-slate-700 text-slate-200 hover:bg-slate-600 border border-slate-600'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer active:scale-95'}
      `}
    >
      <span>{icon}</span>
      <span>{action.label}</span>
    </button>
  );
}

interface ActionListProps {
  actions: Action[];
  onAction: (action: Action) => void;
  disabled?: boolean;
}

export function ActionList({ actions, onAction, disabled }: ActionListProps) {
  if (!actions || actions.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {actions.map((action, index) => (
        <ActionButton
          key={`${action.label}-${index}`}
          action={action}
          onClick={() => onAction(action)}
          disabled={disabled}
        />
      ))}
    </div>
  );
}
