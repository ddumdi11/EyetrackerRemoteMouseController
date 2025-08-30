"""
Eye Tracking Engine - MediaPipe-based implementation
Handles face detection, landmark extraction, and gaze estimation
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

class EyeTracker:
    def __init__(self, max_num_faces: int = 1, min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """Initialize MediaPipe-based eye tracker"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Key landmark indices for eye tracking
        self.LEFT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.RIGHT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.NOSE_TIP = 1
        
        # Calibration data (will be set from external calibration)
        self.calibration_matrix = None
        self.is_calibrated = False
        
        logger.info("EyeTracker initialized with MediaPipe Face Mesh")
    
    def detect_face_landmarks(self, frame: np.ndarray) -> Optional[List]:
        """Detect face landmarks in the given frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark  # Return first face only
        return None
    
    def get_eye_centers(self, landmarks) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Calculate center points of both eyes"""
        # Left eye center
        left_eye_points = [landmarks[i] for i in self.LEFT_EYE_LANDMARKS]
        left_center_x = sum(p.x for p in left_eye_points) / len(left_eye_points)
        left_center_y = sum(p.y for p in left_eye_points) / len(left_eye_points)
        
        # Right eye center
        right_eye_points = [landmarks[i] for i in self.RIGHT_EYE_LANDMARKS]
        right_center_x = sum(p.x for p in right_eye_points) / len(right_eye_points)
        right_center_y = sum(p.y for p in right_eye_points) / len(right_eye_points)
        
        return (left_center_x, left_center_y), (right_center_x, right_center_y)
    
    def get_head_pose(self, landmarks) -> Tuple[float, float]:
        """Estimate head pose from face landmarks"""
        nose_tip = landmarks[self.NOSE_TIP]
        left_eye_outer = landmarks[33]
        right_eye_outer = landmarks[263]
        
        # Calculate head rotation
        eye_center_x = (left_eye_outer.x + right_eye_outer.x) / 2
        eye_center_y = (left_eye_outer.y + right_eye_outer.y) / 2
        
        horizontal_deviation = nose_tip.x - eye_center_x
        vertical_deviation = nose_tip.y - eye_center_y
        
        return horizontal_deviation, vertical_deviation
    
    def get_gaze_point(self, frame: np.ndarray) -> Optional[Tuple[float, float]]:
        """Get estimated gaze point on screen (requires calibration)"""
        landmarks = self.detect_face_landmarks(frame)
        if not landmarks:
            return None
        
        if not self.is_calibrated:
            # Fallback to head pose if not calibrated
            return self.get_head_pose(landmarks)
        
        # TODO: Implement proper gaze estimation with calibration matrix
        left_center, right_center = self.get_eye_centers(landmarks)
        
        # Simple average of both eyes for now
        gaze_x = (left_center[0] + right_center[0]) / 2
        gaze_y = (left_center[1] + right_center[1]) / 2
        
        return gaze_x, gaze_y
    
    def load_calibration(self, calibration_data: dict):
        """Load calibration data from external calibration process"""
        self.calibration_matrix = calibration_data.get('matrix')
        self.is_calibrated = self.calibration_matrix is not None
        logger.info(f"Calibration loaded: {self.is_calibrated}")
    
    def draw_debug_overlay(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """Draw debug overlay with face landmarks and eye centers"""
        if not landmarks:
            return frame
        
        # Draw face mesh
        face_landmarks_proto = type('', (), {})()
        face_landmarks_proto.landmark = landmarks
        
        self.mp_drawing.draw_landmarks(
            frame, face_landmarks_proto, self.mp_face_mesh.FACEMESH_CONTOURS,
            None, self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
        )
        
        # Draw eye centers
        left_center, right_center = self.get_eye_centers(landmarks)
        h, w = frame.shape[:2]
        
        left_pixel = (int(left_center[0] * w), int(left_center[1] * h))
        right_pixel = (int(right_center[0] * w), int(right_center[1] * h))
        
        cv2.circle(frame, left_pixel, 3, (0, 0, 255), -1)
        cv2.circle(frame, right_pixel, 3, (0, 0, 255), -1)
        
        # Draw head pose information
        h_dev, v_dev = self.get_head_pose(landmarks)
        cv2.putText(frame, f"Head: H={h_dev:.3f}, V={v_dev:.3f}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        return frame