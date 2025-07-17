'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  File, 
  X, 
  Play, 
  Settings,
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react';
import { useVideoUpload } from '@/hooks/useApi';
import { validateVideoFile, formatFileSize } from '@/utils';
import { VideoUploadResponse, VideoProcessingConfig } from '@/types';

interface VideoUploadProps {
  onUploadSuccess: (response: VideoUploadResponse) => void;
}

export default function VideoUpload({ onUploadSuccess }: VideoUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [config, setConfig] = useState<VideoProcessingConfig>({
    confidence_threshold: 0.5,
    iou_threshold: 0.4,
    frame_skip: 1,
    output_format: 'mp4',
  });

  const { uploadVideo, uploadProgress, isUploading, error, reset } = useVideoUpload();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      const validation = validateVideoFile(file);
      if (validation.valid) {
        setSelectedFile(file);
        reset();
      }
    }
  }, [reset]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    const result = await uploadVideo(selectedFile, config);
    if (result) {
      onUploadSuccess(result);
      setSelectedFile(null);
      reset();
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    reset();
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
            Upload Parking Video
          </h2>
          <p className="text-gray-600">
            Upload your parking lot video to start AI-powered analysis
          </p>
        </div>

        {!selectedFile ? (
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all
              ${isDragActive && !isDragReject ? 'border-primary-500 bg-primary-50' : ''}
              ${isDragReject ? 'border-error-500 bg-error-50' : ''}
              ${!isDragActive ? 'border-gray-300 hover:border-gray-400 hover:bg-gray-50' : ''}
            `}
          >
            <input {...getInputProps()} />
            
            <motion.div
              initial={{ scale: 1 }}
              animate={{ scale: isDragActive ? 1.05 : 1 }}
              transition={{ duration: 0.2 }}
            >
              <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              
              {isDragActive ? (
                <p className="text-lg font-medium text-primary-600">
                  Drop your video here...
                </p>
              ) : (
                <>
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    Drag & drop your video here
                  </p>
                  <p className="text-gray-600 mb-4">
                    or click to browse files
                  </p>
                  <button className="btn-primary">
                    Choose Video File
                  </button>
                </>
              )}
            </motion.div>

            <div className="mt-6 text-sm text-gray-500">
              <p>Supported formats: MP4, AVI, MOV, MKV, WMV</p>
              <p>Maximum file size: 100MB</p>
            </div>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Selected File Info */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="bg-primary-100 p-2 rounded-lg">
                    <File className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-600">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                </div>
                
                {!isUploading && (
                  <button
                    onClick={removeFile}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>

            {/* Processing Configuration */}
            <div className="border border-gray-200 rounded-lg">
              <button
                onClick={() => setShowConfig(!showConfig)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <Settings className="w-5 h-5 text-gray-600" />
                  <span className="font-medium text-gray-900">
                    Processing Configuration
                  </span>
                </div>
                <motion.div
                  animate={{ rotate: showConfig ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </motion.div>
              </button>

              <AnimatePresence>
                {showConfig && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="border-t border-gray-200 p-4 space-y-4"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="label">
                          Confidence Threshold
                        </label>
                        <input
                          type="range"
                          min="0.1"
                          max="1.0"
                          step="0.1"
                          value={config.confidence_threshold}
                          onChange={(e) => setConfig(prev => ({
                            ...prev,
                            confidence_threshold: parseFloat(e.target.value)
                          }))}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>0.1</span>
                          <span>{config.confidence_threshold}</span>
                          <span>1.0</span>
                        </div>
                      </div>

                      <div>
                        <label className="label">
                          IoU Threshold
                        </label>
                        <input
                          type="range"
                          min="0.1"
                          max="1.0"
                          step="0.1"
                          value={config.iou_threshold}
                          onChange={(e) => setConfig(prev => ({
                            ...prev,
                            iou_threshold: parseFloat(e.target.value)
                          }))}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>0.1</span>
                          <span>{config.iou_threshold}</span>
                          <span>1.0</span>
                        </div>
                      </div>

                      <div>
                        <label className="label">
                          Frame Skip
                        </label>
                        <select
                          value={config.frame_skip}
                          onChange={(e) => setConfig(prev => ({
                            ...prev,
                            frame_skip: parseInt(e.target.value)
                          }))}
                          className="input"
                        >
                          <option value={1}>Process every frame</option>
                          <option value={2}>Process every 2nd frame</option>
                          <option value={3}>Process every 3rd frame</option>
                          <option value={5}>Process every 5th frame</option>
                        </select>
                      </div>

                      <div>
                        <label className="label">
                          Output Format
                        </label>
                        <select
                          value={config.output_format}
                          onChange={(e) => setConfig(prev => ({
                            ...prev,
                            output_format: e.target.value
                          }))}
                          className="input"
                        >
                          <option value="mp4">MP4</option>
                          <option value="avi">AVI</option>
                        </select>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Upload Progress */}
            {isUploading && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">
                    Uploading...
                  </span>
                  <span className="text-sm text-gray-600">
                    {uploadProgress}%
                  </span>
                </div>
                <div className="progress-bar">
                  <motion.div
                    className="progress-fill"
                    initial={{ width: 0 }}
                    animate={{ width: `${uploadProgress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </motion.div>
            )}

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center space-x-2 text-error-600 bg-error-50 p-3 rounded-lg"
              >
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm">{error.message}</span>
              </motion.div>
            )}

            {/* Upload Button */}
            <div className="flex justify-end space-x-3">
              <button
                onClick={removeFile}
                disabled={isUploading}
                className="btn-outline"
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={isUploading}
                className="btn-primary flex items-center space-x-2"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Uploading...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Start Analysis</span>
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
