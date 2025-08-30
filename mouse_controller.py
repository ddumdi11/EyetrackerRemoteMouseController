"""
Mouse Controller - Handles cursor movement, clicks, and visual feedback
"""

import pyautogui
import time
import ctypes
import ctypes.wintypes
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MouseController:
    def __init__(self):
        """Initialize mouse controller with Windows API integration"""
        # Disable PyAutoGUI failsafe (cursor to corner stops program)
        pyautogui.FAILSAFE = False
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        self.rest_position = (self.screen_width // 2, self.screen_height // 2)
        
        # Mouse control parameters
        self.is_active = False
        self.sensitivity = 2.0
        self.dead_zone = 0.02
        self.smoothing_factor = 0.3
        
        # Position tracking
        self.last_target_x = self.rest_position[0]
        self.last_target_y = self.rest_position[1]
        
        # Windows API for cursor manipulation
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Cursor states
        self.normal_cursor = None
        self.enlarged_cursor = None
        self._load_cursors()
        
        logger.info(f"MouseController initialized - Screen: {self.screen_width}x{self.screen_height}")
    
    def _load_cursors(self):
        """Load system cursors for normal and enlarged states"""
        try:
            # Standard arrow cursor
            self.normal_cursor = self.user32.LoadCursorW(0, 32512)  # IDC_ARROW
            # Use hand cursor as "enlarged" for now
            self.enlarged_cursor = self.user32.LoadCursorW(0, 32649)  # IDC_HAND
            logger.info("Cursors loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load custom cursors: {e}")
            self.normal_cursor = None
            self.enlarged_cursor = None
    
    def set_enlarged_cursor(self):
        """Set enlarged cursor to indicate active state"""
        if self.enlarged_cursor:
            try:
                self.user32.SetSystemCursor(self.enlarged_cursor, 32512)
                logger.debug("Enlarged cursor set")
            except Exception as e:
                logger.warning(f"Could not set enlarged cursor: {e}")
    
    def set_normal_cursor(self):
        """Restore normal cursor"""
        if self.normal_cursor:
            try:
                # Restore system cursors
                self.user32.SystemParametersInfoW(0x0057, 0, None, 0)  # SPI_SETCURSORS
                logger.debug("Normal cursor restored")
            except Exception as e:
                logger.warning(f"Could not restore normal cursor: {e}")
    
    def activate(self):
        """Activate mouse control and return to rest position"""
        self.is_active = True
        self.return_to_rest()
        self.set_enlarged_cursor()
        logger.info("Mouse controller activated")
    
    def deactivate(self):
        """Deactivate mouse control"""
        self.is_active = False
        self.set_normal_cursor()
        logger.info("Mouse controller deactivated")
    
    def return_to_rest(self):
        """Move cursor to rest position (center of screen)"""
        try:
            pyautogui.moveTo(self.rest_position[0], self.rest_position[1], duration=0.3)
            self.last_target_x = self.rest_position[0]
            self.last_target_y = self.rest_position[1]
            logger.debug("Cursor returned to rest position")
        except Exception as e:
            logger.error(f"Failed to return cursor to rest: {e}")
    
    def smooth_move_to(self, target_x: int, target_y: int, duration: float = 0.01):
        """Move cursor smoothly to target position with interpolation"""
        if not self.is_active:
            return
        
        try:
            # Apply smoothing
            smooth_x = self.last_target_x + (target_x - self.last_target_x) * self.smoothing_factor
            smooth_y = self.last_target_y + (target_y - self.last_target_y) * self.smoothing_factor
            
            # Constrain to screen bounds
            smooth_x = max(0, min(self.screen_width - 1, int(smooth_x)))
            smooth_y = max(0, min(self.screen_height - 1, int(smooth_y)))
            
            # Move cursor
            pyautogui.moveTo(smooth_x, smooth_y, duration=duration)
            
            # Update tracking
            self.last_target_x = smooth_x
            self.last_target_y = smooth_y
            
        except Exception as e:
            logger.error(f"Failed to move cursor: {e}")
    
    def move_relative_to_rest(self, delta_x: float, delta_y: float):
        """Move cursor relative to rest position based on head/eye movement"""
        if not self.is_active:
            return
        
        # Apply dead zone
        if abs(delta_x) < self.dead_zone and abs(delta_y) < self.dead_zone:
            return
        
        # Calculate target position relative to rest
        target_x = self.rest_position[0] + (delta_x * self.sensitivity * self.screen_width)
        target_y = self.rest_position[1] + (delta_y * self.sensitivity * self.screen_height)
        
        self.smooth_move_to(int(target_x), int(target_y))
    
    def perform_click(self, click_type: str = "double"):
        """Perform mouse click action"""
        if not self.is_active:
            return
        
        try:
            current_pos = pyautogui.position()
            
            if click_type == "left":
                pyautogui.click()
                logger.info(f"Left click at {current_pos}")
            elif click_type == "right":
                pyautogui.rightClick()
                logger.info(f"Right click at {current_pos}")
            elif click_type == "double":
                pyautogui.doubleClick()
                logger.info(f"Double click at {current_pos}")
            
            # Return to rest after action
            time.sleep(0.1)  # Brief pause
            self.return_to_rest()
            
        except Exception as e:
            logger.error(f"Failed to perform {click_type} click: {e}")
    
    def get_current_position(self) -> Tuple[int, int]:
        """Get current cursor position"""
        try:
            return pyautogui.position()
        except Exception as e:
            logger.error(f"Failed to get cursor position: {e}")
            return self.rest_position
    
    def is_at_rest_position(self, tolerance: int = 10) -> bool:
        """Check if cursor is at rest position within tolerance"""
        current_pos = self.get_current_position()
        distance = ((current_pos[0] - self.rest_position[0]) ** 2 + 
                   (current_pos[1] - self.rest_position[1]) ** 2) ** 0.5
        return distance <= tolerance