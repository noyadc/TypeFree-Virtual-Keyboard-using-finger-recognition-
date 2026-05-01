import cv2
import time
import mediapipe as mp
from pynput.keyboard import Controller, Key as PynputKey
import tkinter as tk
from tkinter import simpledialog
import os
import sys


class Key:
    def __init__(self, x, y, w, h, text):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text

    def drawKey(self, img, text_color=(255, 255, 255), bg_color=(0, 0, 0), alpha=0.5, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, thickness=2):
        bg_rec = img[self.y : self.y + self.h, self.x : self.x + self.w]
        overlay = bg_rec.copy()
        overlay[:] = bg_color
        cv2.addWeighted(overlay, alpha, bg_rec, 1 - alpha, 0, bg_rec)

        text_size = cv2.getTextSize(self.text, fontFace, fontScale, thickness)[0]
        text_x = self.x + (self.w - text_size[0]) // 2
        text_y = self.y + (self.h + text_size[1]) // 2
        cv2.putText(img, self.text, (text_x, text_y), fontFace, fontScale, text_color, thickness)

    def isOver(self, x, y):
        return self.x < x < self.x + self.w and self.y < y < self.y + self.h


def getMousePos(event, x, y, flags, param):
    global clickedX, clickedY
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONUP:
        clickedX, clickedY = x, y
    if event == cv2.EVENT_MOUSEMOVE:
        mouseX, mouseY = x, y


keyboard = Controller()

# Import gesture recognizer from Virtuak folder
try:
    # Look in the Virtuak folder for gestures.py
    VIRTUAK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if VIRTUAK_ROOT not in sys.path:
        sys.path.append(VIRTUAK_ROOT)
    from gestures import HandGestureRecognizer
    _gesture_recognizer_available = True
except Exception:
    _gesture_recognizer_available = False

# Hand tracking (kept for pointing and pinch-to-click only)
class HandTracker:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.8, trackCon=0.8):
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

    def getPosition(self, img, handNo=0, draw=False):
        lmList = []
        if hasattr(self, 'results') and self.results and self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return lmList

# Webcam feed for background canvas
cap = cv2.VideoCapture(0)
ptime = 0

ret, frame = cap.read()
if not ret:
    print("Failed to grab frame from camera.")
    exit()

frameHeight, frameWidth, _ = frame.shape

# Keyboard layout
w, h = 45, 35
startX, startY = 40, 280
keys = []
letters = list("QWERTYUIOPASDFGHJKLZXCVBNM")

keyboardWidth = 10 * (w + 5)
maxKeyboardX = startX + keyboardWidth

for i, l in enumerate(letters):
    if i < 10:
        keys.append(Key(startX + i * (w + 5), startY, w, h, l))
    elif i < 19:
        keys.append(Key(startX + (i - 10) * (w + 5), startY + h + 5, w, h, l))
    else:
        keys.append(Key(startX + (i - 19) * (w + 5), startY + 2 * (h + 5), w, h, l))

# Special keys
keys.append(Key(startX, startY + 3 * (h + 5), 5 * (w + 5), h, "Space"))
keys.append(Key(startX + 6 * (w + 5), startY + 3 * (h + 5), 5 * (w + 5), h, "<--"))
keys.append(Key(startX + 12 * (w + 5), startY + 3 * (h + 5), 5 * (w + 5), h, "Enter"))

# Control panel
controlKeyWidth = 100
controlKeyHeight = 50
panelX = frameWidth - controlKeyWidth - 20
panelY = 40
panelSpacing = 70

if panelX < maxKeyboardX + 50:
    panelX = maxKeyboardX + 50
    if panelX + controlKeyWidth > frameWidth - 20:
        panelX = frameWidth - controlKeyWidth - 20

showKey = Key(panelX, panelY, controlKeyWidth, controlKeyHeight, 'Show')
exitKey = Key(panelX, panelY + panelSpacing, controlKeyWidth, controlKeyHeight, 'Exit')
saveKey = Key(panelX, panelY + 2 * panelSpacing, controlKeyWidth, controlKeyHeight, 'Save')
loadKey = Key(panelX, panelY + 3 * panelSpacing, controlKeyWidth, controlKeyHeight, 'Load')

textBoxWidth = min(10 * (w + 5), panelX - startX - 20)
textBox = Key(startX, startY - h - 20, textBoxWidth, h, '')


# Username and file to save/load
root = tk.Tk()
root.withdraw()
username = simpledialog.askstring("Login/Register", "Enter your username:")
if not username:
    print("Username required. Exiting.")
    exit()
filename = f"{username}.txt"


# State
clickedX, clickedY = 0, 0
mouseX, mouseY = 0, 0
show = False
pressedKey = None
lastKeyPressTime = 0
showHelp = True
previousClick = 0
signTipX = 0
signTipY = 0
thumbTipX = 0
thumbTipY = 0

tracker = HandTracker(detectionCon=0.8, trackCon=0.8)

# Initialize gesture recognizer and gesture state
gestureRecognizer = HandGestureRecognizer() if _gesture_recognizer_available else None
currentGestureLabel = "none"
gestureHoldStart = 0.0
lastGestureFireTime = 0.0
lastGestureDetectTime = 0.0
appClipboard = ""

cv2.namedWindow('video', cv2.WINDOW_NORMAL)
cv2.resizeWindow('video', 1280, 900)
cv2.setMouseCallback('video', getMousePos)


while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    # Hand tracking for pinch-to-click
    frame = tracker.findHands(frame, draw=True)
    lmList = tracker.getPosition(frame, draw=False)
    if lmList:
        signTip = lmList[8]
        thumbTip = lmList[4]
        signTipX, signTipY = signTip[1], signTip[2]
        thumbTipX, thumbTipY = thumbTip[1], thumbTip[2]

        # Visual indicators
        cv2.circle(frame, (signTipX, signTipY), 10, (62, 88, 121), -1)
        cv2.circle(frame, (signTipX, signTipY), 8, (216, 196, 182), 2)
        cv2.circle(frame, (thumbTipX, thumbTipY), 8, (216, 196, 182), -1)
        cv2.circle(frame, (thumbTipX, thumbTipY), 6, (245, 239, 231), 2)

        # Pinch detection as click
        distance = int(((signTipX - thumbTipX) ** 2 + (signTipY - thumbTipY) ** 2) ** 0.5)
        if distance < 40:
            currentTime = time.time()
            if currentTime - previousClick > 0.3:
                clickedX, clickedY = signTipX, signTipY
                previousClick = currentTime

    # Gesture recognition (hold 1.0s, cooldown 2.0s) with dropout tolerance
    if gestureRecognizer is not None:
        labels = gestureRecognizer.process(frame)
        detected = labels[0] if labels else "none"
        now = time.time()

        # If we detected something, update last seen time
        if detected != "none":
            lastGestureDetectTime = now

        # Maintain gesture across brief dropouts (<=300ms)
        if detected == "none" and currentGestureLabel != "none" and (now - lastGestureDetectTime) <= 0.3:
            detected = currentGestureLabel

        # Update hold tracking
        if detected != currentGestureLabel:
            currentGestureLabel = detected
            gestureHoldStart = now if detected != "none" else 0.0
        else:
            if detected != "none" and gestureHoldStart > 0:
                holdSeconds = 1.0
                if (now - gestureHoldStart) >= holdSeconds and (now - lastGestureFireTime) >= 2.0:
                    # Map gestures to actions
                    if detected == "pointing":
                        show = not show
                        showKey.text = "Hide" if show else "Show"
                    elif detected == "thumbs_up":
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(textBox.text)
                        cv2.putText(frame, "Text Saved! (Thumbs Up)", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (46, 204, 113), 2)
                    elif detected == "open_palm":
                        try:
                            with open(filename, "r", encoding="utf-8") as f:
                                textBox.text = f.read()
                            cv2.putText(frame, "Text Loaded! (Open Palm)", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (52, 152, 219), 2)
                        except Exception as e:
                            cv2.putText(frame, f"Error Loading: {e}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (231, 76, 60), 2)
                    elif detected == "peace":
                        appClipboard = textBox.text
                        cv2.putText(frame, "Text Copied to App Clipboard!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (62, 88, 121), 2)
                    elif detected == "rock_on":
                        if appClipboard:
                            textBox.text += appClipboard
                            cv2.putText(frame, "Text Pasted from App Clipboard!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (216, 196, 182), 2)
                        else:
                            cv2.putText(frame, "App Clipboard is Empty!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (220, 20, 60), 2)
                    elif detected == "three_fingers":
                        # Treat as backspace/undo: remove last char and send backspace
                        if textBox.text:
                            textBox.text = textBox.text[:-1]
                        keyboard.press(PynputKey.backspace)
                        keyboard.release(PynputKey.backspace)
                        cv2.putText(frame, "Backspace (Three Fingers)", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (142, 68, 173), 2)

                    lastGestureFireTime = now
                    gestureHoldStart = now  # require another full hold before next fire

        # Draw gesture status and progress bar
        friendly = {
            "none": "None",
            "peace": "Peace (Copy)",
            "thumbs_up": "Thumbs Up (Save)",
            "open_palm": "Open Palm (Load)",
            "pointing": "Pointing (Toggle)",
            "rock_on": "Rock On (Paste)",
            "three_fingers": "Three Fingers (Backspace)",
        }
        labelToShow = friendly.get(currentGestureLabel, currentGestureLabel)
        # Header
        cv2.rectangle(frame, (5, 5), (420, 35), (33, 53, 85), -1)
        cv2.rectangle(frame, (5, 5), (420, 35), (62, 88, 121), 2)
        cv2.putText(frame, f"Gesture: {labelToShow}", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 239, 231), 2)

        # Progress bar
        if currentGestureLabel != "none" and gestureHoldStart > 0:
            progress = max(0.0, min(1.0, (now - gestureHoldStart) / 1.0))
            cv2.rectangle(frame, (5, 40), (305, 60), (33, 53, 85), -1)
            cv2.rectangle(frame, (5, 40), (305, 60), (62, 88, 121), 2)
            fillW = int(298 * progress)
            cv2.rectangle(frame, (8, 43), (8 + fillW, 57), (216, 196, 182), -1)

    # (Removed FPS display; replaced with gesture header above)

    # Control keys
    showKey.drawKey(frame, (245, 239, 231), (33, 53, 85), alpha=0.8, fontScale=0.7, thickness=2)
    exitKey.drawKey(frame, (245, 239, 231), (62, 88, 121), alpha=0.8, fontScale=0.7, thickness=2)
    saveKey.drawKey(frame, (33, 53, 85), (216, 196, 182), alpha=0.8, fontScale=0.7, thickness=2)
    loadKey.drawKey(frame, (245, 239, 231), (62, 88, 121), alpha=0.8, fontScale=0.7, thickness=2)

    # Keyboard and textbox
    if show:
        textBox.drawKey(frame, (245, 239, 231), (33, 53, 85), alpha=0.8, fontScale=0.7, thickness=2)

        hoveredKey = None
        for key in keys:
            if key.isOver(signTipX, signTipY) or key.isOver(mouseX, mouseY):
                hoveredKey = key
                break

        for key in keys:
            if key == pressedKey:
                key_alpha = 0.3
                key_color = (245, 239, 231)
                bg_color = (216, 196, 182)
            elif key == hoveredKey:
                key_alpha = 0.4
                key_color = (245, 239, 231)
                bg_color = (62, 88, 121)
            elif key.isOver(signTipX, signTipY) or key.isOver(mouseX, mouseY):
                key_alpha = 0.5
                key_color = (245, 239, 231)
                bg_color = (216, 196, 182)
            else:
                key_alpha = 0.7
                key_color = (245, 239, 231)
                bg_color = (33, 53, 85)

            if key.isOver(clickedX, clickedY):
                currentTime = time.time()
                if currentTime - lastKeyPressTime > 0.2:
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

                    clickedX, clickedY = 0, 0

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

    # Help (no gestures)
    if showHelp:
        helpY = 400
        cv2.rectangle(frame, (5, helpY - 10), (360, helpY + 25), (33, 53, 85), -1)
        cv2.rectangle(frame, (5, helpY - 10), (360, helpY + 25), (62, 88, 121), 2)
        cv2.putText(frame, "HELP - Press ? to toggle", (15, helpY + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 239, 231), 2)

        cv2.putText(frame, "Controls:", (15, helpY + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (216, 196, 182), 1)
        cv2.putText(frame, "- Pinch index+thumb to click", (15, helpY + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)
        cv2.putText(frame, "- Click 'Show' to display keyboard", (15, helpY + 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)
        cv2.putText(frame, "- Click keys to type", (15, helpY + 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)
        cv2.putText(frame, "- Save/Load your text using buttons", (15, helpY + 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)

        cv2.putText(frame, "Shortcuts:", (15, helpY + 155), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (216, 196, 182), 1)
        cv2.putText(frame, "- H: Toggle keyboard", (15, helpY + 175), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)
        cv2.putText(frame, "- S: Save text", (15, helpY + 195), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)
        cv2.putText(frame, "- L: Load text", (15, helpY + 215), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)
        cv2.putText(frame, "- Q: Quit", (15, helpY + 235), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (245, 239, 231), 1)

    cv2.imshow('video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s') and (cv2.getWindowProperty('video', cv2.WND_PROP_VISIBLE) == 1):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(textBox.text)
        cv2.putText(frame, "Text Saved! (Ctrl+S)", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    elif key == ord('h'):
        show = not show
        showKey.text = "Hide" if show else "Show"
    elif key == ord('l'):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                textBox.text = f.read()
            cv2.putText(frame, "Text Loaded! (Ctrl+L)", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        except Exception as e:
            cv2.putText(frame, f"Error Loading Text: {e}", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
    elif key == ord('?'):
        showHelp = not showHelp


cap.release()
cv2.destroyAllWindows()


