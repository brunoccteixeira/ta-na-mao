'use client';

/**
 * useNearbyFarmacias - Hook for fetching nearby pharmacies
 *
 * Combines geolocation with the /api/v1/nearby/farmacias endpoint
 * to find pharmacies near the user's location.
 * Supports filtering by programa (FARMACIA_POPULAR | DIGNIDADE_MENSTRUAL).
 */

import { useState, useCallback } from 'react';
import { useGeolocation, calculateDistance, formatDistance } from './useGeolocation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export interface PharmacyLocation {
  id?: string;
  nome: string;
  endereco: string;
  telefone?: string;
  horario?: string;
  aberto_agora?: boolean;
  delivery?: boolean;
  latitude: number;
  longitude: number;
  distancia?: string;
  distancia_metros?: number;
  links: {
    google_maps?: string;
    waze?: string;
    whatsapp?: string;
  };
}

export interface UseNearbyFarmaciasOptions {
  /** Filter by programa: FARMACIA_POPULAR or DIGNIDADE_MENSTRUAL */
  programa?: 'FARMACIA_POPULAR' | 'DIGNIDADE_MENSTRUAL';
  /** Search radius in meters (default: 3000) */
  raioMetros?: number;
  /** Max results (default: 10) */
  limite?: number;
}

export interface NearbyFarmaciasState {
  farmacias: PharmacyLocation[];
  redesNacionais: string[];
  loading: boolean;
  error: string | null;
  fonte: 'coordenadas' | 'cep' | null;
}

export interface NearbyFarmaciasResult extends NearbyFarmaciasState {
  userLocation: { latitude: number; longitude: number } | null;
  raio: number;
  fetchByLocation: () => Promise<void>;
  fetchByCep: (cep: string) => Promise<void>;
  requestLocationAndFetch: () => Promise<void>;
  clear: () => void;
  locationLoading: boolean;
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
    aberto_agora?: boolean;
    delivery?: boolean;
    latitude?: number;
    longitude?: number;
    distancia?: string;
    distancia_metros?: number;
    links?: Record<string, string>;
  }>;
  redes_nacionais?: string[];
  erro?: string;
  mensagem?: string;
}

export function useNearbyFarmacias(options: UseNearbyFarmaciasOptions = {}): NearbyFarmaciasResult {
  const { programa, raioMetros = 3000, limite = 10 } = options;

  const geolocation = useGeolocation();

  const [state, setState] = useState<NearbyFarmaciasState>({
    farmacias: [],
    redesNacionais: [],
    loading: false,
    error: null,
    fonte: null,
  });

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

        if (programa) {
          params.set('programa', programa);
        }

        const response = await fetch(`${API_BASE}/api/v1/nearby/farmacias?${params}`);

        if (!response.ok) {
          let msg = 'Erro ao buscar farmácias. Verifique se o servidor está ligado.';
          try { const d = await response.json(); msg = d.mensagem || d.detail || msg; } catch {}
          throw new Error(msg);
        }

        const data: ApiResponse = await response.json();

        const list: PharmacyLocation[] = (data.locais || []).map((local, index) => ({
          id: `farmacia-${index}`,
          nome: local.nome,
          endereco: local.endereco,
          telefone: local.telefone,
          horario: local.horario,
          aberto_agora: local.aberto_agora,
          delivery: local.delivery,
          latitude: local.latitude || 0,
          longitude: local.longitude || 0,
          distancia: local.distancia,
          distancia_metros: local.distancia_metros,
          links: local.links || {},
        }));

        list.forEach((item) => {
          if (!item.distancia && item.latitude && item.longitude) {
            const dist = calculateDistance(latitude, longitude, item.latitude, item.longitude);
            item.distancia = formatDistance(dist);
            item.distancia_metros = Math.round(dist * 1000);
          }
        });

        list.sort((a, b) => (a.distancia_metros || 0) - (b.distancia_metros || 0));

        setState({
          farmacias: list,
          redesNacionais: data.redes_nacionais || [],
          loading: false,
          error: null,
          fonte: 'coordenadas',
        });
      } catch (err) {
        setState({
          farmacias: [],
          redesNacionais: [],
          loading: false,
          error: err instanceof Error ? err.message : 'Erro desconhecido',
          fonte: null,
        });
      }
    },
    [raioMetros, limite, programa]
  );

  const fetchByCep = useCallback(
    async (cep: string) => {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        const normalizedCep = cep.replace(/\D/g, '');

        if (normalizedCep.length !== 8) {
          throw new Error('CEP deve ter 8 dígitos');
        }

        const params = new URLSearchParams({
          cep: normalizedCep,
          limite: limite.toString(),
        });

        if (programa) {
          params.set('programa', programa);
        }

        const response = await fetch(`${API_BASE}/api/v1/nearby/farmacias?${params}`);

        if (!response.ok) {
          let msg = 'Erro ao buscar farmácias. Verifique se o servidor está ligado.';
          try { const d = await response.json(); msg = d.mensagem || d.detail || msg; } catch {}
          throw new Error(msg);
        }

        const data: ApiResponse = await response.json();

        const list: PharmacyLocation[] = (data.locais || []).map((local, index) => ({
          id: `farmacia-${index}`,
          nome: local.nome,
          endereco: local.endereco,
          telefone: local.telefone,
          horario: local.horario,
          aberto_agora: local.aberto_agora,
          delivery: local.delivery,
          latitude: local.latitude || 0,
          longitude: local.longitude || 0,
          distancia: local.distancia,
          distancia_metros: local.distancia_metros,
          links: local.links || {},
        }));

        setState({
          farmacias: list,
          redesNacionais: data.redes_nacionais || [],
          loading: false,
          error: null,
          fonte: 'cep',
        });
      } catch (err) {
        setState({
          farmacias: [],
          redesNacionais: [],
          loading: false,
          error: err instanceof Error ? err.message : 'Erro desconhecido',
          fonte: null,
        });
      }
    },
    [limite, programa]
  );

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
            farmacias: [],
            redesNacionais: [],
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

  const clear = useCallback(() => {
    setState({
      farmacias: [],
      redesNacionais: [],
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
