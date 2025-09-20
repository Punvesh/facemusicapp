"""
Music Recommendation Module for Real-Time Emotion-Based Music Recommendation App
Maps detected emotions to music genres and fetches playlists from Spotify API
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, List, Optional
import streamlit as st
import requests
import json

class MusicRecommender:
    """
    A class to handle music recommendations based on detected emotions
    Maps emotions to music genres and fetches playlists from Spotify
    """
    
    def __init__(self):
        """Initialize the music recommender"""
        # Emotion to music genre mapping with specific keywords
        self.emotion_to_genre = {
            'happy': {
                'genres': ['pop', 'dance', 'electronic'],
                'mood': 'upbeat',
                'energy': 'high',
                'description': 'Upbeat and energetic music to match your happy mood!'
            },
            'sad': {
                'genres': ['acoustic', 'chill', 'ambient'],
                'mood': 'calm',
                'energy': 'low',
                'description': 'Calming and soothing music to comfort your mood.'
            },
            'angry': {
                'genres': ['rock', 'metal', 'punk'],
                'mood': 'intense',
                'energy': 'high',
                'description': 'Powerful and intense music to channel your energy!'
            },
            'fear': {
                'genres': ['ambient', 'classical', 'instrumental'],
                'mood': 'peaceful',
                'energy': 'low',
                'description': 'Peaceful and calming music to help you relax.'
            },
            'surprise': {
                'genres': ['electronic', 'funk', 'disco'],
                'mood': 'energetic',
                'energy': 'high',
                'description': 'Energetic and fun music to match your surprise!'
            },
            'disgust': {
                'genres': ['alternative', 'indie', 'experimental'],
                'mood': 'unique',
                'energy': 'medium',
                'description': 'Unique and interesting music for your mood.'
            },
            'neutral': {
                'genres': ['lo-fi', 'instrumental', 'jazz'],
                'mood': 'relaxed',
                'energy': 'medium',
                'description': 'Relaxed and chill music for your neutral mood.'
            }
        }
        
        # Default playlists for each emotion (Spotify playlist IDs)
        self.default_playlists = {
            'happy': [
                {'name': 'Happy Hits', 'id': '37i9dQZF1DX3XNs9D5lWnM'},
                {'name': 'Dance Party', 'id': '37i9dQZF1DXcBWIGoYBM5M'},
                {'name': 'Pop Mix', 'id': '37i9dQZF1DXcF6B6QPhFDv'}
            ],
            'sad': [
                {'name': 'Chill Vibes', 'id': '37i9dQZF1DX4WYpdgoIcn6'},
                {'name': 'Acoustic Covers', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Peaceful Piano', 'id': '37i9dQZF1DX7KNKjOK0o75'}
            ],
            'angry': [
                {'name': 'Rock Classics', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Metal Essentials', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Punk Rock', 'id': '37i9dQZF1DX5Vy6DFOcx00'}
            ],
            'fear': [
                {'name': 'Ambient Relaxation', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Classical Music', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Nature Sounds', 'id': '37i9dQZF1DX5Vy6DFOcx00'}
            ],
            'surprise': [
                {'name': 'Electronic Beats', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Funk & Soul', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Disco Hits', 'id': '37i9dQZF1DX5Vy6DFOcx00'}
            ],
            'disgust': [
                {'name': 'Alternative Rock', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Indie Vibes', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Experimental', 'id': '37i9dQZF1DX5Vy6DFOcx00'}
            ],
            'neutral': [
                {'name': 'Lo-Fi Beats', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Instrumental', 'id': '37i9dQZF1DX5Vy6DFOcx00'},
                {'name': 'Jazz Vibes', 'id': '37i9dQZF1DX5Vy6DFOcx00'}
            ]
        }
        
        # Initialize Spotify client (will be set up in setup_spotify)
        self.spotify_client = None
        self.spotify_configured = False
        
    def setup_spotify(self, client_id: str, client_secret: str) -> bool:
        """
        Set up Spotify API client
        
        Args:
            client_id (str): Spotify Client ID
            client_secret (str): Spotify Client Secret
            
        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            if client_id and client_secret:
                # Set up Spotify client credentials
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
                
                self.spotify_client = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager
                )
                
                # Test the connection
                self.spotify_client.user_playlists('spotify')
                self.spotify_configured = True
                return True
            else:
                st.warning("⚠️ Spotify credentials not provided. Using default playlists only.")
                return False
                
        except Exception as e:
            st.warning(f"⚠️ Spotify setup failed: {str(e)}. Using default playlists only.")
            return False
    
    def get_emotion_info(self, emotion: str) -> Dict:
        """
        Get detailed information about an emotion and its music preferences
        
        Args:
            emotion (str): Detected emotion
            
        Returns:
            Dict: Emotion information including genres and description
        """
        return self.emotion_to_genre.get(emotion, {
            'genres': ['pop'],
            'mood': 'neutral',
            'energy': 'medium',
            'description': 'Music to match your current mood.'
        })
    
    def get_recommended_playlists(self, emotion: str, limit: int = 3) -> List[Dict]:
        """
        Get recommended playlists for a detected emotion
        
        Args:
            emotion (str): Detected emotion
            limit (int): Maximum number of playlists to return
            
        Returns:
            List[Dict]: List of recommended playlists
        """
        if emotion not in self.emotion_to_genre:
            emotion = 'neutral'  # Default to neutral if emotion not recognized
        
        # Get default playlists for the emotion
        playlists = self.default_playlists.get(emotion, [])
        
        # If Spotify is configured, try to get real playlists
        if self.spotify_configured and self.spotify_client:
            try:
                # Search for playlists based on emotion and genre
                emotion_info = self.get_emotion_info(emotion)
                search_query = f"{emotion} {emotion_info['mood']} music"
                
                results = self.spotify_client.search(
                    q=search_query,
                    type='playlist',
                    limit=limit
                )
                
                if results and 'playlists' in results and results['playlists']['items']:
                    spotify_playlists = []
                    for playlist in results['playlists']['items'][:limit]:
                        spotify_playlists.append({
                            'name': playlist['name'],
                            'id': playlist['id'],
                            'url': playlist['external_urls']['spotify'],
                            'description': playlist.get('description', ''),
                            'tracks_total': playlist['tracks']['total'],
                            'source': 'Spotify'
                        })
                    
                    # Combine with default playlists
                    playlists = spotify_playlists + playlists[:max(0, limit - len(spotify_playlists))]
                
            except Exception as e:
                st.warning(f"⚠️ Could not fetch Spotify playlists: {str(e)}")
        
        # Ensure we return the requested number of playlists
        return playlists[:limit]
    
    def get_playlist_tracks(self, playlist_id: str, limit: int = 5) -> List[Dict]:
        """
        Get tracks from a specific playlist
        
        Args:
            playlist_id (str): Spotify playlist ID
            limit (int): Maximum number of tracks to return
            
        Returns:
            List[Dict]: List of tracks in the playlist
        """
        if not self.spotify_configured or not self.spotify_client:
            return []
        
        try:
            results = self.spotify_client.playlist_tracks(playlist_id, limit=limit)
            
            if results and 'items' in results:
                tracks = []
                for item in results['items']:
                    track = item['track']
                    if track:
                        tracks.append({
                            'name': track['name'],
                            'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                            'album': track['album']['name'],
                            'url': track['external_urls']['spotify'],
                            'duration_ms': track['duration_ms']
                        })
                return tracks
            
        except Exception as e:
            st.warning(f"⚠️ Could not fetch playlist tracks: {str(e)}")
        
        return []
    
    def create_spotify_playlist_url(self, playlist_id: str) -> str:
        """
        Create a Spotify playlist URL
        
        Args:
            playlist_id (str): Spotify playlist ID
            
        Returns:
            str: Full Spotify playlist URL
        """
        return f"https://open.spotify.com/playlist/{playlist_id}"
    
    def get_music_recommendation_summary(self, emotion: str) -> str:
        """
        Get a summary of music recommendations for an emotion
        
        Args:
            emotion (str): Detected emotion
            
        Returns:
            str: Summary of music recommendations
        """
        emotion_info = self.get_emotion_info(emotion)
        playlists = self.get_recommended_playlists(emotion, 1)
        
        summary = f"🎵 **{emotion_info['description']}**\n\n"
        summary += f"**Recommended Genres:** {', '.join(emotion_info['genres'])}\n"
        summary += f"**Mood:** {emotion_info['mood'].title()}\n"
        summary += f"**Energy Level:** {emotion_info['energy'].title()}\n\n"
        
        if playlists:
            summary += f"**Top Playlist:** {playlists[0]['name']}\n"
            if 'url' in playlists[0]:
                summary += f"🎧 [Listen on Spotify]({playlists[0]['url']})"
        
        return summary
