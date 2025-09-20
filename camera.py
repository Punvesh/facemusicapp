"""
Camera Module for Real-Time Emotion-Based Music Recommendation App
Handles webcam capture and real-time video streaming using OpenCV
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import streamlit as st

class CameraHandler:
    """
    A class to handle webcam operations including capture, start, stop, and frame processing
    """
    
    def __init__(self):
        """Initialize the camera handler"""
        self.cap = None
        self.is_running = False
        
    def start_camera(self) -> bool:
        """
        Start the webcam capture
        
        Returns:
            bool: True if camera started successfully, False otherwise
        """
        try:
            # Try to open the default camera (usually index 0)
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                # If default camera fails, try other indices
                for i in range(1, 4):
                    self.cap = cv2.VideoCapture(i)
                    if self.cap.isOpened():
                        break
            
            if self.cap.isOpened():
                # Set camera properties for better performance
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.is_running = True
                return True
            else:
                st.error("❌ Could not open camera. Please check if webcam is connected.")
                return False
                
        except Exception as e:
            st.error(f"❌ Error starting camera: {str(e)}")
            return False
    
    def stop_camera(self):
        """Stop the webcam capture and release resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_running = False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the webcam
        
        Returns:
            np.ndarray: Captured frame as numpy array, or None if failed
        """
        if self.cap is None or not self.is_running:
            return None
        
        try:
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR to RGB (OpenCV uses BGR, but we need RGB)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return frame_rgb
            else:
                return None
        except Exception as e:
            st.error(f"❌ Error capturing frame: {str(e)}")
            return None
    
    def is_camera_active(self) -> bool:
        """
        Check if camera is currently active
        
        Returns:
            bool: True if camera is running, False otherwise
        """
        return self.is_running and self.cap is not None
    
    def get_camera_info(self) -> Tuple[int, int]:
        """
        Get camera resolution information
        
        Returns:
            Tuple[int, int]: (width, height) of camera
        """
        if self.cap is not None:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)
        return (640, 480)  # Default values
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_camera()
