'use client';

/**
 * PartnerBanner - Banner de parceiro bancário no resultado de elegibilidade
 * Primeiro parceiro: CAIXA Econômica Federal (Caixa Tem)
 * Nunca bloqueia o acesso ao resultado - é complementar
 */

import { useEffect, useRef } from 'react';

interface Partner {
  name: string;
  slug: string;
  ctaText: string;
  ctaUrl: string;
  description: string;
  benefits: string[];
  color: string;
}

interface Props {
  partner?: Partner;
  source?: string;
  onImpression?: (slug: string) => void;
  onClick?: (slug: string) => void;
}

// Default CAIXA partner - used when API is unavailable
const CAIXA_DEFAULT: Partner = {
  name: 'Caixa Tem',
  slug: 'caixa',
  ctaText: 'Abrir minha conta gratis',
  ctaUrl: 'https://www.caixa.gov.br/caixa-tem/Paginas/default.aspx',
  description: 'Receba seus beneficios direto no Caixa Tem',
  benefits: [
    'Conta gratis',
    'Pix ilimitado',
    'Bolsa Familia direto no app',
    'Saques em loterias',
  ],
  color: '#005CA9',
};

export default function PartnerBanner({
  partner = CAIXA_DEFAULT,
  onImpression,
  onClick,
}: Props) {
  const impressionSent = useRef(false);

  useEffect(() => {
    if (!impressionSent.current) {
      impressionSent.current = true;
      onImpression?.(partner.slug);
    }
  }, [partner.slug, onImpression]);

  const handleClick = () => {
    onClick?.(partner.slug);
    window.open(partner.ctaUrl, '_blank', 'noopener,noreferrer');
  };

  return (
    <div
      className="p-4 rounded-xl border-2 bg-[var(--bg-card)]"
      style={{ borderColor: partner.color }}
    >
      <div className="flex items-start gap-3">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
          style={{ backgroundColor: partner.color }}
        >
          {partner.name.charAt(0)}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-[var(--text-primary)] text-sm">
            {partner.description}
          </p>
          <div className="flex flex-wrap gap-x-3 gap-y-1 mt-2">
            {partner.benefits.map((benefit, i) => (
              <span key={i} className="text-xs text-[var(--text-tertiary)]">
                ✅ {benefit}
              </span>
            ))}
          </div>
        </div>
      </div>

      <button
        onClick={handleClick}
        className="w-full mt-3 py-2.5 rounded-lg font-semibold text-sm text-white transition-all hover:opacity-90"
        style={{ backgroundColor: partner.color }}
      >
        {partner.ctaText} →
      </button>

      <p className="text-[10px] text-[var(--text-tertiary)] text-center mt-2">
        Parceiro oficial - Voce continua tendo acesso a todos os seus resultados
      </p>
    </div>
  );
}
