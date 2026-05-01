import cv2
import mediapipe as mp


class HandGestureRecognizer:
	"""
	Lightweight hand gesture recognizer using MediaPipe Hands.

	Usage:
	- Call process(frame_bgr) with a BGR frame to get a list of gesture labels
	  for each detected hand (left-to-right in the image).
	- Gestures returned: "peace", "thumbs_up", "open_palm", "pointing",
	  "rock_on", "three_fingers", or "none".
	"""

	def __init__(self, detection_confidence: float = 0.7, tracking_confidence: float = 0.7, max_hands: int = 2):
		self._mp_hands = mp.solutions.hands
		self._hands = self._mp_hands.Hands(
			static_image_mode=False,
			max_num_hands=max_hands,
			min_detection_confidence=detection_confidence,
			min_tracking_confidence=tracking_confidence,
		)

	def process(self, frame_bgr):
		"""
		Process a BGR frame and return a list of gesture labels per detected hand.
		"""
		results = self._hands.process(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
		if not results.multi_hand_landmarks:
			return []

		gestures = []
		for hand_landmarks in results.multi_hand_landmarks:
			lm_list = self._landmarks_to_list(hand_landmarks, frame_bgr)
			gestures.append(self._classify(lm_list))
		return gestures

	@staticmethod
	def _landmarks_to_list(hand_landmarks, frame_bgr):
		"""Convert landmarks to list of [id, x, y] pixel coords."""
		h, w, _ = frame_bgr.shape
		lm_list = []
		for idx, lm in enumerate(hand_landmarks.landmark):
			lm_list.append([idx, int(lm.x * w), int(lm.y * h)])
		return lm_list

	def _classify(self, lm_list):
		"""
		Classify gesture based on finger up/down states.
		Assumes mirrored webcam (cv2.flip(frame, 1)). If not mirrored, you may
		need to invert the thumb x-comparison (< -> >) below.
		"""
		if not lm_list or len(lm_list) < 21:
			return "none"

		# Finger tip indices according to MediaPipe Hands
		tip_ids = [4, 8, 12, 16, 20]

		# Determine which fingers are up: [thumb, index, middle, ring, pinky]
		fingers_up = []

		# Thumb: compare x positions (mirrored view)
		thumb_is_up = 1 if lm_list[tip_ids[0]][1] < lm_list[tip_ids[0] - 1][1] else 0
		fingers_up.append(thumb_is_up)

		# Other fingers: tip y above PIP y means up
		for i in range(1, 5):
			is_up = 1 if lm_list[tip_ids[i]][2] < lm_list[tip_ids[i] - 2][2] else 0
			fingers_up.append(is_up)

		# Pattern matching
		# peace: index + middle
		if fingers_up == [0, 1, 1, 0, 0]:
			return "peace"
		# thumbs up: only thumb
		if fingers_up == [1, 0, 0, 0, 0]:
			return "thumbs_up"
		# open palm: all
		if fingers_up == [1, 1, 1, 1, 1]:
			return "open_palm"
		# pointing: only index
		if fingers_up == [0, 1, 0, 0, 0]:
			return "pointing"
		# rock on: index + pinky
		if fingers_up == [0, 1, 0, 0, 1]:
			return "rock_on"
		# three fingers: index + middle + ring
		if fingers_up == [0, 1, 1, 1, 0]:
			return "three_fingers"

		return "none"
