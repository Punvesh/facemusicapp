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
        
        # NEW: Language-specific default playlists (fallbacks)
        # Note: IDs are placeholders; replace with real regional playlists if desired
        self.default_playlists_by_language: Dict[str, Dict[str, List[Dict]]] = {
            'telugu': {
                'happy': [{'name': 'Telugu Party', 'id': '37i9dQZF1DX0XUfTFmNBRM'}],
                'sad': [{'name': 'Telugu Melodies', 'id': '37i9dQZF1DX8HU1L2vQ4dH'}],
                'neutral': [{'name': 'Telugu Chill', 'id': '37i9dQZF1DXbYFKu7Gx0xK'}],
                'angry': [{'name': 'Telugu Rock Mix', 'id': '37i9dQZF1DX8z1uyQZB0QG'}],
                'surprise': [{'name': 'Telugu Electronic', 'id': '37i9dQZF1DX9tPFwDMOaN1'}]
            },
            'tamil': {
                'happy': [{'name': 'Tamil Hits', 'id': '37i9dQZF1DX72V5L1FZ8V2'}],
                'sad': [{'name': 'Tamil Melodies', 'id': '37i9dQZF1DXbJx0B3bKcEb'}],
                'neutral': [{'name': 'Tamil Chill', 'id': '37i9dQZF1DX0XUY2hEjrCW'}],
                'angry': [{'name': 'Tamil Rock Mix', 'id': '37i9dQZF1DX2bI3oPAWZ2U'}],
                'surprise': [{'name': 'Tamil Electronic', 'id': '37i9dQZF1DX2i3gd2hGRqy'}]
            },
            'kannada': {
                'happy': [{'name': 'Kannada Party', 'id': '37i9dQZF1DX0hWmn8d5pRe'}],
                'sad': [{'name': 'Kannada Melodies', 'id': '37i9dQZF1DXd1Bo4QJ3nxb'}],
                'neutral': [{'name': 'Kannada Chill', 'id': '37i9dQZF1DX8O2z5Vd2G8X'}],
                'angry': [{'name': 'Kannada Rock Mix', 'id': '37i9dQZF1DX4jSp9oQ7G5D'}],
                'surprise': [{'name': 'Kannada Electronic', 'id': '37i9dQZF1DX7RZ9k1l0Qj7'}]
            },
            'hindi': {
                'happy': [{'name': 'Bollywood Dance', 'id': '37i9dQZF1DXdFesNN9TzXt'}],
                'sad': [{'name': 'Bollywood Melancholy', 'id': '37i9dQZF1DX7K31D69s4M1'}],
                'neutral': [{'name': 'Lo-fi Hindi', 'id': '37i9dQZF1DX4wta20PHgwo'}],
                'angry': [{'name': 'Hindi Rock Mix', 'id': '37i9dQZF1DX7cLxqtNO3zl'}],
                'surprise': [{'name': 'Hindi Electronic', 'id': '37i9dQZF1DX1i0j9Jz3Z4U'}]
            }
        }
        
        # Initialize Spotify client (will be set up in setup_spotify)
        self.spotify_client = None
        self.spotify_configured = False
        
    def setup_spotify(self, client_id: str, client_secret: str) -> bool:
        """
        Set up Spotify API client
        """
        try:
            if client_id and client_secret:
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
        """Get detailed information about an emotion and its music preferences"""
        return self.emotion_to_genre.get(emotion, {
            'genres': ['pop'],
            'mood': 'neutral',
            'energy': 'medium',
            'description': 'Music to match your current mood.'
        })

    def _language_normalize(self, language: Optional[str]) -> Optional[str]:
        if not language:
            return None
        lang = language.strip().lower()
        aliases = {
            'telegu': 'telugu',
            'bangla': 'bengali',
            'hindhi': 'hindi'
        }
        return aliases.get(lang, lang)

    def _language_defaults(self, emotion: str, language: Optional[str]) -> List[Dict]:
        lang = self._language_normalize(language)
        if not lang:
            return []
        lang_map = self.default_playlists_by_language.get(lang, {})
        return lang_map.get(emotion, [])
    
    def get_recommended_playlists(self, emotion: str, limit: int = 3, language: Optional[str] = None) -> List[Dict]:
        """
        Get recommended playlists for a detected emotion
        Optionally bias results by preferred language (e.g., telugu, tamil, kannada, hindi)
        """
        if emotion not in self.emotion_to_genre:
            emotion = 'neutral'
        
        # Start with defaults
        playlists = self.default_playlists.get(emotion, [])
        
        # Try language-specific defaults early to ensure at least one localized option
        lang_defaults = self._language_defaults(emotion, language)
        if lang_defaults:
            playlists = lang_defaults + playlists
        
        # If Spotify is configured, try to search language-aware playlists
        if self.spotify_configured and self.spotify_client:
            try:
                emotion_info = self.get_emotion_info(emotion)
                mood = emotion_info.get('mood', '')
                lang = self._language_normalize(language)
                
                queries: List[str] = []
                if lang:
                    # Language + mood/emotion combinations
                    queries.append(f"{lang} {mood} music")
                    queries.append(f"{lang} {emotion} playlist")
                    # Language + genre fallbacks
                    for g in emotion_info.get('genres', [])[:2]:
                        queries.append(f"{lang} {g} playlist")
                else:
                    queries.append(f"{emotion} {mood} music")
                
                found: List[Dict] = []
                seen_ids = set()
                for q in queries:
                    results = self.spotify_client.search(q=q, type='playlist', limit=limit, market='IN') or {}
                    playlists_blob = results.get('playlists') or {}
                    items = playlists_blob.get('items', []) or []
                    for item in items:
                        if not item:
                            continue
                        pid = item.get('id')
                        if not pid or pid in seen_ids:
                            continue
                        seen_ids.add(pid)
                        external_urls = item.get('external_urls') or {}
                        tracks_info = item.get('tracks') or {}
                        found.append({
                            'name': item.get('name', 'Playlist'),
                            'id': pid,
                            'url': external_urls.get('spotify'),
                            'description': item.get('description', ''),
                            'tracks_total': tracks_info.get('total'),
                            'source': 'Spotify',
                            'language': lang or 'auto'
                        })
                        if len(found) >= limit:
                            break
                    if len(found) >= limit:
                        break
                
                if found:
                    playlists = found + playlists
            except Exception as e:
                st.warning(f"⚠️ Could not fetch Spotify playlists: {str(e)}")
        
        # Enrich defaults that lack URLs by resolving via Spotify name search (best-effort)
        if self.spotify_configured and self.spotify_client:
            try:
                enriched: List[Dict] = []
                lang = self._language_normalize(language) or 'auto'
                for p in playlists:
                    if not p.get('url') and p.get('name'):
                        q = p['name']
                        if lang != 'auto':
                            q = f"{lang} {q}"
                        res = self.spotify_client.search(q=q, type='playlist', limit=1, market='IN') or {}
                        playlists_blob = res.get('playlists') or {}
                        items = playlists_blob.get('items', []) or []
                        if items:
                            item = items[0] or {}
                            external_urls = item.get('external_urls') or {}
                            tracks_info = item.get('tracks') or {}
                            resolved_id = item.get('id') or p.get('id')
                            if resolved_id and external_urls.get('spotify'):
                                p = {
                                    **p,
                                    'id': resolved_id,
                                    'url': external_urls.get('spotify'),
                                    'tracks_total': tracks_info.get('total'),
                                    'source': p.get('source', 'Default'),
                                    'language': p.get('language', lang)
                                }
                    enriched.append(p)
                playlists = enriched
            except Exception:
                # Best-effort enrichment; silently continue on failure
                pass
        
        return playlists[:limit]
    
    def get_playlist_tracks(self, playlist_id: str, limit: int = 5) -> List[Dict]:
        """Get tracks from a specific playlist"""
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
        return f"https://open.spotify.com/playlist/{playlist_id}"
    
    def get_music_recommendation_summary(self, emotion: str) -> str:
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
