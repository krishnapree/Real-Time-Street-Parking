'use client';

import { useState } from 'react';
import { Upload, BarChart3, Zap } from 'lucide-react';
import VideoUpload from '@/components/features/VideoUpload';
import ProcessingStatus from '@/components/features/ProcessingStatus';
import ResultsDisplay from '@/components/features/ResultsDisplay';
import Header from '@/components/ui/Header';
import { VideoUploadResponse, ProcessingStatus as ProcessingStatusType } from '@/types';

export default function AppPage() {
  const [currentJob, setCurrentJob] = useState<VideoUploadResponse | null>(null);
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatusType | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'processing' | 'results'>('upload');

  const handleUploadSuccess = (response: VideoUploadResponse) => {
    setCurrentJob(response);
    setActiveTab('processing');
  };

  const handleProcessingComplete = (status: ProcessingStatusType) => {
    setProcessingStatus(status);
    if (status.status === 'completed') {
      setActiveTab('results');
    }
  };

  const handleNewUpload = () => {
    setCurrentJob(null);
    setProcessingStatus(null);
    setActiveTab('upload');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg p-1 shadow-soft">
            {[
              { id: 'upload', label: 'Upload Video', icon: Upload },
              { id: 'processing', label: 'Processing', icon: Zap },
              { id: 'results', label: 'Results', icon: BarChart3 },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                disabled={
                  (tab.id === 'processing' && !currentJob) ||
                  (tab.id === 'results' && processingStatus?.status !== 'completed')
                }
                className={`
                  inline-flex items-center px-6 py-3 rounded-md text-sm font-medium transition-all
                  ${
                    activeTab === tab.id
                      ? 'bg-primary-600 text-white shadow-md'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed'
                  }
                `}
              >
                <tab.icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="max-w-6xl mx-auto">
          {activeTab === 'upload' && (
            <VideoUpload onUploadSuccess={handleUploadSuccess} />
          )}
          
          {activeTab === 'processing' && currentJob && (
            <ProcessingStatus
              jobId={currentJob.job_id}
              onProcessingComplete={handleProcessingComplete}
              onNewUpload={handleNewUpload}
            />
          )}
          
          {activeTab === 'results' && currentJob && processingStatus?.status === 'completed' && (
            <ResultsDisplay
              jobId={currentJob.job_id}
              onNewUpload={handleNewUpload}
            />
          )}
        </div>
      </main>
    </div>
  );
}
