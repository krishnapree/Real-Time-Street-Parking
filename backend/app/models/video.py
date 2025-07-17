"""
Video-related Pydantic models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoUploadResponse(BaseModel):
    """Response model for video upload"""
    job_id: str = Field(..., description="Unique job identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Processing status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    message: str = Field(..., description="Response message")


class VideoInfo(BaseModel):
    """Video information model"""
    filename: str = Field(..., description="Video filename")
    duration: float = Field(..., description="Video duration in seconds")
    fps: float = Field(..., description="Frames per second")
    width: int = Field(..., description="Video width")
    height: int = Field(..., description="Video height")
    total_frames: int = Field(..., description="Total number of frames")
    file_size: int = Field(..., description="File size in bytes")


class ProcessingStatus(BaseModel):
    """Processing status model"""
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Current status")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage")
    current_frame: Optional[int] = Field(None, description="Current frame being processed")
    total_frames: Optional[int] = Field(None, description="Total frames to process")
    estimated_time_remaining: Optional[float] = Field(None, description="Estimated time remaining in seconds")
    created_at: datetime = Field(..., description="Job creation time")
    started_at: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class VideoProcessingRequest(BaseModel):
    """Request model for video processing configuration"""
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Detection confidence threshold")
    iou_threshold: Optional[float] = Field(0.4, ge=0.0, le=1.0, description="IoU threshold for NMS")
    frame_skip: Optional[int] = Field(1, ge=1, description="Process every nth frame")
    output_format: Optional[str] = Field("mp4", description="Output video format")
    
    @validator('confidence_threshold')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence threshold must be between 0.0 and 1.0')
        return v
    
    @validator('iou_threshold')
    def validate_iou(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('IoU threshold must be between 0.0 and 1.0')
        return v
