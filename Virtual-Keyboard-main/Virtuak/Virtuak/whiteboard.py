import cv2
import time
import mediapipe as mp
import numpy as np
import os
import sys
from datetime import datetime
import traceback


def _import_gesture_recognizer():
    try:
        from gestures import HandGestureRecognizer
        return HandGestureRecognizer()
    except Exception:
        return None


class HandTracker:
    def __init__(self, detectionCon: float = 0.8, trackCon: float = 0.8):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon,
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img, draw: bool = False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if draw and self.results and self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def getPosition(self, img, handNo: int = 0, draw: bool = False):
        lmList = []
        if self.results and self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for idx, lm in enumerate(myHand.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([idx, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 3, (255, 0, 0), cv2.FILLED)
        return lmList


class Key:
    def __init__(self, x, y, w, h, text):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text

    def drawKey(self, img, text_color=(245, 239, 231), bg_color=(33, 53, 85), alpha=0.8, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, thickness=2):
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


def _log(message: str):
    try:
        out_dir = os.path.join(os.path.dirname(__file__), 'instance')
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, 'whiteboard.log'), 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")
    except Exception:
        pass


def _open_camera():
    # Try common camera indices
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, 0]
    for idx in (0, 1, 2, 3):
        for backend in backends:
            be_name = 'CAP_DSHOW' if backend == cv2.CAP_DSHOW else ('CAP_MSMF' if backend == cv2.CAP_MSMF else 'DEFAULT')
            _log(f'Trying camera index {idx} with {be_name}')
            try:
                cap = cv2.VideoCapture(idx, backend) if backend != 0 else cv2.VideoCapture(idx)
                if cap.isOpened():
                    # Configure
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    # Warmup read
                    ok, frame = cap.read()
                    if ok and frame is not None:
                        _log(f'Opened camera index {idx} with {be_name}')
                        return cap, frame
            except Exception as e:
                _log(f'Exception opening camera {idx} with {be_name}: {e}')
            finally:
                try:
                    if not ('cap' in locals() and cap.isOpened()):
                        pass
                except Exception:
                    pass
            try:
                cap.release()
            except Exception:
                pass
            _log(f'Camera index {idx} failed with {be_name}')
    return None, None


def run_whiteboard():
    cap = None
    try:
        cap, frame = _open_camera()
        if frame is None:
            # Show an error window and wait for key instead of exiting instantly
            _log('No camera available; showing error screen')
            err = np.zeros((360, 800, 3), dtype=np.uint8)
            cv2.putText(err, 'Camera not available', (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(err, 'Close other apps using the camera and try again', (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(err, 'Press Q to quit, or R to retry', (30, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
            cv2.imshow('whiteboard', err)
            while True:
                key = cv2.waitKey(0) & 0xFF
                if key in (ord('q'), ord('Q'), 27):
                    cv2.destroyAllWindows()
                    return
                if key in (ord('r'), ord('R')):
                    cap, frame = _open_camera()
                    if frame is not None:
                        break
                    cv2.imshow('whiteboard', err)

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        canvas = np.full((h, w, 3), 255, dtype=np.uint8)
        tracker = HandTracker()
        recognizer = _import_gesture_recognizer()

        drawing = False
        draw_enabled = True
        eraser_mode = False
        prev_point = None
        # color palette for rock_on
        palette = [
            (62, 88, 121), (216, 196, 182), (231, 76, 60), (46, 204, 113),
            (52, 152, 219), (155, 89, 182), (241, 196, 15), (0, 0, 0)
        ]
        color_index = 0
        color = palette[color_index]
        thickness = 6

        lastGesture = "none"
        holdStart = 0.0
        lastFire = 0.0
        lastDetect = 0.0

        # Use autosize so mouse coordinates match image coordinates
        cv2.namedWindow('whiteboard', cv2.WINDOW_AUTOSIZE)

        # Simple on-screen buttons (top-right)
        btn_w, btn_h = 160, 42
        btn_pad = 12
        btn_x = w - btn_w - 20
        btn_draw_y = 20
        btn_eraser_y = btn_draw_y + btn_h + btn_pad
        btn_save_y = btn_eraser_y + btn_h + btn_pad
        btn_clear_y = btn_save_y + btn_h + btn_pad
        btn_quit_y = btn_clear_y + btn_h + btn_pad

        # Buttons as Keys for consistent UI feel
        btn_draw = Key(btn_x, btn_draw_y, btn_w, btn_h, 'Draw: ON')
        btn_mode = Key(btn_x, btn_eraser_y, btn_w, btn_h, 'Mode: Pen')
        btn_save = Key(btn_x, btn_save_y, btn_w, btn_h, 'Save')
        btn_clear = Key(btn_x, btn_clear_y, btn_w, btn_h, 'Clear')
        btn_quit = Key(btn_x, btn_quit_y, btn_w, btn_h, 'Quit')

        clicked_pos = {'x': -1, 'y': -1}
        last_ui_click = 0.0

        def point_in_rect(px, py, x, y, w_, h_):
            return x <= px <= x + w_ and y <= py <= y + h_

        def _on_mouse(event, mx, my, flags, param):
            if event == cv2.EVENT_LBUTTONUP:
                clicked_pos['x'], clicked_pos['y'] = mx, my
                _log(f'Click at x={mx}, y={my}')

        cv2.setMouseCallback('whiteboard', _on_mouse)

        while True:
            ok, frame = cap.read()
            if not ok:
                # Keep window open with error message instead of closing instantly
                _log('Lost camera feed; showing error and waiting')
                out = np.zeros((360, 800, 3), dtype=np.uint8)
                cv2.putText(out, 'Lost camera feed', (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(out, 'Ensure no other app is using the camera', (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(out, 'Press Q to quit, or R to retry', (30, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
                cv2.imshow('whiteboard', out)
                key = cv2.waitKey(0) & 0xFF
                if key in (ord('q'), ord('Q'), 27):
                    break
                if key in (ord('r'), ord('R')):
                    # Try reopening camera
                    try:
                        cap.release()
                    except Exception:
                        pass
                    cap, frame = _open_camera()
                    if frame is None:
                        break
                    continue

            frame = cv2.flip(frame, 1)
            # Detect hand
            frame = tracker.findHands(frame, draw=False)
            lm = tracker.getPosition(frame, draw=False)

            index_tip = None
            thumb_tip = None
            if lm:
                index_tip = (lm[8][1], lm[8][2])
                thumb_tip = (lm[4][1], lm[4][2])

            # Pinch detection (draw only while pinching)
            pinching = False
            if index_tip and thumb_tip:
                dx = index_tip[0] - thumb_tip[0]
                dy = index_tip[1] - thumb_tip[1]
                dist = int((dx*dx + dy*dy) ** 0.5)
                pinching = dist < 40

            # Gesture recognition
            label = "none"
            now = time.time()
            if recognizer is not None:
                labels = recognizer.process(frame)
                label = labels[0] if labels else "none"
                if label != "none":
                    lastDetect = now
                if label == "none" and lastGesture != "none" and (now - lastDetect) <= 0.3:
                    label = lastGesture

            if label != lastGesture:
                lastGesture = label
                holdStart = now if label != "none" else 0.0
            else:
                if label != "none" and holdStart > 0 and (now - holdStart) >= 1.0 and (now - lastFire) >= 1.5:
                    # Keep only non-conflicting gestures; UI handles draw/eraser/quit
                    if label == "open_palm":
                        canvas[:] = 255
                    elif label == "thumbs_up":
                        out_dir = os.path.join(os.path.dirname(__file__), 'instance')
                        os.makedirs(out_dir, exist_ok=True)
                        out_path = os.path.join(out_dir, f'whiteboard_{int(time.time())}.png')
                        merged = frame.copy()
                        nonzero = np.any(canvas != 0, axis=2)
                        merged[nonzero] = canvas[nonzero]
                        cv2.imwrite(out_path, merged)
                        cv2.putText(frame, f'Saved: {os.path.basename(out_path)}', (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)
                    elif label == "rock_on":
                        color_index = (color_index + 1) % len(palette)
                        color = palette[color_index]
                    # Disable gesture-based eraser/draw toggles to rely on UI buttons
                    lastFire = now
                    holdStart = now

            # Handle air pinch clicks on buttons (cooldown 500ms)
            if pinching and index_tip is not None:
                if (point_in_rect(index_tip[0], index_tip[1], btn_x, btn_draw_y, btn_w, btn_h) or
                    point_in_rect(index_tip[0], index_tip[1], btn_x, btn_eraser_y, btn_w, btn_h) or
                    point_in_rect(index_tip[0], index_tip[1], btn_x, btn_save_y, btn_w, btn_h) or
                    point_in_rect(index_tip[0], index_tip[1], btn_x, btn_clear_y, btn_w, btn_h) or
                    point_in_rect(index_tip[0], index_tip[1], btn_x, btn_quit_y, btn_w, btn_h)):
                    if now - last_ui_click > 0.5:
                        if point_in_rect(index_tip[0], index_tip[1], btn_x, btn_draw_y, btn_w, btn_h):
                            draw_enabled = not draw_enabled
                        elif point_in_rect(index_tip[0], index_tip[1], btn_x, btn_eraser_y, btn_w, btn_h):
                            eraser_mode = not eraser_mode
                        elif point_in_rect(index_tip[0], index_tip[1], btn_x, btn_save_y, btn_w, btn_h):
                            out_dir = os.path.join(os.path.dirname(__file__), 'instance')
                            os.makedirs(out_dir, exist_ok=True)
                            out_path = os.path.join(out_dir, f'whiteboard_{int(time.time())}.png')
                            cv2.imwrite(out_path, canvas)
                        elif point_in_rect(index_tip[0], index_tip[1], btn_x, btn_clear_y, btn_w, btn_h):
                            canvas[:] = 255
                        elif point_in_rect(index_tip[0], index_tip[1], btn_x, btn_quit_y, btn_w, btn_h):
                            break
                        last_ui_click = now
                    # If interacting with UI, skip drawing this frame
                    can_draw_this_frame = False
                else:
                    can_draw_this_frame = True
            else:
                can_draw_this_frame = True

            # Drawing logic: draw when in drawing mode and index finger present
            if can_draw_this_frame and draw_enabled and pinching and index_tip is not None:
                if prev_point is None:
                    prev_point = index_tip
                # Use white for eraser so it clears to the white canvas background
                stroke_color = (255, 255, 255) if eraser_mode else color
                stroke_thickness = max(thickness, 14) if eraser_mode else thickness
                cv2.line(canvas, prev_point, index_tip, stroke_color, stroke_thickness)
                prev_point = index_tip
            else:
                prev_point = None

            # Compose output: show only the canvas (white) and hand indicators
            out = canvas.copy()
            if index_tip:
                cv2.circle(out, index_tip, 10, (62, 88, 121), -1)
                cv2.circle(out, index_tip, 8, (216, 196, 182), 2)
            if thumb_tip:
                cv2.circle(out, thumb_tip, 8, (216, 196, 182), -1)
                cv2.circle(out, thumb_tip, 6, (245, 239, 231), 2)

            # UI: gesture header and progress bar
            friendly = {
                "none": "None",
                "peace": "Peace",
                "thumbs_up": "Save",
                "open_palm": "Clear",
                "pointing": "",
                "rock_on": "Color Toggle",
                "three_fingers": "",
            }
            labelToShow = friendly.get(lastGesture, lastGesture)
            cv2.rectangle(out, (5, 5), (420, 35), (33, 53, 85), -1)
            cv2.rectangle(out, (5, 5), (420, 35), (62, 88, 121), 2)
            cv2.putText(out, f"Gesture: {labelToShow}", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 239, 231), 2)
            if lastGesture != "none" and holdStart > 0:
                progress = max(0.0, min(1.0, (now - holdStart) / 1.0))
                cv2.rectangle(out, (5, 40), (305, 60), (33, 53, 85), -1)
                cv2.rectangle(out, (5, 40), (305, 60), (62, 88, 121), 2)
                fillW = int(298 * progress)
                cv2.rectangle(out, (8, 43), (8 + fillW, 57), (216, 196, 182), -1)

            # HUD: mode indicators
            cv2.putText(out, f'Draw Enabled: {"ON" if draw_enabled else "OFF"}', (15, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (62, 88, 121), 2)
            cv2.putText(out, f'Mode: {"Eraser" if eraser_mode else "Pen"}', (15, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (216, 196, 182), 2)

            # Draw UI buttons
            btn_draw.text = f'Draw: {"ON" if draw_enabled else "OFF"}'
            btn_mode.text = f'Mode: {"Eraser" if eraser_mode else "Pen"}'
            for key_btn, active in [
                (btn_draw, draw_enabled),
                (btn_mode, eraser_mode),
                (btn_save, False),
                (btn_clear, False),
                (btn_quit, False),
            ]:
                bg = (62, 88, 121) if active else (33, 53, 85)
                key_btn.drawKey(out, text_color=(245, 239, 231), bg_color=bg, alpha=0.8, fontScale=0.6, thickness=2)

            cv2.imshow('whiteboard', out)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break
            elif k == ord('c'):
                canvas[:] = 255
            elif k == ord('s'):
                out_dir = os.path.join(os.path.dirname(__file__), 'instance')
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, f'whiteboard_{int(time.time())}.png')
                cv2.imwrite(out_path, out)

            # Handle UI button clicks
            cx, cy = clicked_pos['x'], clicked_pos['y']
            if cx != -1 and cy != -1:
                if btn_draw.isOver(cx, cy):
                    draw_enabled = not draw_enabled
                elif btn_mode.isOver(cx, cy):
                    eraser_mode = not eraser_mode
                elif btn_save.isOver(cx, cy):
                    out_dir = os.path.join(os.path.dirname(__file__), 'instance')
                    os.makedirs(out_dir, exist_ok=True)
                    out_path = os.path.join(out_dir, f'whiteboard_{int(time.time())}.png')
                    cv2.imwrite(out_path, out)
                elif btn_clear.isOver(cx, cy):
                    canvas[:] = 255
                elif btn_quit.isOver(cx, cy):
                    break
                clicked_pos['x'], clicked_pos['y'] = -1, -1

    except Exception:
        err_text = traceback.format_exc()
        _log(f'Unhandled exception in whiteboard: {err_text}')
        img = np.zeros((480, 900, 3), dtype=np.uint8)
        cv2.putText(img, 'Whiteboard crashed:', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        y = 100
        for line in err_text.splitlines()[-10:]:
            cv2.putText(img, line[:90], (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            y += 30
        cv2.putText(img, 'Press any key to exit', (20, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 180), 2)
        cv2.imshow('whiteboard', img)
        cv2.waitKey(0)
    finally:
        try:
            if cap is not None:
                cap.release()
        finally:
            cv2.destroyAllWindows()


if __name__ == '__main__':
    run_whiteboard()


