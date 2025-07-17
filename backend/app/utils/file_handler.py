"""
File handling utilities
"""

import os
import cv2
from pathlib import Path
from typing import Dict, Any
from fastapi import UploadFile

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def validate_video_file(file: UploadFile) -> Dict[str, Any]:
    """
    Validate uploaded video file
    
    Args:
        file: Uploaded file object
        
    Returns:
        Validation result dictionary
    """
    try:
        # Check if file is provided
        if not file or not file.filename:
            return {
                "valid": False,
                "error": "No file provided"
            }
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_VIDEO_EXTENSIONS:
            return {
                "valid": False,
                "error": f"Unsupported file format. Allowed formats: {settings.ALLOWED_VIDEO_EXTENSIONS}"
            }
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
            current_size_mb = file_size // (1024 * 1024)
            return {
                "valid": False,
                "error": f"File too large. Maximum size: {max_size_mb}MB, current size: {current_size_mb}MB"
            }
        
        # Check if file is empty
        if file_size == 0:
            return {
                "valid": False,
                "error": "File is empty"
            }
        
        return {
            "valid": True,
            "file_size": file_size,
            "file_extension": file_extension
        }
        
    except Exception as e:
        logger.error(f"Error validating file: {str(e)}")
        return {
            "valid": False,
            "error": f"File validation error: {str(e)}"
        }


def get_video_info(video_path: Path) -> Dict[str, Any]:
    """
    Get video file information using OpenCV
    
    Args:
        video_path: Path to video file
        
    Returns:
        Video information dictionary
    """
    try:
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError("Could not open video file")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculate duration
        duration = frame_count / fps if fps > 0 else 0
        
        # Get file size
        file_size = video_path.stat().st_size
        
        cap.release()
        
        return {
            "filename": video_path.name,
            "duration": duration,
            "fps": fps,
            "width": width,
            "height": height,
            "total_frames": frame_count,
            "file_size": file_size
        }
        
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        raise ValueError(f"Could not read video information: {str(e)}")


def ensure_directory_exists(directory_path: Path) -> None:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory_path: Path to directory
    """
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ensured: {directory_path}")
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {str(e)}")
        raise


def cleanup_old_files(directory: Path, max_age_hours: int = 24) -> None:
    """
    Clean up old files in directory
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age of files in hours
    """
    try:
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        deleted_count = 0
        for file_path in directory.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old files from {directory}")
            
    except Exception as e:
        logger.error(f"Error cleaning up files in {directory}: {str(e)}")


def get_file_hash(file_path: Path) -> str:
    """
    Get SHA256 hash of file
    
    Args:
        file_path: Path to file
        
    Returns:
        File hash as hex string
    """
    import hashlib
    
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash: {str(e)}")
        raise
