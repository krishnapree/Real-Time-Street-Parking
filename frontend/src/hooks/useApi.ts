import { useState, useCallback } from 'react';
import { apiClient } from '@/utils/api';
import { ApiError } from '@/types';
import toast from 'react-hot-toast';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

/**
 * Generic hook for API calls with loading, error, and success states
 */
export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<T>,
  showToast: boolean = true
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const result = await apiFunction(...args);
        setState({ data: result, loading: false, error: null });
        return result;
      } catch (error) {
        const apiError = error as ApiError;
        setState(prev => ({ ...prev, loading: false, error: apiError }));
        
        if (showToast) {
          toast.error(apiError.message || 'An error occurred');
        }
        
        return null;
      }
    },
    [apiFunction, showToast]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, execute, reset };
}

/**
 * Hook for video upload with progress tracking
 */
export function useVideoUpload() {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const uploadVideo = useCallback(
    async (file: File, config?: any) => {
      setIsUploading(true);
      setError(null);
      setUploadProgress(0);

      try {
        const result = await apiClient.uploadVideo(
          file,
          config,
          (progress) => setUploadProgress(progress)
        );
        
        setIsUploading(false);
        toast.success('Video uploaded successfully!');
        return result;
      } catch (error) {
        const apiError = error as ApiError;
        setError(apiError);
        setIsUploading(false);
        toast.error(apiError.message || 'Upload failed');
        return null;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setUploadProgress(0);
    setIsUploading(false);
    setError(null);
  }, []);

  return {
    uploadVideo,
    uploadProgress,
    isUploading,
    error,
    reset,
  };
}

/**
 * Hook for polling processing status
 */
export function useProcessingStatus(jobId: string | null, interval: number = 3000) {
  const [status, setStatus] = useState<any>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const startPolling = useCallback(() => {
    if (!jobId) return;

    setIsPolling(true);
    setError(null);

    const poll = async () => {
      try {
        const result = await apiClient.getProcessingStatus(jobId);
        setStatus(result);

        // Stop polling if job is completed or failed
        if (result.status === 'completed' || result.status === 'failed') {
          setIsPolling(false);
          return;
        }

        // Continue polling
        if (isPolling) {
          setTimeout(poll, interval);
        }
      } catch (error) {
        const apiError = error as ApiError;
        setError(apiError);
        setIsPolling(false);
      }
    };

    poll();
  }, [jobId, interval, isPolling]);

  const stopPolling = useCallback(() => {
    setIsPolling(false);
  }, []);

  const reset = useCallback(() => {
    setStatus(null);
    setIsPolling(false);
    setError(null);
  }, []);

  return {
    status,
    isPolling,
    error,
    startPolling,
    stopPolling,
    reset,
  };
}

/**
 * Hook for managing multiple API calls
 */
export function useApiQueue() {
  const [queue, setQueue] = useState<Array<{ id: string; promise: Promise<any> }>>([]);
  const [results, setResults] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, ApiError | undefined>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});

  const addToQueue = useCallback(
    async (id: string, apiCall: () => Promise<any>) => {
      setLoading(prev => ({ ...prev, [id]: true }));
      setErrors(prev => ({ ...prev, [id]: undefined }));

      const promise = apiCall();
      setQueue(prev => [...prev, { id, promise }]);

      try {
        const result = await promise;
        setResults(prev => ({ ...prev, [id]: result }));
      } catch (error) {
        setErrors(prev => ({ ...prev, [id]: error as ApiError }));
      } finally {
        setLoading(prev => ({ ...prev, [id]: false }));
        setQueue(prev => prev.filter(item => item.id !== id));
      }
    },
    []
  );

  const clearQueue = useCallback(() => {
    setQueue([]);
    setResults({});
    setErrors({});
    setLoading({});
  }, []);

  return {
    queue,
    results,
    errors,
    loading,
    addToQueue,
    clearQueue,
  };
}

/**
 * Hook for data export functionality
 */
export function useDataExport() {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const exportData = useCallback(
    async (jobId: string, format: 'json' | 'csv' | 'xlsx', filename?: string) => {
      setIsExporting(true);
      setError(null);

      try {
        const blob = await apiClient.exportResults(jobId, format);
        const downloadFilename = filename || `parking-analysis-${jobId}.${format}`;
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = downloadFilename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        toast.success('Export completed successfully!');
      } catch (error) {
        const apiError = error as ApiError;
        setError(apiError);
        toast.error(apiError.message || 'Export failed');
      } finally {
        setIsExporting(false);
      }
    },
    []
  );

  return {
    exportData,
    isExporting,
    error,
  };
}
