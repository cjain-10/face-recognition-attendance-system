import cv2
import face_recognition
import pickle 
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage 
from firebase_admin import db

cred = credentials.Certificate("E:\Projects\FaceRecognitionRealTimeDatabse\serviceAccountKey.json")
firebase_admin.initialize_app(cred , 
                              {
                                  'databaseURL' : "https://faceattendancesystem-27604-default-rtdb.firebaseio.com/" ,
                                  'storageBucket' : 'faceattendancesystem-27604.appspot.com'
                              })


# Importing the student images:


folderPath = 'Images'
imagesPath = os.listdir(folderPath)
imagesList = []
studentIds = []
for path in imagesPath:
    imagesList.append(cv2.imread(os.path.join(folderPath , path)))
    studentIds.append(os.path.splitext(path)[0])
    
    # adding the images to the storage:
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)




#print(len(imagesList))


# GENERATING ENCODINGS: 

def findEncodings(imageList):

    encodeList = []

    for img in imageList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

        encode = face_recognition.face_encodings(img)[0] # getting the first element of the encoded list of each image.
        encodeList.append(encode)

    return encodeList

print("-----Encoding Started-----")
encodeListKnown = findEncodings(imagesList)
encodeListKnownWithIds = [encodeListKnown , studentIds] 
print("-----Encoding Completed-----")
#print(encodeListKnown[1:2])


file = open("EncodeFile.p" ,'wb' )
pickle.dump(encodeListKnownWithIds , file)
file.close()
print("File saved.")
























