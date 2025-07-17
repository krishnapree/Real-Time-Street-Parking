"""
Video upload endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
import uuid
import os
import aiofiles
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.models.video import VideoUploadResponse, JobStatus, VideoProcessingRequest
from app.utils.file_handler import validate_video_file, get_video_info
from app.utils.logger import setup_logger
from app.services.video_processor import VideoProcessor

# Setup router and logger
router = APIRouter()
logger = setup_logger(__name__)

# Import dependency
from app.core.dependencies import get_video_processor


@router.options("/")
async def upload_options():
    """Handle CORS preflight for upload endpoint"""
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
    )


@router.post("/")
async def upload_video(
    file: UploadFile = File(...),
    config: Optional[str] = None
):
    video_processor = get_video_processor()
    """
    Upload a video file for parking detection analysis

    Args:
        file: Video file to upload
        config: Optional processing configuration

    Returns:
        Upload response with job ID and status
    """
    try:
        logger.info(f"Received upload request for file: {file.filename}")
        logger.info(f"File content type: {file.content_type}")
        logger.info(f"Config: {config}")

        # Basic file validation
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file provided"
            )

        # Check file extension
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed: {allowed_extensions}"
            )
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_extension = Path(file.filename).suffix.lower()
        saved_filename = f"{job_id}{file_extension}"
        file_path = upload_dir / saved_filename
        
        # Save file asynchronously with proper error handling
        try:
            content = await file.read()
            file_size = len(content)

            if file_size == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is empty"
                )

            if file_size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
                )

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            # Verify file was written correctly
            if not file_path.exists():
                raise HTTPException(
                    status_code=500,
                    detail="Failed to save uploaded file"
                )

            actual_size = file_path.stat().st_size
            if actual_size != file_size:
                raise HTTPException(
                    status_code=500,
                    detail=f"File size mismatch: expected {file_size}, got {actual_size}"
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save uploaded file: {str(e)}"
            )
        
        logger.info(f"Video uploaded successfully: {file.filename} -> {saved_filename}")
        logger.info(f"Job ID: {job_id}, File size: {file_size} bytes")

        # Parse config if provided
        processing_config = VideoProcessingRequest()
        if config:
            try:
                import json
                config_dict = json.loads(config)
                processing_config = VideoProcessingRequest(**config_dict)
            except Exception as e:
                logger.warning(f"Failed to parse config: {e}, using defaults")

        # Start processing asynchronously
        created_job_id = await video_processor.create_processing_job(file_path, processing_config)
        if not created_job_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to start video processing"
            )

        # Use the job ID from the processor (should be the same)
        job_id = created_job_id

        # Verify job was created
        logger.info(f"Job created. Total jobs now: {len(video_processor.jobs)}")
        logger.info(f"Job {job_id} exists: {job_id in video_processor.jobs}")
        
        # Return upload response as dictionary
        from datetime import datetime
        return {
            "job_id": job_id,
            "filename": file.filename,
            "file_size": file_size,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "message": "Video uploaded successfully and processing started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload video: {str(e)}"
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported video formats
    
    Returns:
        List of supported file extensions
    """
    return {
        "supported_formats": settings.ALLOWED_VIDEO_EXTENSIONS,
        "max_file_size": settings.MAX_FILE_SIZE,
        "max_file_size_mb": settings.MAX_FILE_SIZE // (1024 * 1024)
    }


@router.delete("/{job_id}")
async def delete_upload(job_id: str):
    video_processor = get_video_processor()
    """
    Delete uploaded video and associated files
    
    Args:
        job_id: Job identifier
        
    Returns:
        Deletion confirmation
    """
    try:
        # Find and delete uploaded file
        upload_dir = Path(settings.UPLOAD_DIR)
        processed_dir = Path(settings.PROCESSED_DIR)
        
        deleted_files = []
        
        # Delete uploaded file
        for ext in settings.ALLOWED_VIDEO_EXTENSIONS:
            upload_file = upload_dir / f"{job_id}{ext}"
            if upload_file.exists():
                upload_file.unlink()
                deleted_files.append(str(upload_file))
        
        # Delete processed files
        for file_path in processed_dir.glob(f"{job_id}*"):
            file_path.unlink()
            deleted_files.append(str(file_path))
        
        # Cancel processing if still running
        await video_processor.cancel_job(job_id)
        
        logger.info(f"Deleted files for job {job_id}: {deleted_files}")
        
        return {
            "job_id": job_id,
            "message": "Files deleted successfully",
            "deleted_files": deleted_files
        }
        
    except Exception as e:
        logger.error(f"Error deleting files for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete files: {str(e)}"
        )
