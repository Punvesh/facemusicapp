"""
Configuration file for Emotion-Based Music Recommendation App
Centralized settings for easy customization
"""

# Camera Configuration
CAMERA_CONFIG = {
    'default_width': 640,
    'default_height': 480,
    'default_fps': 30,
    'camera_indices': [0, 1, 2, 3],  # Try these camera indices
    'auto_detect': True
}

# Emotion Detection Configuration
EMOTION_CONFIG = {
    'confidence_threshold': 0.3,  # Minimum confidence for emotion detection
    'detection_interval': 2.0,    # Seconds between emotion detections
    'detector_backend': 'opencv',  # DeepFace detector backend
    'enforce_detection': False     # Don't enforce strict face detection
}

# Music Recommendation Configuration
MUSIC_CONFIG = {
    'default_playlist_limit': 3,   # Number of playlists to recommend
    'spotify_search_limit': 5,     # Spotify API search limit
    'enable_spotify': True,        # Enable Spotify integration
    'fallback_to_default': True    # Use default playlists if Spotify fails
}

# UI Configuration
UI_CONFIG = {
    'page_title': 'Emotion-Based Music Recommender',
    'page_icon': '🎵',
    'layout': 'wide',
    'sidebar_state': 'expanded',
    'theme': 'light'
}

# Spotify API Configuration
SPOTIFY_CONFIG = {
    'api_base_url': 'https://api.spotify.com/v1',
    'auth_url': 'https://accounts.spotify.com/api/token',
    'redirect_uri': 'http://localhost:8501',
    'scope': 'playlist-read-private,playlist-read-collaborative'
}

# Emotion to Music Genre Mapping
EMOTION_GENRE_MAPPING = {
    'happy': {
        'genres': ['pop', 'dance', 'electronic'],
        'mood': 'upbeat',
        'energy': 'high',
        'description': 'Upbeat and energetic music to match your happy mood!',
        'color': '#FFD700'  # Gold
    },
    'sad': {
        'genres': ['acoustic', 'chill', 'ambient'],
        'mood': 'calm',
        'energy': 'low',
        'description': 'Calming and soothing music to comfort your mood.',
        'color': '#87CEEB'  # Sky Blue
    },
    'angry': {
        'genres': ['rock', 'metal', 'punk'],
        'mood': 'intense',
        'energy': 'high',
        'description': 'Powerful and intense music to channel your energy!',
        'color': '#FF4500'  # Orange Red
    },
    'fear': {
        'genres': ['ambient', 'classical', 'instrumental'],
        'mood': 'peaceful',
        'energy': 'low',
        'description': 'Peaceful and calming music to help you relax.',
        'color': '#9370DB'  # Medium Purple
    },
    'surprise': {
        'genres': ['electronic', 'funk', 'disco'],
        'mood': 'energetic',
        'energy': 'high',
        'description': 'Energetic and fun music to match your surprise!',
        'color': '#FF69B4'  # Hot Pink
    },
    'disgust': {
        'genres': ['alternative', 'indie', 'experimental'],
        'mood': 'unique',
        'energy': 'medium',
        'description': 'Unique and interesting music for your mood.',
        'color': '#32CD32'  # Lime Green
    },
    'neutral': {
        'genres': ['lo-fi', 'instrumental', 'jazz'],
        'mood': 'relaxed',
        'energy': 'medium',
        'description': 'Relaxed and chill music for your neutral mood.',
        'color': '#808080'  # Gray
    }
}

# Default Playlists (Fallback when Spotify is not available)
DEFAULT_PLAYLISTS = {
    'happy': [
        {'name': 'Happy Hits', 'id': '37i9dQZF1DX3XNs9D5lWnM', 'description': 'Upbeat pop and dance hits'},
        {'name': 'Dance Party', 'id': '37i9dQZF1DXcBWIGoYBM5M', 'description': 'High-energy dance music'},
        {'name': 'Pop Mix', 'id': '37i9dQZF1DXcF6B6QPhFDv', 'description': 'Popular pop songs'}
    ],
    'sad': [
        {'name': 'Chill Vibes', 'id': '37i9dQZF1DX4WYpdgoIcn6', 'description': 'Relaxing chill music'},
        {'name': 'Acoustic Covers', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Beautiful acoustic covers'},
        {'name': 'Peaceful Piano', 'id': '37i9dQZF1DX7KNKjOK0o75', 'description': 'Calming piano music'}
    ],
    'angry': [
        {'name': 'Rock Classics', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Classic rock anthems'},
        {'name': 'Metal Essentials', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Essential metal tracks'},
        {'name': 'Punk Rock', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'High-energy punk music'}
    ],
    'fear': [
        {'name': 'Ambient Relaxation', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Peaceful ambient sounds'},
        {'name': 'Classical Music', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Beautiful classical pieces'},
        {'name': 'Nature Sounds', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Soothing nature sounds'}
    ],
    'surprise': [
        {'name': 'Electronic Beats', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Electronic music beats'},
        {'name': 'Funk & Soul', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Funky soul music'},
        {'name': 'Disco Hits', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Classic disco tracks'}
    ],
    'disgust': [
        {'name': 'Alternative Rock', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Alternative rock music'},
        {'name': 'Indie Vibes', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Indie music vibes'},
        {'name': 'Experimental', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Experimental music'}
    ],
    'neutral': [
        {'name': 'Lo-Fi Beats', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Relaxing lo-fi music'},
        {'name': 'Instrumental', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Beautiful instrumental music'},
        {'name': 'Jazz Vibes', 'id': '37i9dQZF1DX5Vy6DFOcx00', 'description': 'Smooth jazz music'}
    ]
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'max_frame_processing_time': 0.1,  # Maximum time to process each frame
    'memory_cleanup_interval': 100,    # Clean up memory every N frames
    'enable_frame_skipping': True,     # Skip frames if processing is slow
    'max_queue_size': 10              # Maximum size of frame processing queue
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'app.log',
    'max_file_size': 1024 * 1024,  # 1MB
    'backup_count': 3
}

# Error Handling Configuration
ERROR_CONFIG = {
    'max_retries': 3,
    'retry_delay': 1.0,
    'show_error_details': True,
    'log_errors': True,
    'graceful_degradation': True
}
