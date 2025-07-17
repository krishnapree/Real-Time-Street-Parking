"""
YOLO-based object detection service
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any
from ultralytics import YOLO
import torch

from app.core.config import settings
from app.models.detection import Detection, BoundingBox
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class YOLODetector:
    """YOLO object detection service"""
    
    def __init__(self):
        self.model = None
        self.class_names = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"YOLO detector initialized with device: {self.device}")
    
    def load_model(self, model_path: str = None) -> bool:
        """
        Load YOLO model with enhanced error handling and validation

        Args:
            model_path: Path to YOLO model file

        Returns:
            True if model loaded successfully
        """
        try:
            if model_path is None:
                model_path = "yolov8n.pt"  # Use default YOLOv8 nano model

            logger.info(f"🤖 Loading YOLO model: {model_path}")
            logger.info(f"🤖 Target device: {self.device}")

            # Load model (will auto-download if not exists)
            self.model = YOLO(model_path)

            # CRITICAL: Validate model loaded properly
            if self.model is None:
                logger.error("🤖 ❌ Model is None after loading!")
                return False

            # Get class names
            self.class_names = self.model.names

            # CRITICAL: Validate class names
            if self.class_names is None:
                logger.error("🤖 ❌ Class names is None!")
                return False

            if len(self.class_names) == 0:
                logger.error("🤖 ❌ No class names found!")
                return False

            logger.info(f"🤖 ✅ YOLO model loaded successfully")
            logger.info(f"🤖 Available classes: {len(self.class_names)}")
            logger.info(f"🤖 Device: {self.device}")
            logger.info(f"🤖 Vehicle classes to detect: {settings.VEHICLE_CLASSES}")

            # Log some class names for verification
            vehicle_class_names = [self.class_names.get(cls_id, f"unknown_{cls_id}") for cls_id in settings.VEHICLE_CLASSES]
            logger.info(f"🤖 Vehicle class names: {vehicle_class_names}")

            # Test model with a dummy frame to ensure it works
            try:
                dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
                test_results = self.model(dummy_frame, verbose=False)
                logger.info(f"🤖 ✅ Model test successful - returned {len(test_results)} results")
            except Exception as test_error:
                logger.error(f"🤖 ❌ Model test failed: {test_error}")
                return False

            return True

        except Exception as e:
            logger.error(f"🤖 ❌ Error loading YOLO model: {str(e)}")
            import traceback
            logger.error(f"🤖 ❌ Traceback: {traceback.format_exc()}")
            return False
    
    def detect_objects(
        self,
        frame: np.ndarray,
        confidence_threshold: float = None,
        iou_threshold: float = None
    ) -> List[Detection]:
        """
        Detect objects in a frame with enhanced debugging

        Args:
            frame: Input frame
            confidence_threshold: Detection confidence threshold
            iou_threshold: IoU threshold for NMS

        Returns:
            List of detections
        """
        try:
            if self.model is None:
                logger.error("🤖 YOLO model is None! Model not loaded properly.")
                raise ValueError("Model not loaded. Call load_model() first.")

            # CRITICAL: Validate input frame
            if frame is None:
                logger.error("🤖 Input frame is None!")
                return []

            if frame.size == 0:
                logger.error("🤖 Input frame is empty!")
                return []

            # Log frame properties for debugging
            logger.debug(f"🤖 Input frame: shape={frame.shape}, dtype={frame.dtype}, min={frame.min()}, max={frame.max()}")

            # Use default thresholds if not provided
            conf_thresh = confidence_threshold or settings.CONFIDENCE_THRESHOLD
            iou_thresh = iou_threshold or settings.IOU_THRESHOLD

            logger.debug(f"🤖 Running YOLO inference with conf={conf_thresh}, iou={iou_thresh}")

            # CRITICAL: Ensure frame is in correct format for YOLO
            if len(frame.shape) != 3:
                logger.error(f"🤖 Invalid frame shape: {frame.shape}. Expected 3D array (H, W, C)")
                return []

            if frame.shape[2] != 3:
                logger.error(f"🤖 Invalid frame channels: {frame.shape[2]}. Expected 3 channels (BGR)")
                return []

            # CRITICAL: Handle very high resolution frames
            original_height, original_width = frame.shape[:2]
            max_yolo_size = 1280  # YOLO works best with smaller images

            if original_width > max_yolo_size or original_height > max_yolo_size:
                # Scale down for YOLO processing
                scale_factor = min(max_yolo_size / original_width, max_yolo_size / original_height)
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)

                logger.info(f"🤖 Scaling frame for YOLO: {original_width}x{original_height} -> {new_width}x{new_height}")
                yolo_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            else:
                yolo_frame = frame
                scale_factor = 1.0

            # Run inference with enhanced error handling
            try:
                results = self.model(
                    yolo_frame,  # Use scaled frame for YOLO
                    conf=conf_thresh,
                    iou=iou_thresh,
                    verbose=False,
                    device=self.device
                )
                logger.debug(f"🤖 YOLO inference completed successfully on {yolo_frame.shape[:2]} frame")
            except Exception as inference_error:
                logger.error(f"🤖 YOLO inference failed: {inference_error}")
                return []

            detections = []
            total_detections = 0

            # Process results with enhanced debugging
            logger.debug(f"🤖 Processing {len(results)} result objects")
            for i, result in enumerate(results):
                logger.debug(f"🤖 Processing result {i}")
                boxes = result.boxes
                if boxes is not None:
                    total_detections += len(boxes)
                    logger.debug(f"🤖 Result {i}: found {len(boxes)} boxes")
                    for j, box in enumerate(boxes):
                        try:
                            # Get box coordinates (in scaled frame coordinates)
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                            # CRITICAL: Scale coordinates back to original frame size
                            if scale_factor != 1.0:
                                x1 = x1 / scale_factor
                                y1 = y1 / scale_factor
                                x2 = x2 / scale_factor
                                y2 = y2 / scale_factor
                                logger.debug(f"🤖 Scaled bbox back: ({x1:.1f},{y1:.1f},{x2:.1f},{y2:.1f})")

                            # Get class and confidence
                            class_id = int(box.cls[0].cpu().numpy())
                            confidence = float(box.conf[0].cpu().numpy())
                            class_name = self.class_names.get(class_id, f"class_{class_id}")

                            logger.debug(f"🤖 Detection {j}: class_id={class_id}, class_name={class_name}, confidence={confidence:.3f}, bbox=({x1:.1f},{y1:.1f},{x2:.1f},{y2:.1f})")

                            # Create detection object
                            detection = Detection(
                                class_id=class_id,
                                class_name=class_name,
                                confidence=confidence,
                                bbox=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)
                            )

                            detections.append(detection)
                        except Exception as box_error:
                            logger.error(f"🤖 Error processing box {j}: {box_error}")
                else:
                    logger.debug(f"🤖 Result {i}: no boxes found")

            logger.info(f"YOLO detection complete: {len(detections)} objects detected from {total_detections} total detections")

            # CRITICAL: If no detections found, log detailed debugging info
            if len(detections) == 0:
                logger.warning(f"🤖 ⚠️ NO DETECTIONS FOUND!")
                logger.warning(f"🤖 Frame shape: {frame.shape}")
                logger.warning(f"🤖 Confidence threshold: {conf_thresh}")
                logger.warning(f"🤖 Model device: {self.device}")
                logger.warning(f"🤖 Model classes: {len(self.class_names) if self.class_names else 'None'}")

            return detections

        except Exception as e:
            logger.error(f"🤖 ❌ CRITICAL: Error detecting objects: {str(e)}")
            import traceback
            logger.error(f"🤖 ❌ Traceback: {traceback.format_exc()}")
            return []
    
    def filter_vehicle_detections(self, detections: List[Detection]) -> List[Detection]:
        """
        Filter detections to only include vehicles

        Args:
            detections: List of all detections

        Returns:
            List of vehicle detections
        """
        vehicle_detections = []

        logger.info(f"Filtering vehicles from {len(detections)} detections. Vehicle classes: {settings.VEHICLE_CLASSES}")

        for detection in detections:
            logger.debug(f"Checking detection: class_id={detection.class_id}, class_name={detection.class_name}, confidence={detection.confidence:.3f}")
            if detection.class_id in settings.VEHICLE_CLASSES:
                # Calculate vehicle area for filtering
                bbox = detection.bbox
                vehicle_area = (bbox.x2 - bbox.x1) * (bbox.y2 - bbox.y1)

                # Filter by area to remove very small or very large detections
                min_area = getattr(settings, 'MIN_VEHICLE_AREA', 500)
                max_area = getattr(settings, 'MAX_VEHICLE_AREA', 50000)

                if min_area <= vehicle_area <= max_area:
                    vehicle_detections.append(detection)
                    logger.debug(f"  -> VEHICLE DETECTED: {detection.class_name} (area: {vehicle_area:.0f})")
                else:
                    logger.debug(f"  -> Vehicle filtered by area: {vehicle_area:.0f} (min: {min_area}, max: {max_area})")
            else:
                logger.debug(f"  -> Not a vehicle (class_id={detection.class_id})")

        logger.info(f"Vehicle filtering complete: {len(vehicle_detections)} vehicles found from {len(detections)} total detections")
        return vehicle_detections
    
    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        draw_labels: bool = True,
        color: Tuple[int, int, int] = (0, 255, 0)
    ) -> np.ndarray:
        """
        Draw detections on frame
        
        Args:
            frame: Input frame
            detections: List of detections to draw
            draw_labels: Whether to draw labels
            color: Bounding box color (BGR)
            
        Returns:
            Frame with drawn detections
        """
        try:
            frame_copy = frame.copy()
            
            for detection in detections:
                bbox = detection.bbox
                
                # Draw bounding box
                cv2.rectangle(
                    frame_copy,
                    (int(bbox.x1), int(bbox.y1)),
                    (int(bbox.x2), int(bbox.y2)),
                    color,
                    2
                )
                
                # Draw label if requested
                if draw_labels:
                    label = f"{detection.class_name}: {detection.confidence:.2f}"
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                    
                    # Draw label background
                    cv2.rectangle(
                        frame_copy,
                        (int(bbox.x1), int(bbox.y1) - label_size[1] - 10),
                        (int(bbox.x1) + label_size[0], int(bbox.y1)),
                        color,
                        -1
                    )
                    
                    # Draw label text
                    cv2.putText(
                        frame_copy,
                        label,
                        (int(bbox.x1), int(bbox.y1) - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        2
                    )
            
            return frame_copy
            
        except Exception as e:
            logger.error(f"Error drawing detections: {str(e)}")
            return frame
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Model information dictionary
        """
        if self.model is None:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "device": self.device,
            "num_classes": len(self.class_names),
            "class_names": self.class_names,
            "vehicle_classes": settings.VEHICLE_CLASSES
        }
