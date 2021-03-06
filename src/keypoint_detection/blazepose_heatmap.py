import cv2
import numpy as np
import onnxruntime
from ..utils.heatmap_processing import heatmap_to_keypoints

import mediapipe as mp
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils 
mp_drawing_styles = mp.solutions.drawing_styles

class BlazePoseHeatmap():
    
    def __init__(self, model_path, input_size=(256, 256)):
        self.ort_session = onnxruntime.InferenceSession(model_path)
        self.input_size = input_size

    def preprocess_images(self, images):
        # Convert color to RGB
        resized_images = []
        for i in range(images.shape[0]):
            resized_image = cv2.resize(images[i], self.input_size)
            resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
            resized_images.append(resized_image)
        images = np.array(resized_images)
        mean = np.array([0.5, 0.5, 0.5], dtype=np.float)
        images = np.array(images, dtype=np.float32)
        images = images / 255.0
        images -= mean
        return images

    def detect_keypoints(self, frame, confidence=0.5):
        original_size = np.array([frame.shape[1], frame.shape[0]])
        # net_input = self.preprocess_images(np.array([frame]))
        # ort_inputs = {self.ort_session.get_inputs()[0].name: net_input}
        # ort_outs = self.ort_session.run(None, ort_inputs)

        # # # Visualize
        # # heatmap_viz = np.sum(ort_outs[0][0], axis=2)
        # # heatmap_viz = cv2.resize(heatmap_viz, None, fx=4, fy=4)
        # # cv2.imshow("Heatmap", heatmap_viz)
        # # cv2.waitKey(1)
        
        # keypoints = heatmap_to_keypoints(ort_outs[0])
        # keypoints = keypoints.numpy()
        # keypoints = keypoints[0]

        # thresh_mask = keypoints[:, 2] < confidence
        # keypoints[:, 0][thresh_mask] = 0
        # keypoints[:, 1][thresh_mask] = 0
        # Run MediaPipe Pose and draw pose landmarks.
        with mp_pose.Pose(
            static_image_mode=True, min_detection_confidence=confidence, model_complexity=2) as pose:
            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Print nose landmark.
            x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * original_size[0]
            y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * original_size[1]
            
        keypoints = [x,y]
        return keypoints
