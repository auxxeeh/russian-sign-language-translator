# import block
import cv2
import mediapipe as mp
import time
import math
import numpy as np

#           variables:  one_two
# classes and methods:  oneTwo

class handDetector():
    def __init__(self, mode=False, max_hands=1, detection_conf=0.5, track_conf=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_conf = detection_conf
        self.track_conf = track_conf

        # need to comment it !!!!
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, 
                                        self.detection_conf, self.track_conf)
        self.mp_draw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        image = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(image, hand_landmarks, 
                                                self.mp_hands.HAND_CONNECTIONS)
        
        return image


    def findPosition(self, img, hand_number=0):
        landmarks_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_number]

            for id, lm in enumerate(my_hand.landmark):
                landmarks_list.append([id, [lm.x, lm.y, lm.z]])

        # list of [id, x, y, z]
        return landmarks_list

# for index finger
# 5, 6, 7 on image
def getAngle(point_one, point_two, point_three, edge):
    # point_one = ALWAYS WRIST POINT (0)
    # point_two = 5 (for index finger)
    # point_three  = 6 (for index finger)
    # edge is edge for action
    # point structure is [id, [x, y, z]]

    # preparations
    alpha_point_one = np.array(point_one[1]) - np.array(point_two[1])
    alpha_point_three = np.array(point_three[1]) - np.array(point_two[1])

    # formula
    alpha = 180 - math.acos( math.fabs(alpha_point_one[0] * alpha_point_three[0] +
                                alpha_point_one[1] * alpha_point_three[1] +
                                alpha_point_one[2] * alpha_point_three[2]
                                ) / math.sqrt(
                                    alpha_point_one[0]*alpha_point_one[0] +
                                    alpha_point_one[1]*alpha_point_one[1] +
                                    alpha_point_one[2]*alpha_point_one[2]
                                ) / math.sqrt(
                                    alpha_point_three[0]*alpha_point_three[0] +
                                    alpha_point_three[1]*alpha_point_three[1] +
                                    alpha_point_three[2]*alpha_point_three[2]
                                )) * (180 / math.pi)
    
    # print(alpha)
    return alpha > edge
    
# point one is palm point, other - for finger
# alpha and beta edges - angle bariers
def fingerPose(point_one, point_two, point_three, point_four, alpha_edge, beta_edge):
    if getAngle(point_one, point_two, point_three, alpha_edge):
        if getAngle(point_two, point_three, point_four, beta_edge):
            return "direct"
        else:
            return "arc"
    else:
        if getAngle(point_two, point_three, point_four, beta_edge):
            return "half"
        else:
            return "fold"

# get direction of hand
# point_one is for palm point, point_two is for middle finer firs point
def getDirection(point_one, point_two):
    if point_one[1][1] > point_two[1][1]:
        return "Up"
    else:
        return "Down"

# distance function for two landmarks
def getDistance(point_one, point_two):
    return math.sqrt((point_two[1][0] - point_one[1][0]) * (point_two[1][0] - point_one[1][0]) +
                    (point_two[1][1] - point_one[1][1]) * (point_two[1][1] - point_one[1][1]) +
                    (point_two[1][2] - point_one[1][2]) * (point_two[1][2] - point_one[1][2]))

# check if landmarks are "touched"
def isTouched(point_one, point_two, touch_edge):
    return getDistance(point_one, point_two) <= touch_edge

# main function
def main():
    pTime = 0
    cTime = 0

    cap = cv2.VideoCapture(0)

    detector = handDetector()

    while True:
        # get input image
        success, img = cap.read()
        image = detector.findHands(img)
        landmarks_list = detector.findPosition(img)
        if len(landmarks_list) != 0:
            # pose for index finger
            # print(fingerPose(landmarks_list[0], landmarks_list[5], landmarks_list[6], landmarks_list[7], 150, 110))

            # direction 
            print(getDirection(landmarks_list[0], landmarks_list[9]))

            # distance index-big
            # print(getDistance(landmarks_list[4], landmarks_list[8]))

            # touch index-big
            # print(isTouched(landmarks_list[4], landmarks_list[8], getDistance(landmarks_list[3], landmarks_list[4]) / 1.2))

            # index-middle finger angle
            # true - close
            # false - far
            # print(getFingerPose(landmarks_list[6], landmarks_list[5], landmarks_list[10],160))

        # calculate fps
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        # put fps counter on screen
        cv2.putText(image, str(int(fps)), (50,50), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 200,0), 2)

        #
        cv2.imshow("Image", image) 
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
                break


if __name__ == "__main__":
    main()