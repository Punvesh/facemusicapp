"""
Main Streamlit App for Real-Time Emotion-Based Music Recommendation
Integrates camera, emotion detection, and music recommendation modules
Enhanced UI with emoji avatars, dynamic themes, and interactive features
"""

import streamlit as st
import time
import cv2
import numpy as np
from PIL import Image
import os
import configparser
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# Import our custom modules
from camera import CameraHandler
from emotion_detection import EmotionDetector
from recommendation import MusicRecommender

# Load configuration from config.env file
def load_config():
    """Load configuration from config.env file"""
    config = {}
    config_file = 'config.env'
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config

# Load configuration
app_config = load_config()

# Initialize session state for new features
def initialize_session_state():
    """Initialize session state variables for new UI features"""
    if 'mood_history' not in st.session_state:
        st.session_state.mood_history = []
    if 'user_feedback' not in st.session_state:
        st.session_state.user_feedback = {}
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    if 'current_theme' not in st.session_state:
        st.session_state.current_theme = 'neutral'

# Emotion to emoji mapping for animated avatar
EMOTION_EMOJIS = {
    'happy': '😀',
    'sad': '😢', 
    'angry': '😡',
    'fear': '😨',
    'surprise': '😮',
    'disgust': '🤢',
    'neutral': '😐'
}

# Emotion to theme color mapping
EMOTION_THEMES = {
    'happy': '#FFD700',      # Gold
    'sad': '#87CEEB',        # Sky Blue
    'angry': '#FF4500',      # Orange Red
    'fear': '#9370DB',       # Medium Purple
    'surprise': '#FF69B4',   # Hot Pink
    'disgust': '#32CD32',    # Lime Green
    'neutral': '#808080'     # Gray
}

# Emotion to theme name mapping
EMOTION_THEME_NAMES = {
    'happy': 'Sunshine',
    'sad': 'Ocean',
    'angry': 'Fire',
    'fear': 'Twilight',
    'surprise': 'Neon',
    'disgust': 'Forest',
    'neutral': 'Minimal'
}

# Page configuration
st.set_page_config(
    page_title="Emotion-Based Music Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_dynamic_css(emotion):
    """Generate dynamic CSS based on detected emotion"""
    theme_color = EMOTION_THEMES.get(emotion, '#808080')
    theme_name = EMOTION_THEME_NAMES.get(emotion, 'Minimal')
    
    return f"""
    <style>
        .main-header {{
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            color: {theme_color};
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            transition: color 0.5s ease;
        }}
        .emotion-card {{
            background: linear-gradient(135deg, {theme_color}20, {theme_color}40);
            border: 2px solid {theme_color};
            padding: 1.5rem;
            border-radius: 15px;
            color: #333;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }}
        .music-card {{
            background: linear-gradient(135deg, {theme_color}30, {theme_color}60);
            border: 2px solid {theme_color};
            padding: 1.5rem;
            border-radius: 15px;
            color: #333;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }}
        .camera-container {{
            border: 3px solid {theme_color};
            border-radius: 15px;
            padding: 1rem;
            background: #f0f2f6;
            transition: border-color 0.5s ease;
        }}
        .stButton > button {{
            background: linear-gradient(45deg, {theme_color}, {theme_color}CC);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.5rem 2rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px {theme_color}66;
        }}
        .emoji-avatar {{
            font-size: 4rem;
            text-align: center;
            margin: 1rem 0;
            animation: bounce 2s infinite;
        }}
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-10px); }}
            60% {{ transform: translateY(-5px); }}
        }}
        .theme-indicator {{
            background: {theme_color};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            text-align: center;
            font-weight: bold;
            margin: 1rem 0;
        }}
        .feedback-buttons {{
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        .like-button {{
            background: #4CAF50 !important;
            color: white !important;
        }}
        .dislike-button {{
            background: #f44336 !important;
            color: white !important;
        }}
        .mood-history-chart {{
            background: white;
            border-radius: 15px;
            padding: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .daily-summary {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 2rem 0;
        }}
    </style>
    """

def update_mood_history(emotion, confidence):
    """Update mood history with new emotion detection"""
    timestamp = datetime.now()
    st.session_state.mood_history.append({
        'emotion': emotion,
        'confidence': confidence,
        'timestamp': timestamp
    })
    
    # Keep only last 50 entries for performance
    if len(st.session_state.mood_history) > 50:
        st.session_state.mood_history = st.session_state.mood_history[-50:]

def handle_user_feedback(playlist_id, feedback_type):
    """Handle user feedback for playlists"""
    if playlist_id not in st.session_state.user_feedback:
        st.session_state.user_feedback[playlist_id] = {'likes': 0, 'dislikes': 0}
    
    if feedback_type == 'like':
        st.session_state.user_feedback[playlist_id]['likes'] += 1
    elif feedback_type == 'dislike':
        st.session_state.user_feedback[playlist_id]['dislikes'] += 1
    
    # Save feedback to file
    save_feedback_to_file()

def save_feedback_to_file():
    """Save user feedback to JSON file"""
    try:
        with open('user_feedback.json', 'w') as f:
            json.dump(st.session_state.user_feedback, f, default=str)
    except Exception as e:
        st.warning(f"Could not save feedback: {e}")

def load_feedback_from_file():
    """Load user feedback from JSON file"""
    try:
        if os.path.exists('user_feedback.json'):
            with open('user_feedback.json', 'r') as f:
                st.session_state.user_feedback = json.load(f)
    except Exception as e:
        st.warning(f"Could not load feedback: {e}")

def get_daily_mood_summary():
    """Generate daily mood summary from session data"""
    if not st.session_state.mood_history:
        return None
    
    # Count emotions
    emotion_counts = Counter([entry['emotion'] for entry in st.session_state.mood_history])
    most_frequent_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else 'neutral'
    
    # Calculate average confidence
    avg_confidence = np.mean([entry['confidence'] for entry in st.session_state.mood_history])
    
    # Get top recommended playlist for most frequent emotion
    top_playlist = None
    if st.session_state.music_recommender:
        playlists = st.session_state.music_recommender.get_recommended_playlists(most_frequent_emotion, 1)
        if playlists:
            top_playlist = playlists[0]
    
    return {
        'most_frequent_emotion': most_frequent_emotion,
        'emotion_count': len(st.session_state.mood_history),
        'avg_confidence': avg_confidence,
        'top_playlist': top_playlist,
        'session_duration': datetime.now() - st.session_state.session_start_time
    }

def create_mood_history_chart():
    """Create real-time mood history chart"""
    if not st.session_state.mood_history:
        return None
    
    # Prepare data for chart
    df_data = []
    for entry in st.session_state.mood_history:
        df_data.append({
            'Time': entry['timestamp'],
            'Emotion': entry['emotion'].title(),
            'Confidence': entry['confidence']
        })
    
    if not df_data:
        return None
    
    # Create line chart
    fig = px.line(
        df_data, 
        x='Time', 
        y='Confidence',
        color='Emotion',
        title='Real-Time Mood History',
        labels={'Confidence': 'Confidence Score', 'Time': 'Time'},
        color_discrete_map={
            'Happy': '#FFD700',
            'Sad': '#87CEEB', 
            'Angry': '#FF4500',
            'Fear': '#9370DB',
            'Surprise': '#FF69B4',
            'Disgust': '#32CD32',
            'Neutral': '#808080'
        }
    )
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Confidence Score",
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def main():
    """Main function to run the Streamlit app"""
    
    # Initialize session state
    initialize_session_state()
    load_feedback_from_file()
    
    # Initialize session state variables
    if 'camera_handler' not in st.session_state:
        st.session_state.camera_handler = CameraHandler()
    if 'emotion_detector' not in st.session_state:
        st.session_state.emotion_detector = EmotionDetector()
    if 'music_recommender' not in st.session_state:
        st.session_state.music_recommender = MusicRecommender()
    if 'camera_active' not in st.session_state:
        st.session_state.camera_active = False
    if 'current_emotion' not in st.session_state:
        st.session_state.current_emotion = None
    if 'last_detection_time' not in st.session_state:
        st.session_state.last_detection_time = 0
    if 'spotify_configured' not in st.session_state:
        st.session_state.spotify_configured = False
    
    # Auto-configure Spotify if credentials are in config file
    if not st.session_state.spotify_configured:
        spotify_client_id = app_config.get('SPOTIFY_CLIENT_ID', '')
        spotify_client_secret = app_config.get('SPOTIFY_CLIENT_SECRET', '')
        
        if spotify_client_id and spotify_client_secret and spotify_client_id != 'your_actual_client_id_here':
            try:
                success = st.session_state.music_recommender.setup_spotify(spotify_client_id, spotify_client_secret)
                if success:
                    st.session_state.spotify_configured = True
                    st.success("✅ Spotify API auto-configured from config file!")
                else:
                    st.warning("⚠️ Spotify API auto-configuration failed. Check your credentials in config.env")
            except Exception as e:
                st.warning(f"⚠️ Spotify API auto-configuration error: {str(e)}")
    
    # Get current emotion for dynamic theming
    current_emotion = st.session_state.current_emotion['emotion'] if st.session_state.current_emotion else 'neutral'
    
    # Apply dynamic CSS based on detected emotion
    st.markdown(get_dynamic_css(current_emotion), unsafe_allow_html=True)
    
    # Header with dynamic theme
    st.markdown(f'<h1 class="main-header">🎵 Emotion-Based Music Recommender</h1>', unsafe_allow_html=True)
    
    # Theme indicator
    if st.session_state.current_emotion:
        theme_name = EMOTION_THEME_NAMES.get(current_emotion, 'Minimal')
        st.markdown(f'<div class="theme-indicator">🎨 Current Theme: {theme_name}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Spotify API Status
        st.subheader("🎧 Spotify API Status")
        if st.session_state.spotify_configured:
            st.success("✅ Spotify API Configured")
            st.info("Using credentials from config.env file")
        else:
            st.warning("⚠️ Spotify API Not Configured")
            st.info("Add your credentials to config.env file")
            st.markdown("""
            **To enable Spotify:**
            1. Edit `config.env` file
            2. Replace placeholder values with your actual credentials
            3. Restart the app
            """)
        
        # Manual Spotify Setup (fallback)
        st.subheader("🔑 Manual Spotify Setup (Optional)")
        st.info("Only if auto-configuration fails")
        
        manual_client_id = st.text_input("Client ID (Manual)", type="password", help="Enter manually if auto-config fails")
        manual_client_secret = st.text_input("Client Secret (Manual)", type="password", help="Enter manually if auto-config fails")
        
        if st.button("🔑 Setup Spotify Manually"):
            if manual_client_id and manual_client_secret:
                success = st.session_state.music_recommender.setup_spotify(manual_client_id, manual_client_secret)
                if success:
                    st.session_state.spotify_configured = True
                    st.success("✅ Spotify API configured manually!")
                else:
                    st.error("❌ Spotify API setup failed!")
            else:
                st.warning("⚠️ Please enter both Client ID and Client Secret")
        
        # Mood History Chart in Sidebar
        st.subheader("📊 Mood History")
        mood_chart = create_mood_history_chart()
        if mood_chart:
            st.plotly_chart(mood_chart, use_container_width=True)
        else:
            st.info("Start emotion detection to see mood history")
        
        # App Information
        st.subheader("ℹ️ About")
        st.markdown("""
        This app detects your emotions in real-time using your webcam and recommends music that matches your mood!
        
        **Features:**
        - 🎥 Real-time emotion detection
        - 🎵 Personalized music recommendations
        - 🎧 Spotify playlist integration
        - 📱 Beautiful, responsive interface
        - 🎨 Dynamic themes based on emotions
        - 📊 Real-time mood tracking
        """)
        
        st.markdown("---")
        st.markdown("**Made with ❤️ for CSE Minor Project**")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📹 Live Camera Feed")
        
        # Camera controls
        camera_col1, camera_col2 = st.columns(2)
        
        with camera_col1:
            if st.button("🎥 Start Camera", key="start_camera"):
                if st.session_state.camera_handler.start_camera():
                    st.session_state.camera_active = True
                    st.success("✅ Camera started successfully!")
                else:
                    st.error("❌ Failed to start camera!")
        
        with camera_col2:
            if st.button("⏹️ Stop Camera", key="stop_camera"):
                st.session_state.camera_handler.stop_camera()
                st.session_state.camera_active = False
                st.success("✅ Camera stopped!")
        
        # Camera status
        if st.session_state.camera_active:
            st.success("🟢 Camera is active")
        else:
            st.warning("🟡 Camera is inactive")
        
        # Camera feed container
        camera_container = st.container()
        
        with camera_container:
            if st.session_state.camera_active:
                # Create a placeholder for the camera feed
                camera_placeholder = st.empty()
                
                # Real-time camera feed
                while st.session_state.camera_active:
                    frame = st.session_state.camera_handler.get_frame()
                    
                    if frame is not None:
                        # Detect emotion every 2 seconds to avoid overwhelming the system
                        current_time = time.time()
                        if current_time - st.session_state.last_detection_time > 2:
                            emotion_info = st.session_state.emotion_detector.detect_emotion(frame)
                            if emotion_info:
                                st.session_state.current_emotion = emotion_info
                                st.session_state.last_detection_time = current_time
                                
                                # Update mood history with new emotion
                                update_mood_history(emotion_info['emotion'], emotion_info['confidence'])
                        
                        # Draw emotion info on frame if available
                        if st.session_state.current_emotion:
                            frame_with_info = st.session_state.emotion_detector.draw_emotion_info(
                                frame, st.session_state.current_emotion
                            )
                        else:
                            frame_with_info = frame
                        
                        # Display the frame
                        camera_placeholder.image(frame_with_info, channels="RGB", use_column_width=True)
                        
                        # Small delay to prevent overwhelming the system
                        time.sleep(0.1)
                    else:
                        st.error("❌ Failed to capture frame from camera")
                        break
            else:
                st.info("📷 Click 'Start Camera' to begin emotion detection")
    
    with col2:
        st.header("😊 Emotion Analysis")
        
        if st.session_state.current_emotion:
            # Display current emotion
            emotion_info = st.session_state.current_emotion
            
            # Animated emoji avatar based on emotion
            emoji = EMOTION_EMOJIS.get(emotion_info['emotion'], '😐')
            st.markdown(f'<div class="emoji-avatar">{emoji}</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="emotion-card">
                <h3>{emotion_info['label']}</h3>
                <p><strong>Confidence:</strong> {emotion_info['confidence']:.2f}</p>
                <p><strong>Genre:</strong> {emotion_info['genre']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Emotion details
            st.subheader("📊 Emotion Breakdown")
            emotions = emotion_info['emotions']
            
            # Create a bar chart of all emotions
            emotion_data = {k: v for k, v in emotions.items()}
            st.bar_chart(emotion_data)
            
        else:
            st.info("👀 No emotion detected yet. Start the camera and show your face!")
        
        st.header("🎵 Music Recommendations")
        
        if st.session_state.current_emotion:
            emotion = st.session_state.current_emotion['emotion']
            
            # Get music recommendations
            playlists = st.session_state.music_recommender.get_recommended_playlists(emotion, 3)
            
            if playlists:
                st.markdown(f"""
                <div class="music-card">
                    <h4>🎶 Recommended for {emotion.title()} Mood</h4>
                    <p>{st.session_state.music_recommender.get_emotion_info(emotion)['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display playlists with like/dislike buttons
                for i, playlist in enumerate(playlists):
                    with st.expander(f"🎵 {playlist['name']}", expanded=(i == 0)):
                        if 'url' in playlist:
                            st.markdown(f"**Source:** {playlist.get('source', 'Default')}")
                            st.markdown(f"**Tracks:** {playlist.get('tracks_total', 'Unknown')}")
                            
                            # Create Spotify link
                            if 'url' in playlist:
                                st.markdown(f"[🎧 Open in Spotify]({playlist['url']})")
                            else:
                                spotify_url = st.session_state.music_recommender.create_spotify_playlist_url(playlist['id'])
                                st.markdown(f"[🎧 Open in Spotify]({spotify_url})")
                        else:
                            st.info("Default playlist - no Spotify link available")
                        
                        # Like/Dislike buttons for user feedback
                        playlist_id = playlist.get('id', f'playlist_{i}')
                        col_like, col_dislike = st.columns(2)
                        
                        with col_like:
                            if st.button(f"👍 Like", key=f"like_{playlist_id}"):
                                handle_user_feedback(playlist_id, 'like')
                                st.success("Thanks for your feedback!")
                        
                        with col_dislike:
                            if st.button(f"👎 Dislike", key=f"dislike_{playlist_id}"):
                                handle_user_feedback(playlist_id, 'dislike')
                                st.success("Thanks for your feedback!")
                        
                        # Show feedback counts
                        if playlist_id in st.session_state.user_feedback:
                            feedback = st.session_state.user_feedback[playlist_id]
                            st.info(f"👍 {feedback['likes']} | 👎 {feedback['dislikes']}")
            else:
                st.warning("⚠️ No playlists available for this emotion")
        else:
            st.info("🎵 Start emotion detection to get music recommendations!")
    
    # Daily Mood Summary Section
    st.markdown("---")
    st.header("📈 Session Summary")
    
    # Show mood summary if we have data
    mood_summary = get_daily_mood_summary()
    if mood_summary:
        st.markdown("""
        <div class="daily-summary">
            <h2>🎯 Daily Mood Summary</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Most Frequent Emotion", 
                mood_summary['most_frequent_emotion'].title(),
                f"{mood_summary['emotion_count']} detections"
            )
        
        with col2:
            st.metric(
                "Average Confidence", 
                f"{mood_summary['avg_confidence']:.2f}",
                "High accuracy"
            )
        
        with col3:
            duration = mood_summary['session_duration']
            st.metric(
                "Session Duration", 
                f"{duration.seconds // 60}m {duration.seconds % 60}s",
                "Active tracking"
            )
        
        # Show top recommended playlist
        if mood_summary['top_playlist']:
            st.subheader("🎵 Top Recommendation")
            playlist = mood_summary['top_playlist']
            st.info(f"**{playlist['name']}** - Best match for your {mood_summary['most_frequent_emotion']} mood!")
            
            if 'url' in playlist:
                st.markdown(f"[🎧 Listen on Spotify]({playlist['url']})")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🎵 Real-Time Emotion-Based Music Recommendation System</p>
        <p>Built with Python, OpenCV, DeepFace, and Streamlit</p>
        <p>Enhanced with dynamic themes, mood tracking, and interactive feedback</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
