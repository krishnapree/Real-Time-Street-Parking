// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

// Job Status Types
export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface ProcessingStatus {
  job_id: string;
  status: JobStatus;
  progress: number;
  current_frame?: number;
  total_frames?: number;
  estimated_time_remaining?: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

// Video Types
export interface VideoUploadResponse {
  job_id: string;
  filename: string;
  file_size: number;
  status: JobStatus;
  created_at: string;
  message: string;
}

export interface VideoInfo {
  filename: string;
  duration: number;
  fps: number;
  width: number;
  height: number;
  total_frames: number;
  file_size: number;
}

export interface VideoProcessingConfig {
  confidence_threshold?: number;
  iou_threshold?: number;
  frame_skip?: number;
  output_format?: string;
}

// Detection Types
export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: BoundingBox;
}

export interface ParkingSpace {
  id: string;
  bbox: BoundingBox;
  is_occupied: boolean;
  occupancy_confidence: number;
  detected_vehicle?: Detection;
}

export interface FrameAnalysis {
  frame_number: number;
  timestamp: number;
  detections: Detection[];
  parking_spaces: ParkingSpace[];
  total_spaces: number;
  occupied_spaces: number;
  available_spaces: number;
  occupancy_rate: number;
}

// Analysis Results
export interface VideoAnalysisResult {
  job_id: string;
  video_info: Record<string, any>;
  frames_analyzed: number;
  total_frames: number;
  processing_time: number;
  avg_total_spaces: number;
  avg_occupied_spaces: number;
  avg_available_spaces: number;
  avg_occupancy_rate: number;
  max_occupancy: number;
  min_occupancy: number;
  peak_occupied_spaces: number;
  frame_results?: FrameAnalysis[];
  processed_video_url?: string;
  thumbnail_url?: string;
  created_at: string;
}

export interface ParkingStatistics {
  job_id: string;
  current_total_spaces: number;
  current_occupied_spaces: number;
  current_available_spaces: number;
  current_occupancy_rate: number;
  avg_occupancy_rate: number;
  avg_occupied_spaces: number;
  peak_occupancy_rate: number;
  peak_occupied_spaces: number;
  lowest_occupancy_rate: number;
  busiest_period?: string;
  quietest_period?: string;
  occupancy_trend?: string;
  analysis_duration: number;
  frames_analyzed: number;
  last_updated: string;
}

// UI Types
export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

// Component Props
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

// Form Types
export interface UploadFormData {
  file: File;
  config?: VideoProcessingConfig;
}

// Chart Data Types
export interface ChartDataPoint {
  timestamp: number;
  occupancy_rate: number;
  occupied_spaces: number;
  available_spaces: number;
  total_spaces: number;
}

// Error Types
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}

// Supported file formats
export const SUPPORTED_VIDEO_FORMATS = [
  'video/mp4',
  'video/avi',
  'video/mov',
  'video/quicktime',
  'video/x-msvideo',
  'video/x-ms-wmv',
  'video/x-matroska'
];

export const SUPPORTED_VIDEO_EXTENSIONS = [
  '.mp4',
  '.avi',
  '.mov',
  '.mkv',
  '.wmv'
];
