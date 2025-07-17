'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Download, 
  BarChart3, 
  Clock, 
  Car,
  MapPin,
  TrendingUp,
  Upload,
  ExternalLink,
  FileText,
  Image
} from 'lucide-react';
import { useApi, useDataExport } from '@/hooks/useApi';
import { apiClient } from '@/utils/api';
import { formatDuration, formatPercentage, formatNumber, getOccupancyColor } from '@/utils';
import { VideoAnalysisResult, ParkingStatistics } from '@/types';
import StatisticsChart from '@/components/ui/StatisticsChart';
import VideoPlayer from '@/components/ui/VideoPlayer';

interface ResultsDisplayProps {
  jobId: string;
  onNewUpload: () => void;
}

export default function ResultsDisplay({ jobId, onNewUpload }: ResultsDisplayProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'video' | 'analytics'>('overview');
  
  const { 
    data: results, 
    loading: resultsLoading, 
    execute: fetchResults 
  } = useApi<VideoAnalysisResult>(apiClient.getAnalysisResults);
  
  const { 
    data: statistics, 
    loading: statsLoading, 
    execute: fetchStatistics 
  } = useApi<ParkingStatistics>(apiClient.getParkingStatistics);

  const { exportData, isExporting } = useDataExport();

  useEffect(() => {
    if (jobId) {
      fetchResults(jobId);
      fetchStatistics(jobId);
    }
  }, [jobId, fetchResults, fetchStatistics]);

  const handleExport = async (format: 'json' | 'csv' | 'xlsx') => {
    await exportData(jobId, format);
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'video', label: 'Processed Video', icon: Play },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
  ];

  if (resultsLoading || statsLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card">
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading results...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!results || !statistics) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card">
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">No results found for this job.</p>
            <button onClick={onNewUpload} className="btn-primary">
              Upload New Video
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="card"
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Analysis Results
            </h2>
            <p className="text-gray-600">
              Comprehensive parking detection analysis for your video
            </p>
          </div>
          
          <div className="flex items-center space-x-3 mt-4 md:mt-0">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleExport('json')}
                disabled={isExporting}
                className="btn-outline text-sm"
              >
                <FileText className="w-4 h-4 mr-1" />
                JSON
              </button>
              <button
                onClick={() => handleExport('csv')}
                disabled={isExporting}
                className="btn-outline text-sm"
              >
                <Download className="w-4 h-4 mr-1" />
                CSV
              </button>
            </div>
            <button onClick={onNewUpload} className="btn-primary">
              <Upload className="w-4 h-4 mr-2" />
              New Analysis
            </button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-600">Total Spaces</p>
                <p className="text-2xl font-bold text-primary-900">
                  {Math.round(statistics.current_total_spaces)}
                </p>
              </div>
              <MapPin className="w-8 h-8 text-primary-600" />
            </div>
          </div>

          <div className="bg-gradient-to-r from-success-50 to-success-100 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-success-600">Available</p>
                <p className="text-2xl font-bold text-success-900">
                  {statistics.current_available_spaces}
                </p>
              </div>
              <Car className="w-8 h-8 text-success-600" />
            </div>
          </div>

          <div className="bg-gradient-to-r from-error-50 to-error-100 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-error-600">Occupied</p>
                <p className="text-2xl font-bold text-error-900">
                  {statistics.current_occupied_spaces}
                </p>
              </div>
              <Car className="w-8 h-8 text-error-600" />
            </div>
          </div>

          <div className="bg-gradient-to-r from-warning-50 to-warning-100 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-warning-600">Occupancy Rate</p>
                <p className={`text-2xl font-bold ${getOccupancyColor(statistics.current_occupancy_rate)}`}>
                  {formatPercentage(statistics.current_occupancy_rate)}
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-warning-600" />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Navigation Tabs */}
      <div className="flex justify-center">
        <div className="bg-white rounded-lg p-1 shadow-soft">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`
                inline-flex items-center px-6 py-3 rounded-md text-sm font-medium transition-all
                ${
                  activeTab === tab.id
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }
              `}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
      >
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Processing Summary */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Processing Summary
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <Clock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Processing Time</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {formatDuration(results.processing_time)}
                  </p>
                </div>
                <div className="text-center">
                  <Play className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Frames Analyzed</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {formatNumber(results.frames_analyzed)}
                  </p>
                </div>
                <div className="text-center">
                  <BarChart3 className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Avg Occupancy</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {formatPercentage(statistics.avg_occupancy_rate)}
                  </p>
                </div>
              </div>
            </div>

            {/* Peak Statistics */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Peak Statistics
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-error-50 rounded-lg p-4">
                  <h4 className="font-medium text-error-900 mb-2">Peak Occupancy</h4>
                  <p className="text-2xl font-bold text-error-600">
                    {formatPercentage(statistics.peak_occupancy_rate)}
                  </p>
                  <p className="text-sm text-error-700">
                    {statistics.peak_occupied_spaces} spaces occupied
                  </p>
                </div>
                <div className="bg-success-50 rounded-lg p-4">
                  <h4 className="font-medium text-success-900 mb-2">Lowest Occupancy</h4>
                  <p className="text-2xl font-bold text-success-600">
                    {formatPercentage(statistics.lowest_occupancy_rate)}
                  </p>
                  <p className="text-sm text-success-700">
                    Most available spaces
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'video' && (
          <div className="space-y-6">
            <VideoPlayer
              videoUrl={apiClient.getProcessedVideoUrl(jobId)}
              thumbnailUrl={apiClient.getThumbnailUrl(jobId)}
              title="Processed Video with Parking Detection"
            />
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <StatisticsChart
              data={results.frame_results || []}
              title="Occupancy Over Time"
            />
          </div>
        )}
      </motion.div>
    </div>
  );
}
