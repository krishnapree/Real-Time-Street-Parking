"""
Results retrieval endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional

from app.models.detection import VideoAnalysisResult, ParkingStatistics
from app.services.video_processor import VideoProcessor
from app.core.config import settings
from app.utils.logger import setup_logger

# Setup router and logger
router = APIRouter()
logger = setup_logger(__name__)

# Import dependency
from app.core.dependencies import get_video_processor


@router.get("/{job_id}")
async def get_analysis_results(job_id: str):
    """
    Get complete analysis results for a job

    Args:
        job_id: Job identifier

    Returns:
        Complete video analysis results
    """
    video_processor = get_video_processor()
    try:
        logger.info(f"Getting results for job: {job_id}")

        results = await video_processor.get_analysis_results(job_id)

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"Results for job {job_id} not found"
            )

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting results for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis results: {str(e)}"
        )


@router.get("/{job_id}/statistics")
async def get_parking_statistics(job_id: str):
    """
    Get parking statistics for a job

    Args:
        job_id: Job identifier

    Returns:
        Parking statistics summary
    """
    video_processor = get_video_processor()
    try:
        logger.info(f"Getting statistics for job: {job_id}")

        statistics = await video_processor.get_parking_statistics(job_id)

        if not statistics:
            raise HTTPException(
                status_code=404,
                detail=f"Statistics for job {job_id} not found"
            )

        return statistics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting statistics for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get parking statistics: {str(e)}"
        )


@router.get("/{job_id}/video")
async def get_processed_video(job_id: str):
    """
    Download processed video file
    
    Args:
        job_id: Job identifier
        
    Returns:
        Processed video file
    """
    try:
        processed_dir = Path(settings.PROCESSED_DIR)
        
        # Find processed video file
        video_file = None
        for ext in ['.mp4', '.avi', '.mov']:
            potential_file = processed_dir / f"{job_id}_processed{ext}"
            if potential_file.exists():
                video_file = potential_file
                break
        
        if not video_file:
            raise HTTPException(
                status_code=404,
                detail=f"Processed video for job {job_id} not found"
            )
        
        return FileResponse(
            path=video_file,
            media_type='video/mp4',
            filename=f"{job_id}_processed.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processed video for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get processed video: {str(e)}"
        )


@router.get("/{job_id}/thumbnail")
async def get_video_thumbnail(job_id: str):
    """
    Get video thumbnail image
    
    Args:
        job_id: Job identifier
        
    Returns:
        Thumbnail image file
    """
    try:
        processed_dir = Path(settings.PROCESSED_DIR)
        thumbnail_file = processed_dir / f"{job_id}_thumbnail.jpg"
        
        if not thumbnail_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Thumbnail for job {job_id} not found"
            )
        
        return FileResponse(
            path=thumbnail_file,
            media_type='image/jpeg',
            filename=f"{job_id}_thumbnail.jpg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thumbnail for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get thumbnail: {str(e)}"
        )


@router.get("/{job_id}/export")
async def export_results(
    job_id: str,
    format: str = Query("json", regex="^(json|csv|xlsx)$", description="Export format")
):
    """
    Export analysis results in various formats
    
    Args:
        job_id: Job identifier
        format: Export format (json, csv, xlsx)
        
    Returns:
        Exported results file
    """
    try:
        # Export not implemented yet
        export_file = None
        
        if not export_file or not export_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Export file for job {job_id} not found"
            )
        
        # Determine media type based on format
        media_types = {
            "json": "application/json",
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
        return FileResponse(
            path=export_file,
            media_type=media_types.get(format, "application/octet-stream"),
            filename=f"{job_id}_results.{format}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting results for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export results: {str(e)}"
        )


@router.delete("/{job_id}")
async def delete_results(job_id: str):
    """
    Delete all results and files for a job
    
    Args:
        job_id: Job identifier
        
    Returns:
        Deletion confirmation
    """
    try:
        # Delete not implemented yet
        success = False
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Results for job {job_id} not found"
            )
        
        logger.info(f"Results for job {job_id} deleted successfully")
        
        return {
            "job_id": job_id,
            "message": "Results deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting results for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete results: {str(e)}"
        )
