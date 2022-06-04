from flask import Flask
import pyrebase
import threading
import os
from joblib import load
import numpy as np
import pandas as pd

app = Flask(__name__)

model_path = os.path.abspath('anomaly_detection_.joblib')
m = load(model_path)
interval = 5

config = {
  "apiKey": "AIzaSyB4AQ5Sc689F6KGwqlfGr_CFZ5VuAZey08",
  "authDomain": "algoritmyo.firebaseapp.com",
  "databaseURL": "https://algoritmyo-default-rtdb.firebaseio.com",
  "projectId": "algoritmyo",  
  "storageBucket": "algoritmyo.appspot.com"
}

firebase = pyrebase.initialize_app(config)

db=firebase.database()

@app.route('/')
def myPeriodicFunction():
    path=db.child('path').child('suhu').get()
    pathy=db.child('path').child('waktu').get()
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
    db.child("path").child("Anomaly").set(kondisi)
    db.child("path").child("Kondisi").push(kondisi)
    return(''.join(detect))


def startTimer():
    threading.Timer(interval, startTimer).start()
    myPeriodicFunction()  

    startTimer()

if __name__ == '__main__':
    app.run()