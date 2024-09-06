import firebase_admin
from firebase_admin import credentials

from firebase_admin import db

cred = credentials.Certificate("E:\Projects\FaceRecognitionRealTimeDatabse\serviceAccountKey.json")
firebase_admin.initialize_app(cred , 
                              {
                                  'databaseURL' : "https://faceattendancesystem-27604-default-rtdb.firebaseio.com/"
                              })


ref = db.reference('Students')  # it will create a student directory in our real-time database. 

data = {
    "321654" : {

        "name" : "Chirag" ,
        "major" : "Aeronautical" ,
        "starting year" : 2021 ,
        "total attendance" : 10 ,
        "conduct" : "good" ,
        "year" : 4 ,
        "last attendance time" : "2022-12-11 00:54:34" 
    },
    "852741" : {

        "name" : "Emily Blunt" ,
        "major" : "Arts" ,
        "starting year" : 2019 ,
        "total attendance" : 4 ,
        "conduct" : "good" ,
        "year" : 3 ,
        "last attendance time" : "2022-12-10 00:54:34" 
    },
    "963852" : {

        "name" : "Elon Musk" ,
        "major" : "Aerospace" ,
        "starting year" : 2017 ,
        "total attendance" : 10 ,
        "conduct" : "good" ,
        "year" : 4 ,
        "last attendance time" : "2022-12-11 00:54:34" 
    }
    


}

for key,value in data.items():
    ref.child(key).set(value)


