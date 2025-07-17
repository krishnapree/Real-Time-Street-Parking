"""
COMPLETELY REWRITTEN Video Processing Service - Production Ready
"""

import asyncio
import cv2
import numpy as np
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import uuid
import logging
import json

from app.core.config import settings
from app.services.yolo_detector import YOLODetector
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class VideoProcessor:
    """Production-ready video processor with guaranteed overlay functionality"""
    
    def __init__(self):
        self.jobs: Dict[str, dict] = {}
        self.results: Dict[str, dict] = {}
        self.yolo_detector = YOLODetector()
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        self._model_loaded = False

        # Ensure results directory exists
        self.results_dir = Path(settings.PROCESSED_DIR) / "results"
        self.results_dir.mkdir(exist_ok=True)
    
    def initialize(self):
        """Initialize the video processor with comprehensive validation"""
        try:
            if not self._model_loaded:
                logger.info("🚀 Initializing YOLO detector...")
                success = self.yolo_detector.load_model()
                if success:
                    self._model_loaded = True
                    logger.info("✅ Video processor initialized successfully")

                    # CRITICAL: Test the complete pipeline
                    self._test_detection_pipeline()
                else:
                    logger.error("❌ Failed to load YOLO model")
                    raise RuntimeError("Failed to initialize YOLO model")
        except Exception as e:
            logger.error(f"❌ Error initializing video processor: {str(e)}")
            raise

    def _test_detection_pipeline(self):
        """Test the complete detection pipeline with a synthetic frame"""
        try:
            logger.info("🧪 Testing detection pipeline...")

            # Create a test frame with some basic shapes
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # Add some colored rectangles to simulate vehicles
            cv2.rectangle(test_frame, (100, 100), (200, 200), (255, 0, 0), -1)  # Blue rectangle
            cv2.rectangle(test_frame, (300, 200), (450, 350), (0, 255, 0), -1)  # Green rectangle
            cv2.rectangle(test_frame, (500, 50), (600, 150), (0, 0, 255), -1)   # Red rectangle

            # Test YOLO detection
            detections = self.yolo_detector.detect_objects(test_frame)
            logger.info(f"🧪 Test detection returned {len(detections)} objects")

            # Test vehicle filtering
            vehicle_detections = self.yolo_detector.filter_vehicle_detections(detections)
            logger.info(f"🧪 Test vehicle filtering returned {len(vehicle_detections)} vehicles")

            # Test overlay drawing
            parking_spaces = self._create_parking_grid(640, 480)
            occupied_spaces = []
            frame_analysis = {
                'frame_number': 0,
                'timestamp': 0.0,
                'vehicle_detections': len(vehicle_detections),
                'total_spaces': len(parking_spaces),
                'occupied_spaces': 0,
                'available_spaces': len(parking_spaces),
                'occupancy_rate': 0.0
            }

            overlay_frame = self._draw_guaranteed_overlay(
                test_frame, parking_spaces, occupied_spaces,
                [{'class_name': 'test', 'confidence': 0.9, 'bbox': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}}],
                frame_analysis
            )

            if overlay_frame is not None:
                logger.info("🧪 ✅ Overlay drawing test successful")
            else:
                logger.error("🧪 ❌ Overlay drawing test failed")

            logger.info("🧪 ✅ Detection pipeline test completed")

        except Exception as e:
            logger.error(f"🧪 ❌ Detection pipeline test failed: {e}")
            import traceback
            logger.error(f"🧪 ❌ Traceback: {traceback.format_exc()}")

    def _save_results_to_disk(self, job_id: str, results: dict, job_status: dict):
        """Save results and job status to disk for persistence"""
        try:
            # Save results
            results_file = self.results_dir / f"{job_id}_results.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)

            # Save job status
            status_file = self.results_dir / f"{job_id}_status.json"
            with open(status_file, 'w') as f:
                json.dump(job_status, f, indent=2)

            logger.info(f"💾 Saved results to disk for job {job_id}")

        except Exception as e:
            logger.error(f"💾 Failed to save results to disk for job {job_id}: {e}")

    def _load_results_from_disk(self, job_id: str) -> tuple[dict, dict]:
        """Load results and job status from disk"""
        try:
            results_file = self.results_dir / f"{job_id}_results.json"
            status_file = self.results_dir / f"{job_id}_status.json"

            results = None
            job_status = None

            if results_file.exists():
                with open(results_file, 'r') as f:
                    results = json.load(f)

            if status_file.exists():
                with open(status_file, 'r') as f:
                    job_status = json.load(f)

            if results and job_status:
                logger.info(f"💾 Loaded results from disk for job {job_id}")
                return results, job_status

        except Exception as e:
            logger.error(f"💾 Failed to load results from disk for job {job_id}: {e}")

        return None, None

    def _get_parking_space_polygons(self, width: int, height: int) -> List[Dict]:
        """
        Get parking space polygons scaled to frame dimensions
        Based on the polygon coordinates from your example code
        """
        # Base coordinates from your example (for 1020x500 resolution)
        base_width = 1020
        base_height = 500

        # Scale factors
        scale_x = width / base_width
        scale_y = height / base_height

        # Original polygon coordinates from your code
        base_polygons = [
            [(52,364),(30,417),(73,412),(88,369)],    # Space 1
            [(105,353),(86,428),(137,427),(146,358)], # Space 2
            [(159,354),(150,427),(204,425),(203,353)], # Space 3
            [(217,352),(219,422),(273,418),(261,347)], # Space 4
            [(274,345),(286,417),(338,415),(321,345)], # Space 5
            [(336,343),(357,410),(409,408),(382,340)], # Space 6
            [(396,338),(426,404),(479,399),(439,334)], # Space 7
            [(458,333),(494,397),(543,390),(495,330)], # Space 8
            [(511,327),(557,388),(603,383),(549,324)], # Space 9
            [(564,323),(615,381),(654,372),(596,315)], # Space 10
            [(616,316),(666,369),(703,363),(642,312)], # Space 11
            [(674,311),(730,360),(764,355),(707,308)]  # Space 12
        ]

        # Label positions for each space (scaled)
        base_label_positions = [
            (50,441), (106,440), (175,436), (250,436), (315,429), (386,421),
            (456,414), (527,406), (591,398), (649,384), (697,377), (752,371)
        ]

        parking_spaces = []

        for i, base_polygon in enumerate(base_polygons):
            # Scale polygon coordinates
            scaled_polygon = []
            for x, y in base_polygon:
                scaled_x = int(x * scale_x)
                scaled_y = int(y * scale_y)
                scaled_polygon.append((scaled_x, scaled_y))

            # Scale label position
            label_x = int(base_label_positions[i][0] * scale_x)
            label_y = int(base_label_positions[i][1] * scale_y)

            space = {
                'id': i + 1,
                'polygon': scaled_polygon,
                'label_position': (label_x, label_y),
                'occupied': False,
                'vehicle_count': 0,
                'vehicles': []
            }
            parking_spaces.append(space)

        logger.info(f"🅿️ Created {len(parking_spaces)} polygon-based parking spaces for {width}x{height} resolution")
        return parking_spaces

    def _analyze_polygon_occupancy(self, parking_spaces: List[Dict], vehicles: List[Dict]) -> List[Dict]:
        """
        Analyze parking space occupancy using polygon-based detection
        Similar to your example code logic
        """
        occupied_spaces = []

        for space in parking_spaces:
            # Reset space data
            space['occupied'] = False
            space['vehicle_count'] = 0
            space['vehicles'] = []

            # Get polygon as numpy array
            polygon = np.array(space['polygon'], np.int32)

            # Check each vehicle
            for vehicle in vehicles:
                bbox = vehicle['bbox']

                # Calculate vehicle center point (like in your code)
                cx = int((bbox['x1'] + bbox['x2']) // 2)
                cy = int((bbox['y1'] + bbox['y2']) // 2)

                # Use cv2.pointPolygonTest to check if vehicle center is inside polygon
                result = cv2.pointPolygonTest(polygon, (cx, cy), False)

                if result >= 0:  # Point is inside or on the polygon
                    space['vehicles'].append(vehicle)
                    space['vehicle_count'] += 1

            # Mark space as occupied if any vehicles are detected
            if space['vehicle_count'] > 0:
                space['occupied'] = True
                occupied_spaces.append(space)

        logger.debug(f"🅿️ Polygon analysis: {len(occupied_spaces)}/{len(parking_spaces)} spaces occupied")
        return occupied_spaces

    async def create_processing_job(self, video_path: Path, config=None) -> str:
        """Create a new processing job"""
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0.0,
            "current_frame": 0,
            "total_frames": 0,
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error_message": None
        }
        
        # Start processing task
        task = asyncio.create_task(self.process_video_real(job_id, video_path, config))
        self.processing_tasks[job_id] = task
        
        return job_id

    async def process_video_real(self, job_id: str, video_path: Path, config):
        """Process video with guaranteed overlay functionality"""
        start_time = time.time()

        try:
            # Update job status with detailed logging
            self.jobs[job_id]["status"] = "processing"
            self.jobs[job_id]["started_at"] = datetime.utcnow().isoformat()
            logger.info(f"🎬 Job {job_id} status updated to 'processing'")

            logger.info(f"🎬 Starting PRODUCTION video processing for job {job_id}")
            logger.info(f"📁 Video path: {video_path}")
            logger.info(f"📁 Video exists: {video_path.exists()}")
            logger.info(f"📁 Video size: {video_path.stat().st_size if video_path.exists() else 'N/A'} bytes")

            # Ensure YOLO model is loaded with detailed logging
            if not self._model_loaded:
                logger.info("🤖 YOLO model not loaded, initializing...")
                try:
                    self.initialize()
                    logger.info(f"🤖 YOLO model initialization result: {self._model_loaded}")
                except Exception as init_error:
                    logger.error(f"🤖 YOLO model initialization failed: {init_error}")
                    raise ValueError(f"Failed to load YOLO model: {init_error}")

                if not self._model_loaded:
                    logger.error("🤖 YOLO model still not loaded after initialization")
                    raise ValueError("Failed to load YOLO model - model_loaded flag is False")
            else:
                logger.info("🤖 YOLO model already loaded")

            # Open video with detailed error handling
            logger.info(f"📹 Attempting to open video: {video_path}")
            cap = cv2.VideoCapture(str(video_path))

            if not cap.isOpened():
                error_msg = f"Cannot open video file: {video_path}. File may be corrupted or in unsupported format."
                logger.error(f"📹 {error_msg}")
                raise ValueError(error_msg)

            logger.info("📹 Video opened successfully")

            # Get video properties with validation
            fps = cap.get(cv2.CAP_PROP_FPS)
            original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            logger.info(f"📊 Video Properties:")
            logger.info(f"   - Resolution: {original_width}x{original_height}")
            logger.info(f"   - FPS: {fps}")
            logger.info(f"   - Total frames: {total_frames}")
            logger.info(f"   - Duration: {total_frames/fps:.2f} seconds" if fps > 0 else "   - Duration: Unknown (FPS is 0)")

            # Validate video properties
            if fps <= 0:
                logger.warning("⚠️ Invalid FPS detected, using default value of 30")
                fps = 30.0

            if total_frames <= 0:
                logger.warning("⚠️ Invalid frame count detected")

            if original_width <= 0 or original_height <= 0:
                error_msg = f"Invalid video dimensions: {original_width}x{original_height}"
                logger.error(f"📊 {error_msg}")
                raise ValueError(error_msg)

            # CRITICAL: Scale down very high resolution videos for processing
            max_dimension = 1920  # Max 1080p for processing
            scale_factor = 1.0

            if original_width > max_dimension or original_height > max_dimension:
                scale_factor = min(max_dimension / original_width, max_dimension / original_height)
                width = int(original_width * scale_factor)
                height = int(original_height * scale_factor)
                logger.info(f"📊 Scaling video from {original_width}x{original_height} to {width}x{height} (factor: {scale_factor:.2f})")
            else:
                width = original_width
                height = original_height
                logger.info(f"📊 Using original resolution: {width}x{height}")

            self.jobs[job_id]["total_frames"] = total_frames

            # Create output video writer with robust codec fallback
            output_dir = Path(settings.PROCESSED_DIR)
            output_dir.mkdir(exist_ok=True)

            # Try different output formats if MP4 fails
            output_formats = [
                (f"{job_id}_processed.mp4", "MP4"),
                (f"{job_id}_processed.avi", "AVI"),
                (f"{job_id}_processed.mov", "MOV"),
                (f"{job_id}_processed.wmv", "WMV"),
            ]

            # Try different combinations of formats and codecs
            out = None
            successful_codec = None
            output_path = None

            for output_filename, format_name in output_formats:
                current_output_path = output_dir / output_filename
                logger.info(f"🎬 Trying {format_name} format: {output_filename}")

                # Browser-compatible codec selection for each format
                if format_name == "MP4":
                    codecs_to_try = [
                        # H.264 codecs (browser-compatible)
                        ('H264', cv2.VideoWriter_fourcc(*'H264')),
                        ('avc1', cv2.VideoWriter_fourcc(*'avc1')),
                        ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),
                        # Fallback codecs
                        ('XVID', cv2.VideoWriter_fourcc(*'XVID')),
                        ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),
                    ]
                elif format_name == "AVI":
                    codecs_to_try = [
                        ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),
                        ('XVID', cv2.VideoWriter_fourcc(*'XVID')),
                        ('DIVX', cv2.VideoWriter_fourcc(*'DIVX')),
                    ]
                elif format_name == "MOV":
                    codecs_to_try = [
                        ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),
                        ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),
                    ]
                else:  # WMV
                    codecs_to_try = [
                        ('WMV1', cv2.VideoWriter_fourcc(*'WMV1')),
                        ('WMV2', cv2.VideoWriter_fourcc(*'WMV2')),
                        ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),
                    ]

                for codec_name, fourcc in codecs_to_try:
                    logger.info(f"  🔧 Trying {codec_name} codec with {format_name}")

                    try:
                        # Create video writer
                        out = cv2.VideoWriter(str(current_output_path), fourcc, fps, (width, height))

                        # Test if it's actually working
                        if out.isOpened():
                            try:
                                test_frame = np.zeros((height, width, 3), dtype=np.uint8)
                                out.write(test_frame)
                                # If we get here without exception, it worked
                                logger.info(f"✅ SUCCESS: {codec_name} + {format_name}")
                                successful_codec = f"{codec_name}+{format_name}"
                                output_path = current_output_path
                                break
                            except Exception as write_test_error:
                                logger.warning(f"❌ Test write failed: {codec_name} + {format_name} - {write_test_error}")
                                out.release()
                                out = None
                        else:
                            logger.warning(f"❌ Failed to open: {codec_name} + {format_name}")
                            if out:
                                out.release()
                                out = None

                    except Exception as codec_error:
                        logger.warning(f"❌ Exception: {codec_name} + {format_name}: {codec_error}")
                        if out:
                            out.release()
                            out = None

                # If we found a working combination, break out of format loop
                if out and out.isOpened():
                    break

            if out is None or not out.isOpened():
                # ULTIMATE FALLBACK: Force MP4 with browser-compatible codec
                logger.error("❌ All video codecs failed - trying browser-compatible fallbacks")

                output_path = output_dir / f"{job_id}_processed.mp4"

                # Try browser-compatible codecs as fallback
                fallback_codecs = [
                    ('H264', cv2.VideoWriter_fourcc(*'H264')),
                    ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),
                    ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),  # Last resort
                ]

                for codec_name, fourcc in fallback_codecs:
                    logger.error(f"❌ Trying fallback codec: {codec_name}")
                    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

                    if out.isOpened():
                        successful_codec = f"{codec_name}+MP4 (fallback)"
                        break

                    # Try with lower FPS if codec fails
                    logger.error(f"❌ {codec_name} failed, trying with lower FPS")
                    out = cv2.VideoWriter(str(output_path), fourcc, min(fps, 15.0), (width, height))

                    if out.isOpened():
                        successful_codec = f"{codec_name}+MP4 (fallback, low FPS)"
                        break

                if not out.isOpened():
                    raise RuntimeError("Failed to create video writer with any codec, including fallbacks")
                use_image_sequence = False
            else:
                use_image_sequence = False

            logger.info(f"🎬 Final video writer: {successful_codec}, {width}x{height} resolution")

            logger.info(f"📹 Output: {output_path}")

            # Create parking spaces using polygon-based detection
            parking_spaces = self._get_parking_space_polygons(width, height)
            logger.info(f"🅿️ Created {len(parking_spaces)} polygon-based parking spaces")

            # Process frames
            frame_results = []
            frame_number = 0
            frames_analyzed = 0
            
            # Cache for skipped frames
            last_vehicles = []
            last_occupied = []
            last_analysis = None

            logger.info("🎬 Starting frame processing...")
            logger.info(f"🎬 Will analyze every 5th frame for performance")

            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.info(f"🎬 End of video reached at frame {frame_number}")
                    break

                # CRITICAL: Scale frame if needed
                if scale_factor != 1.0:
                    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
                    logger.debug(f"🎬 Scaled frame {frame_number} to {width}x{height}")

                # Update progress with detailed logging
                progress = (frame_number / total_frames) * 100 if total_frames > 0 else 0
                self.jobs[job_id]["progress"] = progress
                self.jobs[job_id]["current_frame"] = frame_number

                # Log progress every 100 frames
                if frame_number % 100 == 0:
                    logger.info(f"🎬 Processing frame {frame_number}/{total_frames} ({progress:.1f}%)")

                # Analyze every 5th frame for performance
                should_analyze = (frame_number % 5 == 0)

                if should_analyze:
                    logger.debug(f"🎬 Analyzing frame {frame_number}")
                else:
                    logger.debug(f"🎬 Skipping analysis for frame {frame_number}")

                if should_analyze:
                    frames_analyzed += 1

                    # CRITICAL: Validate frame before YOLO detection
                    if frame is None:
                        logger.error(f"🎬 Frame {frame_number} is None!")
                        continue

                    if frame.size == 0:
                        logger.error(f"🎬 Frame {frame_number} is empty!")
                        continue

                    # Log frame properties for debugging
                    logger.debug(f"🎬 Frame {frame_number}: shape={frame.shape}, dtype={frame.dtype}, size={frame.size}")

                    # YOLO detection with comprehensive error handling
                    try:
                        logger.debug(f"🤖 Running YOLO detection on frame {frame_number}")
                        detections = self.yolo_detector.detect_objects(frame)
                        logger.debug(f"🤖 YOLO returned {len(detections)} detections for frame {frame_number}")

                        if len(detections) == 0:
                            logger.debug(f"🤖 No objects detected in frame {frame_number}")

                        vehicle_detections = self.yolo_detector.filter_vehicle_detections(detections)
                        logger.debug(f"🚗 Filtered to {len(vehicle_detections)} vehicle detections")

                        if len(vehicle_detections) == 0:
                            logger.debug(f"🚗 No vehicles detected in frame {frame_number}")

                    except Exception as e:
                        logger.error(f"🤖 YOLO detection failed for frame {frame_number}: {e}")
                        detections = []
                        vehicle_detections = []

                    # Convert to dict format
                    vehicles = []
                    for det in vehicle_detections:
                        vehicles.append({
                            'class_name': det.class_name,
                            'confidence': det.confidence,
                            'bbox': {
                                'x1': float(det.bbox.x1),
                                'y1': float(det.bbox.y1),
                                'x2': float(det.bbox.x2),
                                'y2': float(det.bbox.y2)
                            }
                        })

                    # Analyze occupancy using polygon-based detection
                    occupied_spaces = self._analyze_polygon_occupancy(parking_spaces, vehicles)

                    # Create frame analysis
                    frame_analysis = {
                        'frame_number': frame_number,
                        'timestamp': frame_number / fps,
                        'vehicle_detections': len(vehicles),
                        'total_spaces': len(parking_spaces),
                        'occupied_spaces': len(occupied_spaces),
                        'available_spaces': len(parking_spaces) - len(occupied_spaces),
                        'occupancy_rate': len(occupied_spaces) / len(parking_spaces) if parking_spaces else 0
                    }

                    frame_results.append(frame_analysis)

                    # Cache for next frames
                    last_vehicles = vehicles
                    last_occupied = occupied_spaces
                    last_analysis = frame_analysis
                else:
                    # Use cached data
                    vehicles = last_vehicles
                    occupied_spaces = last_occupied
                    frame_analysis = last_analysis.copy() if last_analysis else {
                        'frame_number': frame_number,
                        'timestamp': frame_number / fps,
                        'vehicle_detections': 0,
                        'total_spaces': len(parking_spaces),
                        'occupied_spaces': 0,
                        'available_spaces': len(parking_spaces),
                        'occupancy_rate': 0
                    }
                    frame_analysis['frame_number'] = frame_number
                    frame_analysis['timestamp'] = frame_number / fps

                # CRITICAL: Draw overlay on EVERY frame
                overlay_frame = self._draw_guaranteed_overlay(
                    frame, parking_spaces, occupied_spaces, vehicles, frame_analysis
                )

                # CRITICAL: Verify overlay was applied
                if overlay_frame is None:
                    logger.error(f"🎨 CRITICAL: Overlay returned None for frame {frame_number}")
                    overlay_frame = frame
                else:
                    # Quick check if overlay was applied
                    if not np.array_equal(frame, overlay_frame):
                        logger.debug(f"🎨 ✅ Overlay applied to frame {frame_number}")
                    else:
                        logger.warning(f"🎨 ⚠️ Overlay identical to original frame {frame_number}")

                # CRITICAL: Ultra-robust frame output (video or image sequence)
                write_success = False
                frame_to_write = None

                try:
                    # Step 1: Validate and prepare overlay frame
                    if overlay_frame is None:
                        logger.warning(f"🎬 Overlay frame {frame_number} is None, using original")
                        frame_to_write = frame.copy()
                    else:
                        frame_to_write = overlay_frame.copy()

                    # Step 2: Ensure frame has correct properties
                    current_height, current_width = frame_to_write.shape[:2]

                    # Fix dimensions if needed
                    if current_height != height or current_width != width:
                        logger.debug(f"🎬 Resizing frame {frame_number}: {current_width}x{current_height} -> {width}x{height}")
                        frame_to_write = cv2.resize(frame_to_write, (width, height), interpolation=cv2.INTER_AREA)

                    # Fix data type if needed
                    if frame_to_write.dtype != np.uint8:
                        logger.debug(f"🎬 Converting frame {frame_number} from {frame_to_write.dtype} to uint8")
                        frame_to_write = np.clip(frame_to_write, 0, 255).astype(np.uint8)

                    # Ensure 3 channels (BGR)
                    if len(frame_to_write.shape) == 3 and frame_to_write.shape[2] == 3:
                        # Step 3: Write frame (video or image)
                        # Always write to video file (no image sequence mode)
                        if True:
                            # Save to video file
                            if out and out.isOpened():
                                try:
                                    out.write(frame_to_write)
                                    write_success = True
                                    logger.debug(f"🎬 ✅ Successfully wrote frame {frame_number}")
                                except Exception as write_error:
                                    logger.error(f"🎬 ❌ Exception writing frame {frame_number}: {write_error}")
                                    write_success = False
                            else:
                                logger.error(f"🎬 ❌ VideoWriter is not opened for frame {frame_number}")
                                write_success = False
                    else:
                        logger.error(f"🎬 ❌ Invalid frame shape for frame {frame_number}: {frame_to_write.shape}")

                except Exception as e:
                    logger.error(f"🎬 ❌ Exception preparing frame {frame_number}: {e}")

                # Step 4: Fallback attempts if writing failed (only for video mode)
                if not write_success and not use_image_sequence:
                    logger.warning(f"🎬 ⚠️ Attempting video fallback for frame {frame_number}")

                    # Fallback 1: Try original frame
                    try:
                        fallback_frame = frame.copy()
                        if fallback_frame.shape[:2] != (height, width):
                            fallback_frame = cv2.resize(fallback_frame, (width, height))
                        if fallback_frame.dtype != np.uint8:
                            fallback_frame = fallback_frame.astype(np.uint8)

                        if out and out.isOpened():
                            write_success = out.write(fallback_frame)
                            if write_success:
                                logger.info(f"🎬 ✅ Fallback successful for frame {frame_number}")
                            else:
                                logger.error(f"🎬 ❌ Fallback also failed for frame {frame_number}")
                    except Exception as fallback_error:
                        logger.error(f"🎬 ❌ Fallback exception for frame {frame_number}: {fallback_error}")

                # Step 5: Log final status
                if not write_success:
                    output_type = "image" if use_image_sequence else "video frame"
                    logger.error(f"🎬 ❌ CRITICAL: All write attempts failed for {output_type} {frame_number}")
                    # Continue processing but log the failure

                frame_number += 1

                # Log progress
                if frame_number % 100 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"📊 Progress: {progress:.1f}% ({frame_number}/{total_frames}) - {elapsed:.1f}s")

            # Cleanup
            cap.release()
            if out:
                out.release()

            # Handle image sequence mode
            # Video processing complete - no image sequence handling needed

            processing_time = time.time() - start_time

            # Verify output file exists and is valid with retry mechanism
            max_retries = 3
            retry_delay = 1.0  # seconds

            for attempt in range(max_retries):
                if output_path and output_path.exists():
                    file_size = output_path.stat().st_size
                    if file_size > 0:
                        # File exists and has content - success!
                        logger.info(f"✅ Video processing complete: {output_path.name} ({file_size} bytes) in {processing_time:.1f}s")
                        break
                    else:
                        logger.warning(f"⚠️ Output file is empty, attempt {attempt + 1}/{max_retries}")
                else:
                    logger.warning(f"⚠️ Output file not found, attempt {attempt + 1}/{max_retries}: {output_path}")

                if attempt < max_retries - 1:
                    logger.info(f"🔄 Waiting {retry_delay}s before retry...")
                    await asyncio.sleep(retry_delay)
                else:
                    # Final attempt failed
                    if not output_path or not output_path.exists():
                        raise ValueError(f"Output video file was not created after {max_retries} attempts: {output_path}")
                    else:
                        raise ValueError(f"Output video file is empty after {max_retries} attempts: {output_path}")

            # Create comprehensive results with enhanced analytics
            if frame_results:
                occupancy_rates = [f['occupancy_rate'] for f in frame_results]
                occupied_counts = [f['occupied_spaces'] for f in frame_results]
                vehicle_counts = [f['vehicle_detections'] for f in frame_results]
                total_spaces_counts = [f['total_spaces'] for f in frame_results]

                # Calculate comprehensive statistics
                avg_occupancy = sum(occupancy_rates) / len(occupancy_rates)
                max_occupancy = max(occupancy_rates)
                min_occupancy = min(occupancy_rates)
                avg_occupied = sum(occupied_counts) / len(occupied_counts)
                peak_occupied = max(occupied_counts)
                avg_vehicles = sum(vehicle_counts) / len(vehicle_counts)
                max_vehicles = max(vehicle_counts)
                avg_total_spaces = sum(total_spaces_counts) / len(total_spaces_counts)
                avg_available = avg_total_spaces - avg_occupied

                # Calculate occupancy trend
                if len(occupancy_rates) >= 10:
                    first_half = occupancy_rates[:len(occupancy_rates)//2]
                    second_half = occupancy_rates[len(occupancy_rates)//2:]
                    first_avg = sum(first_half) / len(first_half)
                    second_avg = sum(second_half) / len(second_half)

                    if second_avg > first_avg + 0.05:
                        trend = "increasing"
                    elif second_avg < first_avg - 0.05:
                        trend = "decreasing"
                    else:
                        trend = "stable"
                else:
                    trend = "insufficient_data"
            else:
                avg_occupancy = max_occupancy = min_occupancy = 0
                avg_occupied = peak_occupied = avg_vehicles = max_vehicles = 0
                avg_total_spaces = avg_available = 0
                trend = "no_data"

            result = {
                'job_id': job_id,
                'status': 'completed',
                'processing_time': processing_time,
                'frames_analyzed': frames_analyzed,
                'total_frames': total_frames,

                # Enhanced statistics
                'avg_total_spaces': avg_total_spaces,
                'avg_occupied_spaces': avg_occupied,
                'avg_available_spaces': avg_available,
                'avg_occupancy_rate': avg_occupancy,
                'max_occupancy': max_occupancy,
                'min_occupancy': min_occupancy,
                'peak_occupied_spaces': peak_occupied,
                'avg_vehicles_detected': avg_vehicles,
                'max_vehicles_detected': max_vehicles,
                'occupancy_trend': trend,

                # Video information
                'video_info': {
                    'filename': video_path.name,
                    'duration': total_frames / fps,
                    'fps': fps,
                    'width': width,
                    'height': height,
                    'total_frames': total_frames,
                    'file_size': video_path.stat().st_size if video_path.exists() else 0
                },

                # Frame-by-frame results
                'frame_results': frame_results,

                # Output URLs
                'processed_video_url': f"/static/{output_path.name}",
                'thumbnail_url': f"/static/{job_id}_thumbnail.jpg",
                'created_at': datetime.utcnow().isoformat()
            }

            self.results[job_id] = result

            # Update job status
            self.jobs[job_id]["status"] = "completed"
            self.jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
            self.jobs[job_id]["progress"] = 100.0

            # CRITICAL: Save results to disk for persistence
            self._save_results_to_disk(job_id, result, self.jobs[job_id])

            logger.info(f"🎉 Processing completed successfully for job {job_id}")
            return result

        except Exception as e:
            logger.error(f"❌ Error processing video for job {job_id}: {str(e)}")
            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["error_message"] = str(e)
            self.jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
            raise

        finally:
            # Clean up task reference
            if job_id in self.processing_tasks:
                del self.processing_tasks[job_id]



    def _draw_guaranteed_overlay(self, frame, parking_spaces, occupied_spaces, vehicles, frame_analysis):
        """Draw overlay with guaranteed visibility"""
        if frame is None:
            logger.error("🎨 Frame is None")
            return frame

        overlay_frame = frame.copy()
        height, width = overlay_frame.shape[:2]

        logger.debug(f"🎨 Drawing overlay: {len(parking_spaces)} spaces, {len(vehicles)} vehicles")

        try:
            # FORCED VISIBLE ELEMENTS - These MUST appear
            # Large yellow rectangle with text (bottom-left)
            cv2.rectangle(overlay_frame, (10, height-100), (400, height-10), (0, 255, 255), -1)
            cv2.rectangle(overlay_frame, (10, height-100), (400, height-10), (0, 0, 0), 3)
            cv2.putText(overlay_frame, "PRODUCTION OVERLAY ACTIVE", (20, height-70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            cv2.putText(overlay_frame, f"Frame: {frame_analysis['frame_number']}", (20, height-40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

            # Red circle (top-right)
            cv2.circle(overlay_frame, (width-50, 50), 30, (0, 0, 255), -1)
            cv2.circle(overlay_frame, (width-50, 50), 30, (255, 255, 255), 3)

            # Green line (top)
            cv2.line(overlay_frame, (0, 10), (width, 10), (0, 255, 0), 15)

            # Blue line (bottom)
            cv2.line(overlay_frame, (0, height-5), (width, height-5), (255, 0, 0), 10)

            logger.debug("🎨 ✅ Forced overlay elements drawn")

        except Exception as e:
            logger.error(f"🎨 ❌ CRITICAL: Forced overlay failed: {e}")
            return frame

        # Draw polygon-based parking spaces (like your example code)
        for space in parking_spaces:
            try:
                polygon = np.array(space['polygon'], np.int32)
                is_occupied = space['occupied']
                space_id = space['id']
                label_pos = space['label_position']

                # Draw polygon outline - RED if occupied, GREEN if available
                if is_occupied:
                    cv2.polylines(overlay_frame, [polygon], True, (0, 0, 255), 2)  # Red for occupied
                    text_color = (0, 0, 255)  # Red text
                else:
                    cv2.polylines(overlay_frame, [polygon], True, (0, 255, 0), 2)  # Green for available
                    text_color = (255, 255, 255)  # White text

                # Draw space number label
                cv2.putText(overlay_frame, str(space_id), label_pos,
                           cv2.FONT_HERSHEY_COMPLEX, 0.5, text_color, 1)



            except Exception as e:
                logger.error(f"🎨 Error drawing space {space.get('id', 'unknown')}: {e}")

        # Draw vehicles (like in your example code)
        for vehicle in vehicles:
            try:
                bbox = vehicle['bbox']
                x1 = max(0, min(int(bbox['x1']), width - 1))
                y1 = max(0, min(int(bbox['y1']), height - 1))
                x2 = max(0, min(int(bbox['x2']), width - 1))
                y2 = max(0, min(int(bbox['y2']), height - 1))

                if x2 <= x1 or y2 <= y1:
                    continue

                # Draw vehicle bounding box in green (like your example)
                cv2.rectangle(overlay_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Draw center point in red (like your example)
                cx = int((x1 + x2) // 2)
                cy = int((y1 + y2) // 2)
                cv2.circle(overlay_frame, (cx, cy), 3, (0, 0, 255), -1)

                # Add vehicle class label
                class_name = vehicle.get('class_name', 'vehicle')
                cv2.putText(overlay_frame, class_name, (x1, y1),
                           cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)



            except Exception as e:
                logger.error(f"🎨 Error drawing vehicle: {e}")

        # Add available spaces counter (like in your example)
        try:
            total_spaces = len(parking_spaces)
            occupied_count = len([s for s in parking_spaces if s['occupied']])
            available_count = total_spaces - occupied_count

            # Display available spaces counter (like your example shows "space" variable)
            cv2.putText(overlay_frame, str(available_count), (23, 30),
                       cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)

            logger.debug(f"🅿️ Spaces: {available_count}/{total_spaces} available")

        except Exception as e:
            logger.error(f"🎨 Error drawing statistics: {e}")

        # Enhanced statistics overlay (top-left)
        try:
            # Calculate additional statistics
            timestamp = frame_analysis.get('timestamp', 0)
            frame_num = frame_analysis.get('frame_number', 0)

            # Format timestamp
            minutes = int(timestamp // 60)
            seconds = int(timestamp % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"

            stats = [
                "🅿️ REAL-TIME PARKING DETECTION",
                f"📊 Frame: {frame_num} | Time: {time_str}",
                f"🏢 Total Spaces: {frame_analysis['total_spaces']}",
                f"🚗 Occupied: {frame_analysis['occupied_spaces']}",
                f"✅ Available: {frame_analysis['available_spaces']}",
                f"📈 Occupancy Rate: {frame_analysis['occupancy_rate']:.1%}",
                f"🚙 Vehicles Detected: {frame_analysis['vehicle_detections']}"
            ]

            # Calculate overlay size based on content
            max_width = 0
            total_height = 0
            line_heights = []

            for stat in stats:
                (text_width, text_height), _ = cv2.getTextSize(stat, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                max_width = max(max_width, text_width)
                line_heights.append(text_height)
                total_height += text_height + 10  # 10px spacing

            # Overlay dimensions with padding
            overlay_width = max_width + 40
            overlay_height = total_height + 40

            # Position overlay (top-left with margin)
            overlay_x = 15
            overlay_y = 15

            # Draw background with gradient effect
            cv2.rectangle(overlay_frame, (overlay_x, overlay_y),
                         (overlay_x + overlay_width, overlay_y + overlay_height), (0, 0, 0), -1)
            cv2.rectangle(overlay_frame, (overlay_x, overlay_y),
                         (overlay_x + overlay_width, overlay_y + overlay_height), (100, 100, 100), 3)

            # Add inner border
            cv2.rectangle(overlay_frame, (overlay_x + 3, overlay_y + 3),
                         (overlay_x + overlay_width - 3, overlay_y + overlay_height - 3), (200, 200, 200), 1)

            # Draw statistics with color coding
            current_y = overlay_y + 25
            for i, stat in enumerate(stats):
                if i == 0:
                    # Title - bright cyan
                    color = (255, 255, 0)
                    font_scale = 0.7
                    thickness = 2
                elif i == 1:
                    # Frame/time info - white
                    color = (255, 255, 255)
                    font_scale = 0.5
                    thickness = 1
                elif "Occupied" in stat:
                    # Occupied spaces - red
                    color = (0, 0, 255)
                    font_scale = 0.6
                    thickness = 2
                elif "Available" in stat:
                    # Available spaces - green
                    color = (0, 255, 0)
                    font_scale = 0.6
                    thickness = 2
                elif "Occupancy Rate" in stat:
                    # Occupancy rate - yellow/orange based on rate
                    rate = frame_analysis['occupancy_rate']
                    if rate > 0.8:
                        color = (0, 0, 255)  # Red for high occupancy
                    elif rate > 0.5:
                        color = (0, 165, 255)  # Orange for medium
                    else:
                        color = (0, 255, 0)  # Green for low
                    font_scale = 0.6
                    thickness = 2
                else:
                    # Default - light blue
                    color = (255, 200, 100)
                    font_scale = 0.6
                    thickness = 1

                cv2.putText(overlay_frame, stat, (overlay_x + 20, current_y),
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
                current_y += line_heights[i] + 12

        except Exception as e:
            logger.error(f"🎨 Error drawing statistics: {e}")

        return overlay_frame

    async def get_parking_statistics(self, job_id: str):
        """Get comprehensive parking statistics for a job"""
        try:
            # First try to get results (this will load from disk if needed)
            result = await self.get_analysis_results(job_id)
            if not result:
                logger.error(f"No results found for job {job_id}")
                return None
            frame_results = result.get('frame_results', [])

            if not frame_results:
                logger.warning(f"No frame results found for job {job_id}")
                return {
                    'job_id': job_id,
                    'current_total_spaces': 0,
                    'current_occupied_spaces': 0,
                    'current_available_spaces': 0,
                    'current_occupancy_rate': 0.0,
                    'avg_occupancy_rate': 0.0,
                    'avg_occupied_spaces': 0.0,
                    'peak_occupancy_rate': 0.0,
                    'peak_occupied_spaces': 0,
                    'lowest_occupancy_rate': 0.0,
                    'busiest_period': None,
                    'quietest_period': None,
                    'occupancy_trend': 'no_data',
                    'analysis_duration': 0.0,
                    'frames_analyzed': 0,
                    'last_updated': datetime.utcnow().isoformat(),
                    'total_frames': 0,
                    'max_occupancy_rate': 0.0,
                    'min_occupancy_rate': 0.0,
                    'avg_vehicles_detected': 0.0,
                    'max_vehicles_detected': 0,
                    'total_spaces': 0,
                    'occupancy_over_time': []
                }

            # Calculate comprehensive statistics
            occupancy_rates = [f['occupancy_rate'] for f in frame_results]
            vehicle_counts = [f['vehicle_detections'] for f in frame_results]
            occupied_spaces_list = [f['occupied_spaces'] for f in frame_results]
            total_spaces = frame_results[0].get('total_spaces', 0) if frame_results else 0

            # Get current (latest) values
            latest_frame = frame_results[-1] if frame_results else {}
            current_occupied = latest_frame.get('occupied_spaces', 0)
            current_available = latest_frame.get('available_spaces', 0)
            current_occupancy_rate = latest_frame.get('occupancy_rate', 0.0)

            statistics = {
                # Current state (what frontend expects)
                'job_id': job_id,
                'current_total_spaces': total_spaces,
                'current_occupied_spaces': current_occupied,
                'current_available_spaces': current_available,
                'current_occupancy_rate': current_occupancy_rate,

                # Aggregate statistics
                'total_frames': len(frame_results),
                'avg_occupancy_rate': sum(occupancy_rates) / len(occupancy_rates),
                'max_occupancy_rate': max(occupancy_rates),
                'min_occupancy_rate': min(occupancy_rates),
                'avg_vehicles_detected': sum(vehicle_counts) / len(vehicle_counts),
                'max_vehicles_detected': max(vehicle_counts),
                'total_spaces': total_spaces,
                'avg_occupied_spaces': sum(occupied_spaces_list) / len(occupied_spaces_list),
                'peak_occupancy_rate': max(occupancy_rates),
                'peak_occupied_spaces': max(occupied_spaces_list),
                'lowest_occupancy_rate': min(occupancy_rates),
                'analysis_duration': result.get('processing_time', 0.0),
                'frames_analyzed': len(frame_results),
                'last_updated': datetime.utcnow().isoformat(),

                # Time series data
                'occupancy_over_time': [
                    {
                        'frame': f['frame_number'],
                        'timestamp': f['timestamp'],
                        'occupancy_rate': f['occupancy_rate'],
                        'vehicles': f['vehicle_detections'],
                        'occupied_spaces': f['occupied_spaces'],
                        'available_spaces': f['available_spaces']
                    }
                    for f in frame_results
                ]
            }

            logger.info(f"Generated statistics for job {job_id}: {len(frame_results)} frames analyzed")
            return statistics

        except Exception as e:
            logger.error(f"Error getting statistics for job {job_id}: {str(e)}")
            return None

    # Job management methods
    async def get_job_status(self, job_id: str):
        """Get job status - load from disk if not in memory"""
        # First check memory
        if job_id in self.jobs:
            return self.jobs[job_id]

        # If not in memory, try to load from disk
        results, job_status = self._load_results_from_disk(job_id)
        if job_status:
            # Restore to memory for faster access
            self.jobs[job_id] = job_status
            if results:
                self.results[job_id] = results
            return job_status

        return None

    async def get_analysis_results(self, job_id: str):
        """Get analysis results - load from disk if not in memory"""
        # First check memory
        if job_id in self.results:
            return self.results[job_id]

        # If not in memory, try to load from disk
        results, job_status = self._load_results_from_disk(job_id)
        if results:
            # Restore to memory for faster access
            self.results[job_id] = results
            if job_status:
                self.jobs[job_id] = job_status
            return results

        return None

    async def get_all_job_status(self):
        """Get status for all jobs"""
        return list(self.jobs.values())

    async def cancel_job(self, job_id: str):
        """Cancel a processing job"""
        if job_id in self.processing_tasks:
            task = self.processing_tasks[job_id]
            task.cancel()

            if job_id in self.jobs:
                self.jobs[job_id]["status"] = "failed"
                self.jobs[job_id]["error_message"] = "Job cancelled by user"
                self.jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()

            return True
        return False
