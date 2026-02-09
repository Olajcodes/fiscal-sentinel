// lib/api.ts
import {
  User, UserCourse, QuizQuestion, QuizAttempt,
  CourseCatalog, GameProgress, LoginCredentials,
  RegisterCredentials, QuizSubmission, CourseEnrollment,
  ApiResponse, RecentActivity, CourseWithDetails, QuestionWithDetails, AdminFilters, ChartData, AdminStats, UserWithDetails,
  AnalyzeRequest, AnalyzeResponse,
} from './types';


const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
  private token: string | null = null;
  private conversationId: string | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
      this.conversationId = localStorage.getItem('conversation_id');
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
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'An error occurred' }));
      throw new Error(error.message || 'Request failed');
    }
    return response.json();
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
      localStorage.setItem('token', 'dummy-token'); // Replace with actual JWT
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
      localStorage.setItem('token', 'dummy-token');
      localStorage.setItem('user', JSON.stringify(result.data));
    }
    
    return result;
  }

  async logout(): Promise<void> {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    this.token = null;
  }

  // User endpoints
  async getCurrentUser(): Promise<User | null> {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    }
    return null;
  }

  async getUserProfile(userId: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async updateUser(userId: string, data: Partial<User>): Promise<ApiResponse<User>> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse<User>(response);
  }

  async deleteUser(userId: string): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    return this.handleResponse<void>(response);
  }

  private setConversationId(conversationId: string | null) {
    this.conversationId = conversationId;
    if (typeof window !== 'undefined') {
      if (conversationId) {
        localStorage.setItem('conversation_id', conversationId);
      } else {
        localStorage.removeItem('conversation_id');
      }
    }
  }

  getConversationId(): string | null {
    return this.conversationId;
  }

  resetConversation(): void {
    this.setConversationId(null);
  }

  async analyze(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    const payload: AnalyzeRequest = { ...request };
    if (!payload.conversation_id && this.conversationId) {
      payload.conversation_id = this.conversationId;
    }

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || error.message || 'Request failed');
    }

    const result = (await response.json()) as AnalyzeResponse;
    if (result.conversation_id) {
      this.setConversationId(result.conversation_id);
    }
    return result;
  }



}







export const api = new ApiService();
