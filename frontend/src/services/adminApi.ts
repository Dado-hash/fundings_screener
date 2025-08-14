import { 
  UserRegistration, 
  AdminStats, 
  ReferralLink, 
  ApprovalRequest, 
  ApiResponse,
  GetRegistrationsParams 
} from '../types/admin';

// API base URL - adjust this to match your backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

class AdminApiService {
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      
      // Handle API responses that have {success: true, data: ...} format
      const data = result.success && result.data !== undefined ? result.data : result;
      
      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error(`API Error for ${endpoint}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Errore sconosciuto',
      };
    }
  }

  // Get admin statistics
  async getAdminStats(): Promise<ApiResponse<AdminStats>> {
    return this.makeRequest<AdminStats>('/api/admin/stats');
  }

  // Get all user registrations with optional filtering
  async getRegistrations(params: GetRegistrationsParams = {}): Promise<ApiResponse<UserRegistration[]>> {
    const searchParams = new URLSearchParams();
    
    if (params.status && params.status !== 'all') {
      searchParams.append('status', params.status);
    }
    if (params.page) {
      searchParams.append('page', params.page.toString());
    }
    if (params.limit) {
      searchParams.append('limit', params.limit.toString());
    }

    const queryString = searchParams.toString();
    const endpoint = `/api/admin/all-registrations${queryString ? `?${queryString}` : ''}`;
    
    return this.makeRequest<UserRegistration[]>(endpoint);
  }

  // Approve a user registration
  async approveRegistration(request: ApprovalRequest): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/api/admin/approve-registration`, {
      method: 'POST',
      body: JSON.stringify({
        registration_id: request.user_id,
        admin_username: 'admin',
        notes: request.approval_notes,
      }),
    });
  }

  // Reject a user registration
  async rejectRegistration(userId: string, notes?: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/api/admin/reject-registration`, {
      method: 'POST',
      body: JSON.stringify({
        registration_id: userId,
        admin_username: 'admin',
        notes: notes,
      }),
    });
  }

  // Get all referral links
  async getReferralLinks(): Promise<ApiResponse<ReferralLink[]>> {
    return this.makeRequest<ReferralLink[]>('/api/admin/referral-links');
  }

  // Create a new referral link
  async createReferralLink(name: string, url: string): Promise<ApiResponse<ReferralLink>> {
    return this.makeRequest<ReferralLink>('/api/admin/referral-links', {
      method: 'POST',
      body: JSON.stringify({ name, url }),
    });
  }

  // Update a referral link
  async updateReferralLink(
    id: string, 
    updates: Partial<Pick<ReferralLink, 'name' | 'url' | 'is_active'>>
  ): Promise<ApiResponse<ReferralLink>> {
    return this.makeRequest<ReferralLink>(`/api/admin/update-referral-links`, {
      method: 'PUT',
      body: JSON.stringify({
        dex_name: updates.name || id, // Use the name from updates, fallback to id
        referral_url: updates.url,
        referral_code: `REF_${(updates.name || id).toUpperCase().replace(/\s+/g, '_')}` // Generate referral code from name
      }),
    });
  }

  // Delete a referral link
  async deleteReferralLink(id: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/api/admin/referral-links/${id}`, {
      method: 'DELETE',
    });
  }
}

export const adminApi = new AdminApiService();