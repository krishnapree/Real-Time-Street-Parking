"""
Processing status endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.models.video import ProcessingStatus, JobStatus
from app.utils.logger import setup_logger

# Setup router and logger
router = APIRouter()
logger = setup_logger(__name__)

# Import dependency
from app.core.dependencies import get_video_processor


@router.get("/{job_id}")
async def get_processing_status(job_id: str):
    video_processor = get_video_processor()
    """
    Get processing status for a specific job

    Args:
        job_id: Job identifier

    Returns:
        Processing status information
    """
    try:
        logger.info(f"Getting status for job: {job_id}")
        logger.info(f"Available jobs: {list(video_processor.jobs.keys())}")

        status = await video_processor.get_job_status(job_id)

        if not status:
            logger.warning(f"Job {job_id} not found in {len(video_processor.jobs)} jobs")
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )

        logger.info(f"Found job {job_id} with status: {status.get('status', 'unknown')}")

        # Ensure status is a proper dictionary with all required fields
        return {
            "job_id": status.get("job_id", job_id),
            "status": status.get("status", "unknown"),
            "progress": status.get("progress", 0.0),
            "current_frame": status.get("current_frame"),
            "total_frames": status.get("total_frames"),
            "estimated_time_remaining": status.get("estimated_time_remaining"),
            "created_at": status.get("created_at"),
            "started_at": status.get("started_at"),
            "completed_at": status.get("completed_at"),
            "error_message": status.get("error_message")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get processing status: {str(e)}"
        )


@router.get("/debug")
async def debug_jobs():
    """Debug endpoint to see all jobs"""
    video_processor = get_video_processor()
    return {
        "total_jobs": len(video_processor.jobs),
        "job_ids": list(video_processor.jobs.keys()),
        "jobs": {k: {"status": v.get("status", "unknown"), "progress": v.get("progress", 0.0)} for k, v in video_processor.jobs.items()}
    }

@router.get("/", response_model=List[ProcessingStatus])
async def get_all_processing_status(
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of jobs to return")
):
    """
    Get processing status for all jobs

    Args:
        status: Optional status filter
        limit: Maximum number of jobs to return

    Returns:
        List of processing status information
    """
    video_processor = get_video_processor()
    try:
        all_status = await video_processor.get_all_job_status()
        
        # Filter by status if provided
        if status:
            all_status = [s for s in all_status if s.get("status") == status]

        # Apply limit
        all_status = all_status[:limit]

        # Ensure all status objects have proper structure
        formatted_status = []
        for s in all_status:
            formatted_status.append({
                "job_id": s.get("job_id", ""),
                "status": s.get("status", "unknown"),
                "progress": s.get("progress", 0.0),
                "current_frame": s.get("current_frame"),
                "total_frames": s.get("total_frames"),
                "estimated_time_remaining": s.get("estimated_time_remaining"),
                "created_at": s.get("created_at"),
                "started_at": s.get("started_at"),
                "completed_at": s.get("completed_at"),
                "error_message": s.get("error_message")
            })

        return formatted_status
        
    except Exception as e:
        logger.error(f"Error getting all job status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get processing status: {str(e)}"
        )


@router.post("/{job_id}/cancel")
async def cancel_processing(job_id: str):
    """
    Cancel a processing job

    Args:
        job_id: Job identifier

    Returns:
        Cancellation confirmation
    """
    video_processor = get_video_processor()
    try:
        success = await video_processor.cancel_job(job_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found or cannot be cancelled"
            )
        
        logger.info(f"Job {job_id} cancelled successfully")
        
        return {
            "job_id": job_id,
            "message": "Job cancelled successfully",
            "status": "cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel job: {str(e)}"
        )


@router.post("/{job_id}/retry")
async def retry_processing(job_id: str):
    """
    Retry a failed processing job
    
    Args:
        job_id: Job identifier
        
    Returns:
        Retry confirmation
    """
    try:
        # Retry not implemented yet
        success = False
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found or cannot be retried"
            )
        
        logger.info(f"Job {job_id} retry initiated successfully")
        
        return {
            "job_id": job_id,
            "message": "Job retry initiated successfully",
            "status": "pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retry job: {str(e)}"
        )


@router.get("/{job_id}/logs")
async def get_processing_logs(
    job_id: str,
    lines: int = Query(100, ge=1, le=1000, description="Number of log lines to return")
):
    """
    Get processing logs for a specific job
    
    Args:
        job_id: Job identifier
        lines: Number of log lines to return
        
    Returns:
        Processing logs
    """
    try:
        # Logs not implemented yet
        logs = None
        
        if logs is None:
            raise HTTPException(
                status_code=404,
                detail=f"Logs for job {job_id} not found"
            )
        
        return {
            "job_id": job_id,
            "logs": logs,
            "lines_returned": len(logs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting logs for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get processing logs: {str(e)}"
        )
