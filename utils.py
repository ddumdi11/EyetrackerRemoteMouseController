"""
Utility functions for the Eyetracker Remote Mouse Controller
"""

import time
import math
import numpy as np
from typing import List, Tuple, Optional, Any
import logging
import psutil
import threading
from collections import deque

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system performance and application metrics"""
    
    def __init__(self, window_size: int = 30):
        """Initialize performance monitor"""
        self.window_size = window_size
        self.fps_buffer = deque(maxlen=window_size)
        self.cpu_buffer = deque(maxlen=window_size)
        self.memory_buffer = deque(maxlen=window_size)
        
        self.last_frame_time = time.time()
        self.frame_count = 0
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system_resources, daemon=True)
        self.monitor_thread.start()
    
    def update_fps(self):
        """Update FPS calculation"""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        
        if frame_time > 0:
            fps = 1.0 / frame_time
            self.fps_buffer.append(fps)
        
        self.last_frame_time = current_time
        self.frame_count += 1
    
    def get_average_fps(self) -> float:
        """Get average FPS over the window"""
        if len(self.fps_buffer) == 0:
            return 0.0
        return sum(self.fps_buffer) / len(self.fps_buffer)
    
    def get_current_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        if len(self.cpu_buffer) == 0:
            return 0.0
        return self.cpu_buffer[-1]
    
    def get_current_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if len(self.memory_buffer) == 0:
            return 0.0
        return self.memory_buffer[-1]
    
    def _monitor_system_resources(self):
        """Background thread to monitor system resources"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_buffer.append(cpu_percent)
                
                # Memory usage
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.memory_buffer.append(memory_mb)
                
            except Exception as e:
                logger.warning(f"Performance monitoring error: {e}")
            
            time.sleep(1.0)
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
    
    def get_stats_summary(self) -> dict:
        """Get comprehensive performance statistics"""
        return {
            'fps': {
                'current': self.fps_buffer[-1] if self.fps_buffer else 0,
                'average': self.get_average_fps(),
                'min': min(self.fps_buffer) if self.fps_buffer else 0,
                'max': max(self.fps_buffer) if self.fps_buffer else 0
            },
            'cpu': {
                'current': self.get_current_cpu_usage(),
                'average': sum(self.cpu_buffer) / len(self.cpu_buffer) if self.cpu_buffer else 0
            },
            'memory': {
                'current_mb': self.get_current_memory_usage(),
                'average_mb': sum(self.memory_buffer) / len(self.memory_buffer) if self.memory_buffer else 0
            },
            'frames_processed': self.frame_count
        }

class MovementAnalyzer:
    """Analyze movement patterns for linear detection and filtering"""
    
    @staticmethod
    def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    @staticmethod
    def calculate_angle(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate angle of movement vector in radians"""
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return math.atan2(dy, dx)
    
    @staticmethod
    def is_linear_movement(points: List[Tuple[float, float]], threshold: float = 0.15) -> bool:
        """Determine if a series of points represents linear movement"""
        if len(points) < 3:
            return False
        
        # Calculate angles between consecutive segments
        angles = []
        for i in range(len(points) - 2):
            p1, p2, p3 = points[i], points[i+1], points[i+2]
            
            # Skip if points are too close
            if (MovementAnalyzer.calculate_distance(p1, p2) < 0.001 or 
                MovementAnalyzer.calculate_distance(p2, p3) < 0.001):
                continue
            
            angle1 = MovementAnalyzer.calculate_angle(p1, p2)
            angle2 = MovementAnalyzer.calculate_angle(p2, p3)
            
            # Calculate angle difference
            angle_diff = abs(angle2 - angle1)
            # Normalize to [0, π]
            angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
            
            angles.append(angle_diff)
        
        if not angles:
            return False
        
        # Linear movement should have small angle variations
        avg_angle_deviation = sum(angles) / len(angles)
        return avg_angle_deviation < threshold
    
    @staticmethod
    def smooth_points(points: List[Tuple[float, float]], alpha: float = 0.3) -> List[Tuple[float, float]]:
        """Apply exponential smoothing to a series of points"""
        if not points:
            return points
        
        smoothed = [points[0]]
        
        for i in range(1, len(points)):
            prev_smoothed = smoothed[-1]
            current_raw = points[i]
            
            smoothed_x = alpha * current_raw[0] + (1 - alpha) * prev_smoothed[0]
            smoothed_y = alpha * current_raw[1] + (1 - alpha) * prev_smoothed[1]
            
            smoothed.append((smoothed_x, smoothed_y))
        
        return smoothed
    
    @staticmethod
    def detect_fixation(points: List[Tuple[float, float]], 
                       radius_threshold: float = 0.02, 
                       min_duration: int = 5) -> bool:
        """Detect if points represent a fixation (staying in one area)"""
        if len(points) < min_duration:
            return False
        
        # Calculate centroid
        center_x = sum(p[0] for p in points) / len(points)
        center_y = sum(p[1] for p in points) / len(points)
        center = (center_x, center_y)
        
        # Check if all points are within radius threshold
        for point in points:
            if MovementAnalyzer.calculate_distance(point, center) > radius_threshold:
                return False
        
        return True

class GeometryUtils:
    """Geometric utility functions"""
    
    @staticmethod
    def normalize_coordinates(x: float, y: float, width: int, height: int) -> Tuple[float, float]:
        """Normalize pixel coordinates to [0, 1] range"""
        return x / width, y / height
    
    @staticmethod
    def denormalize_coordinates(x: float, y: float, width: int, height: int) -> Tuple[int, int]:
        """Convert normalized coordinates back to pixel coordinates"""
        return int(x * width), int(y * height)
    
    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """Clamp value to specified range"""
        return max(min_value, min(value, max_value))
    
    @staticmethod
    def interpolate(start: float, end: float, factor: float) -> float:
        """Linear interpolation between start and end values"""
        return start + (end - start) * factor
    
    @staticmethod
    def apply_dead_zone(x: float, y: float, dead_zone: float) -> Tuple[float, float]:
        """Apply dead zone to coordinates, returning zero if within threshold"""
        magnitude = math.sqrt(x*x + y*y)
        if magnitude < dead_zone:
            return 0.0, 0.0
        
        # Scale values to start from dead zone boundary
        scale_factor = (magnitude - dead_zone) / magnitude
        return x * scale_factor, y * scale_factor

class TimingUtils:
    """Timing and scheduling utilities"""
    
    @staticmethod
    def create_timer(duration: float, callback, *args, **kwargs) -> threading.Timer:
        """Create a timer that calls callback after duration seconds"""
        timer = threading.Timer(duration, callback, args=args, kwargs=kwargs)
        return timer
    
    @staticmethod
    def fps_limiter(target_fps: float = 30.0):
        """Generator that yields at the target FPS rate"""
        frame_time = 1.0 / target_fps
        last_time = time.time()
        
        while True:
            current_time = time.time()
            elapsed = current_time - last_time
            
            if elapsed < frame_time:
                sleep_time = frame_time - elapsed
                time.sleep(sleep_time)
            
            last_time = time.time()
            yield

class LinearMovementDetector:
    """Advanced linear movement detection with state tracking"""
    
    def __init__(self, buffer_size: int = 10, linearity_threshold: float = 0.15):
        """Initialize linear movement detector"""
        self.buffer_size = buffer_size
        self.linearity_threshold = linearity_threshold
        self.movement_buffer = deque(maxlen=buffer_size)
        self.is_linear = False
        self.last_direction = None
    
    def add_point(self, x: float, y: float) -> bool:
        """Add new point and return True if linear movement is detected"""
        self.movement_buffer.append((x, y))
        
        if len(self.movement_buffer) < 3:
            return False
        
        points = list(self.movement_buffer)
        self.is_linear = MovementAnalyzer.is_linear_movement(points, self.linearity_threshold)
        
        if self.is_linear:
            # Update movement direction
            first_point = points[0]
            last_point = points[-1]
            self.last_direction = MovementAnalyzer.calculate_angle(first_point, last_point)
        
        return self.is_linear
    
    def get_movement_vector(self) -> Optional[Tuple[float, float]]:
        """Get current movement vector if linear movement is detected"""
        if not self.is_linear or len(self.movement_buffer) < 2:
            return None
        
        points = list(self.movement_buffer)
        start_point = points[0]
        end_point = points[-1]
        
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        
        return dx, dy
    
    def reset(self):
        """Reset movement detection state"""
        self.movement_buffer.clear()
        self.is_linear = False
        self.last_direction = None

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration"""
    import colorlog
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Setup console handler
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup file handler if requested
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)