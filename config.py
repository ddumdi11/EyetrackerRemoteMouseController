"""
Configuration Manager - Handles settings, calibration data, and user preferences
"""

import yaml
import json
import os
from typing import Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_file: str = "config.yaml"):
        """Initialize configuration manager"""
        self.config_file = Path(config_file)
        self.calibration_file = Path("calibration.json")
        
        # Default configuration
        self.default_config = {
            "camera": {
                "device_id": 0,
                "width": 640,
                "height": 480,
                "fps": 30
            },
            "mouse_control": {
                "sensitivity": 2.0,
                "dead_zone": 0.02,
                "smoothing_factor": 0.3,
                "auto_return_delay": 1.0,
                "auto_shutdown_delay": 10.0
            },
            "eye_tracking": {
                "min_detection_confidence": 0.5,
                "min_tracking_confidence": 0.5,
                "max_num_faces": 1
            },
            "triggers": {
                "head_nod_threshold": 0.03,
                "blink_threshold": 0.7,
                "trigger_cooldown": 1.0,
                "buffer_size": 10
            },
            "ui": {
                "show_debug_overlay": True,
                "show_face_mesh": True,
                "debug_window_size": (640, 480)
            },
            "activation": {
                "start_trigger": "right_double_click",
                "requires_calibration": True,
                "auto_center_on_start": True
            }
        }
        
        # Current configuration
        self.config = self.default_config.copy()
        self.calibration_data = {}
        
        # Load existing config
        self.load_config()
        self.load_calibration()
        
        logger.info(f"Configuration loaded from {self.config_file}")
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        self._merge_config(self.config, loaded_config)
                        logger.info("Configuration loaded successfully")
                        return True
            else:
                logger.info("No config file found, using defaults")
                self.save_config()  # Create default config file
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            logger.info("Using default configuration")
        
        return False
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def load_calibration(self) -> bool:
        """Load calibration data from file"""
        try:
            if self.calibration_file.exists():
                with open(self.calibration_file, 'r', encoding='utf-8') as f:
                    self.calibration_data = json.load(f)
                logger.info("Calibration data loaded successfully")
                return True
            else:
                logger.info("No calibration file found")
        except Exception as e:
            logger.error(f"Failed to load calibration: {e}")
        
        return False
    
    def save_calibration(self, calibration_data: Dict[str, Any]) -> bool:
        """Save calibration data to file"""
        try:
            self.calibration_data = calibration_data
            with open(self.calibration_file, 'w', encoding='utf-8') as f:
                json.dump(calibration_data, f, indent=2)
            logger.info("Calibration data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save calibration: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'camera.width')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config_dict = self.config
        
        try:
            # Navigate to parent of target key
            for key in keys[:-1]:
                if key not in config_dict:
                    config_dict[key] = {}
                config_dict = config_dict[key]
            
            # Set the value
            config_dict[keys[-1]] = value
            logger.debug(f"Config updated: {key_path} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to set config value {key_path}: {e}")
            return False
    
    def is_calibrated(self) -> bool:
        """Check if system is properly calibrated"""
        return bool(self.calibration_data.get('matrix')) and bool(self.calibration_data.get('timestamp'))
    
    def get_calibration_matrix(self) -> Optional[Any]:
        """Get calibration matrix if available"""
        return self.calibration_data.get('matrix')
    
    def _merge_config(self, base_config: Dict, new_config: Dict):
        """Recursively merge new configuration into base configuration"""
        for key, value in new_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = self.default_config.copy()
        logger.info("Configuration reset to defaults")
    
    def validate_config(self) -> List[str]:
        """Validate current configuration and return list of issues"""
        issues = []
        
        # Validate camera settings
        if self.get('camera.device_id') < 0:
            issues.append("Camera device_id must be >= 0")
        
        if self.get('camera.width') <= 0 or self.get('camera.height') <= 0:
            issues.append("Camera resolution must be positive")
        
        # Validate mouse control settings
        if self.get('mouse_control.sensitivity') <= 0:
            issues.append("Mouse sensitivity must be positive")
        
        if not (0 <= self.get('mouse_control.dead_zone') <= 1):
            issues.append("Dead zone must be between 0 and 1")
        
        # Validate trigger settings
        if self.get('triggers.trigger_cooldown') <= 0:
            issues.append("Trigger cooldown must be positive")
        
        return issues
    
    def print_current_config(self):
        """Print current configuration for debugging"""
        print("=== Current Configuration ===")
        print(yaml.dump(self.config, default_flow_style=False, indent=2))
        print("=== Calibration Status ===")
        print(f"Calibrated: {self.is_calibrated()}")
        if self.calibration_data:
            print(f"Calibration timestamp: {self.calibration_data.get('timestamp', 'Unknown')}")
        print("=============================")