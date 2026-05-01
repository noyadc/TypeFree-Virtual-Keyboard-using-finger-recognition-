import cv2
import numpy as np
import time
import mediapipe as mp
from pynput.keyboard import Controller, Key as PynputKey
import tkinter as tk
from tkinter import simpledialog

# HandTracker class using Mediapipe
class HandTracker:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.7, trackCon=0.7):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks and draw:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def getPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return lmList

    def isPeaceSign(self, lmList):
        """
        Detects a "peace sign" gesture:
        - Index and middle fingers up
        - Ring, pinky, and thumb down
        """
        if not lmList:
            return False

        # Finger tip IDs in Mediapipe
        tipIds = [4, 8, 12, 16, 20]

        fingers = []

        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0]-1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for id in range(1,5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # Check for peace sign: index and middle fingers up, others down
        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[3] == 0 and fingers[4] == 0:
            return True
        return False

    def isThumbsUp(self, lmList):
        """
        Detects a "thumbs up" gesture:
        - Thumb up
        - All fingers down
        """
        if not lmList:
            return False

        tipIds = [4, 8, 12, 16, 20]
        fingers = []

        # Thumb (check if pointing up)
        if lmList[tipIds[0]][2] < lmList[tipIds[0]-1][2]:
            fingers.append(1)
        else:
            fingers.append(0)

        # All other fingers should be down
        for id in range(1, 5):
            if lmList[tipIds[id]][2] > lmList[tipIds[id]-2][2]:
                fingers.append(0)
            else:
                fingers.append(1)

        # Check for thumbs up: only thumb up, all fingers down
        if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            return True
        return False

    def isOpenPalm(self, lmList):
        """
        Detects an "open palm" gesture:
        - All fingers extended
        """
        if not lmList:
            return False

        tipIds = [4, 8, 12, 16, 20]
        fingers = []

        # Check all fingers
        for id in range(5):
            if id == 0:  # Thumb
                if lmList[tipIds[id]][2] < lmList[tipIds[id]-1][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else:  # Other fingers
                if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

        # Check for open palm: all fingers extended
        if all(finger == 1 for finger in fingers):
            return True
        return False

    def isPointing(self, lmList):
        """
        Detects a "pointing" gesture:
        - Only index finger up
        - All others down
        """
        if not lmList:
            return False

        tipIds = [4, 8, 12, 16, 20]
        fingers = []

        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0]-1][1]:  # Thumb pointing right (closed)
            fingers.append(0)
        else:
            fingers.append(1)

        # Fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] > lmList[tipIds[id]-2][2]:  # Fingers pointing down (closed)
                fingers.append(0)
            else:
                fingers.append(1)

        # Check for pointing: only index finger up
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            return True
        return False

    def isVictory(self, lmList):
        """
        Detects a "rock on" gesture (index + pinky up):
        - Index and pinky fingers up
        - Middle, ring, and thumb down
        """
        if not lmList or len(lmList) < 21:
            return False

        tipIds = [4, 8, 12, 16, 20]
        fingers = []

        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0]-1][1]:  # Thumb pointing right (closed)
            fingers.append(0)
        else:
            fingers.append(1)

        # Fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] > lmList[tipIds[id]-2][2]:  # Fingers pointing down (closed)
                fingers.append(0)
            else:
                fingers.append(1)

        # Check for rock on: index and pinky up, others down
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
            return True
        return False

    def isThreeFingers(self, lmList):
        """
        Detects a "three fingers" gesture:
        - Index, middle, and ring fingers up
        - Thumb and pinky down
        """
        if not lmList:
            return False

        tipIds = [4, 8, 12, 16, 20]
        fingers = []

        # Thumb
        if lmList[tipIds[0]][2] < lmList[tipIds[0]-1][2]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # Check for three fingers: index, middle, and ring up, others down
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            return True
        return False

# Key class representing each virtual key
class Key:
    def __init__(self, x, y, w, h, text):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text

    def drawKey(self, img, text_color=(255, 255, 255), bg_color=(0, 0, 0), alpha=0.5, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, thickness=2):
        # Draw semi-transparent rectangle
        bg_rec = img[self.y : self.y + self.h, self.x : self.x + self.w]
        overlay = bg_rec.copy()
        overlay[:] = bg_color
        cv2.addWeighted(overlay, alpha, bg_rec, 1 - alpha, 0, bg_rec)

        # Put the letter/text
        text_size = cv2.getTextSize(self.text, fontFace, fontScale, thickness)[0]
        text_x = self.x + (self.w - text_size[0]) // 2
        text_y = self.y + (self.h + text_size[1]) // 2
        cv2.putText(img, self.text, (text_x, text_y), fontFace, fontScale, text_color, thickness)

    def isOver(self, x, y):
        return self.x < x < self.x + self.w and self.y < y < self.y + self.h

# Helper functions
def getMousePos(event, x, y, flags, param):
    global clickedX, clickedY
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONUP:
        clickedX, clickedY = x, y
    if event == cv2.EVENT_MOUSEMOVE:
        mouseX, mouseY = x, y

def calculateDistance(pt1, pt2):
    return int(((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5)

# Initialize keyboard controller
keyboard = Controller()

# Initialize HandTracker
tracker = HandTracker(detectionCon=0.8, trackCon=0.8)

# Initialize video capture
cap = cv2.VideoCapture(0)
ptime = 0

# Define virtual keyboard layout
w, h = 45, 35  # Even smaller key size
startX, startY = 40, 280  # Move keyboard much lower to avoid covering instructions
keys = []
letters = list("QWERTYUIOPASDFGHJKLZXCVBNM")

# Calculate keyboard width to ensure it doesn't overlap with control panel
keyboardWidth = 10 * (w + 5)  # Width of first row
maxKeyboardX = startX + keyboardWidth

# Create a more compact 3-row layout
for i, l in enumerate(letters):
    if i < 10:  # First row: QWERTYUIOP
        keys.append(Key(startX + i * (w + 5), startY, w, h, l))
    elif i < 19:  # Second row: ASDFGHJKL
        keys.append(Key(startX + (i - 10) * (w + 5), startY + h + 5, w, h, l))
    else:  # Third row: ZXCVBNM
        keys.append(Key(startX + (i - 19) * (w + 5), startY + 2 * (h + 5), w, h, l))

# Special keys - ensure they don't extend beyond the calculated width
keys.append(Key(startX, startY + 3 * (h + 5), 5 * (w + 5), h, "Space"))
keys.append(Key(startX + 6 * (w + 5), startY + 3 * (h + 5), 5 * (w + 5), h, "<--"))
keys.append(Key(startX + 12 * (w + 5), startY + 3 * (h + 5), 5 * (w + 5), h, "Enter"))

# Adjust window size and position
ret, frame = cap.read()
if not ret:
    print("Failed to grab frame from camera.")
    exit()
frameHeight, frameWidth, _ = frame.shape

# Define control keys at the top right - ensure they're far enough from keyboard
controlKeyWidth = 100
controlKeyHeight = 50
panelX = frameWidth - controlKeyWidth - 20  # 20px padding from right
panelY = 40
panelSpacing = 70

# Ensure control panel doesn't overlap with keyboard by checking position
if panelX < maxKeyboardX + 50:  # Add 50px buffer
    panelX = maxKeyboardX + 50
    # Adjust if it goes beyond frame width
    if panelX + controlKeyWidth > frameWidth - 20:
        panelX = frameWidth - controlKeyWidth - 20

showKey = Key(panelX, panelY, controlKeyWidth, controlKeyHeight, 'Show')
exitKey = Key(panelX, panelY + panelSpacing, controlKeyWidth, controlKeyHeight, 'Exit')
saveKey = Key(panelX, panelY + 2 * panelSpacing, controlKeyWidth, controlKeyHeight, 'Save')
loadKey = Key(panelX, panelY + 3 * panelSpacing, controlKeyWidth, controlKeyHeight, 'Load')

# Text box above keyboard - ensure it doesn't overlap with control panel
textBoxWidth = min(10 * (w + 5), panelX - startX - 20)  # Don't extend beyond control panel
textBox = Key(startX, startY - h - 20, textBoxWidth, h, '')

# Initialize variables
clickedX, clickedY = 0, 0
mouseX, mouseY = 0, 0
show = False
cv2.namedWindow('video', cv2.WINDOW_NORMAL)
cv2.resizeWindow('video', 1280, 900)
cv2.setMouseCallback('video', getMousePos)
counter = 0
previousClick = 0

# Add new variables for improvements
gestureCooldown = 0
lastGestureTime = 0
keyPressCooldown = 0
lastKeyPressTime = 0
hoveredKey = None
pressedKey = None
frameSkip = 0  # For performance optimization
showHelp = True  # Show help initially

# Add typing mode variables
typingMode = False
lastTypingActivity = 0
gestureHoldTime = 0
gestureStartTime = 0
currentGesture = None

# Add clipboard for the app
appClipboard = ""

# Track the most recent time the current gesture was detected, to allow brief dropouts
lastGestureDetectTime = 0.0

# Prompt for username using a simple dialog
root = tk.Tk()
root.withdraw()
username = simpledialog.askstring("Login/Register", "Enter your username:")
if not username:
    print("Username required. Exiting.")
    exit()
filename = f"{username}.txt"

# Main loop
while True:
    if counter > 0:
        counter -= 1

    signTipX = 0
    signTipY = 0
    thumbTipX = 0
    thumbTipY = 0

    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)  # Mirror image

    # Find hands
    frame = tracker.findHands(frame, draw=True)
    lmList = tracker.getPosition(frame, draw=False)

    if lmList:
        # Get tip positions
        signTip = lmList[8]   # Index finger tip
        thumbTip = lmList[4]  # Thumb tip
        signTipX, signTipY = signTip[1], signTip[2]
        thumbTipX, thumbTipY = thumbTip[1], thumbTip[2]

        # Calculate distance between index finger tip and thumb tip
        distance = calculateDistance((signTipX, signTipY), (thumbTipX, thumbTipY))

        # If distance is small, consider it a "click"
        if distance < 40:
            currentTime = time.time()
            if currentTime - previousClick > 0.3:
                clickedX, clickedY = signTipX, signTipY
                previousClick = currentTime
                # Activate typing mode
                typingMode = True
                lastTypingActivity = currentTime

        # Check for gesture recognition (only when not in typing mode)
        if not typingMode:
            currentTime = time.time()  # Define currentTime for gesture recognition
            # Check for peace sign gesture (Copy action)
            if tracker.isPeaceSign(lmList):
                lastGestureDetectTime = currentTime
                if currentGesture != "peace":
                    currentGesture = "peace"
                    gestureStartTime = currentTime
                else:
                    gestureHoldTime = currentTime - gestureStartTime
                    if gestureHoldTime > 1.0:  # Must hold for 1.0 seconds
                        if currentTime - lastGestureTime > 2.0:  # 2 second cooldown
                            appClipboard = textBox.text  # Copy text to app clipboard
                            cv2.putText(frame, "Text Copied to App Clipboard!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (62, 88, 121), 2)
                            lastGestureTime = currentTime
                            currentGesture = None
            # Check for thumbs up gesture (Save text)
            elif tracker.isThumbsUp(lmList):
                lastGestureDetectTime = currentTime
                if currentGesture != "thumbs":
                    currentGesture = "thumbs"
                    gestureStartTime = currentTime
                else:
                    gestureHoldTime = currentTime - gestureStartTime
                    if gestureHoldTime > 1.0:
                        if currentTime - lastGestureTime > 2.0:
                            with open(filename, "w", encoding="utf-8") as f:
                                f.write(textBox.text)
                            cv2.putText(frame, "Text Saved! (Thumbs Up)", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (46, 204, 113), 2)
                            lastGestureTime = currentTime
                            currentGesture = None
            # Check for open palm gesture (Load text)
            elif tracker.isOpenPalm(lmList):
                lastGestureDetectTime = currentTime
                if currentGesture != "open_palm":
                    currentGesture = "open_palm"
                    gestureStartTime = currentTime
                else:
                    gestureHoldTime = currentTime - gestureStartTime
                    if gestureHoldTime > 1.0:
                        if currentTime - lastGestureTime > 2.0:
                            try:
                                with open(filename, "r", encoding="utf-8") as f:
                                    textBox.text = f.read()
                                cv2.putText(frame, "Text Loaded! (Open Palm)", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (52, 152, 219), 2)
                            except Exception as e:
                                cv2.putText(frame, f"Error Loading: {e}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (231, 76, 60), 2)
                            lastGestureTime = currentTime
                            currentGesture = None
            # Check for pointing gesture (Toggle keyboard)
            elif tracker.isPointing(lmList):
                lastGestureDetectTime = currentTime
                if currentGesture != "pointing":
                    currentGesture = "pointing"
                    gestureStartTime = currentTime
                else:
                    gestureHoldTime = currentTime - gestureStartTime
                    if gestureHoldTime > 1.0:
                        if currentTime - lastGestureTime > 2.0:
                            show = not show
                            showKey.text = "Hide" if show else "Show"
                            cv2.putText(frame, "Keyboard Toggled! (Pointing)", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (241, 196, 15), 2)
                            lastGestureTime = currentTime
                            currentGesture = None
            # Check for victory gesture (Paste action)
            elif tracker.isVictory(lmList):
                lastGestureDetectTime = currentTime
                if currentGesture != "victory":
                    currentGesture = "victory"
                    gestureStartTime = currentTime
                else:
                    gestureHoldTime = currentTime - gestureStartTime
                    if gestureHoldTime > 1.0:
                        if currentTime - lastGestureTime > 2.0:
                            if appClipboard:  # If there's text in app clipboard
                                textBox.text += appClipboard  # Paste to text box
                                cv2.putText(frame, "Text Pasted from App Clipboard!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (216, 196, 182), 2)
                            else:
                                cv2.putText(frame, "App Clipboard is Empty!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (220, 20, 60), 2)
                            lastGestureTime = currentTime
                            currentGesture = None
            # Check for three fingers gesture (Undo action)
            elif tracker.isThreeFingers(lmList):
                lastGestureDetectTime = currentTime
                if currentGesture != "three":
                    currentGesture = "three"
                    gestureStartTime = currentTime
                else:
                    gestureHoldTime = currentTime - gestureStartTime
                    if gestureHoldTime > 1.0:
                        if currentTime - lastGestureTime > 2.0:
                            keyboard.press(PynputKey.ctrl)
                            keyboard.press('z')
                            keyboard.release('z')
                            keyboard.release(PynputKey.ctrl)
                            cv2.putText(frame, "Undo Action Triggered", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (142, 68, 173), 2)
                            lastGestureTime = currentTime
                            currentGesture = None
            else:
                # Allow brief detection dropouts without resetting progress
                if currentGesture and (currentTime - lastGestureDetectTime) <= 0.3:
                    pass
                else:
                    currentGesture = None
                    gestureStartTime = 0
                    gestureHoldTime = 0
        else:
            # In typing mode, check if user has been inactive
            currentTime = time.time()  # Define currentTime for typing mode check
            if currentTime - lastTypingActivity > 3.0:  # 3 seconds of inactivity
                typingMode = False
                currentGesture = None

    # Draw FPS with aesthetic styling
    ctime = time.time()
    fps = int(1 / (ctime - ptime)) if ctime - ptime > 0 else 0
    ptime = ctime
    
    # Create a beautiful FPS display with gradient-like effect
    cv2.rectangle(frame, (5, 5), (120, 35), (33, 53, 85), -1)  # #213555 dark blue
    cv2.rectangle(frame, (5, 5), (120, 35), (62, 88, 121), 2)   # #3E5879 medium blue border
    cv2.putText(frame, f'FPS: {fps}', (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 239, 231), 2)  # #F5EFE7 very light beige text
    
    # Draw hand position indicator with aesthetic colors
    if signTipX > 0 and signTipY > 0:
        # Beautiful gradient-like circles for hand tracking
        cv2.circle(frame, (signTipX, signTipY), 10, (62, 88, 121), -1)  # #3E5879 medium blue circle for finger tip
        cv2.circle(frame, (signTipX, signTipY), 8, (216, 196, 182), 2)   # #D8C4B6 light beige border
        cv2.circle(frame, (thumbTipX, thumbTipY), 8, (216, 196, 182), -1)  # #D8C4B6 light beige circle for thumb
        cv2.circle(frame, (thumbTipX, thumbTipY), 6, (245, 239, 231), 2)  # #F5EFE7 very light beige border
    
    # Draw distance indicator with aesthetic styling
    if signTipX > 0 and thumbTipX > 0:
        distance = calculateDistance((signTipX, signTipY), (thumbTipX, thumbTipY))
        if distance < 40:
            # Beautiful click indicator
            cv2.putText(frame, "CLICK!", (signTipX + 25, signTipY - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (62, 88, 121), 2)  # #3E5879 medium blue
            cv2.putText(frame, "CLICK!", (signTipX + 25, signTipY - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (216, 196, 182), 1)  # #D8C4B6 light beige outline
    
    # Draw gesture status with aesthetic colors
    gestureStatus = "No Gesture"
    gestureColor = (169, 169, 169)  # Dark gray
    
    if lmList:
        if tracker.isPeaceSign(lmList):
            gestureStatus = "Peace Sign - Copy"
            gestureColor = (62, 88, 121)  # #3E5879 medium blue
        elif tracker.isThumbsUp(lmList):
            gestureStatus = "Thumbs Up - Save"
            gestureColor = (216, 196, 182)  # #D8C4B6 light beige
        elif tracker.isOpenPalm(lmList):
            gestureStatus = "Open Palm - Load"
            gestureColor = (62, 88, 121)  # #3E5879 medium blue
        elif tracker.isPointing(lmList):
            gestureStatus = "Pointing - Toggle"
            gestureColor = (245, 239, 231)  # #F5EFE7 very light beige
        elif tracker.isVictory(lmList):
            gestureStatus = "Rock On - Paste"
            gestureColor = (216, 196, 182)  # #D8C4B6 light beige
        elif tracker.isThreeFingers(lmList):
            gestureStatus = "Three Fingers - Undo"
            gestureColor = (62, 88, 121)  # #3E5879 medium blue
        
        # Debug: Show finger states
        tipIds = [4, 8, 12, 16, 20]
        fingerStates = []
        for id in range(5):
            if id == 0:  # Thumb
                if lmList[tipIds[id]][1] > lmList[tipIds[id]-1][1]:
                    fingerStates.append("T:0")  # Thumb closed
                else:
                    fingerStates.append("T:1")  # Thumb open
            else:  # Other fingers
                if lmList[tipIds[id]][2] > lmList[tipIds[id]-2][2]:
                    fingerStates.append(f"F{id}:0")  # Finger closed
                else:
                    fingerStates.append(f"F{id}:1")  # Finger open
        
        # Display finger states for debugging
        cv2.putText(frame, f"Fingers: {' '.join(fingerStates)}", (15, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (245, 239, 231), 1)
        
        # Debug: Show current gesture and progress
        if currentGesture:
            cv2.putText(frame, f"Current: {currentGesture} - Hold: {gestureHoldTime:.1f}s", (15, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (245, 239, 231), 1)
        
        # Show app clipboard status
        clipboardPreview = appClipboard[:20] + "..." if len(appClipboard) > 20 else appClipboard
        if appClipboard:
            cv2.putText(frame, f"Clipboard: {clipboardPreview}", (15, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (62, 88, 121), 1)
        else:
            cv2.putText(frame, "Clipboard: Empty", (15, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (169, 169, 169), 1)

    # Beautiful gesture status display
    cv2.rectangle(frame, (5, 85), (400, 115), (33, 53, 85), -1)  # #213555 dark blue
    cv2.rectangle(frame, (5, 85), (400, 115), (62, 88, 121), 2)  # #3E5879 medium blue border
    cv2.putText(frame, f"Gesture: {gestureStatus}", (15, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, gestureColor, 2)
    
    # Draw typing mode status with aesthetic styling
    if typingMode:
        # Beautiful typing mode indicator
        cv2.rectangle(frame, (5, 120), (450, 150), (216, 196, 182), -1)  # #D8C4B6 light beige
        cv2.rectangle(frame, (5, 120), (450, 150), (62, 88, 121), 2)  # #3E5879 medium blue border
        cv2.putText(frame, "TYPING MODE - Gestures Disabled", (15, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (33, 53, 85), 2)  # #213555 dark blue text
        # Show countdown to exit typing mode
        timeLeft = 3.0 - (currentTime - lastTypingActivity)
        if timeLeft > 0:
            cv2.rectangle(frame, (5, 155), (300, 180), (33, 53, 85), -1)  # #213555 dark blue
            cv2.rectangle(frame, (5, 155), (300, 180), (62, 88, 121), 2)  # #3E5879 medium blue border
            cv2.putText(frame, f"Exit typing mode in: {timeLeft:.1f}s", (15, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 2)  # #F5EFE7 very light beige text
    else:
        # Beautiful gesture mode indicator
        cv2.rectangle(frame, (5, 120), (400, 150), (33, 53, 85), -1)  # #213555 dark blue
        cv2.rectangle(frame, (5, 120), (400, 150), (62, 88, 121), 2)  # #3E5879 medium blue border
        cv2.putText(frame, "GESTURE MODE - Hold gestures for 1.0s", (15, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 239, 231), 2)  # #F5EFE7 very light beige text
        # Show gesture progress if one is being held
        if currentGesture and gestureStartTime > 0:
            progress = min(1.0, (currentTime - gestureStartTime) / 1.0)
            # Beautiful progress bar
            cv2.rectangle(frame, (5, 155), (300, 180), (33, 53, 85), -1)  # #213555 dark blue
            cv2.rectangle(frame, (5, 155), (300, 180), (62, 88, 121), 2)  # #3E5879 medium blue border
            progressWidth = int(290 * progress)
            cv2.rectangle(frame, (10, 160), (10 + progressWidth, 175), (216, 196, 182), -1)  # #D8C4B6 light beige progress
            cv2.putText(frame, f"Gesture Progress: {progress*100:.0f}%", (15, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (33, 53, 85), 2)  # #213555 dark blue text

    # Performance optimization: skip frames for better FPS
    frameSkip += 1
    if frameSkip % 2 == 0:  # Process every other frame for hand detection
        frame = tracker.findHands(frame, draw=True)
        lmList = tracker.getPosition(frame, draw=False)
    else:
        lmList = []

    # Draw control keys with aesthetic styling
    showKey.drawKey(frame, (245, 239, 231), (33, 53, 85), alpha=0.8, fontScale=0.7, thickness=2)  # #F5EFE7 text, #213555 dark blue bg
    exitKey.drawKey(frame, (245, 239, 231), (62, 88, 121), alpha=0.8, fontScale=0.7, thickness=2)  # #F5EFE7 text, #3E5879 medium blue bg
    saveKey.drawKey(frame, (33, 53, 85), (216, 196, 182), alpha=0.8, fontScale=0.7, thickness=2)  # #213555 dark blue text, #D8C4B6 light beige bg
    loadKey.drawKey(frame, (245, 239, 231), (62, 88, 121), alpha=0.8, fontScale=0.7, thickness=2)  # #F5EFE7 text, #3E5879 medium blue bg

    # Draw keyboard and text box only if show is True
    if show:
        # Beautiful text box with aesthetic styling
        textBox.drawKey(frame, (245, 239, 231), (33, 53, 85), alpha=0.8, fontScale=0.7, thickness=2)  # #F5EFE7 text, #213555 dark blue bg
        
        # Find which key is being hovered over
        hoveredKey = None
        for key in keys:
            if key.isOver(signTipX, signTipY):
                hoveredKey = key
                break
        
        for key in keys:
            # Determine key appearance based on state with aesthetic colors
            if key == pressedKey:
                key_alpha = 0.3  # Semi-transparent when pressed
                key_color = (245, 239, 231)  # #F5EFE7 very light beige when pressed
                bg_color = (216, 196, 182)  # #D8C4B6 light beige background
            elif key == hoveredKey:
                key_alpha = 0.4  # Semi-transparent when hovered
                key_color = (245, 239, 231)  # #F5EFE7 very light beige when hovered
                bg_color = (62, 88, 121)  # #3E5879 medium blue background
            elif key.isOver(mouseX, mouseY):
                key_alpha = 0.5  # Semi-transparent when mouse hovered
                key_color = (245, 239, 231)  # #F5EFE7 very light beige text
                bg_color = (216, 196, 182)  # #D8C4B6 light beige background
            else:
                key_alpha = 0.7  # Normal appearance
                key_color = (245, 239, 231)  # #F5EFE7 very light beige text
                bg_color = (33, 53, 85)  # #213555 dark blue background
            
            # Handle key press
            if key.isOver(clickedX, clickedY):
                currentTime = time.time()
                if currentTime - lastKeyPressTime > 0.2:  # Prevent rapid key presses
                    pressedKey = key
                    lastKeyPressTime = currentTime
                    
                    if key.text == "<--":
                        textBox.text = textBox.text[:-1]
                        keyboard.press(PynputKey.backspace)
                        keyboard.release(PynputKey.backspace)
                    elif key.text == "Space":
                        textBox.text += " "
                        keyboard.press(PynputKey.space)
                        keyboard.release(PynputKey.space)
                    elif key.text == "Enter":
                        textBox.text += "\n"
                        keyboard.press(PynputKey.enter)
                        keyboard.release(PynputKey.enter)
                    else:
                        textBox.text += key.text
                        keyboard.press(key.text.lower())
                        keyboard.release(key.text.lower())
                    
                    clickedX, clickedY = 0, 0  # Reset click
                    
                    # Reset pressed key after a short delay
                    def resetPressedKey():
                        global pressedKey
                        time.sleep(0.1)
                        pressedKey = None
                    
                    import threading
                    threading.Thread(target=resetPressedKey, daemon=True).start()
            
            key.drawKey(frame, text_color=key_color, bg_color=bg_color, alpha=key_alpha, fontScale=0.8, thickness=2)

    # Handle control keys
    if showKey.isOver(clickedX, clickedY):
        show = not show
        showKey.text = "Hide" if show else "Show"
        clickedX, clickedY = 0, 0

    if exitKey.isOver(clickedX, clickedY):
        break

    if saveKey.isOver(clickedX, clickedY):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(textBox.text)
        cv2.putText(frame, "Text Saved!", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        clickedX, clickedY = 0, 0

    if loadKey.isOver(clickedX, clickedY):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                textBox.text = f.read()
            cv2.putText(frame, "Text Loaded!", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        except Exception as e:
            cv2.putText(frame, f"Error Loading Text: {e}", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
        clickedX, clickedY = 0, 0

    # Display the frame
    cv2.imshow('video', frame)

    # Break the loop with 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    # Add keyboard shortcuts
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s') and (cv2.getWindowProperty('video', cv2.WND_PROP_VISIBLE) == 1):
        # Ctrl+S equivalent
        with open(filename, "w", encoding="utf-8") as f:
            f.write(textBox.text)
        cv2.putText(frame, "Text Saved! (Ctrl+S)", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    elif key == ord('h'):
        # Toggle show/hide
        show = not show
        showKey.text = "Hide" if show else "Show"
    elif key == ord('l'):
        # Load text
        try:
            with open(filename, "r", encoding="utf-8") as f:
                textBox.text = f.read()
            cv2.putText(frame, "Text Loaded! (Ctrl+L)", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        except Exception as e:
            cv2.putText(frame, f"Error Loading Text: {e}", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
    elif key == ord('?'):
        # Toggle help
        showHelp = not showHelp
    elif key == ord('t'):
        # Toggle typing mode manually
        typingMode = not typingMode
        if typingMode:
            lastTypingActivity = currentTime
        currentGesture = None
    elif key == ord('c'):
        # Clear app clipboard
        appClipboard = ""
        cv2.putText(frame, "App Clipboard Cleared!", (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (62, 88, 121), 2)
    
    # Draw help information with aesthetic styling
    if showHelp:
        helpY = 400
        # Beautiful help header
        cv2.rectangle(frame, (5, helpY - 10), (300, helpY + 25), (33, 53, 85), -1)  # #213555 dark blue
        cv2.rectangle(frame, (5, helpY - 10), (300, helpY + 25), (62, 88, 121), 2)  # #3E5879 medium blue border
        cv2.putText(frame, "HELP - Press ? to toggle", (15, helpY + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 239, 231), 2)  # #F5EFE7 very light beige text
        
        # Help content with aesthetic colors
        cv2.putText(frame, "TYPING MODE SYSTEM:", (15, helpY + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (216, 196, 182), 1)  # #D8C4B6 light beige text
        cv2.putText(frame, "- Pinch to type = Auto-enters typing mode", (15, helpY + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- Typing mode disables gestures for 3 seconds", (15, helpY + 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- Press T to manually toggle typing mode", (15, helpY + 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "Hand Gestures (Hold 1.0s):", (15, helpY + 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (216, 196, 182), 1)  # #D8C4B6 light beige text
        cv2.putText(frame, "- Peace sign (V) to copy text to app clipboard", (15, helpY + 145), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- Thumbs up to save text", (15, helpY + 165), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- Open palm to load text", (15, helpY + 185), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- Pointing (index only) to toggle keyboard", (15, helpY + 205), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- Rock On (index + pinky) to paste from app clipboard", (15, helpY + 225), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- Three fingers to undo (Ctrl+Z)", (15, helpY + 245), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "Keyboard Shortcuts:", (15, helpY + 275), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (216, 196, 182), 1)  # #D8C4B6 light beige text
        cv2.putText(frame, "- H: Toggle keyboard", (15, helpY + 295), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- S: Save text", (15, helpY + 315), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- L: Load text", (15, helpY + 335), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- T: Toggle typing mode", (15, helpY + 355), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- C: Clear app clipboard", (15, helpY + 375), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text
        cv2.putText(frame, "- Q: Quit", (15, helpY + 395), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)  # #F5EFE7 very light beige text

# Release resources
cap.release()
cv2.destroyAllWindows()
