from inspect import currentframe
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
    # From all the Mediapipe Computer Vision Solutions, select to use Mediapipe Pose============================================
    mp_pose = mp.solutions.pose

    # Call the MediaPipe Pose Model with defined parameters.
    # min_detection_confidence - minimum confidence required to detect a PERSON (not landmarks)
    # min_tracking_confidence  - minimum confidence required to detect the landmarks
    # model_complexity - complexity of the pose landmark model (0,1,2) Where 2 is the most complex, increasing landmark accuracy and time taken to run
    # smooth_landmarks - reduce the jitter for the detected landmarks based on the previous landmark position
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.8, model_complexity=2, smooth_landmarks=True)

    BackCurrentFrameNumber=dict.fromkeys(["Angle1","Angle2","Angle3","Angle4","Angle5"])
    timingframenumber=[]
    AngleAtStep=[]
    TimingofRelease=[]
    TimingOrBack=True
    feetLenAccess = 1
    # Variables for dynamic font size
    fontsize = 1
    thick = 4
    text_y = 50
    font_access = 1
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
    
    def timing(self,file_path, name):
        # Choose which video to use
        # (For webcam input replace file name with 0)
        file_path = file_path
        cap = cv2.VideoCapture(file_path)
        # CV2  properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_size = (width, height)
        fourcc = cv2.VideoWriter_fourcc(*'h264') #for mp4 video to be played in website
        print("main ", type(name))
        # Initialize video writer. might take a look at this again.
        # video_output = cv2.VideoWriter('test_{0}.mp4'.format(datetime.datetime.now().strftime("%d-%m-%Y")), fourcc, fps, frame_size)
        savingpath="./application/static/analysedvideo/{}.mp4".format(name)
        video_output = cv2.VideoWriter(savingpath, fourcc, fps, frame_size)
        print('Starting...')
       

        # Variables for Step Counter
        steps = 0
        stage = None
        maxFeetLength = 50

        # Preparing the dataframes
        # Dataframe to store the Velocity Information
        feetVelo = pd.DataFrame(columns=["Frame","LH_X","LI_X", "Heel Velo", "Index Velo", "Wrist_Y","Wrist_X"])

        # Variables for Timing
        access = 1
        velo = 0
        ball_release = None
        sliding = False
        kneesDis = 0
        diffBtY = 0
        throwing = False
        throwCount = 0
        fastFeet = False
        # preFrame_Y=0        
        
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
            # Get the current frame number
            currentFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)

            #============ Getting landmarks ============
            lm = keypoints.pose_landmarks
            lmPose = self.mp_pose.PoseLandmark
            if lm is not None:
                # To account to most videos being rectangular, we have to multiply width and height
                # X-Axis will multiply be the width of the video and the Y-Axis will multiply by the height
                # This is to remain the aspect ratio of the video, and make sure the X and Y will be in the same scale.

                # For Timing Component
                r_wrist_x = int(lm.landmark[lmPose.RIGHT_WRIST].x * w)
                r_knee_x = int(lm.landmark[lmPose.RIGHT_KNEE].x * w)
                l_knee_x = int(lm.landmark[lmPose.LEFT_KNEE].x * w)
                r_wrist_y = int(lm.landmark[lmPose.RIGHT_WRIST].y * h)
                r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * w)

                # Ankles for feet distance calculation
                l_ank_x = int(lm.landmark[lmPose.LEFT_ANKLE].x * w)
                r_ank_x = int(lm.landmark[lmPose.RIGHT_ANKLE].x * w)

                r_ind_x = int(lm.landmark[lmPose.RIGHT_INDEX].x * w)
                r_heel_x = int(lm.landmark[lmPose.RIGHT_HEEL].x * w)
                
                # Calculation of Velo
                # Heel is not * w to standardise for all videos (Make all videos have the same range)
                l_heel_x = int(lm.landmark[lmPose.LEFT_HEEL].x * 500)

                # When x-val is at the max, foot is placed on the floor
                # If foot is able to be detected do this
                if (r_ind_x != None or r_heel_x != None )and self.feetLenAccess == 1:
                    maxFrame = currentFrame + 20
                    self.feetLenAccess = 0
                if (currentFrame < maxFrame):
                    feetLength = r_ind_x - r_heel_x
                    if feetLength > maxFeetLength:
                        maxFeetLength = feetLength
                        
                #============ Functions ============

                feetDist =  abs(self.findX(l_ank_x, r_ank_x))

                # Steps Counter (To be improved - ie Thresholds improvements)
                if steps < 5:
                    if feetDist > maxFeetLength and stage == 'up':
                        steps += 1
                        stage = "down"
                    elif feetDist < maxFeetLength:
                        stage = "up"
            
                if currentFrame > 20:
                    preFrame_Y = currentFrame - 3
                    diffBtY = r_wrist_y - feetVelo["Wrist_Y"][preFrame_Y]
                    diffBtX = r_wrist_x - feetVelo["Wrist_X"][preFrame_Y]
                if diffBtY > 0 and r_shldr_x>r_wrist_x:
                    throwCount = throwCount+1
                    if throwCount == 3:
                        throwing = True
                else:
                    throwCount = 0 

                if (feetDist > 2*maxFeetLength and throwing == True) or sliding==True :
                    sliding=True
                    # currentFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    pre = currentFrame - 4
                    if currentFrame > 10:
                        # Calculate Velocity with this frame and 4 frames before
                        velo = abs(((l_heel_x - feetVelo["LH_X"][pre])/(currentFrame-pre)))
                        if velo > 3:
                            fastFeet = True
                        if velo < 0.6 and access == 1 and fastFeet == True:
                            kneesDis = abs(r_knee_x - l_knee_x)
                            print("distance between knee are ", kneesDis)
                            access = 0
                            ball_train_feet_dis = self.findX(r_knee_x, r_wrist_x)
                            ball_slide_feet_dis = self.findX(l_knee_x, r_wrist_x)
                            # Calculate distance between hand and knees to determine ball release type
                            if ball_train_feet_dis < 0:
                                ballDisBtKnees = abs(ball_train_feet_dis)
                                print("Ball distance betweeen traning leg are ", ballDisBtKnees)
                                if ballDisBtKnees <= 0.20*kneesDis:
                                    ball_release = "Delayed 2"
                                else:
                                    ball_release = "Late"
                            elif ball_train_feet_dis > 0 and ball_slide_feet_dis < 0:
                                ballDisBtKnees = abs(ball_train_feet_dis)
                                print("Ball distance betweeen traning leg are ", ballDisBtKnees)
                                if ballDisBtKnees  <= 0.20*kneesDis:
                                    ball_release = "Delayed 2"
                                elif ballDisBtKnees <= 0.80*kneesDis:
                                    ball_release = "Delayed 1"
                                else:
                                    ball_release = "Traditional"
                            elif ball_slide_feet_dis > 0:
                                ball_release = "Early"
                            self.timingframenumber.append(currentFrame)
                            
            
                # Append to array
                feetStuff = {"Frame": currentFrame+1, "LH_X":l_heel_x,"Velocity": velo,"Wrist_Y":r_wrist_y,"Wrist_X":r_wrist_x}
                feetVelo = feetVelo.append(feetStuff, ignore_index=True)
                #============ Annotations onto video ============
                # Define font size 
                if h >= 2160 and self.font_access == 1:
                    print("bigger than 2160", h)
                    self.thick = 10
                    self.text_y = 80
                    self.fontsize = 3
                    self.font_access = 0
                elif h >= 1080 and self.font_access == 1:
                    print("bigger than 1080, ", h)
                    self.fontsize = 1.5
                    self.font_access = 0
                elif self.font_access == 1:
                    print("smaller than 1080, ", h)
                    self.thick = 2
                    self.fontsize = 0.6
                    self.font_access = 0
                    
                # TIMING
                # Display the skeleton
                mp_drawing.draw_landmarks(
                    image,
                    keypoints.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                # Text for Neck/Torso Angle, Feet distance & Steps

                # STR for timing
                angle_text_string = 'Frame: '+str(currentFrame) +' Feet distance: '+ str(int(feetDist)) + ' Release: '+ str(ball_release) +" Thrown " +str(throwing)+' Velocity '+ str(velo) 
                cv2.putText(image, angle_text_string, (10, self.text_y), self.font, self.fontsize, self.dark_blue, self.thick, cv2.LINE_AA)
                
                video_output.write(image)
            else:
                # print("Cannot Detect Anything!")
                # Write frames.
                video_output.write(image)    
        print('Video is done!')
        cap.release()
        video_output.release()
        self.TimingOrBack=True
        return ball_release     
 

    def backAngle(self,file_path,name):
        # Choose which video to use
        # (For webcam input replace file name with 0)
        file_path = file_path
        cap = cv2.VideoCapture(file_path)
        # CV2  properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_size = (width, height)
        fourcc = cv2.VideoWriter_fourcc(*'h264') #for mp4 video to be played in website
        print("main ", type(name))
        # Initialize video writer. might take a look at this again.
        # video_output = cv2.VideoWriter('test_{0}.mp4'.format(datetime.datetime.now().strftime("%d-%m-%Y")), fourcc, fps, frame_size)
        savingpath="./application/static/analysedvideo/{}.mp4".format(name)
        video_output = cv2.VideoWriter(savingpath, fourcc, fps, frame_size)
        print('Starting...')
        # Variables for dynamic font size
        

        # Variables for Step Counter
        steps = 0
        stage = None
        maxFeetLength = 50
        currentFrame= 0
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
            # Get the current frame number
            currentFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)

            #============ Getting landmarks ============
            lm = keypoints.pose_landmarks
            lmPose = self.mp_pose.PoseLandmark
            if lm is not None:
                # To account to most videos being rectangular, we have to multiply width and height
                # X-Axis will multiply be the width of the video and the Y-Axis will multiply by the height
                # This is to remain the aspect ratio of the video, and make sure the X and Y will be in the same scale.

                # For Angle Component 
                l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)
                l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * h)
                r_shldr_x = int(lm.landmark[lmPose.RIGHT_SHOULDER].x * w)
                r_shldr_y = int(lm.landmark[lmPose.RIGHT_SHOULDER].y * h)
                l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * w)
                l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * h)

                # Ankles for feet distance calculation
                l_ank_x = int(lm.landmark[lmPose.LEFT_ANKLE].x * w)
                l_ank_y = int(lm.landmark[lmPose.LEFT_ANKLE].y * h)
                r_ank_x = int(lm.landmark[lmPose.RIGHT_ANKLE].x * w)
                r_ank_y = int(lm.landmark[lmPose.RIGHT_ANKLE].y * h)
                r_ind_x = int(lm.landmark[lmPose.RIGHT_INDEX].x * w)
                r_heel_x = int(lm.landmark[lmPose.RIGHT_HEEL].x * w)

                # When x-val is at the max, foot is placed on the floor
                # If foot is able to be detected do this
                if (r_ind_x != None or r_heel_x != None )and self.feetLenAccess == 1:
                    maxFrame = currentFrame + 20
                    self.feetLenAccess = 0
                if (currentFrame < maxFrame):
                    feetLength = r_ind_x - r_heel_x
                    if feetLength > maxFeetLength:
                        maxFeetLength = feetLength
                        
                #============ Functions ============

                # Check for Camera Alignment to be in Proper Sideview
                offset = self.findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)
                if offset < 100:
                    cv2.putText(image, str(int(offset)) + ' Aligned', (w - 150, 30), self.font, 0.9, self.green, 2)
                else:
                    cv2.putText(image, str(int(offset)) + ' Not Aligned', (w - 150, 30), self.font, 0.9, self.red, 2)

                feetDist = abs(self.findX(l_ank_x, r_ank_x))

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
                # Define font size 
                if h >= 2160 and self.font_access == 1:
                    print("bigger than 2160", h)
                    self.thick = 10
                    self.text_y = 80
                    self.fontsize = 3
                    self.font_access = 0
                elif h >= 1080 and self.font_access == 1:
                    print("bigger than 1080, ", h)
                    self.fontsize = 1.5
                    self.font_access = 0
                elif self.font_access == 1:
                    print("smaller than 1080, ", h)
                    self.thick = 2
                    self.fontsize = 0.6
                    self.font_access = 0
                    
                # Draw landmarks
                cv2.circle(image, (l_shldr_x, l_shldr_y), 7, self.yellow, -1)
                cv2.circle(image, (l_shldr_x, l_shldr_y - 100), 7, self.yellow, -1)
                # Right shoulder is pink ball
                cv2.circle(image, (r_shldr_x, r_shldr_y), 7, self.pink, -1)
                cv2.circle(image, (l_hip_x, l_hip_y), 7, self.yellow, -1)
                cv2.circle(image, (l_hip_x, l_hip_y - 100), 7, self.yellow, -1)
                # STR for back angle
                angle_text_string ='Frame: '+str(currentFrame)+' Torso Angle : ' + str(int(torso_inclination)) + 'deg Feet distance: '+ str(int(feetDist)) + ' Steps: '+ str(int(steps)) 
                cv2.putText(image, angle_text_string, (10, self.text_y), self.font, self.fontsize, self.dark_blue, self.thick, cv2.LINE_AA)
                # Join landmarks
                cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), self.green, self.thick)
                cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), self.green, self.thick)
                cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), self.green, self.thick)
                # Display angles on the annotation
                cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), self.font, self.fontsize, self.pink, self.thick, cv2.LINE_AA)

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
            else:
                # print("Cannot Detect Anything!")
                # Write frames.
                video_output.write(image)    
        print('Video is done!')
        cap.release()
        video_output.release()
        self.TimingOrBack=False
        return self.AngleAtStep
        
        
    def Timingscreenshot(self,file_path,name):
        print("Screenshot Started")
        Analpath ='./application/static/Analysedphoto'
        AnalisExist = os.path.exists(Analpath)

        if not AnalisExist:
        # Create a new directory because it does not exist 
            os.makedirs(Analpath)
            print("Analysedphoto folder is created!")

        Thumbpath ='./application/static/Thumbnail'
        ThumbisExist = os.path.exists(Thumbpath)

        if not ThumbisExist:
        # Create a new directory because it does not exist 
            os.makedirs(Thumbpath)
            print("Thumbnail folder is created!")       
        cap=cv2.VideoCapture(file_path)
        x=0
        bool=True
        # print(self.BackCurrentFrameNumber.values())
        #('test_{0}.mp4'.format(datetime.datetime.now().strftime("%d-%m-%Y")
        # date=datetime.utcnow()
        # print(date)
        # print(name)
        frameLen=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # total number of frames in the video
        print(frameLen)
        print("timingframenumber", self.timingframenumber)
        while bool:
            for i in range(0,frameLen,1):
                if x>=len(self.timingframenumber):
                    bool=False
                    break
                ret, frame= cap.read()
            
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                if i == 1:
                    cv2.imwrite("./application/static/Thumbnail/frame_%d%s.jpg"%(x,name), frame)  
                if i==self.timingframenumber[0]:
                    cv2.imwrite("./application/static/Analysedphoto/frame_%d%s.jpg"%(x,name), frame)
                    print('Read a new frame: ', ret)
                    x=x+1
    
    def Backscreenshot(self,file_path,name):
        print("Screenshot Started")
        Analpath ='./application/static/Analysedphoto'
        AnalisExist = os.path.exists(Analpath)

        if not AnalisExist:
        # Create a new directory because it does not exist 
            os.makedirs(Analpath)
            print("Analysedphoto folder is created!")

        Thumbpath ='./application/static/Thumbnail'
        ThumbisExist = os.path.exists(Thumbpath)

        if not ThumbisExist:
        # Create a new directory because it does not exist 
            os.makedirs(Thumbpath)
            print("Thumbnail folder is created!")
          
        cap=cv2.VideoCapture(file_path)
        x=0
        bool=True
        frameLen=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # total number of frames in the video
        while bool:
            for i in range(0,frameLen,1):
                if x>=len(self.BackCurrentFrameNumber):
                    bool=False
                    break
                ret, frame= cap.read()
            
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                for val in self.BackCurrentFrameNumber.values():
                    if i == 1:
                        cv2.imwrite("./application/static/Thumbnail/frame_%d%s.jpg"%(x,name), frame)       
                    if i == val[0] :
                        print(cap.get(cv2.CAP_PROP_POS_FRAMES))
                        # print("iv2", i)
                        
                        print(x)
        
                        cv2.imwrite("./application/static/Analysedphoto/frame_%d%s.jpg"%(x,name), frame)     # save frame as JPEG file   
                        x=x+1
                        print('Read a new frame: ', ret)
        