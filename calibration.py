"""
Calibration System - 3x3 Grid calibration for precise gaze estimation
"""

import cv2
import numpy as np
import time
import json
from typing import List, Tuple, Dict, Any, Optional
import logging
from pathlib import Path

from eye_tracker import EyeTracker
from config import Config

logger = logging.getLogger(__name__)

class CalibrationSystem:
    def __init__(self, config: Config):
        """Initialize calibration system"""
        self.config = config
        self.eye_tracker = EyeTracker()
        
        # Calibration parameters
        self.grid_size = (3, 3)  # 3x3 calibration grid
        self.point_display_time = 3.0  # Seconds to display each point
        self.collection_start_delay = 1.0  # Delay before starting data collection
        self.samples_per_point = 30  # Number of samples to collect per point
        
        # Calibration data
        self.calibration_points = []
        self.eye_data = []
        self.calibration_matrix = None
        
        # UI parameters
        self.point_radius = 20
        self.point_color = (0, 0, 255)  # Red
        self.background_color = (50, 50, 50)  # Dark gray
        
        logger.info("CalibrationSystem initialized")
    
    def generate_calibration_points(self, screen_width: int, screen_height: int) -> List[Tuple[int, int]]:
        """Generate 3x3 grid of calibration points"""
        points = []
        
        # Margins from screen edges (10% on each side)
        margin_x = int(screen_width * 0.1)
        margin_y = int(screen_height * 0.1)
        
        # Usable screen area
        usable_width = screen_width - 2 * margin_x
        usable_height = screen_height - 2 * margin_y
        
        # Generate grid points
        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                x = margin_x + col * usable_width // (self.grid_size[0] - 1)
                y = margin_y + row * usable_height // (self.grid_size[1] - 1)
                points.append((x, y))
        
        logger.info(f"Generated {len(points)} calibration points")
        return points
    
    def run_calibration(self) -> bool:
        """Run full calibration process"""
        logger.info("Starting calibration process")
        
        # Initialize camera
        cap = cv2.VideoCapture(self.config.get('camera.device_id', 0))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.get('camera.width', 640))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.get('camera.height', 480))
        
        if not cap.isOpened():
            logger.error("Cannot open camera for calibration")
            return False
        
        try:
            # Get screen dimensions
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            # Generate calibration points
            self.calibration_points = self.generate_calibration_points(screen_width, screen_height)
            
            # Create fullscreen window for calibration
            cv2.namedWindow('Calibration', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty('Calibration', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            # Show instructions
            if not self._show_instructions():
                return False
            
            # Collect calibration data for each point
            self.eye_data = []
            for i, point in enumerate(self.calibration_points):
                logger.info(f"Calibrating point {i+1}/{len(self.calibration_points)}: {point}")
                
                point_data = self._calibrate_point(cap, point, screen_width, screen_height)
                if not point_data:
                    logger.error(f"Failed to calibrate point {i+1}")
                    return False
                
                self.eye_data.append(point_data)
            
            # Calculate calibration matrix
            success = self._calculate_calibration_matrix()
            if success:
                self._save_calibration()
            
            return success
            
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            return False
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def _show_instructions(self) -> bool:
        """Show calibration instructions to user"""
        instructions = [
            "EYETRACKER CALIBRATION",
            "",
            "Instructions:",
            "1. Look directly at each red dot that appears",
            "2. Keep your head still and eyes focused on the dot",
            "3. Each dot will be displayed for 3 seconds",
            "4. Try to minimize blinking during data collection",
            "",
            "Press SPACE to start calibration",
            "Press ESC to cancel"
        ]
        
        while True:
            # Create instruction screen
            screen = np.full((600, 800, 3), self.background_color, dtype=np.uint8)
            
            # Draw instructions
            y_offset = 100
            for line in instructions:
                if line == "EYETRACKER CALIBRATION":
                    font_scale = 1.0
                    color = (255, 255, 255)
                    thickness = 2
                else:
                    font_scale = 0.7
                    color = (200, 200, 200)
                    thickness = 1
                
                text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
                text_x = (screen.shape[1] - text_size[0]) // 2
                
                cv2.putText(screen, line, (text_x, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                           font_scale, color, thickness)
                y_offset += 40
            
            cv2.imshow('Calibration', screen)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord(' '):  # Space to start
                return True
            elif key == 27:  # ESC to cancel
                return False
    
    def _calibrate_point(self, cap, point: Tuple[int, int], screen_width: int, 
                        screen_height: int) -> Optional[Dict[str, Any]]:
        """Calibrate single point and collect eye tracking data"""
        point_samples = []
        start_time = time.time()
        collection_started = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to read from camera")
                return None
            
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Create calibration screen
            screen = np.full((screen_height, screen_width, 3), self.background_color, dtype=np.uint8)
            
            # Draw calibration point
            cv2.circle(screen, point, self.point_radius, self.point_color, -1)
            
            # Draw countdown or progress
            if elapsed < self.collection_start_delay:
                countdown = int(self.collection_start_delay - elapsed) + 1
                cv2.putText(screen, f"Get ready... {countdown}", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            else:
                if not collection_started:
                    collection_started = True
                    logger.debug("Starting data collection for current point")
                
                # Show progress
                collection_time = elapsed - self.collection_start_delay
                progress = min(collection_time / self.point_display_time, 1.0)
                cv2.putText(screen, f"Look at the dot - {progress:.1%}", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                
                # Collect eye tracking data
                landmarks = self.eye_tracker.detect_face_landmarks(frame)
                if landmarks and len(point_samples) < self.samples_per_point:
                    # Get eye centers
                    left_center, right_center = self.eye_tracker.get_eye_centers(landmarks)
                    
                    sample = {
                        'timestamp': current_time,
                        'screen_point': point,
                        'left_eye': left_center,
                        'right_eye': right_center,
                        'head_pose': self.eye_tracker.get_head_pose(landmarks)
                    }
                    point_samples.append(sample)
            
            cv2.imshow('Calibration', screen)
            
            # Check if we're done with this point
            if collection_started and len(point_samples) >= self.samples_per_point:
                break
            
            # Allow user to cancel
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                return None
        
        # Calculate average eye position for this calibration point
        if point_samples:
            avg_left_x = sum(s['left_eye'][0] for s in point_samples) / len(point_samples)
            avg_left_y = sum(s['left_eye'][1] for s in point_samples) / len(point_samples)
            avg_right_x = sum(s['right_eye'][0] for s in point_samples) / len(point_samples)
            avg_right_y = sum(s['right_eye'][1] for s in point_samples) / len(point_samples)
            
            result = {
                'screen_point': point,
                'avg_left_eye': (avg_left_x, avg_left_y),
                'avg_right_eye': (avg_right_x, avg_right_y),
                'sample_count': len(point_samples),
                'raw_samples': point_samples
            }
            
            logger.debug(f"Collected {len(point_samples)} samples for point {point}")
            return result
        
        return None
    
    def _calculate_calibration_matrix(self) -> bool:
        """Calculate calibration matrix from collected data"""
        if len(self.eye_data) != len(self.calibration_points):
            logger.error("Mismatch between calibration points and collected data")
            return False
        
        try:
            # Prepare data for matrix calculation
            screen_points = []
            eye_points = []
            
            for data in self.eye_data:
                screen_x, screen_y = data['screen_point']
                
                # Use average of both eyes
                left_eye = data['avg_left_eye']
                right_eye = data['avg_right_eye']
                avg_eye_x = (left_eye[0] + right_eye[0]) / 2
                avg_eye_y = (left_eye[1] + right_eye[1]) / 2
                
                screen_points.append([screen_x, screen_y])
                eye_points.append([avg_eye_x, avg_eye_y])
            
            # Convert to numpy arrays
            screen_points = np.array(screen_points, dtype=np.float32)
            eye_points = np.array(eye_points, dtype=np.float32)
            
            # Calculate transformation matrix (affine transformation)
            # This is a simplified approach - more sophisticated methods exist
            self.calibration_matrix = cv2.getAffineTransform(
                eye_points[:3], screen_points[:3]
            )
            
            logger.info("Calibration matrix calculated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to calculate calibration matrix: {e}")
            return False
    
    def _save_calibration(self) -> bool:
        """Save calibration data to file"""
        calibration_data = {
            'timestamp': time.time(),
            'matrix': self.calibration_matrix.tolist() if self.calibration_matrix is not None else None,
            'grid_size': self.grid_size,
            'calibration_points': self.calibration_points,
            'sample_count': len(self.eye_data),
            'quality_metrics': self._calculate_quality_metrics()
        }
        
        return self.config.save_calibration(calibration_data)
    
    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """Calculate calibration quality metrics"""
        # TODO: Implement quality assessment
        return {
            'accuracy': 0.85,  # Placeholder
            'precision': 0.90,  # Placeholder
            'completeness': len(self.eye_data) / len(self.calibration_points)
        }

def main():
    """Standalone calibration program"""
    print("=== Eyetracker Calibration ===")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Load config
    config = Config()
    
    # Run calibration
    calibration_system = CalibrationSystem(config)
    success = calibration_system.run_calibration()
    
    if success:
        print("✅ Calibration completed successfully!")
        print("You can now use the main eyetracker application.")
    else:
        print("❌ Calibration failed. Please try again.")

if __name__ == "__main__":
    main()