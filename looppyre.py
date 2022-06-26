import pyrebase
import threading
import os
from joblib import load
import numpy as np
import pandas as pd


model_path = os.path.abspath('suhuanomaly.joblib')
model_path2=os.path.abspath('gtranomaly.joblib')
m = load(model_path)
n = load(model_path2)
interval = 5

config = {
  "apiKey": "AIzaSyCRBdKqw53VdK0y-9KZy1qcLUJHNywLP0k",
  "authDomain": "nodemcu-01-818e1.firebaseapp.com",
  "databaseURL": "https://nodemcu-01-818e1-default-rtdb.firebaseio.com",
  "projectId": "nodemcu-01-818e1",  
  "storageBucket": "nodemcu-01-818e1.appspot.com"
}

firebase = pyrebase.initialize_app(config)

db=firebase.database()


def myPeriodicFunction1():
    path=db.child('Realtimesuhuget').child('suhuRT').get()
    pathy=db.child('Realtimesuhuget').child('waktuSG').get()
    Suhu=[path.val()]
    Waktu=[pathy.val()]
    values = {'ds': Waktu, 'y':Suhu}
    df = pd.DataFrame(values)
    df['ds'] = pd.to_datetime(df['ds'])
    forecast = m.predict(df)
    result = pd.concat([df.set_index('ds')['y'], forecast.set_index('ds')[['yhat','yhat_lower','yhat_upper']]], axis=1)
    result['error'] = float(result['y']) - float(result['yhat'])
    result['uncertainty'] = float(result['yhat_upper']) - float(result['yhat_lower'])
    result['anomaly'] = result.apply(lambda x: 'Anomaly' if(np.abs(x['error']) > 0.8*x['uncertainty']) else 'Normal', axis = 1)
    detect = result['anomaly'].values
    kondisi = str(''.join(detect))
    db.child('Realtimesuhuget').child('kondisisuhu').set(kondisi)
    return(''.join(detect))

def myPeriodicFunction2():
    pathi=db.child('Realtimesuhuget').child('getRT').get()
    pathy2=db.child('Realtimesuhuget').child('waktuSG').get()
    Getaran=[pathi.val()]
    Waktu2=[pathy2.val()]
    values2 = {'ds': Waktu2, 'y':Getaran}
    df2 = pd.DataFrame(values2)
    df2['ds'] = pd.to_datetime(df2['ds'])
    forecast2 = n.predict(df2)
    result2 = pd.concat([df2.set_index('ds')['y'], forecast2.set_index('ds')[['yhat','yhat_lower','yhat_upper']]], axis=1)
    result2['error'] = float(result2['y']) - float(result2['yhat'])
    result2['uncertainty'] = float(result2['yhat_upper']) - float(result2['yhat_lower'])
    result2['anomaly'] = result2.apply(lambda x: 'Anomaly' if(np.abs(x['error']) > 0.8*x['uncertainty']) else 'Normal', axis = 1)
    detect2 = result2['anomaly'].values
    kondisi2 = str(''.join(detect2))
    db.child('Realtimesuhuget').child('kondisiget').set(kondisi2)
    return(''.join(detect2))    

def historicaldata1():
  path2=db.child('Realtimesuhuget').child('suhuRT').get()
  pathy3=db.child('Realtimesuhuget').child('waktuSG').get()
  pathi2=db.child('Realtimesuhuget').child('getRT').get()
  paths=db.child('Realtimesuhuget').child('kondisisuhu').get()
  pathg=db.child('Realtimesuhuget').child('kondisiget').get()
  suhu=path2.val()
  getaran=pathi2.val()
  waktu=pathy3.val()
  kondisisuhu=paths.val()
  kondisigetar=pathg.val()
  suhus= str(''.join(suhu))
  getarans= str(''.join(getaran))
  waktus= str(''.join(waktu))
  kondisisuhus= str(''.join(kondisisuhu))
  kondisigetars= str(''.join(kondisigetar))
  db.child("HistSGall").push({"waktu1":waktus, "suhu1":suhus, "getaran1":getarans, "kondisisuhu1":kondisisuhus, "kondisigetar1":kondisigetars})
  

def startTimer():
    threading.Timer(interval, startTimer).start()
    myPeriodicFunction1()  
    myPeriodicFunction2() 

startTimer()

