/**
 * React Query Hooks for Call Yala API
 * Production-ready hooks with caching, refetching, and mutations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, type CreateAppointmentRequest, type CreateCustomerRequest, type CreateScriptRequest, type SubmitReviewRequest } from '@/lib/api';

// ============================================================================
// Query Keys
// ============================================================================

export const queryKeys = {
  // Overview
  overview: ['overview'] as const,
  overviewStats: ['overview', 'stats'] as const,

  // Calls
  calls: ['calls'] as const,
  callsList: (params?: Record<string, unknown>) => ['calls', 'list', params] as const,
  callDetail: (id: string) => ['calls', 'detail', id] as const,

  // Campaigns
  campaigns: ['campaigns'] as const,
  campaignsList: (params?: Record<string, unknown>) => ['campaigns', 'list', params] as const,
  campaignDetail: (id: string) => ['campaigns', 'detail', id] as const,

  // Appointments
  appointments: ['appointments'] as const,
  appointmentsList: (params?: Record<string, unknown>) => ['appointments', 'list', params] as const,
  appointmentDetail: (id: string) => ['appointments', 'detail', id] as const,
  appointmentStats: ['appointments', 'stats'] as const,

  // Customers
  customers: ['customers'] as const,
  customersList: (params?: Record<string, unknown>) => ['customers', 'list', params] as const,
  customerDetail: (id: string) => ['customers', 'detail', id] as const,
  customerVehicles: (params?: Record<string, unknown>) => ['customers', 'vehicles', params] as const,
  customerStats: ['customers', 'stats'] as const,

  // Scripts
  scripts: ['scripts'] as const,
  scriptsList: (params?: Record<string, unknown>) => ['scripts', 'list', params] as const,
  scriptDetail: (id: string) => ['scripts', 'detail', id] as const,
  scriptStats: ['scripts', 'stats'] as const,

  // QA
  qa: ['qa'] as const,
  qaCalls: (params?: Record<string, unknown>) => ['qa', 'calls', params] as const,
  qaCallDetail: (id: string) => ['qa', 'call', id] as const,
  qaStats: ['qa', 'stats'] as const,
  qaTrends: ['qa', 'trends'] as const,
};

// ============================================================================
// Overview Hooks
// ============================================================================

export function useOverviewStats() {
  return useQuery({
    queryKey: queryKeys.overviewStats,
    queryFn: () => api.overview.stats(),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute
  });
}

// ============================================================================
// Calls Hooks
// ============================================================================

export function useCalls(params?: { status?: string; campaign_id?: string; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.callsList(params),
    queryFn: () => api.calls.list(params),
    staleTime: 30 * 1000,
  });
}

export function useCall(id: string) {
  return useQuery({
    queryKey: queryKeys.callDetail(id),
    queryFn: () => api.calls.get(id),
    enabled: !!id,
  });
}

// ============================================================================
// Campaigns Hooks
// ============================================================================

export function useCampaigns(params?: { status?: string; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.campaignsList(params),
    queryFn: () => api.campaigns.list(params),
    staleTime: 30 * 1000,
  });
}

export function useCampaign(id: string) {
  return useQuery({
    queryKey: queryKeys.campaignDetail(id),
    queryFn: () => api.campaigns.get(id),
    enabled: !!id,
  });
}

export function useCreateCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof api.campaigns.create>[0]) => api.campaigns.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.campaigns });
    },
  });
}

export function useUpdateCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof api.campaigns.update>[1] }) =>
      api.campaigns.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.campaigns });
      queryClient.invalidateQueries({ queryKey: queryKeys.campaignDetail(id) });
    },
  });
}

export function useDeleteCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.campaigns.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.campaigns });
    },
  });
}

export function useStartCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.campaigns.start(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.campaigns });
      queryClient.invalidateQueries({ queryKey: queryKeys.campaignDetail(id) });
    },
  });
}

export function usePauseCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.campaigns.pause(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.campaigns });
      queryClient.invalidateQueries({ queryKey: queryKeys.campaignDetail(id) });
    },
  });
}

// ============================================================================
// Appointments Hooks
// ============================================================================

export function useAppointments(params?: { status?: string; date_from?: string; date_to?: string; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.appointmentsList(params),
    queryFn: () => api.appointments.list(params),
    staleTime: 30 * 1000,
  });
}

export function useAppointment(id: string) {
  return useQuery({
    queryKey: queryKeys.appointmentDetail(id),
    queryFn: () => api.appointments.get(id),
    enabled: !!id,
  });
}

export function useAppointmentStats() {
  return useQuery({
    queryKey: queryKeys.appointmentStats,
    queryFn: () => api.appointments.stats(),
    staleTime: 30 * 1000,
  });
}

export function useCreateAppointment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateAppointmentRequest) => api.appointments.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.appointments });
      queryClient.invalidateQueries({ queryKey: queryKeys.appointmentStats });
    },
  });
}

export function useUpdateAppointment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateAppointmentRequest> }) =>
      api.appointments.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.appointments });
      queryClient.invalidateQueries({ queryKey: queryKeys.appointmentDetail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.appointmentStats });
    },
  });
}

export function useCancelAppointment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.appointments.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.appointments });
      queryClient.invalidateQueries({ queryKey: queryKeys.appointmentStats });
    },
  });
}

// ============================================================================
// Customers Hooks
// ============================================================================

export function useCustomers(params?: { search?: string; status?: string; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.customersList(params),
    queryFn: () => api.customers.list(params),
    staleTime: 30 * 1000,
  });
}

export function useCustomer(id: string) {
  return useQuery({
    queryKey: queryKeys.customerDetail(id),
    queryFn: () => api.customers.get(id),
    enabled: !!id,
  });
}

export function useCustomerVehicles(params?: { limit?: number }) {
  return useQuery({
    queryKey: queryKeys.customerVehicles(params),
    queryFn: () => api.customers.vehicles(params),
    staleTime: 30 * 1000,
  });
}

export function useCustomerStats() {
  return useQuery({
    queryKey: queryKeys.customerStats,
    queryFn: () => api.customers.stats(),
    staleTime: 30 * 1000,
  });
}

export function useCreateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateCustomerRequest) => api.customers.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.customers });
      queryClient.invalidateQueries({ queryKey: queryKeys.customerStats });
    },
  });
}

export function useUpdateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateCustomerRequest> }) =>
      api.customers.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.customers });
      queryClient.invalidateQueries({ queryKey: queryKeys.customerDetail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.customerStats });
    },
  });
}

export function useDeleteCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.customers.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.customers });
      queryClient.invalidateQueries({ queryKey: queryKeys.customerStats });
    },
  });
}

// ============================================================================
// Scripts Hooks
// ============================================================================

export function useScripts(params?: { type?: string; status?: string; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.scriptsList(params),
    queryFn: () => api.scripts.list(params),
    staleTime: 30 * 1000,
  });
}

export function useScript(id: string) {
  return useQuery({
    queryKey: queryKeys.scriptDetail(id),
    queryFn: () => api.scripts.get(id),
    enabled: !!id,
  });
}

export function useScriptStats() {
  return useQuery({
    queryKey: queryKeys.scriptStats,
    queryFn: () => api.scripts.stats(),
    staleTime: 30 * 1000,
  });
}

export function useCreateScript() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateScriptRequest) => api.scripts.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.scripts });
      queryClient.invalidateQueries({ queryKey: queryKeys.scriptStats });
    },
  });
}

export function useUpdateScript() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateScriptRequest> }) =>
      api.scripts.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.scripts });
      queryClient.invalidateQueries({ queryKey: queryKeys.scriptDetail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.scriptStats });
    },
  });
}

export function useDeleteScript() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.scripts.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.scripts });
      queryClient.invalidateQueries({ queryKey: queryKeys.scriptStats });
    },
  });
}

export function useTestScript() {
  return useMutation({
    mutationFn: ({ id, testData }: { id: string; testData: Record<string, string> }) =>
      api.scripts.test(id, testData),
  });
}

// ============================================================================
// QA Hooks
// ============================================================================

export function useQACalls(params?: { status?: string; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.qaCalls(params),
    queryFn: () => api.qa.calls(params),
    staleTime: 30 * 1000,
  });
}

export function useQACall(id: string) {
  return useQuery({
    queryKey: queryKeys.qaCallDetail(id),
    queryFn: () => api.qa.getCall(id),
    enabled: !!id,
  });
}

export function useQAStats() {
  return useQuery({
    queryKey: queryKeys.qaStats,
    queryFn: () => api.qa.stats(),
    staleTime: 30 * 1000,
  });
}

export function useQATrends() {
  return useQuery({
    queryKey: queryKeys.qaTrends,
    queryFn: () => api.qa.trends(),
    staleTime: 60 * 1000, // 1 minute
  });
}

export function useSubmitReview() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: SubmitReviewRequest }) =>
      api.qa.submitReview(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.qa });
      queryClient.invalidateQueries({ queryKey: queryKeys.qaCallDetail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.qaStats });
    },
  });
}

export function useFlagCall() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.qa.flag(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.qa });
      queryClient.invalidateQueries({ queryKey: queryKeys.qaCallDetail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.qaStats });
    },
  });
}

export function useUnflagCall() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.qa.unflag(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.qa });
      queryClient.invalidateQueries({ queryKey: queryKeys.qaCallDetail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.qaStats });
    },
  });
}
