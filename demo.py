"""
Demo Script for Emotion-Based Music Recommendation System
Simple command-line interface to test core functionality
"""

import cv2
import numpy as np
from camera import CameraHandler
from emotion_detection import EmotionDetector
from recommendation import MusicRecommender
import time

def demo_emotion_detection():
    """Demo function to test emotion detection"""
    print("🎵 Emotion-Based Music Recommendation Demo")
    print("=" * 50)
    
    # Initialize components
    camera = CameraHandler()
    emotion_detector = EmotionDetector()
    music_recommender = MusicRecommender()
    
    print("📷 Starting camera...")
    if not camera.start_camera():
        print("❌ Failed to start camera!")
        return
    
    print("✅ Camera started successfully!")
    print("👀 Look at the camera and show different expressions...")
    print("⏹️  Press 'q' to quit")
    print("-" * 50)
    
    try:
        while True:
            # Capture frame
            frame = camera.get_frame()
            if frame is None:
                print("❌ Failed to capture frame")
                break
            
            # Detect emotion (every 2 seconds)
            if int(time.time()) % 2 == 0:
                emotion_info = emotion_detector.detect_emotion(frame)
                
                if emotion_info:
                    print(f"😊 Detected Emotion: {emotion_info['label']}")
                    print(f"📊 Confidence: {emotion_info['confidence']:.2f}")
                    print(f"🎵 Recommended Genre: {emotion_info['genre']}")
                    
                    # Get music recommendations
                    playlists = music_recommender.get_recommended_playlists(
                        emotion_info['emotion'], 2
                    )
                    
                    if playlists:
                        print("🎶 Recommended Playlists:")
                        for i, playlist in enumerate(playlists, 1):
                            print(f"  {i}. {playlist['name']}")
                            if 'url' in playlist:
                                print(f"     🎧 {playlist['url']}")
                    
                    print("-" * 30)
                else:
                    print("👀 No emotion detected...")
            
            # Display frame
            cv2.imshow('Emotion Detection Demo', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    finally:
        # Cleanup
        camera.stop_camera()
        cv2.destroyAllWindows()
        print("✅ Demo finished!")

def demo_music_recommendations():
    """Demo function to test music recommendations without camera"""
    print("🎵 Music Recommendation Demo (No Camera)")
    print("=" * 50)
    
    music_recommender = MusicRecommender()
    
    # Test different emotions
    test_emotions = ['happy', 'sad', 'angry', 'neutral', 'surprise']
    
    for emotion in test_emotions:
        print(f"\n😊 Testing Emotion: {emotion.upper()}")
        print("-" * 30)
        
        # Get emotion info
        emotion_info = music_recommender.get_emotion_info(emotion)
        print(f"📝 Description: {emotion_info['description']}")
        print(f"🎵 Genres: {', '.join(emotion_info['genres'])}")
        print(f"💫 Mood: {emotion_info['mood']}")
        print(f"⚡ Energy: {emotion_info['energy']}")
        
        # Get playlists
        playlists = music_recommender.get_recommended_playlists(emotion, 2)
        if playlists:
            print("🎶 Playlists:")
            for i, playlist in enumerate(playlists, 1):
                print(f"  {i}. {playlist['name']}")
        else:
            print("❌ No playlists available")
    
    print("\n✅ Music recommendation demo completed!")

if __name__ == "__main__":
    print("🎵 Welcome to the Emotion-Based Music Recommendation Demo!")
    print("Choose a demo option:")
    print("1. Full demo with camera and emotion detection")
    print("2. Music recommendation demo (no camera)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            demo_emotion_detection()
            break
        elif choice == '2':
            demo_music_recommendations()
            break
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
