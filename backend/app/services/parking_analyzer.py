"""
Parking space analysis service
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import json

from app.core.config import settings
from app.models.detection import Detection, BoundingBox, ParkingSpace, FrameAnalysis
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ParkingAnalyzer:
    """Parking space analysis service"""
    
    def __init__(self):
        self.parking_spaces: List[ParkingSpace] = []
        self.auto_detect_spaces = True
        self.space_detection_history = []
    
    def auto_detect_parking_spaces(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        min_area: int = None
    ) -> List[ParkingSpace]:
        """
        Automatically detect parking spaces based on vehicle positions
        
        Args:
            frame: Input frame
            detections: Vehicle detections
            min_area: Minimum area for a parking space
            
        Returns:
            List of detected parking spaces
        """
        try:
            min_area = min_area or settings.PARKING_SPACE_MIN_AREA
            frame_height, frame_width = frame.shape[:2]
            
            # Create a grid-based approach for parking space detection
            parking_spaces = []
            
            # If we have vehicle detections, use them to infer parking spaces
            if detections:
                # Sort detections by position (left to right, top to bottom)
                sorted_detections = sorted(
                    detections,
                    key=lambda d: (d.bbox.y1, d.bbox.x1)
                )
                
                # Group detections into rows
                rows = self._group_detections_into_rows(sorted_detections)
                
                # Create parking spaces based on vehicle positions
                space_id = 0
                for row_idx, row_detections in enumerate(rows):
                    for det_idx, detection in enumerate(row_detections):
                        bbox = detection.bbox
                        
                        # Expand bounding box slightly to create parking space
                        expansion = 20  # pixels
                        space_bbox = BoundingBox(
                            x1=max(0, bbox.x1 - expansion),
                            y1=max(0, bbox.y1 - expansion),
                            x2=min(frame_width, bbox.x2 + expansion),
                            y2=min(frame_height, bbox.y2 + expansion)
                        )
                        
                        # Check if area is large enough
                        if space_bbox.area >= min_area:
                            parking_space = ParkingSpace(
                                id=f"space_{space_id}",
                                bbox=space_bbox,
                                is_occupied=True,
                                occupancy_confidence=detection.confidence,
                                detected_vehicle=detection
                            )
                            parking_spaces.append(parking_space)
                            space_id += 1
                
                # Add potential empty spaces between vehicles
                for row_idx, row_detections in enumerate(rows):
                    for i in range(len(row_detections) - 1):
                        current_det = row_detections[i]
                        next_det = row_detections[i + 1]
                        
                        # Check if there's enough space between vehicles
                        gap_width = next_det.bbox.x1 - current_det.bbox.x2
                        avg_height = (current_det.bbox.height + next_det.bbox.height) / 2
                        
                        if gap_width > avg_height * 0.8:  # Reasonable gap for a parking space
                            space_bbox = BoundingBox(
                                x1=current_det.bbox.x2,
                                y1=min(current_det.bbox.y1, next_det.bbox.y1),
                                x2=next_det.bbox.x1,
                                y2=max(current_det.bbox.y2, next_det.bbox.y2)
                            )
                            
                            if space_bbox.area >= min_area:
                                parking_space = ParkingSpace(
                                    id=f"space_{space_id}",
                                    bbox=space_bbox,
                                    is_occupied=False,
                                    occupancy_confidence=0.0
                                )
                                parking_spaces.append(parking_space)
                                space_id += 1
            
            else:
                # No vehicles detected, create a grid of potential parking spaces
                parking_spaces = self._create_grid_parking_spaces(frame, min_area)
            
            logger.info(f"Auto-detected {len(parking_spaces)} parking spaces")
            return parking_spaces
            
        except Exception as e:
            logger.error(f"Error auto-detecting parking spaces: {str(e)}")
            return []
    
    def _group_detections_into_rows(
        self,
        detections: List[Detection],
        row_threshold: float = 50.0
    ) -> List[List[Detection]]:
        """
        Group detections into rows based on Y coordinates
        
        Args:
            detections: List of detections
            row_threshold: Maximum Y difference to be in same row
            
        Returns:
            List of detection rows
        """
        if not detections:
            return []
        
        rows = []
        current_row = [detections[0]]
        
        for detection in detections[1:]:
            # Check if detection is in the same row as the current row
            current_row_y = sum(d.bbox.y1 for d in current_row) / len(current_row)
            
            if abs(detection.bbox.y1 - current_row_y) <= row_threshold:
                current_row.append(detection)
            else:
                # Start new row
                rows.append(current_row)
                current_row = [detection]
        
        # Add the last row
        if current_row:
            rows.append(current_row)
        
        return rows
    
    def _create_grid_parking_spaces(
        self,
        frame: np.ndarray,
        min_area: int,
        grid_cols: int = 6,
        grid_rows: int = 2
    ) -> List[ParkingSpace]:
        """
        Create a grid of parking spaces when no vehicles are detected
        
        Args:
            frame: Input frame
            min_area: Minimum area for parking space
            grid_cols: Number of columns in grid
            grid_rows: Number of rows in grid
            
        Returns:
            List of grid-based parking spaces
        """
        frame_height, frame_width = frame.shape[:2]
        parking_spaces = []
        
        # Calculate space dimensions
        space_width = frame_width // grid_cols
        space_height = frame_height // grid_rows
        
        space_id = 0
        for row in range(grid_rows):
            for col in range(grid_cols):
                x1 = col * space_width
                y1 = row * space_height
                x2 = x1 + space_width
                y2 = y1 + space_height
                
                space_bbox = BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)
                
                if space_bbox.area >= min_area:
                    parking_space = ParkingSpace(
                        id=f"grid_space_{space_id}",
                        bbox=space_bbox,
                        is_occupied=False,
                        occupancy_confidence=0.0
                    )
                    parking_spaces.append(parking_space)
                    space_id += 1
        
        return parking_spaces
    
    def analyze_parking_occupancy(
        self,
        parking_spaces: List[ParkingSpace],
        detections: List[Detection],
        occupancy_threshold: float = None
    ) -> List[ParkingSpace]:
        """
        Analyze parking space occupancy based on vehicle detections
        
        Args:
            parking_spaces: List of parking spaces
            detections: Vehicle detections
            occupancy_threshold: Threshold for considering space occupied
            
        Returns:
            Updated parking spaces with occupancy information
        """
        try:
            threshold = occupancy_threshold or settings.OCCUPANCY_THRESHOLD
            updated_spaces = []
            
            for space in parking_spaces:
                # Find vehicles that overlap with this parking space
                overlapping_vehicles = []
                
                for detection in detections:
                    overlap_ratio = self._calculate_overlap_ratio(space.bbox, detection.bbox)
                    if overlap_ratio > threshold:
                        overlapping_vehicles.append((detection, overlap_ratio))
                
                # Update space occupancy
                if overlapping_vehicles:
                    # Find the vehicle with highest overlap
                    best_vehicle, best_overlap = max(overlapping_vehicles, key=lambda x: x[1])
                    
                    updated_space = ParkingSpace(
                        id=space.id,
                        bbox=space.bbox,
                        is_occupied=True,
                        occupancy_confidence=best_overlap,
                        detected_vehicle=best_vehicle
                    )
                else:
                    updated_space = ParkingSpace(
                        id=space.id,
                        bbox=space.bbox,
                        is_occupied=False,
                        occupancy_confidence=0.0,
                        detected_vehicle=None
                    )
                
                updated_spaces.append(updated_space)
            
            return updated_spaces
            
        except Exception as e:
            logger.error(f"Error analyzing parking occupancy: {str(e)}")
            return parking_spaces
    
    def _calculate_overlap_ratio(self, bbox1: BoundingBox, bbox2: BoundingBox) -> float:
        """
        Calculate overlap ratio between two bounding boxes
        
        Args:
            bbox1: First bounding box
            bbox2: Second bounding box
            
        Returns:
            Overlap ratio (0.0 to 1.0)
        """
        # Calculate intersection
        x1 = max(bbox1.x1, bbox2.x1)
        y1 = max(bbox1.y1, bbox2.y1)
        x2 = min(bbox1.x2, bbox2.x2)
        y2 = min(bbox1.y2, bbox2.y2)
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection_area = (x2 - x1) * (y2 - y1)
        bbox1_area = bbox1.area
        
        if bbox1_area == 0:
            return 0.0
        
        return intersection_area / bbox1_area
    
    def create_frame_analysis(
        self,
        frame_number: int,
        timestamp: float,
        detections: List[Detection],
        parking_spaces: List[ParkingSpace]
    ) -> FrameAnalysis:
        """
        Create frame analysis results
        
        Args:
            frame_number: Frame number
            timestamp: Timestamp in video
            detections: All detections in frame
            parking_spaces: Parking space analysis
            
        Returns:
            Frame analysis object
        """
        total_spaces = len(parking_spaces)
        occupied_spaces = sum(1 for space in parking_spaces if space.is_occupied)
        available_spaces = total_spaces - occupied_spaces
        occupancy_rate = occupied_spaces / total_spaces if total_spaces > 0 else 0.0
        
        return FrameAnalysis(
            frame_number=frame_number,
            timestamp=timestamp,
            detections=detections,
            parking_spaces=parking_spaces,
            total_spaces=total_spaces,
            occupied_spaces=occupied_spaces,
            available_spaces=available_spaces,
            occupancy_rate=occupancy_rate
        )
    
    def draw_parking_spaces(
        self,
        frame: np.ndarray,
        parking_spaces: List[ParkingSpace],
        show_labels: bool = True
    ) -> np.ndarray:
        """
        Draw parking spaces on frame
        
        Args:
            frame: Input frame
            parking_spaces: List of parking spaces
            show_labels: Whether to show labels
            
        Returns:
            Frame with drawn parking spaces
        """
        try:
            frame_copy = frame.copy()
            
            for space in parking_spaces:
                bbox = space.bbox
                
                # Choose color based on occupancy
                if space.is_occupied:
                    color = (0, 0, 255)  # Red for occupied
                    status = "OCCUPIED"
                else:
                    color = (0, 255, 0)  # Green for available
                    status = "AVAILABLE"
                
                # Draw bounding box
                cv2.rectangle(
                    frame_copy,
                    (int(bbox.x1), int(bbox.y1)),
                    (int(bbox.x2), int(bbox.y2)),
                    color,
                    2
                )
                
                # Draw label if requested
                if show_labels:
                    label = f"{space.id}: {status}"
                    if space.occupancy_confidence > 0:
                        label += f" ({space.occupancy_confidence:.2f})"
                    
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
                    
                    # Draw label background
                    cv2.rectangle(
                        frame_copy,
                        (int(bbox.x1), int(bbox.y1) - label_size[1] - 5),
                        (int(bbox.x1) + label_size[0], int(bbox.y1)),
                        color,
                        -1
                    )
                    
                    # Draw label text
                    cv2.putText(
                        frame_copy,
                        label,
                        (int(bbox.x1), int(bbox.y1) - 2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 255, 255),
                        1
                    )
            
            return frame_copy
            
        except Exception as e:
            logger.error(f"Error drawing parking spaces: {str(e)}")
            return frame
