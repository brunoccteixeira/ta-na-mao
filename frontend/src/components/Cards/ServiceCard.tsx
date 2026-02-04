/**
 * ServiceCard - Card para seções do hub de Empoderamento.
 * Cada card representa um serviço/área com CTA para o chat.
 */

interface ServiceCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  ctaText: string;
  onAction: () => void;
  color: string; // Tailwind gradient class
}

export default function ServiceCard({
  icon,
  title,
  description,
  ctaText,
  onAction,
  color,
}: ServiceCardProps) {
  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-6 hover:border-emerald-500/30 transition-colors">
      <div className={`w-12 h-12 rounded-xl ${color} flex items-center justify-center text-2xl mb-4`}>
        {icon}
      </div>
      <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">{title}</h3>
      <p className="text-sm text-[var(--text-secondary)] mb-4 leading-relaxed">{description}</p>
      <button
        onClick={onAction}
        className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition-colors"
      >
        {ctaText}
      </button>
    </div>
  );
}
