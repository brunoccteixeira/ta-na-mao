'use client';

/**
 * SocialProof - Contadores animados + depoimentos
 * Inspiração: Wizbii Trustpilot + media logos + user counter
 */

import { useState, useEffect, useRef } from 'react';

interface Stat {
  value: number;
  suffix: string;
  label: string;
}

interface Testimonial {
  name: string;
  city: string;
  quote: string;
  avatar: string;
}

const STATS: Stat[] = [
  { value: 12847, suffix: '+', label: 'Familias ja descobriram seus direitos' },
  { value: 229, suffix: '', label: 'Beneficios mapeados' },
  { value: 27, suffix: '', label: 'Estados cobertos' },
  { value: 42, suffix: ' bi', label: 'Em dinheiro esquecido no Brasil' },
];

const TESTIMONIALS: Testimonial[] = [
  {
    name: 'Maria S.',
    city: 'Recife, PE',
    quote: 'Descobri que tinha direito ao BPC e ninguem nunca tinha me falado. Agora recebo todo mes.',
    avatar: '👩',
  },
  {
    name: 'Jose C.',
    city: 'Manaus, AM',
    quote: 'A carta do CRAS me ajudou a ser atendido mais rapido. Em 30 minutos resolvi tudo.',
    avatar: '👨',
  },
  {
    name: 'Ana P.',
    city: 'Salvador, BA',
    quote: 'Nao sabia que podia pegar remedio de graca na farmacia. Agora economizo mais de R$ 200 por mes.',
    avatar: '👩‍🦱',
  },
];

function useCountUp(target: number, duration: number = 2000) {
  const [count, setCount] = useState(0);
  const [started, setStarted] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof IntersectionObserver === 'undefined') {
      // Fallback for environments without IntersectionObserver (SSR, tests)
      setStarted(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started) {
          setStarted(true);
        }
      },
      { threshold: 0.3 }
    );

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [started]);

  useEffect(() => {
    if (!started) return;

    const steps = 60;
    const increment = target / steps;
    const stepDuration = duration / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, stepDuration);

    return () => clearInterval(timer);
  }, [started, target, duration]);

  return { count, ref };
}

function StatCard({ stat }: { stat: Stat }) {
  const { count, ref } = useCountUp(stat.value);

  const formatNumber = (n: number) => {
    if (stat.suffix === ' bi') return `R$ ${n}`;
    return n.toLocaleString('pt-BR');
  };

  return (
    <div ref={ref} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] text-center">
      <div className="text-2xl font-bold text-emerald-600">
        {formatNumber(count)}{stat.suffix}
      </div>
      <div className="text-xs text-[var(--text-tertiary)] mt-1">
        {stat.label}
      </div>
    </div>
  );
}

function TestimonialCard({ testimonial }: { testimonial: Testimonial }) {
  return (
    <div className="p-4 rounded-xl bg-[var(--bg-card)] border-l-4 border-emerald-500 border-r border-t border-b border-r-[var(--border-color)] border-t-[var(--border-color)] border-b-[var(--border-color)]">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 rounded-full bg-emerald-600/10 flex items-center justify-center text-xl">
          {testimonial.avatar}
        </div>
        <div>
          <p className="text-sm font-medium text-[var(--text-primary)]">{testimonial.name}</p>
          <p className="text-xs text-[var(--text-tertiary)]">{testimonial.city}</p>
        </div>
      </div>
      <p className="text-sm text-[var(--text-secondary)] italic">
        "{testimonial.quote}"
      </p>
    </div>
  );
}

export default function SocialProof() {
  return (
    <div className="space-y-12">
      {/* Numeros */}
      <div>
        <h2 className="text-xl font-semibold text-[var(--text-primary)] text-center mb-6">
          Numeros que falam
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {STATS.map((stat, i) => (
            <StatCard key={i} stat={stat} />
          ))}
        </div>
      </div>

      {/* Depoimentos */}
      <div>
        <h2 className="text-xl font-semibold text-[var(--text-primary)] text-center mb-6">
          Quem ja usou recomenda
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          {TESTIMONIALS.map((t, i) => (
            <TestimonialCard key={i} testimonial={t} />
          ))}
        </div>
      </div>
    </div>
  );
}
