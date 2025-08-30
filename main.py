#!/usr/bin/env python3
"""
Eyetracker Remote Mouse Controller - Main Application
Basic prototype with head-based mouse control
"""

import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import time
import sys
from typing import Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BasicEyetracker:
    def __init__(self):
        """Initialize the basic eyetracker with MediaPipe face detection"""
        # MediaPipe setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        # Control parameters
        self.is_active = False
        self.sensitivity = 3.0  # Mouse movement sensitivity
        self.dead_zone = 0.02   # Dead zone to prevent jittering
        
        # Camera setup
        self.cap = None
        
        logger.info(f"Screen resolution: {self.screen_width}x{self.screen_height}")
        logger.info("BasicEyetracker initialized successfully")
    
    def initialize_camera(self) -> bool:
        """Initialize webcam"""
        try:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.cap.isOpened():
                logger.error("Cannot open camera")
                return False
                
            logger.info("Camera initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            return False
    
    def get_head_pose(self, landmarks) -> Tuple[float, float]:
        """Calculate head pose from face landmarks"""
        # Get key landmarks for head pose estimation
        nose_tip = landmarks[1]  # Nose tip
        left_eye = landmarks[33]  # Left eye outer corner
        right_eye = landmarks[263]  # Right eye outer corner
        
        # Calculate horizontal position (left-right head movement)
        eye_center_x = (left_eye.x + right_eye.x) / 2
        horizontal_deviation = nose_tip.x - eye_center_x
        
        # Calculate vertical position (up-down head movement)
        eye_center_y = (left_eye.y + right_eye.y) / 2
        vertical_deviation = nose_tip.y - eye_center_y
        
        return horizontal_deviation, vertical_deviation
    
    def move_mouse_based_on_head(self, h_dev: float, v_dev: float):
        """Move mouse cursor based on head movement"""
        # Apply dead zone to prevent small movements
        if abs(h_dev) < self.dead_zone and abs(v_dev) < self.dead_zone:
            return
        
        # Calculate mouse movement
        delta_x = h_dev * self.sensitivity * self.screen_width
        delta_y = v_dev * self.sensitivity * self.screen_height
        
        # Get current mouse position
        current_x, current_y = pyautogui.position()
        
        # Calculate new position
        new_x = max(0, min(self.screen_width - 1, current_x + int(delta_x)))
        new_y = max(0, min(self.screen_height - 1, current_y + int(delta_y)))
        
        # Move mouse smoothly
        pyautogui.moveTo(new_x, new_y, duration=0.01)
    
    def return_to_center(self):
        """Return mouse cursor to center of screen"""
        pyautogui.moveTo(self.center_x, self.center_y, duration=0.5)
        logger.info("Mouse returned to center position")
    
    def run(self):
        """Main application loop"""
        if not self.initialize_camera():
            return
        
        logger.info("Starting eyetracker... Press 'q' to quit, 'c' to center mouse")
        self.return_to_center()
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.error("Failed to read from camera")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process face landmarks
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        # Get head pose
                        h_dev, v_dev = self.get_head_pose(face_landmarks.landmark)
                        
                        # Move mouse based on head movement
                        self.move_mouse_based_on_head(h_dev, v_dev)
                        
                        # Draw face mesh on frame for debugging
                        self.mp_drawing.draw_landmarks(
                            frame, face_landmarks, self.mp_face_mesh.FACEMESH_CONTOURS,
                            None, self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
                        )
                        
                        # Show head movement values on screen
                        cv2.putText(frame, f"H: {h_dev:.3f}, V: {v_dev:.3f}", 
                                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Display status
                status_text = "ACTIVE - Head tracking enabled"
                cv2.putText(frame, status_text, (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Show frame
                cv2.imshow('Eyetracker Remote Mouse Controller', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    self.return_to_center()
                
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Cleanup completed")

def main():
    """Main entry point"""
    print("=== Eyetracker Remote Mouse Controller ===")
    print("Basic Prototype - Head Movement Control")
    print("Controls:")
    print("  - Move your head to control mouse cursor")
    print("  - Press 'c' to center mouse")
    print("  - Press 'q' to quit")
    print("==========================================")
    
    tracker = BasicEyetracker()
    tracker.run()

if __name__ == "__main__":
    main()