'use client';

/**
 * useNearbyCras - Hook for fetching nearby CRAS locations
 *
 * Combines geolocation with the /api/v1/nearby/cras endpoint
 * to find CRAS centers near the user's location.
 */

import { useState, useCallback } from 'react';
import { useGeolocation, calculateDistance, formatDistance } from './useGeolocation';
import type { CrasLocation } from '../components/Map/CrasMap';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export interface UseNearbyCrasOptions {
  /** Search radius in meters (default: 5000) */
  raioMetros?: number;
  /** Max results (default: 10) */
  limite?: number;
  /** Auto-fetch on mount (default: false) */
  autoFetch?: boolean;
}

export interface NearbyCrasState {
  cras: CrasLocation[];
  loading: boolean;
  error: string | null;
  fonte: 'coordenadas' | 'cep' | null;
}

export interface NearbyCrasResult extends NearbyCrasState {
  /** User's current position */
  userLocation: { latitude: number; longitude: number } | null;
  /** Search radius in meters */
  raio: number;
  /** Fetch CRAS using current location */
  fetchByLocation: () => Promise<void>;
  /** Fetch CRAS by CEP */
  fetchByCep: (cep: string) => Promise<void>;
  /** Request location permission and fetch */
  requestLocationAndFetch: () => Promise<void>;
  /** Clear results */
  clear: () => void;
  /** Geolocation loading state */
  locationLoading: boolean;
  /** Geolocation error */
  locationError: string | null;
}

interface ApiResponse {
  sucesso: boolean;
  encontrados: number;
  locais?: Array<{
    nome: string;
    endereco: string;
    telefone?: string;
    horario?: string;
    servicos?: string[];
    latitude?: number;
    longitude?: number;
    distancia?: string;
    distancia_metros?: number;
  }>;
  erro?: string;
  mensagem?: string;
}

export function useNearbyCras(options: UseNearbyCrasOptions = {}): NearbyCrasResult {
  const { raioMetros = 5000, limite = 10 } = options;

  const geolocation = useGeolocation();

  const [state, setState] = useState<NearbyCrasState>({
    cras: [],
    loading: false,
    error: null,
    fonte: null,
  });

  // Fetch CRAS by coordinates
  const fetchByCoordinates = useCallback(
    async (latitude: number, longitude: number) => {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        const params = new URLSearchParams({
          latitude: latitude.toString(),
          longitude: longitude.toString(),
          raio_metros: raioMetros.toString(),
          limite: limite.toString(),
        });

        const response = await fetch(`${API_BASE}/api/v1/nearby/cras?${params}`);

        if (!response.ok) {
          let msg = 'Erro ao buscar CRAS. Verifique se o servidor está ligado.';
          try { const d = await response.json(); msg = d.mensagem || d.detail || msg; } catch {}
          throw new Error(msg);
        }

        const data: ApiResponse = await response.json();

        const crasList: CrasLocation[] = (data.locais || []).map((local, index) => ({
          id: `cras-${index}`,
          nome: local.nome,
          endereco: local.endereco,
          telefone: local.telefone,
          horario: local.horario,
          servicos: local.servicos,
          latitude: local.latitude || 0,
          longitude: local.longitude || 0,
          distancia: local.distancia,
          distancia_metros: local.distancia_metros,
        }));

        // Calculate distances if not provided
        crasList.forEach((cras) => {
          if (!cras.distancia && cras.latitude && cras.longitude) {
            const dist = calculateDistance(latitude, longitude, cras.latitude, cras.longitude);
            cras.distancia = formatDistance(dist);
            cras.distancia_metros = Math.round(dist * 1000);
          }
        });

        // Sort by distance
        crasList.sort((a, b) => (a.distancia_metros || 0) - (b.distancia_metros || 0));

        setState({
          cras: crasList,
          loading: false,
          error: null,
          fonte: 'coordenadas',
        });
      } catch (err) {
        setState({
          cras: [],
          loading: false,
          error: err instanceof Error ? err.message : 'Erro desconhecido',
          fonte: null,
        });
      }
    },
    [raioMetros, limite]
  );

  // Fetch CRAS by CEP
  const fetchByCep = useCallback(
    async (cep: string) => {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        // Normalize CEP (remove non-digits)
        const normalizedCep = cep.replace(/\D/g, '');

        if (normalizedCep.length !== 8) {
          throw new Error('CEP deve ter 8 dígitos');
        }

        const params = new URLSearchParams({
          cep: normalizedCep,
          limite: limite.toString(),
        });

        const response = await fetch(`${API_BASE}/api/v1/nearby/cras?${params}`);

        if (!response.ok) {
          let msg = 'Erro ao buscar CRAS. Verifique se o servidor está ligado.';
          try { const d = await response.json(); msg = d.mensagem || d.detail || msg; } catch {}
          throw new Error(msg);
        }

        const data: ApiResponse = await response.json();

        const crasList: CrasLocation[] = (data.locais || []).map((local, index) => ({
          id: `cras-${index}`,
          nome: local.nome,
          endereco: local.endereco,
          telefone: local.telefone,
          horario: local.horario,
          servicos: local.servicos,
          latitude: local.latitude || 0,
          longitude: local.longitude || 0,
          distancia: local.distancia,
          distancia_metros: local.distancia_metros,
        }));

        setState({
          cras: crasList,
          loading: false,
          error: null,
          fonte: 'cep',
        });
      } catch (err) {
        setState({
          cras: [],
          loading: false,
          error: err instanceof Error ? err.message : 'Erro desconhecido',
          fonte: null,
        });
      }
    },
    [limite]
  );

  // Fetch using current location
  const fetchByLocation = useCallback(async () => {
    if (!geolocation.position) {
      setState((prev) => ({
        ...prev,
        error: 'Localização não disponível. Clique em "Usar minha localização" primeiro.',
      }));
      return;
    }

    await fetchByCoordinates(geolocation.position.latitude, geolocation.position.longitude);
  }, [geolocation.position, fetchByCoordinates]);

  // Request location and fetch
  const requestLocationAndFetch = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    return new Promise<void>((resolve) => {
      if (!navigator.geolocation) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: 'Geolocalização não suportada neste navegador',
        }));
        resolve();
        return;
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          await fetchByCoordinates(position.coords.latitude, position.coords.longitude);
          resolve();
        },
        (error) => {
          let errorMessage = 'Erro ao obter localização';
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Permissão de localização negada. Por favor, ative a localização nas configurações.';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Localização indisponível. Tente novamente.';
              break;
            case error.TIMEOUT:
              errorMessage = 'Tempo esgotado. Verifique sua conexão e tente novamente.';
              break;
          }
          setState({
            cras: [],
            loading: false,
            error: errorMessage,
            fonte: null,
          });
          resolve();
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        }
      );
    });
  }, [fetchByCoordinates]);

  // Clear results
  const clear = useCallback(() => {
    setState({
      cras: [],
      loading: false,
      error: null,
      fonte: null,
    });
  }, []);

  return {
    ...state,
    userLocation: geolocation.position
      ? { latitude: geolocation.position.latitude, longitude: geolocation.position.longitude }
      : null,
    raio: raioMetros,
    fetchByLocation,
    fetchByCep,
    requestLocationAndFetch,
    clear,
    locationLoading: geolocation.loading,
    locationError: geolocation.error,
  };
}
