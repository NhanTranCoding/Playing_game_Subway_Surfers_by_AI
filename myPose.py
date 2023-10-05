import cv2
import mediapipe as mp
import math
class myPose():
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5, threshold_lef_right=110,
                 threshold_up_down=65, threshold_clap=100):
        self.mp_pose = mp.solutions.pose
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.pose = self.mp_pose.Pose(min_detection_confidence=self.min_detection_confidence,
                                      min_tracking_confidence=self.min_tracking_confidence)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.threshold_lef_right = threshold_lef_right
        self.threshold_up_down = threshold_up_down
        self.threshold_clap = threshold_clap

        self.count_l = 0
        self.count_r = 0
    def dectectPose(self, image):
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = self.pose.process(image)
        image.flags.writeable = True
        return image, result
    def getCheckPoint(self, image, result, center_box, drawing=True):
        if result.pose_landmarks is not None:
            img_height, img_width, _ = image.shape
            # accuracy của các vị trí
            # print(result.pose_landmarks.landmark[11].visibility)
            left_shoulder_x, left_shoulder_y = int(result.pose_landmarks.landmark[11].x * img_width), \
                                               int(result.pose_landmarks.landmark[11].y * img_height)
            right_shoulder_x, right_shoulder_y = int(result.pose_landmarks.landmark[12].x * img_width), \
                                                 int(result.pose_landmarks.landmark[12].y * img_height)
            left_hip_x, left_hip_y = int(result.pose_landmarks.landmark[23].x * img_width), \
                                     int(result.pose_landmarks.landmark[23].y * img_height)
            right_hip_x, right_hip_y = int(result.pose_landmarks.landmark[24].x * img_width), \
                                       int(result.pose_landmarks.landmark[24].y * img_height)
            checkpoint = ((left_shoulder_x + right_shoulder_x + left_hip_x + right_hip_x) // 4,
                          (left_shoulder_y + right_shoulder_y + left_hip_y + right_hip_y) // 4)
            # print(checkpoint)
            cv2.circle(image, checkpoint, 20, (0, 0, 255), 3)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            image = cv2.rectangle(image, center_box[0], center_box[1], (0, 255, 0), 3)
            if drawing:
                self.mp_drawing.draw_landmarks(
                    image,
                    result.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )

            return image, checkpoint
        return image, None
    def checkPose_LRUD(self, checkpoint,center_box):
        LRUD = None
        if checkpoint is not None:
            if checkpoint[1] < center_box[0][1]:
                LRUD = "up"
            elif checkpoint[0] < center_box[1][0] and center_box[0][1] <= checkpoint[1] <= center_box[1][1]:
                LRUD = "right"
                self.count_r += 1
                if self.count_r == 1:
                    center_box = [(center_box[0][0] - self.threshold_lef_right, center_box[0][1] + 30),
                                  (center_box[1][0] - self.threshold_lef_right, center_box[1][1] + 30)]
                else:
                    center_box = [(center_box[0][0] - self.threshold_lef_right, center_box[0][1]),
                                  (center_box[1][0] - self.threshold_lef_right, center_box[1][1])]
            elif checkpoint[1] > center_box[1][1]:
                LRUD = "down"
            elif checkpoint[0] > center_box[0][0] and center_box[0][1] <= checkpoint[1] <= center_box[1][1]:
                self.count_l += 1
                if self.count_l == 1:
                    center_box = [(center_box[0][0] + self.threshold_lef_right, center_box[0][1] + 30),
                                  (center_box[1][0] + self.threshold_lef_right, center_box[1][1] + 30)]
                else:
                    center_box = [(center_box[0][0] + self.threshold_lef_right, center_box[0][1]),
                                  (center_box[1][0] + self.threshold_lef_right, center_box[1][1])]
                LRUD = "left"

        return LRUD, center_box
    def checkClap(self, image, result):
        if result.pose_landmarks is not None:
            img_height, img_width, _ = image.shape
            CLAP = "N"
            left_hand_x, left_hand_y = int(result.pose_landmarks.landmark[15].x * img_width), \
                                               int(result.pose_landmarks.landmark[15].y * img_height)
            right_hand_x, right_hand_y = int(result.pose_landmarks.landmark[16].x * img_width), \
                                                 int(result.pose_landmarks.landmark[16].y * img_height)
            distance = int(math.hypot(left_hand_x - right_hand_x, left_hand_y-right_hand_y))
            if distance < self.threshold_clap:
                CLAP = "Y"
            return CLAP
        return None





