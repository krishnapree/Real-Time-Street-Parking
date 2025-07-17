'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Clock, 
  Play, 
  CheckCircle, 
  XCircle, 
  Loader2,
  RotateCcw,
  X,
  Upload
} from 'lucide-react';
import { useProcessingStatus } from '@/hooks/useApi';
import { formatDuration, formatRelativeTime, getStatusColor } from '@/utils';
import { ProcessingStatus as ProcessingStatusType } from '@/types';

interface ProcessingStatusProps {
  jobId: string;
  onProcessingComplete: (status: ProcessingStatusType) => void;
  onNewUpload: () => void;
}

export default function ProcessingStatus({ 
  jobId, 
  onProcessingComplete, 
  onNewUpload 
}: ProcessingStatusProps) {
  const { status, isPolling, error, startPolling, stopPolling } = useProcessingStatus(jobId);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    if (jobId) {
      startPolling();
    }

    return () => {
      stopPolling();
    };
  }, [jobId, startPolling, stopPolling]);

  useEffect(() => {
    if (status && (status.status === 'completed' || status.status === 'failed')) {
      onProcessingComplete(status);
      stopPolling();
    }
  }, [status, onProcessingComplete, stopPolling]);

  // Update elapsed time
  useEffect(() => {
    if (!status || status.status !== 'processing') return;

    const interval = setInterval(() => {
      if (status.started_at) {
        const elapsed = (Date.now() - new Date(status.started_at).getTime()) / 1000;
        setElapsedTime(elapsed);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [status]);

  const getStatusIcon = () => {
    if (!status) return <Loader2 className="w-6 h-6 animate-spin" />;

    switch (status.status) {
      case 'pending':
        return <Clock className="w-6 h-6 text-warning-600" />;
      case 'processing':
        return <Loader2 className="w-6 h-6 animate-spin text-primary-600" />;
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-success-600" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-error-600" />;
      default:
        return <Clock className="w-6 h-6 text-gray-400" />;
    }
  };

  const getStatusMessage = () => {
    if (!status) return 'Loading status...';

    switch (status.status) {
      case 'pending':
        return 'Video uploaded successfully. Processing will start shortly...';
      case 'processing':
        return 'Analyzing video with AI-powered parking detection...';
      case 'completed':
        return 'Analysis completed successfully! View your results below.';
      case 'failed':
        return status.error_message || 'Processing failed. Please try again.';
      default:
        return 'Unknown status';
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="card"
      >
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Processing Status
          </h2>
          <p className="text-gray-600">
            Track the progress of your video analysis
          </p>
        </div>

        {/* Status Header */}
        <div className="flex items-center justify-center mb-8">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="flex items-center space-x-4"
          >
            {getStatusIcon()}
            <div className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                status ? getStatusColor(status.status) : 'text-gray-600 bg-gray-100'
              }`}>
                {status?.status.toUpperCase() || 'LOADING'}
              </div>
              <p className="text-gray-600 mt-2 max-w-md">
                {getStatusMessage()}
              </p>
            </div>
          </motion.div>
        </div>

        {/* Progress Bar */}
        {status && status.status === 'processing' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-900">
                Processing Progress
              </span>
              <span className="text-sm text-gray-600">
                {status.progress.toFixed(1)}%
              </span>
            </div>
            <div className="progress-bar">
              <motion.div
                className="progress-fill"
                initial={{ width: 0 }}
                animate={{ width: `${status.progress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            
            {/* Frame Progress */}
            {status.current_frame && status.total_frames && (
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>Frame {status.current_frame.toLocaleString()} of {status.total_frames.toLocaleString()}</span>
                {status.estimated_time_remaining && (
                  <span>~{formatDuration(status.estimated_time_remaining)} remaining</span>
                )}
              </div>
            )}
          </motion.div>
        )}

        {/* Status Details */}
        {status && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gray-50 rounded-lg p-6 mb-6"
          >
            <h3 className="font-semibold text-gray-900 mb-4">Job Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Job ID:</span>
                <span className="ml-2 font-mono text-gray-900">{status.job_id}</span>
              </div>
              <div>
                <span className="text-gray-600">Created:</span>
                <span className="ml-2 text-gray-900">
                  {formatRelativeTime(status.created_at)}
                </span>
              </div>
              {status.started_at && (
                <div>
                  <span className="text-gray-600">Started:</span>
                  <span className="ml-2 text-gray-900">
                    {formatRelativeTime(status.started_at)}
                  </span>
                </div>
              )}
              {status.status === 'processing' && elapsedTime > 0 && (
                <div>
                  <span className="text-gray-600">Elapsed Time:</span>
                  <span className="ml-2 text-gray-900">
                    {formatDuration(elapsedTime)}
                  </span>
                </div>
              )}
              {status.completed_at && (
                <div>
                  <span className="text-gray-600">Completed:</span>
                  <span className="ml-2 text-gray-900">
                    {formatRelativeTime(status.completed_at)}
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Error Details */}
        {status?.status === 'failed' && status.error_message && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-error-50 border border-error-200 rounded-lg p-4 mb-6"
          >
            <div className="flex items-start space-x-3">
              <XCircle className="w-5 h-5 text-error-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-medium text-error-900 mb-1">Processing Failed</h4>
                <p className="text-sm text-error-700">{status.error_message}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Loading Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-error-50 border border-error-200 rounded-lg p-4 mb-6"
          >
            <div className="flex items-start space-x-3">
              <XCircle className="w-5 h-5 text-error-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-medium text-error-900 mb-1">Connection Error</h4>
                <p className="text-sm text-error-700">{error.message}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          {status?.status === 'failed' && (
            <button
              onClick={() => startPolling()}
              className="btn-outline flex items-center space-x-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Retry</span>
            </button>
          )}
          
          {(status?.status === 'completed' || status?.status === 'failed') && (
            <button
              onClick={onNewUpload}
              className="btn-primary flex items-center space-x-2"
            >
              <Upload className="w-4 h-4" />
              <span>Upload New Video</span>
            </button>
          )}
          
          {status?.status === 'processing' && (
            <button
              onClick={stopPolling}
              className="btn-outline flex items-center space-x-2"
            >
              <X className="w-4 h-4" />
              <span>Cancel</span>
            </button>
          )}
        </div>

        {/* Real-time Updates Indicator */}
        {isPolling && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-center mt-6 text-sm text-gray-500"
          >
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse" />
              <span>Real-time updates active</span>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
