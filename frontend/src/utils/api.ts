import axios, { AxiosResponse, AxiosError } from 'axios';
import {
  VideoUploadResponse,
  ProcessingStatus,
  VideoAnalysisResult,
  ParkingStatistics,
  VideoProcessingConfig,
  ApiError,
} from '@/types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 300000, // 5 minutes for video processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    const apiError: ApiError = {
      message: 'An unexpected error occurred',
      status: error.response?.status,
    };

    if (error.response?.data) {
      const errorData = error.response.data as any;
      apiError.message = errorData.detail || errorData.message || apiError.message;
    } else if (error.message) {
      apiError.message = error.message;
    }

    return Promise.reject(apiError);
  }
);

// API functions
export const apiClient = {
  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await api.get('/health');
    return response.data;
  },

  // Upload video
  async uploadVideo(
    file: File,
    config?: VideoProcessingConfig,
    onUploadProgress?: (progress: number) => void
  ): Promise<VideoUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (config) {
      formData.append('config', JSON.stringify(config));
    }

    const response = await api.post('/api/v1/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 600000, // 10 minutes for large video uploads
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onUploadProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onUploadProgress(progress);
        }
      },
    });

    return response.data;
  },

  // Get supported formats
  async getSupportedFormats(): Promise<{
    supported_formats: string[];
    max_file_size: number;
    max_file_size_mb: number;
  }> {
    const response = await api.get('/api/v1/upload/supported-formats');
    return response.data;
  },

  // Get processing status
  async getProcessingStatus(jobId: string): Promise<ProcessingStatus> {
    const response = await api.get(`/api/v1/processing/${jobId}`);
    return response.data;
  },

  // Get all processing status
  async getAllProcessingStatus(
    status?: string,
    limit?: number
  ): Promise<ProcessingStatus[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (limit) params.append('limit', limit.toString());

    const response = await api.get(`/api/v1/processing/?${params.toString()}`);
    return response.data;
  },

  // Cancel processing
  async cancelProcessing(jobId: string): Promise<{ message: string }> {
    const response = await api.post(`/api/v1/processing/${jobId}/cancel`);
    return response.data;
  },

  // Retry processing
  async retryProcessing(jobId: string): Promise<{ message: string }> {
    const response = await api.post(`/api/v1/processing/${jobId}/retry`);
    return response.data;
  },

  // Get processing logs
  async getProcessingLogs(
    jobId: string,
    lines?: number
  ): Promise<{ logs: string[]; lines_returned: number }> {
    const params = new URLSearchParams();
    if (lines) params.append('lines', lines.toString());

    const response = await api.get(`/api/v1/processing/${jobId}/logs?${params.toString()}`);
    return response.data;
  },

  // Get analysis results
  async getAnalysisResults(jobId: string): Promise<VideoAnalysisResult> {
    const response = await api.get(`/api/v1/results/${jobId}`);
    return response.data;
  },

  // Get parking statistics
  async getParkingStatistics(jobId: string): Promise<ParkingStatistics> {
    const response = await api.get(`/api/v1/results/${jobId}/statistics`);
    return response.data;
  },

  // Get processed video URL
  getProcessedVideoUrl(jobId: string): string {
    // Use API endpoint with proper CORS headers
    return `${api.defaults.baseURL}/api/v1/video/${jobId}`;
  },

  // Get processed video URL (API endpoint alternative)
  getProcessedVideoUrlApi(jobId: string): string {
    return `${api.defaults.baseURL}/api/v1/video/${jobId}`;
  },

  // Get thumbnail URL
  getThumbnailUrl(jobId: string): string {
    return `${api.defaults.baseURL}/api/v1/thumbnail/${jobId}`;
  },

  // Get thumbnail URL (API endpoint alternative)
  getThumbnailUrlApi(jobId: string): string {
    return `${api.defaults.baseURL}/api/v1/thumbnail/${jobId}`;
  },

  // Export results
  async exportResults(
    jobId: string,
    format: 'json' | 'csv' | 'xlsx'
  ): Promise<Blob> {
    const response = await api.get(`/api/v1/results/${jobId}/export?format=${format}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Delete upload
  async deleteUpload(jobId: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/v1/upload/${jobId}`);
    return response.data;
  },

  // Delete results
  async deleteResults(jobId: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/v1/results/${jobId}`);
    return response.data;
  },
};

export default apiClient;
