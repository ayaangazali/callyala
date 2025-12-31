/**
 * API Client for Call Yala Backend
 * Production-ready API client with error handling and type safety
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, data);
  }
  return response.json();
}

const defaultHeaders = {
  'Content-Type': 'application/json',
};

// ============================================================================
// Generic API Methods
// ============================================================================

export async function get<T>(endpoint: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: defaultHeaders,
  });
  return handleResponse<T>(response);
}

export async function post<T>(endpoint: string, data?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: defaultHeaders,
    body: data ? JSON.stringify(data) : undefined,
  });
  return handleResponse<T>(response);
}

export async function put<T>(endpoint: string, data?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'PUT',
    headers: defaultHeaders,
    body: data ? JSON.stringify(data) : undefined,
  });
  return handleResponse<T>(response);
}

export async function del<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'DELETE',
    headers: defaultHeaders,
  });
  return handleResponse<T>(response);
}

// ============================================================================
// Types
// ============================================================================

// Overview
export interface OverviewStats {
  totalCalls: number;
  activeCampaigns: number;
  avgCallDuration: string;
  successRate: number;
  callsToday: number;
  appointmentsBooked: number;
}

// Calls
export interface Call {
  id: string;
  customer_name: string;
  customer_phone: string;
  campaign_name: string;
  status: 'completed' | 'in-progress' | 'failed' | 'scheduled';
  duration: string;
  outcome: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  started_at: string;
  ended_at?: string;
  recording_url?: string;
  transcript?: string;
}

export interface CallsResponse {
  calls: Call[];
  count: number;
  total: number;
}

// Campaigns
export interface Campaign {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'completed' | 'draft';
  type: string;
  total_leads: number;
  contacted: number;
  success_rate: number;
  start_date: string;
  end_date?: string;
  script_id?: string;
  created_at: string;
}

export interface CampaignsResponse {
  campaigns: Campaign[];
  count: number;
  total: number;
}

// Appointments
export interface Appointment {
  id: string;
  customer_name: string;
  customer_phone: string;
  customer_email?: string;
  date: string;
  time: string;
  service_type: string;
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
  vehicle_info?: string;
  created_at: string;
  updated_at?: string;
}

export interface AppointmentsResponse {
  appointments: Appointment[];
  count: number;
  total: number;
}

export interface AppointmentStats {
  total: number;
  scheduled: number;
  confirmed: number;
  completed: number;
  cancelled: number;
  today: number;
}

export interface CreateAppointmentRequest {
  customer_name: string;
  customer_phone: string;
  customer_email?: string;
  date: string;
  time: string;
  service_type: string;
  notes?: string;
  vehicle_info?: string;
}

// Customers
export interface Vehicle {
  id: string;
  customer_id: string;
  make: string;
  model: string;
  year: number;
  vin?: string;
  license_plate?: string;
  created_at: string;
}

export interface Customer {
  id: string;
  name: string;
  phone: string;
  email?: string;
  address?: string;
  vehicles: Vehicle[];
  status: 'active' | 'inactive';
  created_at: string;
  updated_at?: string;
}

export interface CustomersResponse {
  customers: Customer[];
  count: number;
  total: number;
}

export interface CustomerStats {
  total: number;
  active: number;
  inactive: number;
  totalVehicles: number;
}

export interface CreateCustomerRequest {
  name: string;
  phone: string;
  email?: string;
  address?: string;
  vehicles?: {
    make: string;
    model: string;
    year: number;
    vin?: string;
    license_plate?: string;
  }[];
}

// Scripts
export interface VoiceSettings {
  voice: string;
  speed: number;
  pitch: number;
}

export interface Script {
  id: string;
  name: string;
  type: string;
  prompt: string;
  variables: string[];
  voice_settings?: VoiceSettings;
  tags: string[];
  status: 'draft' | 'active' | 'archived';
  usage_count: number;
  created_at: string;
  updated_at?: string;
}

export interface ScriptsResponse {
  scripts: Script[];
  count: number;
  total: number;
}

export interface ScriptStats {
  total: number;
  active: number;
  draft: number;
  archived: number;
  totalUsage: number;
}

export interface CreateScriptRequest {
  name: string;
  type: string;
  prompt: string;
  voice_settings?: VoiceSettings;
  tags?: string[];
}

// QA
export interface CallScores {
  greeting: number;
  clarity: number;
  persuasion: number;
  objectionHandling: number;
  closing: number;
  overall?: number;
}

export interface QACall {
  id: string;
  customer_name: string;
  customer_phone: string;
  campaign_name: string;
  duration: string;
  reviewed: boolean;
  flagged: boolean;
  scores?: CallScores;
  feedback?: string;
  reviewed_at?: string;
  transcript?: string;
}

export interface QACallsResponse {
  calls: QACall[];
  count: number;
}

export interface QAStats {
  pendingReview: number;
  reviewed: number;
  flagged: number;
  avgScore: number;
  totalCalls: number;
  scoreDistribution: {
    excellent: number;
    good: number;
    fair: number;
    poor: number;
  };
}

export interface SubmitReviewRequest {
  scores: Omit<CallScores, 'overall'>;
  feedback?: string;
  flagged?: boolean;
}

// ============================================================================
// API Endpoints
// ============================================================================

export const api = {
  // Health
  health: () => get<{ status: string; timestamp: string }>('/api/health'),

  // Overview
  overview: {
    stats: () => get<OverviewStats>('/api/overview/stats'),
  },

  // Calls
  calls: {
    list: (params?: { status?: string; campaign_id?: string; limit?: number }) =>
      get<CallsResponse>('/api/calls', params),
    get: (id: string) => get<Call>(`/api/calls/${id}`),
  },

  // Campaigns
  campaigns: {
    list: (params?: { status?: string; limit?: number }) =>
      get<CampaignsResponse>('/api/campaigns', params),
    get: (id: string) => get<Campaign>(`/api/campaigns/${id}`),
    create: (data: Partial<Campaign>) => post<Campaign>('/api/campaigns', data),
    update: (id: string, data: Partial<Campaign>) => put<Campaign>(`/api/campaigns/${id}`, data),
    delete: (id: string) => del<{ id: string; message: string }>(`/api/campaigns/${id}`),
    start: (id: string) => post<Campaign>(`/api/campaigns/${id}/start`),
    pause: (id: string) => post<Campaign>(`/api/campaigns/${id}/pause`),
  },

  // Appointments
  appointments: {
    list: (params?: { status?: string; date_from?: string; date_to?: string; limit?: number }) =>
      get<AppointmentsResponse>('/api/appointments', params),
    get: (id: string) => get<Appointment>(`/api/appointments/${id}`),
    create: (data: CreateAppointmentRequest) => post<Appointment>('/api/appointments', data),
    update: (id: string, data: Partial<CreateAppointmentRequest>) =>
      put<Appointment>(`/api/appointments/${id}`, data),
    cancel: (id: string) => del<{ id: string; status: string; message: string }>(`/api/appointments/${id}`),
    stats: () => get<AppointmentStats>('/api/appointments/stats/summary'),
  },

  // Customers
  customers: {
    list: (params?: { search?: string; status?: string; limit?: number }) =>
      get<CustomersResponse>('/api/customers', params),
    get: (id: string) => get<Customer>(`/api/customers/${id}`),
    create: (data: CreateCustomerRequest) => post<Customer>('/api/customers', data),
    update: (id: string, data: Partial<CreateCustomerRequest>) =>
      put<Customer>(`/api/customers/${id}`, data),
    delete: (id: string) => del<{ id: string; message: string }>(`/api/customers/${id}`),
    vehicles: (params?: { limit?: number }) =>
      get<{ vehicles: (Vehicle & { customer_name: string; customer_phone: string })[]; count: number }>(
        '/api/customers/vehicles/all',
        params
      ),
    stats: () => get<CustomerStats>('/api/customers/stats/summary'),
  },

  // Scripts
  scripts: {
    list: (params?: { type?: string; status?: string; limit?: number }) =>
      get<ScriptsResponse>('/api/scripts', params),
    get: (id: string) => get<Script>(`/api/scripts/${id}`),
    create: (data: CreateScriptRequest) => post<Script>('/api/scripts', data),
    update: (id: string, data: Partial<CreateScriptRequest>) => put<Script>(`/api/scripts/${id}`, data),
    delete: (id: string) => del<{ id: string; message: string }>(`/api/scripts/${id}`),
    test: (id: string, testData: Record<string, string>) =>
      post<{ script_id: string; rendered_prompt: string; variables_provided: string[]; variables_required: string[] }>(
        `/api/scripts/${id}/test`,
        testData
      ),
    stats: () => get<ScriptStats>('/api/scripts/stats/summary'),
  },

  // QA
  qa: {
    calls: (params?: { status?: string; limit?: number }) => get<QACallsResponse>('/api/qa/calls', params),
    getCall: (id: string) => get<QACall>(`/api/qa/calls/${id}`),
    submitReview: (id: string, data: SubmitReviewRequest) =>
      post<{ id: string; reviewed: boolean; scores: CallScores; message: string }>(
        `/api/qa/calls/${id}/review`,
        data
      ),
    flag: (id: string) => post<{ id: string; flagged: boolean; message: string }>(`/api/qa/calls/${id}/flag`),
    unflag: (id: string) => post<{ id: string; flagged: boolean; message: string }>(`/api/qa/calls/${id}/unflag`),
    stats: () => get<QAStats>('/api/qa/stats/summary'),
    trends: () =>
      get<{
        daily: { date: string; avgScore: number }[];
        byCampaign: { campaign: string; avgScore: number; totalReviewed: number }[];
      }>('/api/qa/trends'),
  },
};

export default api;
