'use client';

import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  Maximize, 
  Download,
  RotateCcw,
  SkipBack,
  SkipForward
} from 'lucide-react';

interface VideoPlayerProps {
  videoUrl: string;
  thumbnailUrl?: string;
  title?: string;
  className?: string;
}

export default function VideoPlayer({ 
  videoUrl, 
  thumbnailUrl, 
  title = "Video Player",
  className = ""
}: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDebug, setShowDebug] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
      setIsMuted(newVolume === 0);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
      setIsLoading(false);
    }
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (progressRef.current && videoRef.current) {
      const rect = progressRef.current.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const newTime = (clickX / rect.width) * duration;
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const skip = (seconds: number) => {
    if (videoRef.current) {
      const newTime = Math.max(0, Math.min(duration, currentTime + seconds));
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        videoRef.current.requestFullscreen();
      }
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = videoUrl;
    link.download = 'processed-video.mp4';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleError = (e: any) => {
    console.error('Video loading error:', e);
    console.error('Video URL:', videoUrl);

    // Get more specific error information
    const video = videoRef.current;
    if (video) {
      console.error('Video error details:', {
        error: video.error,
        networkState: video.networkState,
        readyState: video.readyState,
        currentSrc: video.currentSrc
      });

      // Check for specific error types
      if (video.error) {
        const errorCode = video.error.code;
        const errorMessage = video.error.message;
        console.error('Video error code:', errorCode, 'Message:', errorMessage);

        // Provide more specific error messages
        switch (errorCode) {
          case 1: // MEDIA_ERR_ABORTED
            setError('Video loading was aborted. Please try again.');
            break;
          case 2: // MEDIA_ERR_NETWORK
            setError('Network error while loading video. Please check your connection and try again.');
            break;
          case 3: // MEDIA_ERR_DECODE
            setError('Video format not supported or corrupted. Please try uploading a different video.');
            break;
          case 4: // MEDIA_ERR_SRC_NOT_SUPPORTED
            setError('Video format not supported by your browser. This may be due to codec compatibility issues. Please try uploading a new video or use a different browser.');
            break;
          default:
            setError('Failed to load video. Please check the video URL and try again.');
        }
      } else {
        setError('Failed to load video. Please check the video URL and try again.');
      }
    } else {
      setError('Failed to load video. Please check the video URL and try again.');
    }

    setIsLoading(false);
  };

  const retryVideoLoad = () => {
    if (retryCount < 3) { // Max 3 retries
      console.log(`Retrying video load, attempt ${retryCount + 1}`);
      setRetryCount(prev => prev + 1);
      setError(null);
      setIsLoading(true);

      if (videoRef.current) {
        // Add a small delay before retry
        setTimeout(() => {
          if (videoRef.current) {
            videoRef.current.load();
          }
        }, 1000 * (retryCount + 1)); // Increasing delay: 1s, 2s, 3s
      }
    } else {
      setError('Failed to load video after multiple attempts. Please try uploading a new video.');
    }
  };

  return (
    <div className={`card ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-600">
          Processed video with AI-powered parking space detection and annotations
        </p>
      </div>

      <div 
        className="relative bg-black rounded-lg overflow-hidden group"
        onMouseEnter={() => setShowControls(true)}
        onMouseLeave={() => setShowControls(false)}
      >
        {/* Video Element */}
        <video
          ref={videoRef}
          className="w-full h-auto"
          poster={thumbnailUrl}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onError={handleError}
          preload="metadata"
        >
          <source src={videoUrl} type="video/mp4" />
          Your browser does not support the video tag.
        </video>

        {/* Loading Overlay */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
            <div className="text-white text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p>Loading video...</p>
            </div>
          </div>
        )}

        {/* Error Overlay */}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75">
            <div className="text-white text-center max-w-md mx-auto px-4">
              <p className="mb-4">{error}</p>
              {error.includes('format not supported') && (
                <div className="mb-4 text-sm text-gray-300">
                  <p className="mb-2">💡 <strong>Tip:</strong> This video was processed with an older codec that some browsers don't support.</p>
                  <p>Try uploading a new video for better compatibility, or use Chrome/Firefox for better codec support.</p>
                </div>
              )}
              <button 
                onClick={retryVideoLoad}
                className="btn-primary"
                disabled={retryCount >= 3}
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                {retryCount >= 3 ? 'Max Retries Reached' : `Retry ${retryCount > 0 ? `(${retryCount}/3)` : ''}`}
              </button>
            </div>
          </div>
        )}

        {/* Play Button Overlay */}
        {!isPlaying && !isLoading && !error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30 cursor-pointer"
            onClick={togglePlay}
          >
            <div className="bg-white bg-opacity-90 rounded-full p-4 hover:bg-opacity-100 transition-all">
              <Play className="w-12 h-12 text-gray-900 ml-1" />
            </div>
          </motion.div>
        )}

        {/* Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ 
            opacity: showControls || !isPlaying ? 1 : 0,
            y: showControls || !isPlaying ? 0 : 20
          }}
          transition={{ duration: 0.3 }}
          className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4"
        >
          {/* Progress Bar */}
          <div 
            ref={progressRef}
            className="w-full h-2 bg-white bg-opacity-30 rounded-full cursor-pointer mb-4"
            onClick={handleProgressClick}
          >
            <div 
              className="h-full bg-primary-500 rounded-full transition-all"
              style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
            />
          </div>

          {/* Control Buttons */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => skip(-10)}
                className="text-white hover:text-primary-400 transition-colors"
              >
                <SkipBack className="w-5 h-5" />
              </button>

              <button
                onClick={togglePlay}
                className="text-white hover:text-primary-400 transition-colors"
              >
                {isPlaying ? (
                  <Pause className="w-6 h-6" />
                ) : (
                  <Play className="w-6 h-6" />
                )}
              </button>

              <button
                onClick={() => skip(10)}
                className="text-white hover:text-primary-400 transition-colors"
              >
                <SkipForward className="w-5 h-5" />
              </button>

              <div className="flex items-center space-x-2">
                <button
                  onClick={toggleMute}
                  className="text-white hover:text-primary-400 transition-colors"
                >
                  {isMuted ? (
                    <VolumeX className="w-5 h-5" />
                  ) : (
                    <Volume2 className="w-5 h-5" />
                  )}
                </button>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={isMuted ? 0 : volume}
                  onChange={handleVolumeChange}
                  className="w-20 h-1 bg-white bg-opacity-30 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div className="text-white text-sm">
                {formatTime(currentTime)} / {formatTime(duration)}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleDownload}
                className="text-white hover:text-primary-400 transition-colors"
                title="Download video"
              >
                <Download className="w-5 h-5" />
              </button>

              <button
                onClick={toggleFullscreen}
                className="text-white hover:text-primary-400 transition-colors"
              >
                <Maximize className="w-5 h-5" />
              </button>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Video Info */}
      <div className="mt-4 text-sm text-gray-600">
        <p>
          This video shows the original footage with AI-generated overlays indicating
          detected parking spaces and their occupancy status. Green boxes represent
          available spaces, while red boxes indicate occupied spaces.
        </p>

        {/* Debug Info */}
        <div className="mt-2">
          <button
            onClick={() => setShowDebug(!showDebug)}
            className="text-xs text-blue-600 hover:text-blue-800 underline"
          >
            {showDebug ? 'Hide' : 'Show'} Debug Info
          </button>

          {showDebug && (
            <div className="mt-2 p-3 bg-gray-100 rounded text-xs font-mono">
              <div><strong>Video URL:</strong> {videoUrl}</div>
              <div><strong>Thumbnail URL:</strong> {thumbnailUrl || 'None'}</div>
              <div><strong>Loading:</strong> {isLoading ? 'Yes' : 'No'}</div>
              <div><strong>Error:</strong> {error || 'None'}</div>
              {videoRef.current && (
                <>
                  <div><strong>Network State:</strong> {videoRef.current.networkState}</div>
                  <div><strong>Ready State:</strong> {videoRef.current.readyState}</div>
                  <div><strong>Current Src:</strong> {videoRef.current.currentSrc}</div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
