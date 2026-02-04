'use client';

/**
 * ReferralProgram - Componente de indicação (Member-Get-Member)
 * Mostra CTA para compartilhar o Tá na Mão com amigos/família via WhatsApp.
 */

import { useState } from 'react';

interface ReferralProgramProps {
  /** Valor mensal estimado (para personalizar mensagem) */
  valorMensal?: number;
}

export default function ReferralProgram({ valorMensal }: ReferralProgramProps) {
  const [copied, setCopied] = useState(false);
  const [shared, setShared] = useState(false);

  const referralCode = getOrCreateReferralCode();
  const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
  const referralLink = `${baseUrl}/descobrir?ref=${referralCode}`;

  const shareMessage = valorMensal && valorMensal > 0
    ? `Descobri que posso receber ate R$ ${valorMensal.toLocaleString('pt-BR', { maximumFractionDigits: 0 })}/mes em beneficios sociais! Veja quais sao os seus direitos tambem:`
    : 'Descobri meus direitos a beneficios sociais com o Ta na Mao! Veja os seus tambem:';

  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(`${shareMessage}\n${referralLink}`)}`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(referralLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      trackReferral('copy');
    } catch {
      // Fallback
      const input = document.createElement('input');
      input.value = referralLink;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleWhatsApp = () => {
    setShared(true);
    trackReferral('whatsapp');
    window.open(whatsappUrl, '_blank');
  };

  return (
    <div className="p-5 rounded-xl bg-gradient-to-br from-violet-500/10 via-purple-500/5 to-transparent border border-violet-500/20">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-violet-500/20 flex items-center justify-center shrink-0">
          <svg className="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-[var(--text-primary)] mb-1">
            Conhece alguem que precisa?
          </h3>
          <p className="text-sm text-[var(--text-secondary)] mb-4">
            Compartilhe o Ta na Mao com familiares e amigos.
            Muita gente tem direito a beneficios e nao sabe!
          </p>

          <div className="flex flex-wrap gap-2">
            {/* WhatsApp */}
            <button
              onClick={handleWhatsApp}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm font-medium transition-colors"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
              </svg>
              {shared ? 'Enviado!' : 'Compartilhar no WhatsApp'}
            </button>

            {/* Copy link */}
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)] hover:border-violet-500/30 text-[var(--text-secondary)] text-sm transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              {copied ? 'Copiado!' : 'Copiar link'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function getOrCreateReferralCode(): string {
  const key = 'tnm-referral-code';
  let code = localStorage.getItem(key);
  if (!code) {
    code = crypto.randomUUID().slice(0, 8);
    localStorage.setItem(key, code);
  }
  return code;
}

function trackReferral(method: 'whatsapp' | 'copy' | 'sms'): void {
  try {
    fetch('/api/v1/referrals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        referral_code: getOrCreateReferralCode(),
        method,
      }),
    });
  } catch {
    // Silently fail
  }
}
