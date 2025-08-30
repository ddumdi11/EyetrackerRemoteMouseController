"""
Trigger Detector - Detects head nods, blinks, and other trigger gestures
"""

import numpy as np
import cv2
from typing import List, Tuple, Optional
from collections import deque
import time
import logging

logger = logging.getLogger(__name__)

class TriggerDetector:
    def __init__(self, buffer_size: int = 10):
        """Initialize trigger detection with configurable buffer size"""
        self.buffer_size = buffer_size
        
        # Buffers for tracking movements over time
        self.head_position_buffer = deque(maxlen=buffer_size)
        self.eye_closure_buffer = deque(maxlen=buffer_size)
        
        # Trigger thresholds
        self.head_nod_threshold = 0.03
        self.blink_threshold = 0.7
        self.trigger_cooldown = 1.0  # Seconds between triggers
        
        # State tracking
        self.last_trigger_time = 0
        self.is_blinking = False
        
        # Eye landmarks for blink detection
        self.LEFT_EYE_TOP = [159, 158, 157, 173]
        self.LEFT_EYE_BOTTOM = [144, 145, 153, 154]
        self.RIGHT_EYE_TOP = [386, 387, 388, 466]
        self.RIGHT_EYE_BOTTOM = [374, 373, 390, 249]
        
        logger.info("TriggerDetector initialized")
    
    def calculate_eye_aspect_ratio(self, landmarks, eye_top_indices: List[int], 
                                  eye_bottom_indices: List[int]) -> float:
        """Calculate Eye Aspect Ratio (EAR) for blink detection"""
        # Get top and bottom eye points
        top_points = [landmarks[i] for i in eye_top_indices]
        bottom_points = [landmarks[i] for i in eye_bottom_indices]
        
        # Calculate vertical distances
        vertical_distances = []
        for top, bottom in zip(top_points, bottom_points):
            distance = abs(top.y - bottom.y)
            vertical_distances.append(distance)
        
        # Average vertical distance
        avg_vertical = sum(vertical_distances) / len(vertical_distances)
        
        # Calculate horizontal distance (eye width)
        left_point = min(top_points + bottom_points, key=lambda p: p.x)
        right_point = max(top_points + bottom_points, key=lambda p: p.x)
        horizontal_distance = abs(right_point.x - left_point.x)
        
        # Eye Aspect Ratio
        if horizontal_distance > 0:
            ear = avg_vertical / horizontal_distance
        else:
            ear = 0
        
        return ear
    
    def detect_blink(self, landmarks) -> bool:
        """Detect blink based on Eye Aspect Ratio"""
        if not landmarks:
            return False
        
        # Calculate EAR for both eyes
        left_ear = self.calculate_eye_aspect_ratio(landmarks, self.LEFT_EYE_TOP, self.LEFT_EYE_BOTTOM)
        right_ear = self.calculate_eye_aspect_ratio(landmarks, self.RIGHT_EYE_TOP, self.RIGHT_EYE_BOTTOM)
        
        # Average EAR
        avg_ear = (left_ear + right_ear) / 2
        
        # Add to buffer
        self.eye_closure_buffer.append(avg_ear)
        
        # Detect blink pattern
        if len(self.eye_closure_buffer) >= 3:
            recent_ears = list(self.eye_closure_buffer)[-3:]
            
            # Look for rapid decrease then increase (blink pattern)
            if (recent_ears[0] > self.blink_threshold and 
                recent_ears[1] < self.blink_threshold and 
                recent_ears[2] > self.blink_threshold):
                
                return self._check_trigger_cooldown()
        
        return False
    
    def detect_head_nod(self, landmarks) -> bool:
        """Detect head nod (up-down movement)"""
        if not landmarks:
            return False
        
        # Use nose tip for head tracking
        nose_tip = landmarks[1]
        head_y = nose_tip.y
        
        # Add to buffer
        self.head_position_buffer.append(head_y)
        
        # Need enough data points
        if len(self.head_position_buffer) < self.buffer_size:
            return False
        
        positions = list(self.head_position_buffer)
        
        # Look for nod pattern: down then up movement
        # Find local minimum and maximum
        mid_point = len(positions) // 2
        first_half_min = min(positions[:mid_point])
        second_half_max = max(positions[mid_point:])
        
        # Check if there's significant movement
        movement_range = second_half_max - first_half_min
        
        if movement_range > self.head_nod_threshold:
            # Verify it's a nod pattern (down then up)
            min_index = positions.index(first_half_min)
            max_index = positions.index(second_half_max, mid_point)
            
            if min_index < max_index:  # Down movement followed by up
                return self._check_trigger_cooldown()
        
        return False
    
    def detect_head_shake(self, landmarks) -> bool:
        """Detect head shake (left-right movement) - Future implementation"""
        # TODO: Implement head shake detection for additional triggers
        return False
    
    def detect_triggers(self, landmarks) -> List[str]:
        """Detect all possible triggers and return list of detected triggers"""
        triggers = []
        
        if self.detect_blink(landmarks):
            triggers.append("blink")
            logger.info("Blink trigger detected")
        
        if self.detect_head_nod(landmarks):
            triggers.append("nod")
            logger.info("Head nod trigger detected")
        
        return triggers
    
    def _check_trigger_cooldown(self) -> bool:
        """Check if enough time has passed since last trigger"""
        current_time = time.time()
        if current_time - self.last_trigger_time > self.trigger_cooldown:
            self.last_trigger_time = current_time
            return True
        return False
    
    def reset_buffers(self):
        """Reset all tracking buffers"""
        self.head_position_buffer.clear()
        self.eye_closure_buffer.clear()
        logger.debug("Trigger detection buffers reset")
    
    def draw_debug_info(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """Draw debug information on frame"""
        if not landmarks:
            return frame
        
        # Calculate current EAR
        left_ear = self.calculate_eye_aspect_ratio(landmarks, self.LEFT_EYE_TOP, self.LEFT_EYE_BOTTOM)
        right_ear = self.calculate_eye_aspect_ratio(landmarks, self.RIGHT_EYE_TOP, self.RIGHT_EYE_BOTTOM)
        avg_ear = (left_ear + right_ear) / 2
        
        # Show EAR value
        cv2.putText(frame, f"EAR: {avg_ear:.3f}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Show trigger status
        if len(self.head_position_buffer) > 0:
            head_y = list(self.head_position_buffer)[-1]
            cv2.putText(frame, f"Head Y: {head_y:.3f}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Show cooldown status
        current_time = time.time()
        time_since_trigger = current_time - self.last_trigger_time
        if time_since_trigger < self.trigger_cooldown:
            remaining = self.trigger_cooldown - time_since_trigger
            cv2.putText(frame, f"Cooldown: {remaining:.1f}s", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return frame