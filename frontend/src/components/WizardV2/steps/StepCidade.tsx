'use client';

/**
 * Step 2: Cidade (with IBGE autocomplete)
 */

import { useState, useEffect, useCallback } from 'react';
import { useWizard } from '../WizardContext';
import SelectWithSearch, { SelectOption } from '../inputs/SelectWithSearch';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS, fetchCitiesByState } from '../../../data/questions';
import { ArrowRight, Loader2, AlertTriangle, RefreshCw } from 'lucide-react';

export default function StepCidade() {
  const { profile, updateProfile, nextStep } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const [cities, setCities] = useState<SelectOption[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [lastFetchedState, setLastFetchedState] = useState<string | undefined>(undefined);
  const question = QUESTIONS.cidade;

  // Fetch cities when state changes
  useEffect(() => {
    if (profile.estado) {
      // Limpar município se o estado mudou
      if (lastFetchedState && lastFetchedState !== profile.estado) {
        updateProfile({ municipioIbge: undefined, municipioNome: undefined });
      }
      setLastFetchedState(profile.estado);
      setIsLoading(true);
      setFetchError(null);
      fetchCitiesByState(profile.estado)
        .then((data) => {
          setCities(data);
        })
        .catch(() => {
          setFetchError('Não foi possível carregar as cidades. Verifique sua conexão.');
          setCities([]);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [profile.estado]);

  const handleCityChange = useCallback((value: string, option?: SelectOption) => {
    updateProfile({
      municipioIbge: value,
      municipioNome: option?.label,
    });
  }, [updateProfile]);

  const handleNext = () => {
    if (profile.municipioIbge) {
      nextStep();
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl lg:text-2xl font-bold text-[var(--text-primary)] mb-2">
          {question.title}
        </h2>
        <p className="text-[var(--text-secondary)] text-sm">
          {question.subtitle}
        </p>
        <WhyButton onClick={() => setShowExplanation(true)} className="mt-2" />
      </div>

      {/* State badge */}
      {profile.estado && (
        <div className="mb-4 inline-flex items-center gap-2 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 rounded-full text-sm">
          <span className="font-medium">Estado:</span> {profile.estado}
        </div>
      )}

      {/* City select */}
      <div className="mb-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 text-emerald-500 animate-spin" />
            <span className="ml-2 text-[var(--text-secondary)]">Carregando cidades...</span>
          </div>
        ) : fetchError ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <AlertTriangle className="w-8 h-8 text-amber-500 mb-3" />
            <p className="text-sm text-[var(--text-secondary)] mb-4">{fetchError}</p>
            <button
              type="button"
              onClick={() => {
                setFetchError(null);
                setIsLoading(true);
                fetchCitiesByState(profile.estado!)
                  .then((data) => setCities(data))
                  .catch(() => setFetchError('Não foi possível carregar as cidades. Verifique sua conexão.'))
                  .finally(() => setIsLoading(false));
              }}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg text-sm font-medium hover:bg-emerald-600 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Tentar novamente
            </button>
          </div>
        ) : (
          <SelectWithSearch
            options={cities}
            value={profile.municipioIbge}
            onChange={handleCityChange}
            placeholder="Selecione sua cidade"
            searchPlaceholder="Digite o nome da cidade..."
          />
        )}
      </div>

      {/* Selected city info */}
      {profile.municipioNome && (
        <div className="mb-6 p-4 bg-[var(--bg-primary)] rounded-xl">
          <p className="text-sm text-[var(--text-secondary)]">
            Cidade selecionada: <span className="font-semibold text-[var(--text-primary)]">{profile.municipioNome}</span>
          </p>
          <p className="text-xs text-[var(--text-tertiary)] mt-1">
            Código IBGE: {profile.municipioIbge}
          </p>
        </div>
      )}

      {/* Continue button */}
      <button
        onClick={handleNext}
        disabled={!profile.municipioIbge}
        className={`
          w-full py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all
          ${
            profile.municipioIbge
              ? 'bg-emerald-500 hover:bg-emerald-600'
              : 'bg-gray-300 cursor-not-allowed'
          }
        `}
      >
        Continuar
        <ArrowRight className="w-5 h-5" />
      </button>

      {/* Explanation modal */}
      <ExplanationModal
        isOpen={showExplanation}
        onClose={() => setShowExplanation(false)}
        title={question.explanation.title}
        explanation={question.explanation.text}
        examples={question.explanation.examples}
      />
    </div>
  );
}
