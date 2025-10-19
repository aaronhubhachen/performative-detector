"""
Spotify controller module for playing specific songs
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import subprocess
import threading
from dotenv import load_dotenv

load_dotenv()

class SpotifyController:
    def __init__(self):
        self.sp = None
        self.device_id = None
        self.is_playing = False
        self.current_track_uri = None
        self.target_track_uri = "spotify:track:2mWfVxEo4xZYDaz0v7hYrN"  # Juna by Clairo
        self.window_opened = False  # Track if we've already opened the window
        self._initialize_spotify()
    
    def _initialize_spotify(self):
        """Initialize Spotify client with OAuth"""
        try:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8888/callback')
            
            if not client_id or not client_secret:
                print("⚠️  Spotify credentials not found. Music playback disabled.")
                print("   Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file")
                return
            
            scope = "user-modify-playback-state user-read-playback-state"
            
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope,
                cache_path=".spotify_cache"
            ))
            
            # Get available devices
            devices = self.sp.devices()
            if devices['devices']:
                self.device_id = devices['devices'][0]['id']
                print(f"✓ Spotify connected to device: {devices['devices'][0]['name']}")
            else:
                print("⚠️  No active Spotify devices found. Please open Spotify on a device.")
                
        except Exception as e:
            print(f"⚠️  Failed to initialize Spotify: {e}")
            self.sp = None
    
    def show_spotify_window(self):
        """Show and enlarge Spotify window using AppleScript (macOS only) - non-blocking"""
        if self.window_opened:
            return  # Already opened, don't do it again
        
        try:
            # AppleScript to activate Spotify and make window large
            applescript = '''
            tell application "Spotify"
                activate
                tell application "System Events"
                    tell process "Spotify"
                        set frontmost to true
                        -- Try to maximize window
                        try
                            tell window 1
                                set position to {100, 100}
                                set size to {800, 600}
                            end tell
                        end try
                    end tell
                end tell
            end tell
            '''
            # Run in background to avoid blocking
            subprocess.Popen(['osascript', '-e', applescript], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            self.window_opened = True
            print("🎵 Spotify window opened")
        except Exception as e:
            print(f"⚠️  Could not control Spotify window: {e}")
    
    def _play_juna_async(self):
        """Internal method to play Juna - runs in background thread"""
        try:
            # Check current playback
            current = self.sp.current_playback()
            
            # If already playing the right song, don't restart
            if current and current.get('item'):
                current_uri = current['item']['uri']
                if current_uri == self.target_track_uri and current['is_playing']:
                    return True
            
            # Start playing the track
            self.sp.start_playback(
                device_id=self.device_id,
                uris=[self.target_track_uri]
            )
            self.is_playing = True
            print("🎵 Playing: Juna by Clairo")
            
            # Show Spotify window
            self.show_spotify_window()
            
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to play track: {e}")
            return False
    
    def play_juna(self):
        """Play 'Juna by Clairo' on Spotify - non-blocking"""
        if not self.sp:
            return False
        
        # Run in background thread to avoid blocking
        thread = threading.Thread(target=self._play_juna_async, daemon=True)
        thread.start()
        return True
    
    def pause(self):
        """Pause playback"""
        if not self.sp or not self.is_playing:
            return
        
        try:
            self.sp.pause_playback(device_id=self.device_id)
            self.is_playing = False
            print("⏸️  Paused playback")
        except Exception as e:
            print(f"⚠️  Failed to pause: {e}")
    
    def is_spotify_available(self):
        """Check if Spotify is available and ready"""
        return self.sp is not None and self.device_id is not None

