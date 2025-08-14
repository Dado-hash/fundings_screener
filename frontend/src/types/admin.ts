// Admin dashboard types

export interface UserRegistration {
  id: string;
  username: string;
  wallet_address: string;
  preferred_dex: string;
  registration_date: string;
  status: 'pending' | 'approved' | 'rejected';
  approval_notes?: string;
  approved_by?: string;
  approved_at?: string;
}

export interface AdminStats {
  total_registrations: number;
  pending_registrations: number;
  approved_registrations: number;
  rejected_registrations: number;
}

export interface ReferralLink {
  id: string;
  name: string;
  url: string;
  clicks: number;
  registrations: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface ApprovalRequest {
  user_id: string;
  approval_notes?: string;
}

export type RegistrationFilter = 'all' | 'pending' | 'approved' | 'rejected';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface GetRegistrationsParams extends PaginationParams {
  status?: RegistrationFilter;
}