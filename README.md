# TypeFree-Virtual-Keyboard-using-finger-recognition-
Developed an AI-powered touchless interface that enables users to type, draw on a virtual whiteboard, and execute system shortcuts using hand gestures captured via a webcam. The system enhances hygiene and accessibility by replacing physical input devices with real-time hand tracking and a custom "dwell-time" algorithm to ensure input accuracy

Features
* 3-in-1 Interaction: Includes a virtual keyboard for typing, a digital whiteboard for drawing, and gesture shortcuts for system commands.
* Touchless Interface: Uses a webcam to track hand movements, removing the need for a physical mouse or keyboard.
* User Dashboard: Features a sign-in system and a personal profile to track typing speed and accuracy.
* Session Saving: Allows users to save their text and whiteboard drawings directly to their account.

How it Works
* AI Hand Tracking: Uses MediaPipe and OpenCV to identify and track 21 points on your hand in real-time.
* Smart Typing: Uses a "dwell-time" rule—a key is only pressed if your finger stays on it for a moment—to prevent mistakes.
* System Integration: Uses the Pynput library so you can type into any app on your computer, not just the project window.

Key Benefits
* Hygienic: Ideal for public places like ATMs and hospitals because it is completely touch-free.
* Accessible: Helps elderly users and people with motor impairments interact with computers more easily.
* Secure: No physical contact means no fingerprints are left behind on screens or buttons.
