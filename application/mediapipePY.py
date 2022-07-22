import cv2
import time
import math as m
import mediapipe as mp
from datetime import datetime
import pandas as pd
import os
class mpEstimate:
    #Static Elements
    # Font (For OpenCV Video)
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Colors
    blue = (255, 127, 0)
    red = (50, 50, 255)
    green = (127, 255, 0)
    dark_blue = (127, 20, 0)
    light_green = (127, 233, 100)
    yellow = (0, 255, 255)
    pink = (255, 0, 255)
    
    feetInfo = pd.DataFrame(columns=["Frame","LH_X","LI_X"])
    #Using Mediapipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    BackCurrentFrameNumber=dict.fromkeys(["Angle1","Angle2","Angle3","Angle4","Angle5"])
    AngleAtStep=[]
    
        
    # Find Distance between 2 points
    def findDistance(self,x1, y1, x2, y2):
        dist = m.sqrt((x2-x1)**2+(y2-y1)**2)
        return dist

    # Calculate angle
    def findAngle(self,x1, y1, x2, y2):
        theta = m.acos((y2 -y1)*(-y1) / (m.sqrt((x2 - x1)**2 + (y2 - y1)**2) * y1))
        degree = int(180/m.pi)*theta
        return degree

    # Calculate difference of x-coordinate of two points
    def findX(self,x_knee,x_hand):
        X = x_hand - x_knee
        return X
    
    
 

    def main(self,file_path,name):
        # Choose which video to use
        # (For webcam input replace file name with 0)
        file_path = file_path
        cap = cv2.VideoCapture(file_path)

        # CV2  properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_size = (width, height)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        print("main ", type(name))
        # Initialize video writer. might take a look at this again.
        # video_output = cv2.VideoWriter('test_{0}.mp4'.format(datetime.datetime.now().strftime("%d-%m-%Y")), fourcc, fps, frame_size)
        savingpath="./application/static/analysedvideo/{}.mp4".format(name)
        video_output = cv2.VideoWriter(savingpath, fourcc, fps, frame_size)
        print('Starting...')
        steps = 0
        stage = None
        max_dis = 0
        access = 1
        velo = 0
        ball_release = None
        maxFeetLength = 0
        currentFrame= 0
        
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        while cap.isOpened():
            # Capture frames
            success, image = cap.read()
            if not success:
                print("No frames left to process!!!")
                break
            # Get fps, height and width
            fps = cap.get(cv2.CAP_PROP_FPS)
            h, w = image.shape[:2]
            # Convert the BGR image to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Process the frame with Mediapipe Pose
            keypoints = self.pose.process(image)
            # Convert the image back to BGR
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            #============ Getting landmarks ============
            lm = keypoints.pose_landmarks
            lmPose = self.mp_pose.PoseLandmark

            # For Angle Component 
            l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)
            l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * h)
            r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * w)
            r_shldr_y = int(lm.landmark[lmPose.RIGHT_SHOULDER].y * h)
            l_ear_x = int(lm.landmark[lmPose.LEFT_EAR].x * w)
            l_ear_y = int(lm.landmark[lmPose.LEFT_EAR].y * h)
            l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * w)
            l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * h)

            # Ankles for feet distance calculation
            l_ank_x = int(lm.landmark[lmPose.LEFT_ANKLE].x * 100)
            l_ank_y = int(lm.landmark[lmPose.LEFT_ANKLE].y * 100)
            r_ank_x = int(lm.landmark[lmPose.RIGHT_ANKLE].x * 100)
            r_ank_y = int(lm.landmark[lmPose.RIGHT_ANKLE].y * 100)

            r_ind_x = int(lm.landmark[lmPose.RIGHT_INDEX].x * 100)
            r_ind_y = int(lm.landmark[lmPose.RIGHT_INDEX].y * 100)
            r_heel_x = int(lm.landmark[lmPose.RIGHT_HEEL].x * 100)
            r_heel_y = int(lm.landmark[lmPose.RIGHT_HEEL].y * 100)

            l_ind_x = int(lm.landmark[lmPose.LEFT_INDEX].x * 100)
            l_ind_y = int(lm.landmark[lmPose.LEFT_INDEX].y * 100)
            l_heel_x = int(lm.landmark[lmPose.LEFT_HEEL].x * 100)
            l_heel_y = int(lm.landmark[lmPose.LEFT_HEEL].y * 100)

            if (cap.get(cv2.CAP_PROP_POS_FRAMES) < 20):
                feetLength = r_ind_x - r_heel_x
                if feetLength > maxFeetLength:
                    maxFeetLength = feetLength

            # For Timing Component
            r_wrist_x = int(lm.landmark[lmPose.RIGHT_WRIST].x * w)
            r_knee_x = int(lm.landmark[lmPose.RIGHT_KNEE].x * w)
            l_knee_x = int(lm.landmark[lmPose.LEFT_KNEE].x * w)

            #============ Functions ============

            # Check for Camera Alignment to be in Proper Sideview
            offset = self.findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)
            if offset < 100:
                cv2.putText(image, str(int(offset)) + ' Aligned', (w - 150, 30), self.font, 0.9, self.green, 2)
            else:
                cv2.putText(image, str(int(offset)) + ' Not Aligned', (w - 150, 30), self.font, 0.9, self.red, 2)

            feetDist = self.findDistance(l_ank_x, l_ank_y, r_ank_x, r_ank_y)

            # Steps Counter (To be improved - ie Thresholds improvements)
            if steps < 5:
                if feetDist > maxFeetLength and stage == 'up':
                    steps += 1
                    stage = "down"
                elif feetDist < maxFeetLength:
                    stage = "up"
        
            # Calculate torso angle
            torso_inclination = self.findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

            #============ Annotations onto video ============
            # Draw landmarks
            cv2.circle(image, (l_shldr_x, l_shldr_y), 7, self.yellow, -1)
            cv2.circle(image, (l_ear_x, l_ear_y), 7, self.yellow, -1)
            cv2.circle(image, (l_shldr_x, l_shldr_y - 100), 7, self.yellow, -1)
            # Right shoulder is pink ball
            cv2.circle(image, (r_shldr_x, r_shldr_y), 7, self.pink, -1)
            cv2.circle(image, (l_hip_x, l_hip_y), 7, self.yellow, -1)
            cv2.circle(image, (l_hip_x, l_hip_y - 100), 7, self.yellow, -1)

            # Display the skeleton
            mp_drawing.draw_landmarks(
                image,
                keypoints.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            # Text for Neck/Torso Angle, Feet distance & Steps
            angle_text_string = 'Back Angle : ' + str(int(torso_inclination)) + 'deg Feet distance: '+ str(int(feetDist)) + ' Steps: '+ str(int(steps))  
            cv2.putText(image, angle_text_string, (10, 50), self.font, 0.8, self.dark_blue, 4)

            # Display angles on the annotation
            cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), self.font, 1.2, self.pink, 2)

            # Join landmarks
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), self.green, 4)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), self.green, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), self.green, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), self.green, 4)
            # if torso_inclination >= 43:
            #     detectedFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            #     BackCurrentFrameNumber.append(detectedFrame-3)
            # # Write frames.
            # video_output.write(image)

            # Write frames.
            if self.BackCurrentFrameNumber['Angle1']==None:
                if steps==1:
                    self.BackCurrentFrameNumber['Angle1']=[cap.get(cv2.CAP_PROP_POS_FRAMES)]
                    self.AngleAtStep.append(torso_inclination)
            if self.BackCurrentFrameNumber['Angle2']==None:
                if steps==2:
                    self.BackCurrentFrameNumber['Angle2']=[cap.get(cv2.CAP_PROP_POS_FRAMES)]
                    self.AngleAtStep.append(torso_inclination)
            if self.BackCurrentFrameNumber['Angle3']==None:
                if steps==3:
                    self.BackCurrentFrameNumber['Angle3']=[cap.get(cv2.CAP_PROP_POS_FRAMES)]
                    self.AngleAtStep.append(torso_inclination)
            if self.BackCurrentFrameNumber['Angle4']==None:
                if steps==4:
                    self.BackCurrentFrameNumber['Angle4']=[cap.get(cv2.CAP_PROP_POS_FRAMES)]
                    self.AngleAtStep.append(torso_inclination)
            if self.BackCurrentFrameNumber['Angle5']==None:
                if steps==5:
                    self.BackCurrentFrameNumber['Angle5']=[cap.get(cv2.CAP_PROP_POS_FRAMES)]
                    self.AngleAtStep.append(torso_inclination)
            
            video_output.write(image)
        
        print('Video is done!')
        cap.release()
        video_output.release()
        return self.AngleAtStep
        
        
    def screenshot(self,file_path,name):
        print("Screenshot Started")
        path ='./application/static/Analysedphoto'
        isExist = os.path.exists(path)

        if not isExist:
        # Create a new directory because it does not exist 
            os.makedirs(path)
            print("Analysedphoto folder is created!")
        print(file_path)
        cap=cv2.VideoCapture(file_path)
        x=0
        bool=True
        print(self.BackCurrentFrameNumber.values())
        #('test_{0}.mp4'.format(datetime.datetime.now().strftime("%d-%m-%Y")
        # date=datetime.utcnow()
        # print(date)
        # print(name)
        frameLen=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # total number of frames in the video
        print(frameLen)
        while bool:  
            for i in range(0,frameLen,1):
                if x>=len(self.BackCurrentFrameNumber):
                    bool=False
                    break
                # print("iv1 ", i)
                # print(x<len(BackCurrentFrameNumber))
                ret, frame= cap.read()
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                for val in self.BackCurrentFrameNumber.values():       
                    if i == val[0] :
                        print(cap.get(cv2.CAP_PROP_POS_FRAMES))
                        # print("iv2", i)
                        
                        print(x)
                        # REMOVED TEMPORARILY FOR PRESENTATION.
                        #cv2.imwrite("./application/static/Analysedphoto/frame_%s_%d.jpg"%(name,x), frame)     # save frame as JPEG file   
                        cv2.imwrite("./application/static/Analysedphoto/frame_%d%s.jpg"%(x,name), frame)     # save frame as JPEG file   
                        x=x+1
                        print('Read a new frame: ', ret)