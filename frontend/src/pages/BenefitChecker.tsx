/**
 * BenefitChecker — page for /beneficios/:id/verificar
 * Light-themed single-benefit eligibility checker.
 */

import { useState, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useBenefitDetail } from '../hooks/useBenefitsAPI';
import { BenefitEligibilityChecker } from '../components/BenefitChecker';
import type { CitizenProfile } from '../engine/types';

const STORAGE_KEY = 'tnm_profile';

function loadProfile(): CitizenProfile | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as CitizenProfile;
  } catch {
    return null;
  }
}

function saveProfile(profile: CitizenProfile) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
  } catch {
    // sessionStorage may be disabled
  }
}

export default function BenefitChecker() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: benefit, isLoading, isError, error } = useBenefitDetail(id);

  const [profile, setProfile] = useState<CitizenProfile | null>(loadProfile);

  const handleProfileSubmit = useCallback((newProfile: CitizenProfile) => {
    saveProfile(newProfile);
    setProfile(newProfile);
  }, []);

  // Loading
  if (isLoading) {
    return (
      <div className="theme-light min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="flex items-center gap-3 text-[var(--text-secondary)]">
          <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span>Carregando...</span>
        </div>
      </div>
    );
  }

  // Error / Not found
  if (isError || !benefit) {
    return (
      <div className="theme-light min-h-screen bg-[var(--bg-primary)] flex items-center justify-center px-4">
        <div className="text-center">
          <p className="text-[var(--text-secondary)] mb-4">
            {error instanceof Error ? error.message : 'Benefício não encontrado'}
          </p>
          <Link
            to="/beneficios"
            className="text-emerald-600 hover:text-emerald-700 font-medium"
          >
            Voltar ao catálogo
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="theme-light min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="sticky top-0 z-30 bg-white/95 border-b border-[var(--border-color)]">
        <div className="max-w-lg mx-auto px-4 py-3 flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="w-12 h-12 min-w-[48px] rounded-full bg-[var(--bg-primary)] flex items-center justify-center transition-colors hover:bg-gray-200"
            aria-label="Voltar"
          >
            <ArrowLeft className="w-5 h-5 text-[var(--text-primary)]" />
          </button>
          <div className="flex-1 min-w-0">
            <h1 className="text-base font-bold text-[var(--text-primary)] truncate">
              Verificar elegibilidade
            </h1>
            <p className="text-xs text-[var(--text-tertiary)] truncate">
              {benefit.name}
            </p>
          </div>
          <Link
            to="/"
            className="text-sm font-semibold text-emerald-600"
          >
            Tá na Mão
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-lg mx-auto px-4 py-6 pb-12">
        <BenefitEligibilityChecker
          benefit={benefit}
          profile={profile}
          onProfileSubmit={handleProfileSubmit}
        />
      </main>
    </div>
  );
}
