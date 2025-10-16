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
import streamlit.components.v1 as components
import requests

# Sticky header and utility CSS additions
STICKY_CSS = """
<style>
  .sticky-header {
    position: sticky; top: 0; z-index: 1000; background: rgba(18,18,18,0.9);
    backdrop-filter: blur(6px); border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 0.6rem 0.8rem; margin-bottom: 0.8rem; border-radius: 8px;
  }
  .chip {display:inline-block;padding:4px 10px;border-radius:999px;font-size:12px;margin-right:6px;background:rgba(255,255,255,0.08);}
  .separator {height:1px;background:rgba(255,255,255,0.08);margin:8px 0 0 0}
  .skeleton {background: linear-gradient(90deg, #2a2a2a 25%, #333 37%, #2a2a2a 63%); background-size: 400% 100%; animation: shimmer 1.4s ease infinite; border-radius: 12px;}
  @keyframes shimmer {0%{background-position: 200% 0}100%{background-position: -200% 0}}
  /* Album-style card */
  .album-card {border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); margin: 14px 0;}
  .album-hero {display:flex; align-items:center; gap:22px; padding:22px; background: linear-gradient(135deg, #1f1f1f, #2a2a2a);}
  .album-cover {width:120px; height:120px; border-radius:8px; object-fit:cover; box-shadow:0 8px 24px rgba(0,0,0,0.45);}
  .album-title {font-size:1.8rem; font-weight:900; margin:0;}
  .album-meta {font-size:0.85rem; color:#c8c8c8; margin-top:4px;}
  .album-body {padding:12px 18px; background:#111;}
  .badge {display:inline-block;padding:3px 8px;border-radius:999px;font-size:11px;margin-right:6px;background:rgba(255,255,255,0.08);}
</style>
"""

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
    # NEW: preferred language for recommendations
    if 'preferred_language' not in st.session_state:
        st.session_state.preferred_language = 'auto'
    # NEW: global inline play preference
    if 'play_inline_default' not in st.session_state:
        st.session_state.play_inline_default = True
    # thumbnail cache for spotify oEmbed
    if 'thumb_cache' not in st.session_state:
        st.session_state.thumb_cache = {}

# Emotion to emoji mapping for animated avatar
EMOTION_EMOJIS = {
    'happy': '\U0001F600',
    'sad': '😢',
    'angry': '😡',
    'fear': '😨',
    'surprise': '\U0001F62E',
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
        playlists = st.session_state.music_recommender.get_recommended_playlists(most_frequent_emotion, 1, language=st.session_state.preferred_language if st.session_state.preferred_language != 'auto' else None)
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

# Helper: fetch Spotify thumbnail via oEmbed (UI-only)
def get_spotify_thumbnail(spotify_url: str) -> str:
    if not spotify_url:
        return ""
    cache = st.session_state.thumb_cache
    if spotify_url in cache:
        return cache[spotify_url]
    try:
        resp = requests.get("https://open.spotify.com/oembed", params={"url": spotify_url}, timeout=4)
        if resp.ok:
            data = resp.json()
            thumb = data.get("thumbnail_url", "")
            cache[spotify_url] = thumb
            return thumb
    except Exception:
        pass
    return ""

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
    st.markdown(STICKY_CSS, unsafe_allow_html=True)

    # Sticky header bar (UI only)
    header_color = EMOTION_THEMES.get(current_emotion, '#808080')
    with st.container():
        st.markdown(
            f"""
            <div class="sticky-header">
              <span style="font-size:1.25rem;font-weight:700;">🎵 Emotion-Based Music Recommender</span>
              <span class="chip">Theme: {EMOTION_THEME_NAMES.get(current_emotion,'Minimal')}</span>
              <span class="chip">Language: {('Auto' if st.session_state.preferred_language=='auto' else st.session_state.preferred_language.title())}</span>
              <span class="chip" style="background:{('#1DB954' if st.session_state.get('camera_active') else '#7a7a7a')};color:white;">{('Camera On' if st.session_state.get('camera_active') else 'Camera Off')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

        # Preferred Language selector (existing)
        st.subheader("🌐 Preferred Language")
        lang_choice = st.selectbox(
            "Choose your preferred language",
            ["Auto (All)", "Telugu", "Tamil", "Kannada", "Hindi"],
            index=["Auto (All)", "Telugu", "Tamil", "Kannada", "Hindi"].index({
                'auto': "Auto (All)", 'telugu': "Telugu", 'tamil': "Tamil", 'kannada': "Kannada", 'hindi': "Hindi"
            }.get(st.session_state.preferred_language, "Auto (All)"))
        )
        st.session_state.preferred_language = ('auto' if lang_choice.startswith('Auto') else lang_choice.lower())

        # NEW: Global inline play toggle (UI only)
        st.subheader("▶ Playback")
        st.session_state.play_inline_default = st.toggle("Play playlists inline by default", value=st.session_state.play_inline_default)

        # Mood History in Sidebar (compact)
        st.subheader("📊 Mood History")
        mood_chart = create_mood_history_chart()
        if mood_chart:
            st.plotly_chart(mood_chart, use_container_width=True)
        else:
            st.info("Start emotion detection to see mood history")

        st.markdown("---")
        st.markdown("**Made with ❤️ for CSE Minor Project**")

    # Tabs layout
    tab_camera, tab_reco, tab_history, tab_summary = st.tabs(["📹 Camera", "🎵 Recommendations", "📈 History", "🧾 Summary"])

    # Camera Tab
    with tab_camera:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.header("📹 Live Camera Feed")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🎥 Start Camera", key="start_camera_btn"):
                    if st.session_state.camera_handler.start_camera():
                        st.session_state.camera_active = True
                        st.success("✅ Camera started successfully!")
                        try:
                            st.toast("Camera started", icon="🎥")
                        except Exception:
                            pass
                    else:
                        st.error("❌ Failed to start camera!")
            with c2:
                if st.button("⏹️ Stop Camera", key="stop_camera_btn"):
                    st.session_state.camera_handler.stop_camera()
                    st.session_state.camera_active = False
                    st.success("✅ Camera stopped!")
                    try:
                        st.toast("Camera stopped", icon="⏹️")
                    except Exception:
                        pass

            if st.session_state.get('camera_active'):
                st.success("🟢 Camera is active")
            else:
                st.warning("🟡 Camera is inactive")

            feed_placeholder = st.empty()
            if st.session_state.get('camera_active'):
                with st.spinner('Detecting emotions...'):
                    feed_placeholder.markdown('<div class="skeleton" style="height:260px"></div>', unsafe_allow_html=True)
                # Stream frames
                while st.session_state.camera_active:
                    frame = st.session_state.camera_handler.get_frame()
                    if frame is not None:
                        current_time = time.time()
                        if current_time - st.session_state.last_detection_time > 2:
                            emotion_info = st.session_state.emotion_detector.detect_emotion(frame)
                            if emotion_info:
                                st.session_state.current_emotion = emotion_info
                                st.session_state.last_detection_time = current_time
                                update_mood_history(emotion_info['emotion'], emotion_info['confidence'])
                        frame_with_info = frame if not st.session_state.current_emotion else st.session_state.emotion_detector.draw_emotion_info(frame, st.session_state.current_emotion)
                        feed_placeholder.image(frame_with_info, channels="RGB", use_column_width=True)
                        time.sleep(0.1)
                    else:
                        st.error("❌ Failed to capture frame from camera")
                        break
            else:
                st.info("📷 Click 'Start Camera' to begin emotion detection")

        with col2:
            st.header("😊 Emotion Analysis")
            if st.session_state.current_emotion:
                emotion_info = st.session_state.current_emotion
                emoji = EMOTION_EMOJIS.get(emotion_info['emotion'], '😐')
                st.markdown(f'<div class="emoji-avatar">{emoji}</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="emotion-card">
                    <h3>{emotion_info['label']}</h3>
                    <p><strong>Confidence:</strong> {emotion_info['confidence']:.2f}</p>
                    <p><strong>Genre:</strong> {emotion_info['genre']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.subheader("📊 Emotion Breakdown")
                st.bar_chart({k: v for k, v in emotion_info['emotions'].items()})
            else:
                st.info("👀 No emotion detected yet. Start the camera and show your face!")
                      # Browser camera snapshot fallback (works on Render)
        st.subheader("📸 Browser Camera (Snapshot)")
        snap = st.camera_input("Take a photo")
        if snap is not None:
            try:
                # Convert snapshot to numpy RGB frame
                img = Image.open(snap)
                frame = np.array(img.convert('RGB'))
                # Run existing detector
                emotion_info = st.session_state.emotion_detector.detect_emotion(frame)
                if emotion_info:
                    st.session_state.current_emotion = emotion_info
                    update_mood_history(emotion_info['emotion'], emotion_info['confidence'])
                    st.success(f"Detected: {emotion_info['label']} — {emotion_info['genre']}")
                    st.image(frame, caption="Snapshot", use_column_width=True)
                else:
                    st.warning("No face/emotion detected. Try another snapshot with better lighting.")
            except Exception as e:
                st.warning(f"Could not process snapshot: {e}")


        # NEW: Centered Recommendations section below camera
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
        st.subheader("🎵 Recommended for You")
        center_left, center_mid, center_right = st.columns([1, 2, 1])
        with center_mid:
            if st.session_state.current_emotion:
                emotion = st.session_state.current_emotion['emotion']
                language_param = st.session_state.preferred_language if st.session_state.preferred_language != 'auto' else None
                playlists = st.session_state.music_recommender.get_recommended_playlists(emotion, 3, language=language_param)
                if playlists:
                    st.markdown(f"""
                    <div class="music-card">
                        <h4>🎶 Recommended for {emotion.title()} Mood</h4>
                        <p>{st.session_state.music_recommender.get_emotion_info(emotion)['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    for i, playlist in enumerate(playlists):
                        with st.expander(f"🎵 {playlist['name']}", expanded=(i == 0)):
                            lang_tag = playlist.get('language') or (st.session_state.preferred_language if st.session_state.preferred_language != 'auto' else None)
                            if lang_tag:
                                st.caption(f"🌐 Language: {lang_tag.title()}")
                            spotify_url = playlist.get('url')
                            if not spotify_url and playlist.get('id'):
                                spotify_url = st.session_state.music_recommender.create_spotify_playlist_url(playlist['id'])
                            # Album-style header
                            cover = get_spotify_thumbnail(spotify_url) if spotify_url else ""
                            title = playlist['name']
                            meta = f"{playlist.get('source','Default')} • {playlist.get('tracks_total','Unknown')} tracks"
                            hero_bg = EMOTION_THEMES.get(emotion, '#1f1f1f')
                            st.markdown(
                                f"""
                                <div class="album-card">
                                  <div class="album-hero" style="background: linear-gradient(135deg, {hero_bg}55, #1b1b1b 70%);">
                                    <img class="album-cover" src="{cover}" onerror="this.style.display='none'" />
                                    <div>
                                      <div class="album-title">{title}</div>
                                      <div class="album-meta">{meta}</div>
                                      <div style="margin-top:6px;">
                                        {'<span class="badge">'+lang_tag.title()+'</span>' if lang_tag else ''}
                                      </div>
                                    </div>
                                  </div>
                                  <div class="album-body"></div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            if spotify_url:
                                st.markdown(f"[🎧 Open in Spotify]({spotify_url})")
                                # Auto-embed based on global setting (no per-card prompt)
                                if st.session_state.play_inline_default:
                                    try:
                                        embed_url = spotify_url.replace('open.spotify.com/', 'open.spotify.com/embed/')
                                        components.iframe(embed_url, height=380)
                                    except Exception:
                                        st.info("Unable to embed player. Use the Spotify link above.")
                            else:
                                st.info("Default playlist - no Spotify link available")
                            playlist_id = playlist.get('id', f'playlist_{i}')
                            unique_key = f"cam_{playlist_id}_{emotion}_{st.session_state.preferred_language}_{i}"
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("👍 Like", key=f"like_{unique_key}"):
                                    handle_user_feedback(playlist_id, 'like')
                                    try:
                                        st.toast("Added Like", icon="👍")
                                    except Exception:
                                        pass
                                    st.success("Thanks for your feedback!")
                            with c2:
                                if st.button("👎 Dislike", key=f"dislike_{unique_key}"):
                                    handle_user_feedback(playlist_id, 'dislike')
                                    try:
                                        st.toast("Added Dislike", icon="👎")
                                    except Exception:
                                        pass
                                    st.success("Thanks for your feedback!")
                            if playlist_id in st.session_state.user_feedback:
                                fb = st.session_state.user_feedback[playlist_id]
                                st.info(f"👍 {fb['likes']} | 👎 {fb['dislikes']}")
                else:
                    st.warning("⚠️ No playlists available for this emotion")
            else:
                st.info("Recommendations will appear once an emotion is detected.")

    # Recommendations Tab
    with tab_reco:
        st.header("🎵 Music Recommendations")
        if st.session_state.current_emotion:
            emotion = st.session_state.current_emotion['emotion']
            language_param = st.session_state.preferred_language if st.session_state.preferred_language != 'auto' else None
            playlists = st.session_state.music_recommender.get_recommended_playlists(emotion, 3, language=language_param)
            if playlists:
                st.markdown(f"""
                <div class="music-card">
                    <h4>🎶 Recommended for {emotion.title()} Mood</h4>
                    <p>{st.session_state.music_recommender.get_emotion_info(emotion)['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                for i, playlist in enumerate(playlists):
                    with st.expander(f"🎵 {playlist['name']}", expanded=(i == 0)):
                        lang_tag = playlist.get('language') or (st.session_state.preferred_language if st.session_state.preferred_language != 'auto' else None)
                        if lang_tag:
                            st.caption(f"🌐 Language: {lang_tag.title()}")
                        spotify_url = playlist.get('url')
                        if not spotify_url and playlist.get('id'):
                            spotify_url = st.session_state.music_recommender.create_spotify_playlist_url(playlist['id'])
                        cover = get_spotify_thumbnail(spotify_url) if spotify_url else ""
                        title = playlist['name']
                        meta = f"{playlist.get('source','Default')} • {playlist.get('tracks_total','Unknown')} tracks"
                        hero_bg = EMOTION_THEMES.get(emotion, '#1f1f1f')
                        header_html = (
                            '<div class="sticky-header">'
                            '<span style="font-size:1.25rem;font-weight:700;">🎵 Emotion-Based Music Recommender</span>'
                            '<span class="chip">Theme: ' + EMOTION_THEME_NAMES.get(current_emotion, 'Minimal') + '</span>'
                            '<span class="chip">Language: ' + ('Auto' if st.session_state.preferred_language == 'auto' else st.session_state.preferred_language.title()) + '</span>'
                            '<span class="chip" style="background:' + ('#1DB954' if st.session_state.get('camera_active') else '#7a7a7a') + ';color:white;">' + ('Camera On' if st.session_state.get('camera_active') else 'Camera Off') + '</span>'
                            '</div>'
                        )
                        st.markdown(header_html, unsafe_allow_html=True)
                        if spotify_url:
                            st.markdown(f"[🎧 Open in Spotify]({spotify_url})")
                            # Auto-embed based on global setting
                            if st.session_state.play_inline_default:
                                try:
                                    embed_url = spotify_url.replace('open.spotify.com/', 'open.spotify.com/embed/')
                                    components.iframe(embed_url, height=380)
                                except Exception:
                                    st.info("Unable to embed player. Use the Spotify link above.")
                        else:
                            st.info("Default playlist - no Spotify link available")
                        playlist_id = playlist.get('id', f'playlist_{i}')
                        unique_suffix = f"{playlist_id}_{emotion}_{st.session_state.preferred_language}_{i}"
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("👍 Like", key=f"like_{unique_suffix}"):
                                handle_user_feedback(playlist_id, 'like')
                                try:
                                    st.toast("Added Like", icon="👍")
                                except Exception:
                                    pass
                                st.success("Thanks for your feedback!")
                        with c2:
                            if st.button("👎 Dislike", key=f"dislike_{unique_suffix}"):
                                handle_user_feedback(playlist_id, 'dislike')
                                try:
                                    st.toast("Added Dislike", icon="👎")
                                except Exception:
                                    pass
                                st.success("Thanks for your feedback!")
                        if playlist_id in st.session_state.user_feedback:
                            fb = st.session_state.user_feedback[playlist_id]
                            st.info(f"👍 {fb['likes']} | 👎 {fb['dislikes']}")
            else:
                st.warning("⚠️ No playlists available for this emotion")
        else:
            st.info("🎵 Start emotion detection to get music recommendations!")

    # History Tab
    with tab_history:
        st.header("📈 Mood History")
        chart = create_mood_history_chart()
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No history yet. Start the camera to build your timeline.")

    # Summary Tab
    with tab_summary:
        st.header("🧾 Session Summary")
        mood_summary = get_daily_mood_summary()
        if mood_summary:
            st.markdown("""
            <div class="daily-summary">
                <h2>🎯 Daily Mood Summary</h2>
            </div>
            """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Most Frequent Emotion", mood_summary['most_frequent_emotion'].title(), f"{mood_summary['emotion_count']} detections")
            with col2:
                st.metric("Average Confidence", f"{mood_summary['avg_confidence']:.2f}", "High accuracy")
            with col3:
                dur = mood_summary['session_duration']
                st.metric("Session Duration", f"{dur.seconds // 60}m {dur.seconds % 60}s", "Active tracking")
            if mood_summary['top_playlist'] and mood_summary['top_playlist'].get('name'):
                st.subheader("🎵 Top Recommendation")
                p = mood_summary['top_playlist']
                st.info(f"**{p['name']}** - Best match for your {mood_summary['most_frequent_emotion']} mood!")
                if p.get('url'):
                    st.markdown(f"[🎧 Listen on Spotify]({p['url']})")
        else:
            st.info("Summary will appear after some detections.")

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
