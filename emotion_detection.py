"""
Emotion Detection Module for Real-Time Emotion-Based Music Recommendation App
Uses DeepFace library to detect emotions from facial expressions in real-time
"""

import cv2
import numpy as np
from deepface import DeepFace
from typing import Dict, Tuple, Optional
import streamlit as st
import time

class EmotionDetector:
    """
    A class to handle emotion detection using DeepFace library
    Detects 7 basic emotions: happy, sad, angry, fear, surprise, disgust, neutral
    """
    
    def __init__(self):
        """Initialize the emotion detector"""
        self.emotion_labels = {
            'happy': '😊 Happy',
            'sad': '😢 Sad', 
            'angry': '😠 Angry',
            'fear': '😨 Fear',
            'surprise': '😲 Surprised',
            'disgust': '🤢 Disgusted',
            'neutral': '😐 Neutral'
        }
        
        # Emotion to music genre mapping
        self.emotion_to_genre = {
            'happy': 'Pop/Dance',
            'sad': 'Acoustic/Chill',
            'angry': 'Rock/Metal',
            'fear': 'Ambient/Calm',
            'surprise': 'Electronic/Funk',
            'disgust': 'Alternative/Indie',
            'neutral': 'Lo-fi/Instrumental'
        }
        
        # Confidence threshold for emotion detection
        self.confidence_threshold = 0.3
        
    def detect_emotion(self, frame: np.ndarray) -> Optional[Dict]:
        """
        Detect emotion from a given frame
        
        Args:
            frame (np.ndarray): Input frame as numpy array (RGB format)
            
        Returns:
            Optional[Dict]: Dictionary containing emotion info or None if detection fails
        """
        try:
            # DeepFace expects RGB format, which we already have
            # Analyze the frame for emotions
            result = DeepFace.analyze(
                frame, 
                actions=['emotion'],
                enforce_detection=False,  # Don't enforce face detection strictly
                detector_backend='opencv'  # Use OpenCV for faster detection
            )
            
            if result and len(result) > 0:
                # Get the first detected face
                face_result = result[0] if isinstance(result, list) else result
                
                if 'emotion' in face_result:
                    emotions = face_result['emotion']
                    
                    # Find the emotion with highest confidence
                    dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                    emotion_name, confidence = dominant_emotion
                    
                    # Only return if confidence is above threshold
                    if confidence > self.confidence_threshold:
                        return {
                            'emotion': emotion_name,
                            'confidence': confidence,
                            'emotions': emotions,
                            'genre': self.emotion_to_genre.get(emotion_name, 'Unknown'),
                            'label': self.emotion_labels.get(emotion_name, emotion_name)
                        }
            
            return None
            
        except Exception as e:
            # Handle various DeepFace errors gracefully
            if "Face could not be detected" in str(e):
                return None  # No face detected
            elif "No faces were extracted" in str(e):
                return None  # No faces extracted
            else:
                st.warning(f"⚠️ Emotion detection error: {str(e)}")
                return None
    
    def draw_emotion_info(self, frame: np.ndarray, emotion_info: Dict) -> np.ndarray:
        """
        Draw emotion information on the frame
        
        Args:
            frame (np.ndarray): Input frame
            emotion_info (Dict): Emotion detection results
            
        Returns:
            np.ndarray: Frame with emotion information drawn on it
        """
        if emotion_info is None:
            return frame
        
        # Create a copy to avoid modifying original
        frame_with_info = frame.copy()
        
        # Get frame dimensions
        height, width = frame_with_info.shape[:2]
        
        # Create background rectangle for text
        cv2.rectangle(frame_with_info, (10, 10), (300, 120), (0, 0, 0), -1)
        cv2.rectangle(frame_with_info, (10, 10), (300, 120), (255, 255, 255), 2)
        
        # Add emotion text
        emotion_text = f"Emotion: {emotion_info['label']}"
        cv2.putText(frame_with_info, emotion_text, (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add confidence text
        confidence_text = f"Confidence: {emotion_info['confidence']:.2f}"
        cv2.putText(frame_with_info, confidence_text, (20, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add genre text
        genre_text = f"Genre: {emotion_info['genre']}"
        cv2.putText(frame_with_info, genre_text, (20, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame_with_info
    
    def get_emotion_summary(self, emotion_info: Dict) -> str:
        """
        Get a formatted summary of detected emotion
        
        Args:
            emotion_info (Dict): Emotion detection results
            
        Returns:
            str: Formatted emotion summary
        """
        if emotion_info is None:
            return "No emotion detected"
        
        return f"{emotion_info['label']} - {emotion_info['genre']} (Confidence: {emotion_info['confidence']:.2f})"
    
    def get_recommended_genre(self, emotion_info: Dict) -> str:
        """
        Get the recommended music genre based on detected emotion
        
        Args:
            emotion_info (Dict): Emotion detection results
            
        Returns:
            str: Recommended music genre
        """
        if emotion_info is None:
            return "Unknown"
        
        return emotion_info['genre']
