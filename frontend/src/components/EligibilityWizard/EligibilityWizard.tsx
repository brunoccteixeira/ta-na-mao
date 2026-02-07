'use client';

/**
 * EligibilityWizard - Wizard principal de triagem de elegibilidade
 *
 * Fluxo:
 * 1. BasicInfoStep - CPF (opcional), cidade
 * 2. FamilyStep - Composição familiar
 * 3. IncomeStep - Renda
 * 4. SpecialStep - Situações especiais
 * 5. RightsWallet - Resultado (Carteira de Direitos)
 *
 * Uses API v2 for eligibility check with fallback to local simulation
 */

import { useState, useCallback, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  CitizenProfile,
  TriagemResult,
  WizardStep,
  WIZARD_STEPS,
  STEP_TITLES,
  DEFAULT_PROFILE,
} from './types';
import { useEligibilityCheck, type EligibilityResponse } from '../../hooks/useBenefitsAPI';
import { decodeProfile } from '../../utils/shareResult';
import BasicInfoStep from './steps/BasicInfoStep';
import FamilyStep from './steps/FamilyStep';
import IncomeStep from './steps/IncomeStep';
import WorkStep from './steps/WorkStep';
import SpecialStep from './steps/SpecialStep';
import RightsWallet from './results/RightsWallet';

interface Props {
  onComplete?: (result: TriagemResult) => void;
  onGenerateCarta?: (profile: CitizenProfile, result: TriagemResult) => void;
  onFindCras?: (profile: CitizenProfile) => void;
  apiEndpoint?: string;
}

export default function EligibilityWizard({
  onComplete,
  onGenerateCarta,
  onFindCras,
  apiEndpoint: _apiEndpoint = '/api/v2/benefits/eligibility/check',
}: Props) {
  const [searchParams] = useSearchParams();
  const [currentStep, setCurrentStep] = useState<WizardStep>('basic');
  const [profile, setProfile] = useState<CitizenProfile>(DEFAULT_PROFILE);
  const [result, setResult] = useState<TriagemResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // API mutation hook for eligibility check
  const eligibilityMutation = useEligibilityCheck();

  // Auto-load profile from shared link (?r=...)
  useEffect(() => {
    const encoded = searchParams.get('r');
    if (encoded) {
      const decoded = decodeProfile(encoded);
      if (decoded) {
        const restoredProfile = { ...DEFAULT_PROFILE, ...decoded };
        setProfile(restoredProfile);
        // Auto-run triagem with the restored profile
        setTimeout(() => {
          runTriagemWithProfile(restoredProfile);
        }, 100);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const currentStepIndex = WIZARD_STEPS.indexOf(currentStep);
  const progress = ((currentStepIndex + 1) / WIZARD_STEPS.length) * 100;

  const updateProfile = useCallback((updates: Partial<CitizenProfile>) => {
    setProfile((prev) => ({ ...prev, ...updates }));
  }, []);

  const goToStep = useCallback((step: WizardStep) => {
    setCurrentStep(step);
    setError(null);
  }, []);

  const goNext = useCallback(() => {
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < WIZARD_STEPS.length) {
      goToStep(WIZARD_STEPS[nextIndex]);
    }
  }, [currentStepIndex, goToStep]);

  const goBack = useCallback(() => {
    const prevIndex = currentStepIndex - 1;
    if (prevIndex >= 0) {
      goToStep(WIZARD_STEPS[prevIndex]);
    }
  }, [currentStepIndex, goToStep]);

  const runTriagemWithProfile = useCallback(async (profileToUse: CitizenProfile) => {
    setIsLoading(true);
    setError(null);

    try {
      const apiProfile = transformProfileForAPI(profileToUse);
      const apiResponse = await eligibilityMutation.mutateAsync({ profile: apiProfile });
      const triagemResult = transformAPIResponse(apiResponse, profileToUse);

      setResult(triagemResult);
      goToStep('result');
      onComplete?.(triagemResult);
    } catch (err) {
      console.warn('API unavailable, using local simulation:', err);

      try {
        const mockResult = simulateTriagem(profileToUse);
        setResult(mockResult);
        goToStep('result');
        onComplete?.(mockResult);
      } catch (fallbackErr) {
        console.error('Erro na triagem:', fallbackErr);
        setError('Não foi possível processar. Tente novamente.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [goToStep, onComplete, eligibilityMutation]);

  const runTriagem = useCallback(async () => {
    runTriagemWithProfile(profile);
  }, [profile, runTriagemWithProfile]);

  const handleSpecialNext = useCallback(() => {
    runTriagem();
  }, [runTriagem]);

  const handleGenerateCarta = useCallback(() => {
    if (result) {
      onGenerateCarta?.(profile, result);
    }
  }, [profile, result, onGenerateCarta]);

  const handleFindCras = useCallback(() => {
    onFindCras?.(profile);
  }, [profile, onFindCras]);

  const handleReset = useCallback(() => {
    setProfile(DEFAULT_PROFILE);
    setResult(null);
    setCurrentStep('basic');
    setError(null);
  }, []);

  return (
    <div className="max-w-md mx-auto">
      {/* Progress bar */}
      {currentStep !== 'result' && (
        <div className="mb-6">
          <div className="flex justify-between text-xs text-[var(--text-tertiary)] mb-2">
            <span>{STEP_TITLES[currentStep]}</span>
            <span>{currentStepIndex + 1} de {WIZARD_STEPS.length - 1}</span>
          </div>
          <div className="h-2 bg-[var(--border-color)] rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="mb-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-500 text-sm">
          {error}
        </div>
      )}

      {/* Steps */}
      <div className="bg-[var(--bg-card)] rounded-2xl p-6 border border-[var(--border-color)]">
        {currentStep === 'basic' && (
          <BasicInfoStep
            profile={profile}
            onUpdate={updateProfile}
            onNext={goNext}
          />
        )}
        {currentStep === 'family' && (
          <FamilyStep
            profile={profile}
            onUpdate={updateProfile}
            onNext={goNext}
            onBack={goBack}
          />
        )}
        {currentStep === 'income' && (
          <IncomeStep
            profile={profile}
            onUpdate={updateProfile}
            onNext={goNext}
            onBack={goBack}
          />
        )}
        {currentStep === 'work' && (
          <WorkStep
            profile={profile}
            onUpdate={updateProfile}
            onNext={goNext}
            onBack={goBack}
          />
        )}
        {currentStep === 'special' && (
          <SpecialStep
            profile={profile}
            onUpdate={updateProfile}
            onNext={handleSpecialNext}
            onBack={goBack}
            isLoading={isLoading}
          />
        )}
        {currentStep === 'result' && result && (
          <RightsWallet
            result={result}
            profile={profile}
            onGenerateCarta={handleGenerateCarta}
            onFindCras={handleFindCras}
            onReset={handleReset}
          />
        )}
      </div>
    </div>
  );
}

/**
 * Simulação local de triagem (para funcionar sem backend)
 * Em produção, substituir por chamada real à API
 */
function simulateTriagem(profile: CitizenProfile): TriagemResult {
  const rendaPerCapita = profile.pessoasNaCasa > 0
    ? profile.rendaFamiliarMensal / profile.pessoasNaCasa
    : profile.rendaFamiliarMensal;

  const beneficiosElegiveis: any[] = [];
  const beneficiosJaRecebe: any[] = [];
  const beneficiosInelegiveis: any[] = [];
  const beneficiosInconclusivos: any[] = [];

  // Bolsa Família
  if (profile.recebeBolsaFamilia) {
    beneficiosJaRecebe.push({
      programa: 'BOLSA_FAMILIA',
      programaNome: 'Bolsa Família',
      status: 'ja_recebe',
      motivo: `Você já recebe Bolsa Família (R$ ${profile.valorBolsaFamilia}/mês)`,
      valorEstimado: profile.valorBolsaFamilia,
    });
  } else if (rendaPerCapita <= 218) {
    const valorEstimado = 600 + (profile.quantidadeFilhos * 100);
    beneficiosElegiveis.push({
      programa: 'BOLSA_FAMILIA',
      programaNome: 'Bolsa Família',
      status: 'elegivel',
      motivo: `Renda per capita de R$ ${rendaPerCapita.toFixed(0)} está dentro do limite de R$ 218`,
      valorEstimado,
      ondeSolicitar: 'CRAS',
    });
  }

  // BPC
  if (profile.recebeBpc) {
    beneficiosJaRecebe.push({
      programa: 'BPC',
      programaNome: 'BPC/LOAS',
      status: 'ja_recebe',
      motivo: 'Você já recebe BPC/LOAS',
      valorEstimado: 1412,
    });
  } else if ((profile.temIdoso65Mais || profile.temPcd) && rendaPerCapita <= 353) {
    beneficiosElegiveis.push({
      programa: 'BPC',
      programaNome: profile.temIdoso65Mais ? 'BPC Idoso' : 'BPC PCD',
      status: 'elegivel',
      motivo: `${profile.temIdoso65Mais ? 'Idoso 65+ anos' : 'Pessoa com deficiência'} com renda dentro do limite`,
      valorEstimado: 1412,
      ondeSolicitar: 'INSS (agendar pelo 135)',
    });
  }

  // Farmácia Popular
  beneficiosElegiveis.push({
    programa: 'FARMACIA_POPULAR',
    programaNome: 'Farmácia Popular',
    status: 'elegivel',
    motivo: profile.cadastradoCadunico || rendaPerCapita <= 706
      ? 'Você tem direito a medicamentos GRATUITOS'
      : 'Medicamentos para hipertensão, diabetes e asma são gratuitos para todos',
    ondeSolicitar: 'Qualquer farmácia credenciada',
  });

  // TSEE
  if (profile.cadastradoCadunico || profile.recebeBolsaFamilia || rendaPerCapita <= 706) {
    beneficiosElegiveis.push({
      programa: 'TSEE',
      programaNome: 'Tarifa Social de Energia',
      status: 'elegivel',
      motivo: 'Desconto de até 65% na conta de luz',
      ondeSolicitar: 'Distribuidora de energia',
    });
  }

  // Auxílio Gás
  if (profile.recebeBolsaFamilia || profile.recebeBpc) {
    beneficiosElegiveis.push({
      programa: 'AUXILIO_GAS',
      programaNome: 'Auxílio Gás',
      status: 'elegivel',
      motivo: 'R$ 104 a cada 2 meses para gás de cozinha',
      valorEstimado: 52, // mensal
      ondeSolicitar: 'Automático com Bolsa Família/BPC',
    });
  }

  // MCMV
  if (profile.rendaFamiliarMensal <= 12000 && !profile.temCasaPropria) {
    let faixa = '';
    if (profile.rendaFamiliarMensal <= 2830) faixa = 'Faixa 1';
    else if (profile.rendaFamiliarMensal <= 4700) faixa = 'Faixa 2';
    else if (profile.rendaFamiliarMensal <= 8600) faixa = 'Faixa 3';
    else faixa = 'Classe Média';

    beneficiosElegiveis.push({
      programa: 'MCMV',
      programaNome: `Minha Casa Minha Vida - ${faixa}`,
      status: 'elegivel',
      motivo: `Financiamento habitacional com subsídio e juros reduzidos`,
      ondeSolicitar: 'CAIXA Econômica Federal',
    });
  }

  // PIS/PASEP
  beneficiosInconclusivos.push({
    programa: 'PIS_PASEP',
    programaNome: 'PIS/PASEP (Dinheiro Esquecido)',
    status: 'inconclusivo',
    motivo: 'Se você trabalhou entre 1971-1988, pode ter dinheiro esquecido',
    ondeSolicitar: 'CAIXA (PIS) ou Banco do Brasil (PASEP)',
  });

  // Calcular totais
  const valorPotencialMensal = beneficiosElegiveis
    .filter(b => b.valorEstimado)
    .reduce((sum, b) => sum + (b.valorEstimado || 0), 0);

  const valorJaRecebeMensal = beneficiosJaRecebe
    .filter(b => b.valorEstimado)
    .reduce((sum, b) => sum + (b.valorEstimado || 0), 0);

  // Próximos passos
  const proximosPassos: string[] = [];
  if (!profile.cadastradoCadunico && beneficiosElegiveis.length > 1) {
    proximosPassos.push('Fazer CadÚnico no CRAS (necessário para maioria dos benefícios)');
  }
  if (beneficiosElegiveis.some(b => b.programa === 'BOLSA_FAMILIA')) {
    proximosPassos.push('Solicitar Bolsa Família no CRAS');
  }
  if (beneficiosElegiveis.some(b => b.programa === 'BPC')) {
    proximosPassos.push('Agendar atendimento no INSS (ligue 135)');
  }
  proximosPassos.push('Ir à farmácia com receita médica para remédios gratuitos');

  // Documentos
  const documentos = [
    'CPF de todos da família',
    'RG ou Certidão de Nascimento',
    'Comprovante de residência',
    'Comprovante de renda (se tiver)',
  ];

  return {
    beneficiosElegiveis,
    beneficiosJaRecebe,
    beneficiosInelegiveis,
    beneficiosInconclusivos,
    totalProgramasAnalisados: 8,
    valorPotencialMensal,
    valorJaRecebeMensal,
    proximosPassosPrioritarios: proximosPassos,
    documentosNecessarios: documentos,
  };
}

/**
 * Transform local CitizenProfile to API format
 */
function transformProfileForAPI(profile: CitizenProfile): import('../../engine/types').CitizenProfile {
  return {
    estado: profile.uf || 'SP',
    municipioIbge: profile.municipioIbge,
    municipioNome: profile.municipio,
    idade: profile.idade,
    cpf: profile.cpf,
    nome: profile.nome,
    cep: profile.cep,
    pessoasNaCasa: profile.pessoasNaCasa,
    quantidadeFilhos: profile.quantidadeFilhos,
    temIdoso65Mais: profile.temIdoso65Mais,
    temGestante: profile.temGestante,
    temPcd: profile.temPcd,
    temCrianca0a6: profile.temCrianca0a6,
    rendaFamiliarMensal: profile.rendaFamiliarMensal,
    trabalhoFormal: profile.trabalhoFormal,
    temCasaPropria: profile.temCasaPropria,
    moradiaZonaRural: profile.moradiaZonaRural,
    cadastradoCadunico: profile.cadastradoCadunico,
    nisCadunico: undefined,
    recebeBolsaFamilia: profile.recebeBolsaFamilia,
    valorBolsaFamilia: profile.valorBolsaFamilia,
    recebeBpc: profile.recebeBpc,
    trabalhou1971_1988: profile.trabalhou1971_1988,
    temCarteiraAssinada: profile.temCarteiraAssinada,
    tempoCarteiraAssinada: profile.tempoCarteiraAssinada,
    profissao: profile.profissao,
    temMei: profile.temMei,
    trabalhaAplicativo: profile.trabalhaAplicativo,
    agricultorFamiliar: profile.agricultorFamiliar,
    pescadorArtesanal: profile.pescadorArtesanal,
    catadorReciclavel: profile.catadorReciclavel,
    trabalhadoraDomestica: profile.trabalhadoraDomestica ?? false,
    mulherMenstruante: profile.mulherMenstruante,
    estudante: profile.estudante,
    redePublica: profile.redePublica,
  };
}

/**
 * Transform API response to local TriagemResult format
 */
function transformAPIResponse(response: EligibilityResponse, _profile: CitizenProfile): TriagemResult {
  const { summary } = response;

  // Map API results to local format
  const mapBenefit = (item: { benefit: { id: string; name: string }; status: string; estimatedValue?: number; reason?: string }) => ({
    programa: item.benefit.id,
    programaNome: item.benefit.name,
    status: item.status as 'elegivel' | 'ja_recebe' | 'inelegivel' | 'inconclusivo',
    motivo: item.reason || '',
    valorEstimado: item.estimatedValue,
  });

  const beneficiosElegiveis = summary.eligible.map(mapBenefit);
  const beneficiosJaRecebe = summary.alreadyReceiving.map(mapBenefit);
  const beneficiosInelegiveis = summary.notEligible.map(mapBenefit);
  const beneficiosInconclusivos = [
    ...summary.maybe.map(mapBenefit),
    ...summary.likelyEligible.map(mapBenefit),
  ];

  return {
    beneficiosElegiveis,
    beneficiosJaRecebe,
    beneficiosInelegiveis,
    beneficiosInconclusivos,
    totalProgramasAnalisados: summary.totalAnalyzed,
    valorPotencialMensal: summary.totalPotentialMonthly,
    valorJaRecebeMensal: 0, // API doesn't calculate this
    proximosPassosPrioritarios: summary.prioritySteps,
    documentosNecessarios: summary.documentsNeeded,
  };
}
