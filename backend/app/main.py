"""
FastAPI application for Real-Time Street Parking Detection
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import uvicorn
import re
from pathlib import Path

from app.api.v1.api import api_router
from app.core.config import settings
from app.utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Real-Time Street Parking Detection API",
    description="API for processing parking detection videos using OpenCV and YOLO",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware with flexible localhost support
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://real-time-street-parking-1.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Include API router
app.include_router(api_router, prefix="/api/v1")

# Ensure processed directory exists
processed_dir = Path(settings.PROCESSED_DIR)
processed_dir.mkdir(exist_ok=True)

# Mount static files for serving processed videos
app.mount("/static", StaticFiles(directory=settings.PROCESSED_DIR), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Real-Time Street Parking Detection API")
    
    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    os.makedirs("assets/models", exist_ok=True)
    
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"Processed directory: {settings.PROCESSED_DIR}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down Real-Time Street Parking Detection API")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real-Time Street Parking Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "parking-detection-api",
        "version": "1.0.0"
    }


@app.get("/debug/files")
async def debug_files():
    """Debug endpoint to list available static files"""
    try:
        processed_dir = Path(settings.PROCESSED_DIR)
        if not processed_dir.exists():
            return {"error": "Processed directory does not exist"}

        files = []
        total_size = 0
        for file_path in processed_dir.iterdir():
            if file_path.is_file():
                file_size = file_path.stat().st_size
                total_size += file_size

                # Check if it's a video file
                is_video = file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']

                # For video files, try to get additional info
                video_info = None
                if is_video:
                    try:
                        import cv2
                        cap = cv2.VideoCapture(str(file_path))
                        if cap.isOpened():
                            video_info = {
                                "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                                "fps": cap.get(cv2.CAP_PROP_FPS),
                                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                                "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0
                            }
                            cap.release()
                    except Exception as e:
                        video_info = {"error": str(e)}

                files.append({
                    "name": file_path.name,
                    "size": file_size,
                    "size_mb": round(file_size / 1024 / 1024, 2),
                    "url": f"/static/{file_path.name}",
                    "is_video": is_video,
                    "video_info": video_info,
                    "modified": file_path.stat().st_mtime
                })

        return {
            "processed_directory": str(processed_dir.absolute()),
            "file_count": len(files),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "files": sorted(files, key=lambda x: x["modified"], reverse=True)  # Most recent first
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/debug/video/{job_id}")
async def debug_video(job_id: str):
    """Debug endpoint to check specific video file"""
    try:
        processed_dir = Path(settings.PROCESSED_DIR)
        video_path = processed_dir / f"{job_id}_processed.mp4"

        if not video_path.exists():
            return {
                "error": f"Video file not found: {video_path}",
                "job_id": job_id,
                "expected_path": str(video_path),
                "directory_exists": processed_dir.exists(),
                "directory_contents": [f.name for f in processed_dir.iterdir()] if processed_dir.exists() else []
            }

        # Get file info
        file_stat = video_path.stat()

        # Test video accessibility
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        video_readable = cap.isOpened()

        video_info = {}
        if video_readable:
            video_info = {
                "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "fps": cap.get(cv2.CAP_PROP_FPS),
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0
            }
        cap.release()

        return {
            "job_id": job_id,
            "file_exists": True,
            "file_path": str(video_path),
            "file_size": file_stat.st_size,
            "file_size_mb": round(file_stat.st_size / 1024 / 1024, 2),
            "video_readable": video_readable,
            "video_info": video_info,
            "api_video_url": f"/api/v1/video/{job_id}",
            "static_url": f"/static/{job_id}_processed.mp4",
            "modified_time": file_stat.st_mtime
        }
    except Exception as e:
        return {"error": str(e), "job_id": job_id}


@app.get("/debug/recent-jobs")
async def debug_recent_jobs():
    """Debug endpoint to show recent processing jobs"""
    try:
        processed_dir = Path(settings.PROCESSED_DIR)

        # Get all processed video files
        video_files = list(processed_dir.glob("*_processed.mp4"))

        # Sort by modification time (most recent first)
        video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        recent_jobs = []
        for video_file in video_files[:10]:  # Show last 10 jobs
            job_id = video_file.stem.replace("_processed", "")
            file_stat = video_file.stat()

            recent_jobs.append({
                "job_id": job_id,
                "filename": video_file.name,
                "size_mb": round(file_stat.st_size / 1024 / 1024, 2),
                "modified_time": file_stat.st_mtime,
                "api_video_url": f"/api/v1/video/{job_id}",
                "static_url": f"/static/{job_id}_processed.mp4"
            })

        return {
            "total_processed_videos": len(video_files),
            "recent_jobs": recent_jobs
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/v1/video/{job_id}")
@app.head("/api/v1/video/{job_id}")
async def serve_processed_video(job_id: str, request: Request):
    """Serve processed video file with proper streaming support"""
    try:
        logger.info(f"🎬 Video request for job: {job_id}")
        logger.info(f"🎬 Request headers: {dict(request.headers)}")

        processed_dir = Path(settings.PROCESSED_DIR)

        # Try different video formats that the processor might have created
        video_formats = [
            (".mp4", "video/mp4"),
            (".avi", "video/x-msvideo"),
            (".mov", "video/quicktime"),
            (".wmv", "video/x-ms-wmv")
        ]

        video_path = None
        media_type = "video/mp4"

        for ext, mime_type in video_formats:
            potential_path = processed_dir / f"{job_id}_processed{ext}"
            logger.info(f"🎬 🔍 Checking for video file: {potential_path}")
            logger.info(f"🎬 🔍 File exists: {potential_path.exists()}")

            if potential_path.exists() and potential_path.is_file():
                # Verify file is not empty and is readable
                try:
                    file_size = potential_path.stat().st_size
                    logger.info(f"🎬 📏 File size: {file_size} bytes")
                    if file_size > 0:
                        video_path = potential_path
                        media_type = mime_type
                        logger.info(f"🎬 ✅ Found processed video: {video_path} ({file_size} bytes)")
                        break
                    else:
                        logger.warning(f"🎬 ⚠️ Video file is empty: {potential_path}")
                except Exception as e:
                    logger.warning(f"🎬 ⚠️ Error checking video file {potential_path}: {e}")
                    continue
            else:
                logger.info(f"🎬 ❌ File not found: {potential_path}")

        if not video_path:
            logger.warning(f"🎬 ❌ No processed video found for job {job_id} in any format")

            # List available files for debugging
            available_files = list(processed_dir.glob(f"{job_id}*"))
            logger.warning(f"🎬 Available files for job {job_id}: {[f.name for f in available_files]}")

            # Check if job exists in processing system
            from app.core.dependencies import get_video_processor
            video_processor = get_video_processor()
            job_status = await video_processor.get_job_status(job_id)

            if job_status:
                status = job_status.get('status', 'unknown')
                logger.warning(f"🎬 Job {job_id} exists with status: {status}")
                if status == 'processing':
                    raise HTTPException(status_code=202, detail=f"Video for job {job_id} is still processing")
                elif status == 'failed':
                    raise HTTPException(status_code=500, detail=f"Video processing failed for job {job_id}")
                else:
                    raise HTTPException(status_code=404, detail=f"Processed video for job {job_id} not found")
            else:
                logger.warning(f"🎬 Job {job_id} not found in processing system")
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        # Get file size
        file_size = video_path.stat().st_size

        # Handle range requests for video streaming
        range_header = request.headers.get('range')

        if range_header:
            # Parse range header
            range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2)) if range_match.group(2) else file_size - 1

                # Ensure end doesn't exceed file size
                end = min(end, file_size - 1)
                content_length = end - start + 1

                # Read the requested range
                with open(video_path, 'rb') as f:
                    f.seek(start)
                    data = f.read(content_length)

                from fastapi.responses import Response
                return Response(
                    content=data,
                    status_code=206,
                    headers={
                        "Content-Range": f"bytes {start}-{end}/{file_size}",
                        "Accept-Ranges": "bytes",
                        "Content-Length": str(content_length),
                        "Content-Type": media_type,
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                        "Access-Control-Allow-Headers": "Range, Content-Range, Content-Length, Content-Type",
                        "Cache-Control": "public, max-age=3600"
                    }
                )

        # No range request - serve full file
        from fastapi.responses import FileResponse
        return FileResponse(
            path=str(video_path),
            media_type=media_type,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Disposition": f"inline; filename={video_path.name}",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Access-Control-Allow-Headers": "Range, Content-Range, Content-Length, Content-Type",
                "Cache-Control": "public, max-age=3600"
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error serving video {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while serving video")


@app.options("/api/v1/video/{job_id}")
async def video_options(job_id: str):
    """Handle CORS preflight for video endpoint"""
    from fastapi.responses import Response
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "Range, Content-Range, Content-Length, Content-Type",
            "Access-Control-Max-Age": "3600"
        }
    )


@app.get("/api/v1/thumbnail/{job_id}")
@app.head("/api/v1/thumbnail/{job_id}")
async def serve_thumbnail(job_id: str):
    """Serve thumbnail image"""
    try:
        processed_dir = Path(settings.PROCESSED_DIR)
        thumbnail_path = processed_dir / f"{job_id}_thumbnail.jpg"

        if not thumbnail_path.exists():
            raise HTTPException(status_code=404, detail="Thumbnail not found")

        from fastapi.responses import FileResponse

        return FileResponse(
            path=str(thumbnail_path),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"inline; filename={job_id}_thumbnail.jpg",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Cache-Control": "public, max-age=3600"
            }
        )
    except Exception as e:
        logger.error(f"Error serving thumbnail {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Error serving thumbnail")


@app.get("/debug/detection")
async def debug_detection():
    """Debug endpoint to check detection system status"""
    try:
        from app.core.dependencies import get_video_processor

        video_processor = get_video_processor()

        # Check YOLO model status
        yolo_status = {
            "model_loaded": video_processor._model_loaded,
            "yolo_detector_exists": video_processor.yolo_detector is not None,
        }

        if video_processor.yolo_detector and video_processor.yolo_detector.model:
            yolo_status.update({
                "model_type": str(type(video_processor.yolo_detector.model)),
                "class_names_count": len(video_processor.yolo_detector.class_names) if video_processor.yolo_detector.class_names else 0,
                "device": video_processor.yolo_detector.device
            })

        # Check configuration
        from app.core.config import settings
        config_status = {
            "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
            "iou_threshold": settings.IOU_THRESHOLD,
            "vehicle_classes": settings.VEHICLE_CLASSES,
            "enable_real_processing": settings.ENABLE_REAL_PROCESSING,
            "debug_mode": getattr(settings, 'DEBUG_MODE', False)
        }

        # Check recent jobs
        recent_jobs = {}
        for job_id, job_info in list(video_processor.jobs.items())[-5:]:  # Last 5 jobs
            recent_jobs[job_id] = {
                "status": job_info.get("status"),
                "progress": job_info.get("progress"),
                "error_message": job_info.get("error_message")
            }

        return {
            "yolo_status": yolo_status,
            "config_status": config_status,
            "recent_jobs": recent_jobs,
            "system_status": "ready" if video_processor._model_loaded else "not_ready"
        }
    except Exception as e:
        return {"error": str(e)}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
