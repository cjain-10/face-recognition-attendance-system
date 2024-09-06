import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage 
from firebase_admin import db
from datetime import datetime

cred = credentials.Certificate("E:\Projects\FaceRecognitionRealTimeDatabse\serviceAccountKey.json")
firebase_admin.initialize_app(cred , 
                              {
                                  'databaseURL' : "https://faceattendancesystem-27604-default-rtdb.firebaseio.com/" ,
                                  'storageBucket' : 'faceattendancesystem-27604.appspot.com'
                              })

bucket = storage.bucket()


#cap = cv2.VideoCapture()
#cap.set(3,1280)
#cap.set(4,720)


#while True:
#    success , img = cap.read()
 #   cv2.imshow("Face Attendance" , img)
  #  cv2.waitKey(1)

imgBackground = cv2.imread('Resources/background.png')

folderModesPath = 'Resources/Modes'
modesPath = os.listdir(folderModesPath)
imagesModesPath = []
for path in modesPath:
    imagesModesPath.append(cv2.imread(os.path.join(folderModesPath , path)))


# Loading The encoding file:

print("Loading the encode file...")
file = open("EncodeFile.p" , 'rb')
encodeListKnownWithIds =  pickle.load(file)
file.close()
encodeListKnown , studentIds = encodeListKnownWithIds

print("Encode File Loaded.")


modeType = 0
counter = 0




# reducing the size of our image. instead of giving
                                                         # actual pixel values, we are scaling it to 0.25
  




while True:
   
   
   video = cv2.VideoCapture(0)
   video.set(3,640)
   video.set(4,480)
   #video.set(cv2.CAP_PROP_BUFFERSIZE , 1)
   check, frame = video.read()

   #imgS = cv2.resize(frame , (0,0) , 0.25,0.25) 
   imgS = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
   # reducing the size of our image. instead of giving actual pixel values, we are scaling it to 0.25

   faceCurrFrame = face_recognition.face_locations(imgS)
   encodeCurrFrame = face_recognition.face_encodings(imgS , faceCurrFrame) 
   # dont want to find encoding if the whole frame, just of the face. 
   # so we search current imgS for thwe current faceCurrFrame and generate the encoding for that. 
   


   imgBackground[162:162+480 , 55:55+640] = frame
   imgBackground[44:44+633 , 808:808+414] = imagesModesPath[modeType]

   if faceCurrFrame: 
    for encodeFace , faceLoc in zip(encodeCurrFrame , faceCurrFrame):
        matches = face_recognition.compare_faces(encodeListKnown , encodeFace) # comparing the scanned faces with the data faces
        faceDistance = face_recognition.face_distance(encodeListKnown ,encodeFace) # lesser the ditance , better the match.
        #print("matches:",  matches)
        #print("face distance:" , faceDistance)

        matchIndex = np.argmin(faceDistance)
        #print("Match Index:" , matchIndex)
        if matches[matchIndex]:
            #print("Known face detected")
            #print(studentIds[matchIndex])
            y1,x2,y2,x1 = faceLoc
            #y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
            bbox = 55+x1 , 162+y1 , x2-x1 , y2-y1
            imgBackground = cvzone.cornerRect(imgBackground , bbox,rt=0)
            id = studentIds[matchIndex]
            if counter == 0:
                counter = 1 
                modeType = 1 

            if counter!=0:
            
                if counter == 1:
                    # getting the data
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)

                    # getting the image from the storage
                    blob = bucket.get_blob(f'Images/{id}.png')

                    array = np.frombuffer(blob.download_as_string() , np.uint8)
                    imgStudent = cv2.imdecode(array , cv2.COLOR_BGRA2BGR)

                    #updating attendance:
                    ref = db.reference(f'Students/{id}')
                    
                    datetimeObject = datetime.strptime(studentInfo['last attendance time'],"%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    if secondsElapsed > 30:
                        ref.child('last attendance time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        ref = db.reference(f'Students/{id}')
                        studentInfo['total attendance'] +=1
                        ref.child('total attendance').set(studentInfo['total attendance'])

                    else: 
                        modeType = 3
                        counter = 0
                        imgBackground[44:44+633 , 808:808+414] = imagesModesPath[modeType]


                    if modeType !=3:

                        if 10<counter<20:
                            modeType =2
                            imgBackground[44:44+633 , 808:808+414] = imagesModesPath[modeType]


                        if counter<=10:

                            cv2.putText(imgBackground , str(studentInfo['total attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                            cv2.putText(imgBackground , str(studentInfo['major']),(1006,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                            cv2.putText(imgBackground , str(id),(1006,493),cv2.FONT_HERSHEY_COMPLEX,0.5,(100,100,100),1)
                            cv2.putText(imgBackground , str(studentInfo['conduct']),(910,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                            cv2.putText(imgBackground , str(studentInfo['year']),(1025,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                            cv2.putText(imgBackground , str(studentInfo['starting year']),(1125,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)

                            # we need to position name in the middle. For that subtract pixel len of name from total pixel length of the area where name goes.
                            # then divide the value by two and push the name pixel that far from the starting pixel of the area 


                            (w,h),t = cv2.getTextSize(studentInfo['name'] , cv2.FONT_HERSHEY_COMPLEX , 1 , 1)
                            offset = (414-w)//2
                            cv2.putText(imgBackground , str(studentInfo['name']),(808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)


                            imgBackground[175:175+216 ,909:909+216 ] = imgStudent

                        counter +=1

                        if counter>=20:
                            counter = 0
                            modeType=0
                            studentInfo=[]
                            imgStudent = []
                            imgBackground[44:44+633 , 808:808+414] = imagesModesPath[modeType]



    else:
        modeType = 0
        counter = 0


   #print(frame)
   #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #This is the Erroneous line 
   #cv2.imshow("Webcam", frame)
   cv2.imshow("Face Attendance", imgBackground)
   key = cv2.waitKey(1)
   if key == ord("q"):
       break

video.release()
cv2.destroyAllWindows()




