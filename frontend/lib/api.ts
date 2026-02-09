// lib/api.ts
import { 
  User, LoginCredentials, RegisterCredentials, ApiResponse, 
  RecentActivity, ChartData, Transaction, 
  UploadPreviewResponse, AnalysisRequest, AnalysisResponse 
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://fiscal-sentinel-production.up.railway.app';

class ApiService {
  private token: string | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    const data = await response.json().catch(() => ({ message: 'Invalid response from server' }));
    
    if (!response.ok) {
      throw new Error(data.message || data.detail || `Request failed with status ${response.status}`);
    }
    
    return data;
  }

  // Auth endpoints
  async login(credentials: LoginCredentials): Promise<ApiResponse<User>> {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(credentials),
    });

    const result = await this.handleResponse<User>(response);
    
    if (typeof window !== 'undefined') {
      // Store dummy token (backend doesn't return JWT)
      localStorage.setItem('token', 'dummy-token');
      this.token = 'dummy-token';
      localStorage.setItem('user', JSON.stringify(result.data));
    }
    
    return result;
  }

  async register(credentials: RegisterCredentials): Promise<ApiResponse<User>> {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(credentials),
    });

    const result = await this.handleResponse<User>(response);
    
    if (typeof window !== 'undefined') {
      // Store dummy token (backend doesn't return JWT)
      localStorage.setItem('token', 'dummy-token');
      this.token = 'dummy-token';
      localStorage.setItem('user', JSON.stringify(result.data));
    }
    
    return result;
  }

  async logout(): Promise<void> {
    try {
      await fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        headers: this.getHeaders(),
      });
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
      this.token = null;
    }
  }

  // User endpoints
  async getCurrentUser(): Promise<User | null> {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          return JSON.parse(userStr);
        } catch (error) {
          console.error('Failed to parse user from localStorage:', error);
          return null;
        }
      }
    }
    return null;
  }

  async updateUser(userId: string, data: Partial<User>): Promise<ApiResponse<User>> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse<User>(response);
  }

  // Transaction endpoints
  async getTransactions(): Promise<Transaction[]> {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      headers: this.getHeaders(),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch transactions');
    }
    
    return response.json();
  }

  async previewTransactions(file: File): Promise<UploadPreviewResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/transactions/preview`, {
      method: 'POST',
      headers: {
        'Authorization': this.token ? `Bearer ${this.token}` : '',
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Preview failed');
    }
    
    return response.json();
  }

  async confirmTransactions(previewId: string, mapping: Record<string, string>): Promise<{ count: number }> {
    const response = await fetch(`${API_BASE_URL}/transactions/confirm`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ preview_id: previewId, mapping }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Confirmation failed');
    }
    
    return response.json();
  }

  async uploadTransactions(file: File): Promise<{ count: number }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/transactions/upload`, {
      method: 'POST',
      headers: {
        'Authorization': this.token ? `Bearer ${this.token}` : '',
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }
    
    return response.json();
  }

  async analyzeTransactions(query: string, debug?: boolean): Promise<AnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ 
        query, 
        debug: debug || false,
        history: []
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Analysis failed');
    }
    
    return response.json();
  }
}

export const api = new ApiService();