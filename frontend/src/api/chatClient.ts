/**
 * Chat API client for Tá na Mão agent (v2 - A2UI)
 */

import { api } from './client';

// =============================================================================
// Types - A2UI Components
// =============================================================================

export type UIComponentType =
  | 'pharmacy_card'
  | 'medication_list'
  | 'checklist'
  | 'status_badge'
  | 'map_location'
  | 'benefit_card'
  | 'cras_card'
  | 'order_status'
  | 'alert';

export type ActionType =
  | 'send_message'
  | 'open_url'
  | 'call_phone'
  | 'open_whatsapp'
  | 'share'
  | 'camera'
  | 'open_map';

export interface UIComponent {
  type: UIComponentType;
  data: Record<string, any>;
}

export interface Action {
  label: string;
  action_type: ActionType;
  payload: string;
  icon?: string;
  primary?: boolean;
}

// =============================================================================
// Specific Component Data Types
// =============================================================================

export interface MedicationItem {
  name: string;
  dosage: string;
  quantity?: number;
  free: boolean;
  available?: boolean;
}

export interface MedicationListData {
  medications: MedicationItem[];
  all_free: boolean;
  estimated_savings?: string;
}

export interface ChecklistItem {
  text: string;
  required: boolean;
  hint?: string;
  checked?: boolean;
}

export interface ChecklistData {
  title: string;
  items: ChecklistItem[];
  program?: string;
}

export interface PharmacyCardData {
  id: string;
  name: string;
  address: string;
  phone?: string;
  distance?: string;
  hours?: string;
  has_whatsapp?: boolean;
  whatsapp_number?: string;
}

export interface BenefitCardData {
  code: string;
  name: string;
  status: 'active' | 'eligible' | 'ineligible' | 'pending';
  value?: string;
  next_payment?: string;
  icon?: string;
}

export interface CrasCardData {
  name: string;
  address: string;
  phone?: string;
  hours?: string;
  distance?: string;
  services?: string[];
}

export interface OrderStatusData {
  order_number: string;
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'delivered';
  pharmacy: string;
  estimated_ready?: string;
  steps: Array<{
    label: string;
    done: boolean;
  }>;
}

export interface AlertData {
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  dismissable?: boolean;
}

// =============================================================================
// Location Types
// =============================================================================

export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy?: number;
}

// =============================================================================
// Request/Response Types
// =============================================================================

export interface ChatRequest {
  message: string;
  session_id?: string;
  image_base64?: string;
  location?: LocationData;
}

export interface ChatResponse {
  text: string;
  session_id: string;
  ui_components: UIComponent[];
  suggested_actions: Action[];
  flow_state?: string;
  tools_used: string[];
}

export interface WelcomeResponse {
  text: string;
  session_id: string;
  ui_components: UIComponent[];
  suggested_actions: Action[];
}

export interface SessionInfo {
  session_id: string;
  active_flow?: string;
  flow_state?: string;
  message_count: number;
  created_at: string;
}

// =============================================================================
// Message Type (for UI state)
// =============================================================================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  ui_components?: UIComponent[];
  suggested_actions?: Action[];
  timestamp: Date;
  image_base64?: string;
}

// =============================================================================
// API Functions
// =============================================================================

const CHAT_API_BASE = '/agent/v2';

/**
 * Start a new chat session
 */
export const startChat = async (): Promise<WelcomeResponse> => {
  const response = await api.post(`${CHAT_API_BASE}/start`);
  return response.data;
};

/**
 * Send a message to the chat
 */
export const sendMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post(`${CHAT_API_BASE}/chat`, request);
  return response.data;
};

/**
 * Reset a chat session
 */
export const resetSession = async (sessionId: string): Promise<{ success: boolean; message: string }> => {
  const response = await api.post(`${CHAT_API_BASE}/reset/${sessionId}`);
  return response.data;
};

/**
 * Get session info
 */
export const getSessionInfo = async (sessionId: string): Promise<SessionInfo> => {
  const response = await api.get(`${CHAT_API_BASE}/session/${sessionId}`);
  return response.data;
};

/**
 * Check agent status
 */
export const getAgentStatus = async (): Promise<{
  available: boolean;
  model: string;
  tools: string[];
  version: string;
}> => {
  const response = await api.get(`${CHAT_API_BASE}/status`);
  return response.data;
};

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Generate a unique message ID
 */
export const generateMessageId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Execute an action
 */
export const executeAction = async (
  action: Action,
  _sessionId: string,
  onSendMessage: (message: string) => Promise<void>
): Promise<void> => {
  switch (action.action_type) {
    case 'send_message':
      await onSendMessage(action.payload);
      break;

    case 'open_url':
      window.open(action.payload, '_blank');
      break;

    case 'call_phone':
      window.location.href = `tel:${action.payload}`;
      break;

    case 'open_whatsapp':
      window.open(`https://wa.me/${action.payload.replace(/\D/g, '')}`, '_blank');
      break;

    case 'share':
      if (navigator.share) {
        await navigator.share({ text: action.payload });
      } else {
        await navigator.clipboard.writeText(action.payload);
      }
      break;

    case 'open_map':
      window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(action.payload)}`, '_blank');
      break;

    case 'camera':
      // This should trigger camera input - handled by component
      console.log('Camera action - should be handled by component');
      break;
  }
};
