"""
Detection and parking analysis models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class BoundingBox(BaseModel):
    """Bounding box coordinates"""
    x1: float = Field(..., description="Top-left x coordinate")
    y1: float = Field(..., description="Top-left y coordinate")
    x2: float = Field(..., description="Bottom-right x coordinate")
    y2: float = Field(..., description="Bottom-right y coordinate")
    
    @property
    def width(self) -> float:
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        return self.y2 - self.y1
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @property
    def center(self) -> tuple:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)


class Detection(BaseModel):
    """Single object detection"""
    class_id: int = Field(..., description="Detected class ID")
    class_name: str = Field(..., description="Detected class name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")


class ParkingSpace(BaseModel):
    """Parking space definition"""
    id: str = Field(..., description="Unique parking space identifier")
    bbox: BoundingBox = Field(..., description="Parking space bounding box")
    is_occupied: bool = Field(default=False, description="Whether the space is occupied")
    occupancy_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Occupancy confidence")
    detected_vehicle: Optional[Detection] = Field(None, description="Detected vehicle if occupied")


class FrameAnalysis(BaseModel):
    """Analysis results for a single frame"""
    frame_number: int = Field(..., description="Frame number")
    timestamp: float = Field(..., description="Timestamp in video")
    detections: List[Detection] = Field(default=[], description="All detections in frame")
    parking_spaces: List[ParkingSpace] = Field(default=[], description="Parking space analysis")
    total_spaces: int = Field(default=0, description="Total parking spaces")
    occupied_spaces: int = Field(default=0, description="Number of occupied spaces")
    available_spaces: int = Field(default=0, description="Number of available spaces")
    occupancy_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Occupancy rate")


class VideoAnalysisResult(BaseModel):
    """Complete video analysis results"""
    job_id: str = Field(..., description="Job identifier")
    video_info: Dict[str, Any] = Field(..., description="Video metadata")
    frames_analyzed: int = Field(..., description="Number of frames analyzed")
    total_frames: int = Field(..., description="Total frames in video")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    # Overall statistics
    avg_total_spaces: float = Field(default=0.0, description="Average total parking spaces")
    avg_occupied_spaces: float = Field(default=0.0, description="Average occupied spaces")
    avg_available_spaces: float = Field(default=0.0, description="Average available spaces")
    avg_occupancy_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Average occupancy rate")
    
    # Peak statistics
    max_occupancy: float = Field(default=0.0, description="Maximum occupancy rate")
    min_occupancy: float = Field(default=0.0, description="Minimum occupancy rate")
    peak_occupied_spaces: int = Field(default=0, description="Peak number of occupied spaces")
    
    # Frame-by-frame results (optional, for detailed analysis)
    frame_results: Optional[List[FrameAnalysis]] = Field(None, description="Detailed frame analysis")
    
    # Output files
    processed_video_url: Optional[str] = Field(None, description="URL to processed video")
    thumbnail_url: Optional[str] = Field(None, description="URL to video thumbnail")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis creation time")


class ParkingStatistics(BaseModel):
    """Parking statistics summary"""
    job_id: str = Field(..., description="Job identifier")
    
    # Current state (last frame)
    current_total_spaces: int = Field(default=0, description="Current total spaces")
    current_occupied_spaces: int = Field(default=0, description="Current occupied spaces")
    current_available_spaces: int = Field(default=0, description="Current available spaces")
    current_occupancy_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Current occupancy rate")
    
    # Historical averages
    avg_occupancy_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Average occupancy rate")
    avg_occupied_spaces: float = Field(default=0.0, description="Average occupied spaces")
    
    # Peak values
    peak_occupancy_rate: float = Field(default=0.0, description="Peak occupancy rate")
    peak_occupied_spaces: int = Field(default=0, description="Peak occupied spaces")
    lowest_occupancy_rate: float = Field(default=0.0, description="Lowest occupancy rate")
    
    # Time-based analysis
    busiest_period: Optional[str] = Field(None, description="Time period with highest occupancy")
    quietest_period: Optional[str] = Field(None, description="Time period with lowest occupancy")
    
    # Trends
    occupancy_trend: Optional[str] = Field(None, description="Overall occupancy trend (increasing/decreasing/stable)")
    
    # Metadata
    analysis_duration: float = Field(..., description="Duration of analyzed video in seconds")
    frames_analyzed: int = Field(..., description="Number of frames analyzed")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
