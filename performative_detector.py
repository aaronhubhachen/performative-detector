"""
Performative Detector - Detects if you're holding a matcha (or any cup-like object)
and plays Juna by Clairo on Spotify while displaying "PERFORMATIVE"
"""
import cv2
import mediapipe as mp
import numpy as np
from spotify_controller import SpotifyController
import time
import subprocess

class PerformativeDetector:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.3
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Initialize Spotify controller
        self.spotify = SpotifyController()
        
        # State tracking
        self.is_holding = False
        self.holding_start_time = None
        self.holding_duration_threshold = 0.2  # seconds to confirm holding (smooth)
        self.spotify_mode = False  # Track if we're in Spotify display mode
        self.spotify_mode_start_time = None  # Track when Spotify mode started
        self.face_cam_delay = 1.0  # Wait 1 second before showing face cam
        self.face_cam_shown = False  # Track if face cam has been shown
        self.force_top_counter = 0  # Counter to periodically force window to top
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("🎥 Performative Detector Started!")
        print(f"🎵 Spotify: {'Connected' if self.spotify.is_spotify_available() else 'Disabled'}")
        print("📋 Instructions:")
        print("   - Hold a cup/matcha in front of camera to be PERFORMATIVE")
        print("   - Press 'q' to quit")
    
    def detect_holding_gesture(self, hand_landmarks_list, image_shape):
        """
        Detect if hands are in a 'holding' position
        This checks if:
        1. Both hands are visible
        2. Hands are close together (indicating holding something between them)
        3. Hands are in the center region of the frame
        """
        if len(hand_landmarks_list) < 2:
            return False
        
        height, width = image_shape[:2]
        
        # Get center points of both hands
        hand_centers = []
        for hand_landmarks in hand_landmarks_list:
            # Calculate center of hand (average of all landmarks)
            x_coords = [lm.x for lm in hand_landmarks.landmark]
            y_coords = [lm.y for lm in hand_landmarks.landmark]
            center_x = np.mean(x_coords)
            center_y = np.mean(y_coords)
            hand_centers.append((center_x, center_y))
        
        if len(hand_centers) < 2:
            return False
        
        # Calculate distance between hands
        dist = np.sqrt((hand_centers[0][0] - hand_centers[1][0])**2 + 
                      (hand_centers[0][1] - hand_centers[1][1])**2)
        
        # Check if hands are close together (holding something)
        # Made more lenient - increased from 0.3 to 0.5
        if dist < 0.5:  # Normalized distance (0-1)
            # Check if hands are in center-ish area
            avg_x = (hand_centers[0][0] + hand_centers[1][0]) / 2
            avg_y = (hand_centers[0][1] + hand_centers[1][1]) / 2
            
            # Center region check (not at edges) - more lenient
            if 0.1 < avg_x < 0.9 and 0.1 < avg_y < 0.95:
                print(f"🙌 Two hands detected! Distance: {dist:.2f}")
                return True
        
        return False
    
    def detect_single_hand_holding(self, hand_landmarks, image_shape):
        """
        Detect if a single hand is in a holding position
        (fingers partially closed, as if gripping something)
        """
        # Get key landmarks
        wrist = hand_landmarks.landmark[0]
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]
        
        # Get MCP (knuckle) points
        index_mcp = hand_landmarks.landmark[5]
        middle_mcp = hand_landmarks.landmark[9]
        
        # Calculate if fingers are curled (holding position)
        # Fingers are curled if fingertips are below or close to MCP joints
        index_curled = index_tip.y > index_mcp.y - 0.08
        middle_curled = middle_tip.y > middle_mcp.y - 0.08
        
        # Thumb should be somewhat opposed - made more lenient
        thumb_dist = np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
        
        # Check if hand is in center region and fingers show holding gesture - more lenient area
        if 0.1 < wrist.x < 0.9 and 0.1 < wrist.y < 0.95:
            if (index_curled or middle_curled) and thumb_dist < 0.3:
                print(f"👋 Single hand holding detected!")
                return True
        
        return False
    
    def create_status_window(self, text, color, width=1200, height=800):
        """Create a separate window just for status display"""
        # Create a blank canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Fill with background color based on status
        if "PERFORMATIVE" == text:
            # Matcha green tinted background
            canvas[:] = (40, 50, 30)  # Dark matcha green tint
        else:
            # Dark red tinted background
            canvas[:] = (20, 20, 40)  # Dark red tint
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # LOUD text - large and bold
        scale = 5.0
        thickness = 12
        
        # Split text into lines if it's multi-line
        lines = text.split('\n')
        
        # Calculate total height needed
        line_heights = []
        line_widths = []
        for line in lines:
            text_size = cv2.getTextSize(line, font, scale, thickness)[0]
            line_widths.append(text_size[0])
            line_heights.append(text_size[1])
        
        line_spacing = 30  # Space between lines
        total_height = sum(line_heights) + (len(lines) - 1) * line_spacing
        
        # Calculate starting y position to center all lines
        start_y = (height - total_height) // 2 + line_heights[0]
        
        # Draw each line
        current_y = start_y
        for i, line in enumerate(lines):
            # Center each line horizontally
            text_x = (width - line_widths[i]) // 2
            
            # Draw text with thick black outline for better visibility
            cv2.putText(canvas, line, (text_x, current_y), font, scale, (0, 0, 0), thickness + 8)
            cv2.putText(canvas, line, (text_x, current_y), font, scale, color, thickness)
            
            # Move to next line position
            if i < len(lines) - 1:
                current_y += line_heights[i] + line_spacing
        
        return canvas
    
    def create_face_cam_overlay(self, frame):
        """Create a smaller face cam with hardcoded 'performative' label"""
        # Resize frame to smaller size for PIP (picture-in-picture)
        small_height = 300
        small_width = 400
        small_frame = cv2.resize(frame, (small_width, small_height))
        
        # Add hardcoded "performative" label at the top
        font = cv2.FONT_HERSHEY_SIMPLEX
        label = "performative"
        scale = 1.2
        thickness = 3
        
        # Get text size for centering
        text_size = cv2.getTextSize(label, font, scale, thickness)[0]
        text_x = (small_width - text_size[0]) // 2
        text_y = 40
        
        # Draw semi-transparent background for label
        overlay = small_frame.copy()
        cv2.rectangle(overlay, (0, 0), (small_width, 60), (40, 50, 30), -1)
        cv2.addWeighted(overlay, 0.7, small_frame, 0.3, 0, small_frame)
        
        # Draw text with outline
        cv2.putText(small_frame, label, (text_x, text_y), font, scale, (0, 0, 0), thickness + 2)
        cv2.putText(small_frame, label, (text_x, text_y), font, scale, (100, 200, 100), thickness)
        
        return small_frame
    
    def force_face_cam_to_top(self):
        """Force Face Cam window to be on top using AppleScript (macOS only)"""
        try:
            # More aggressive AppleScript to bring window to front
            applescript = '''
            tell application "System Events"
                tell (first process whose frontmost is true)
                    set windowName to name of first window
                end tell
                
                repeat with proc in processes
                    if name of proc contains "Python" then
                        tell proc
                            repeat with w in windows
                                if name of w is "Face Cam" then
                                    set frontmost to true
                                    perform action "AXRaise" of w
                                    set position of w to {100, 100}
                                    exit repeat
                                end if
                            end repeat
                        end tell
                    end if
                end repeat
            end tell
            '''
            subprocess.Popen(['osascript', '-e', applescript], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        except Exception as e:
            pass  # Silently fail if AppleScript doesn't work
    
    def draw_status(self, frame, num_hands):
        """Draw status information at bottom of frame"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Instructions at bottom
        cv2.putText(frame, "Press 'q' to quit", 
                   (10, frame.shape[0] - 20), font, 0.6, (200, 200, 200), 1)
    
    def run(self):
        """Main detection loop"""
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe Hands
            results = self.hands.process(rgb_frame)
            
            # Check for holding gesture
            holding_detected = False
            num_hands = 0
            
            if results.multi_hand_landmarks:
                hand_landmarks_list = results.multi_hand_landmarks
                num_hands = len(hand_landmarks_list)
                
                # Draw hand landmarks
                for hand_landmarks in hand_landmarks_list:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
                
                # Simplified: Any hands detected = PERFORMATIVE!
                holding_detected = True
            
            # Update holding state with debouncing
            current_time = time.time()
            
            if holding_detected:
                if self.holding_start_time is None:
                    self.holding_start_time = current_time
                elif current_time - self.holding_start_time > self.holding_duration_threshold:
                    if not self.is_holding:
                        self.is_holding = True
                        self.spotify_mode = True  # Enter Spotify mode
                        self.spotify_mode_start_time = current_time  # Record when we entered Spotify mode
                        print("✨ PERFORMATIVE DETECTED!")
                        if self.spotify.is_spotify_available():
                            self.spotify.play_juna()
            else:
                self.holding_start_time = None
                if self.is_holding:
                    self.is_holding = False
                    print("😐 Not performative anymore")
                    # Note: We don't pause the song - let it keep playing!
            
            # Create status display window
            if self.is_holding:
                # Matcha green color (BGR format)
                status_display = self.create_status_window("PERFORMATIVE", (100, 200, 100))
            else:
                # Bright red color (BGR format) - split into two lines
                status_display = self.create_status_window("NOT\nPERFORMATIVE", (0, 0, 255))
            
            self.draw_status(frame, num_hands)
            
            # Display windows based on mode
            cv2.imshow('Status', status_display)
            
            if self.spotify_mode:
                # Check if enough time has passed since entering Spotify mode
                time_in_spotify_mode = current_time - self.spotify_mode_start_time if self.spotify_mode_start_time else 0
                
                if time_in_spotify_mode >= self.face_cam_delay:
                    # Spotify mode: Show small face cam with label after delay
                    face_cam_overlay = self.create_face_cam_overlay(frame)
                    
                    # Create window if first time
                    if not self.face_cam_shown:
                        cv2.namedWindow('Face Cam', cv2.WINDOW_NORMAL)
                        cv2.resizeWindow('Face Cam', 400, 300)
                        self.face_cam_shown = True
                        print("📹 Face Cam window created")
                    
                    cv2.imshow('Face Cam', face_cam_overlay)
                    cv2.moveWindow('Face Cam', 100, 100)
                    
                    # Try to set topmost property
                    try:
                        cv2.setWindowProperty('Face Cam', cv2.WND_PROP_TOPMOST, 1)
                    except:
                        pass
                    
                    # Force window to top periodically (every 10 frames)
                    self.force_top_counter += 1
                    if self.force_top_counter % 10 == 0:
                        self.force_face_cam_to_top()
                    
                    # Destroy the full camera feed window if it exists
                    try:
                        cv2.destroyWindow('Camera Feed')
                    except:
                        pass
                else:
                    # Still showing full camera during delay period
                    cv2.imshow('Camera Feed', frame)
            else:
                # Normal mode: Show full camera feed
                cv2.imshow('Camera Feed', frame)
                
                # Destroy the face cam window if it exists
                try:
                    cv2.destroyWindow('Face Cam')
                except:
                    pass
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n👋 Closing Performative Detector...")
                break
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()

def main():
    detector = PerformativeDetector()
    detector.run()

if __name__ == "__main__":
    main()

