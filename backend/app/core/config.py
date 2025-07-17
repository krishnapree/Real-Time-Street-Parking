"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # File Storage (use /tmp for Render deployment)
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    PROCESSED_DIR: str = os.getenv("PROCESSED_DIR", "/tmp/processed")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB in bytes
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [".mp4", ".avi", ".mov", ".mkv", ".wmv"]
    
    # YOLO Configuration
    YOLO_MODEL_PATH: str = "assets/models/yolov8n.pt"
    CONFIDENCE_THRESHOLD: float = 0.3  # Threshold matching user's preference
    IOU_THRESHOLD: float = 0.4
    
    # Detection Classes (COCO dataset classes for vehicles)
    VEHICLE_CLASSES: List[int] = [2, 3, 5, 7]  # car, motorcycle, bus, truck
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        os.getenv("FRONTEND_URL", "https://your-frontend-app.onrender.com")
    ]
    
    # Processing Configuration
    MAX_CONCURRENT_JOBS: int = 3
    JOB_TIMEOUT_SECONDS: int = 300  # 5 minutes
    
    # Video Processing
    OUTPUT_FPS: int = 30
    OUTPUT_QUALITY: int = 80
    FRAME_SKIP: int = 1  # Process every nth frame for performance
    
    # Parking Detection
    PARKING_SPACE_MIN_AREA: int = 1000  # Minimum area for a parking space
    OCCUPANCY_THRESHOLD: float = 0.3  # Threshold for considering a space occupied
    ENABLE_REAL_PROCESSING: bool = True  # Enable real YOLO processing vs demo mode
    DEBUG_MODE: bool = True  # Enable debug logging for detection issues

    # Enhanced detection settings
    MIN_VEHICLE_AREA: int = 500  # Minimum area for vehicle detection
    MAX_VEHICLE_AREA: int = 50000  # Maximum area for vehicle detection
    OVERLAP_THRESHOLD_SPACE: float = 0.20  # Lower threshold for space overlap (20%)
    OVERLAP_THRESHOLD_VEHICLE: float = 0.35  # Lower threshold for vehicle overlap (35%)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
