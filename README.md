# 🍵 Performative Detector

A fun Python project that uses MediaPipe and computer vision to detect when you're holding a matcha (or any cup) and plays "Juna by Clairo" on Spotify while displaying "PERFORMATIVE" on screen.

## Features

- 🎥 Real-time camera input processing
- 🤚 Hand gesture detection using MediaPipe
- 🎵 Spotify integration to play specific songs
- 🎨 Live video display with text overlays
- ✨ Detects when you're holding something (like a matcha cup!)

## How It Works

The detector uses MediaPipe Hands to:
1. **Two-hand detection**: Detects when both hands are close together (holding something between them)
2. **Single-hand detection**: Detects when fingers are in a gripping position (holding a cup)

When holding is detected:
- Display shows "PERFORMATIVE" in pink
- Automatically plays "Juna by Clairo" on Spotify (if configured)

When not holding:
- Display shows "not performative" in gray

## Prerequisites

- Python 3.8 or higher
- A webcam
- (Optional) Spotify Premium account for music playback
- (Optional) An active Spotify device (desktop app, mobile, web player, etc.)

## Installation

1. **Clone or navigate to this directory**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Spotify API (Optional but recommended)**

   The app works without Spotify, but you won't get the music playback feature.

   a. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   
   b. Log in and click "Create an App"
   
   c. Fill in the app details:
      - App name: "Performative Detector"
      - App description: "Detects performative matcha holding"
      - Redirect URI: `http://localhost:8888/callback`
   
   d. Copy your Client ID and Client Secret
   
   e. Create a `.env` file in the project directory:
      ```bash
      cp .env.example .env
      ```
   
   f. Edit `.env` and add your credentials:
      ```
      SPOTIFY_CLIENT_ID=your_client_id_here
      SPOTIFY_CLIENT_SECRET=your_client_secret_here
      SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
      ```

4. **Make sure Spotify is open**
   
   Before running the detector, open Spotify on any device (desktop app, phone, web player). This is needed for playback control.

## Usage

Run the detector:
```bash
python performative_detector.py
```

**Controls:**
- Hold a cup/matcha in front of the camera
- Press `q` to quit

**Tips for best detection:**
- Hold the cup with both hands close together, OR
- Hold with one hand in a clear gripping gesture
- Keep hands in the center area of the frame
- Ensure good lighting for better hand detection

## First Run - Spotify Authorization

The first time you run the app with Spotify enabled:
1. A browser window will open asking you to log in to Spotify
2. Authorize the app
3. You'll be redirected to a localhost page (which may not load - that's OK!)
4. The app will automatically cache your credentials

## Troubleshooting

### "No active Spotify devices found"
- Open Spotify on your computer, phone, or web player
- Play any song briefly to activate the device
- Run the detector again

### "Spotify credentials not found"
- Make sure you created the `.env` file
- Verify your Client ID and Secret are correct
- Check that the `.env` file is in the same directory as the scripts

### Hand detection not working well
- Ensure good lighting
- Try holding the cup with both hands
- Move closer to or further from the camera
- Adjust the `min_detection_confidence` in `performative_detector.py` (line 23)

### Camera not opening
- Check if another application is using the camera
- Try changing the camera index in `performative_detector.py` line 37: `self.cap = cv2.VideoCapture(0)` - change 0 to 1, 2, etc.

## Customization

### Change the Song
Edit `spotify_controller.py` line 16 to change the track URI:
```python
self.target_track_uri = "spotify:track:YOUR_TRACK_URI"
```

To find a track URI:
1. Open Spotify
2. Right-click a song
3. Share → Copy Song Link
4. The URI is in the format: `spotify:track:ID` (extract from the link)

### Adjust Detection Sensitivity
In `performative_detector.py`:
- Line 23: Change `min_detection_confidence` (0.5-0.9, lower = more sensitive)
- Line 33: Change `holding_duration_threshold` (seconds before triggering)
- Line 88: Change distance threshold for two-hand detection
- Line 113: Adjust curl detection for single-hand holding

### Change Display Text
In `performative_detector.py`, lines 215-218:
```python
self.draw_text(frame, "YOUR TEXT HERE", (147, 20, 255), 3.0)
```

## Project Structure

```
performative/
├── performative_detector.py   # Main detection script
├── spotify_controller.py      # Spotify API integration
├── requirements.txt           # Python dependencies
├── .env.example              # Template for environment variables
├── .env                      # Your actual credentials (create this)
└── README.md                 # This file
```

## Dependencies

- **opencv-python**: Camera input and video display
- **mediapipe**: Hand detection and tracking
- **numpy**: Numerical computations
- **spotipy**: Spotify API client
- **python-dotenv**: Environment variable management

## Known Limitations

- Spotify playback requires an active Spotify Premium account
- Hand detection works best with good lighting
- "Matcha detection" is simplified to "holding detection" (actual object recognition would require custom ML model training)
- The app needs an active Spotify device to play music

## Future Improvements

- Train a custom model to specifically recognize matcha cups
- Add support for different gestures
- Multiple song choices based on different objects
- Better UI with gesture feedback
- Record "performative moments" as video clips

## Credits

Created with ❤️ using MediaPipe, OpenCV, and Spotipy.

Song: "Juna" by Clairo

---

**Enjoy being performative! 🍵✨**



