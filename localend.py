import serial
import pandas as pd
import time
import threading
from prophet import Prophet as P
from statsmodels.tsa.arima_model import ARIMA
from matplotlib.animation import FuncAnimation as fnanimate
import matplotlib.pyplot as plt
from matplotlib import dates
import os
import keras
from datetime import datetime
from prophet.serialize import model_to_json, model_from_json
import pickle
import numpy

ser = serial.Serial('COM4', 115200)
if not ser.isOpen():
    ser.open()
print('com4 is open', ser.isOpen())

def __getnewargs__(self):
    return ((self.endog),(self.k_lags, self.k_diff, self.k_ma))
ARIMA.__getnewargs__ = __getnewargs__

df = pd.DataFrame(columns=['ds', 'y'])
predict = pd.DataFrame(columns=['yhat', 'yhat_lower', 'yhat_upper'])
mlpyhat = pd.DataFrame(columns=['yhat'])

def split_sequence(sequence, n_steps_in, n_steps_out):
  X, y = list(), list()
  for i in range(len(sequence)):
    # find the end of this pattern
    end_ix = i + n_steps_in
    out_end_ix = end_ix + n_steps_out
    # check if we are beyond the sequence
    if out_end_ix > len(sequence):
      break
    # gather input and output parts of the pattern
    seq_x, seq_y = sequence[i:end_ix], sequence[end_ix:out_end_ix]
    X.append(seq_x)
    y.append(seq_y)
  return numpy.array(X), numpy.array(y)

def datagather():
    # time.sleep(60)
    # while True:
        # if len(data) == 100:
    timestamp= ser.readline(128)
    ppm = ser.readline(128)
    temp = ser.readline(128)
    date_format = '%Y-%m-%d %H:%M:%S'
    tim = str(timestamp).strip("b'").replace("\\r", '').replace("\\n", '')
    # times = time.ctime(time.time())
    timestamps = datetime.strptime(tim, date_format)
    ppm = float(str(ppm).strip("b'").replace("\\r", '').replace("\\n", ''))
    # temp = float(str(temp).strip("b'").replace("\\r", '').replace("\\n", ''))
    # data.append([times, ppm, temp])
    return tim, ppm

def datadf():
    global df
    global predict
    ppmavg = []
    while True:
        dttimes, dtppm = datagather()
        ppmavg.append(dtppm)
        print(len(ppmavg), dtppm)
        if len(ppmavg) == 60:
            avg = sum(ppmavg) / len(ppmavg)
            new_rows = pd.DataFrame({'ds': [dttimes], 'y': [avg]})
            # if len(df) > 3600:
            #     del df
            #     df = pd.concat([df, new_rows], ignore_index=True)
            # else:
            df = pd.concat([df, new_rows], ignore_index=True)
            ppmavg = []
            print(df.tail())
        # print(df)
        if len(df) % 60 == 0 and len(df) != 0:
            df.to_csv('dataoutput.csv', index=False)
        # print(len(df))

        
def predictProphet():
    # with open('prophet_model.json', 'r') as fin:
    #     prophet = model_from_json(fin.read())  # Load model
    counter = 0
    global predict
    while True:
        time.sleep(3600)
        pmodel = P().fit(df)
        targetdate = pd.DataFrame(pd.date_range(df['ds'].iloc[-1], periods=len(df) + 60, freq='1min'), columns=['ds'])
        # targetdate = pd.concat([df['ds'], targetdate])
        temp = pmodel.predict(targetdate)
        # predict = pred[['yhat', 'yhat_lower', 'yhat_upper']]
        predict = temp[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        print(predict)
        predict.to_csv(f'./prophet_predict/prophet_prediction{counter}.csv', index=False)
        counter += 1
        # print(integ)

def predictMLP():
    mlp = keras.saving.load_model('new_mlp_base2.keras')
    counter = 0
    global mlpyhat
    while True:
        time.sleep(3600)
        firstpred = mlp.predict(df['y'].iloc[-60:])
        future = firstpred[-1:]
        print(firstpred)
        for i in range(60):
            pred = mlp.predict(future[-1:])
            future = numpy.append(future, pred, axis = 0)
        print(len(future))
        print(future)
        # out = open("mlpout.txt", "a")
        # out.write(str(future))
        
        predi = pd.DataFrame(future, columns=['yhat'])
        annualpred = pd.DataFrame(firstpred, columns=['yhat'])
        mlpyhat = pd.concat([mlpyhat, annualpred, predi], ignore_index=True)
        print(mlpyhat)
        mlpyhat.to_csv(f'./mlp_predict/mlp_prediction{counter}.csv', index=False, float_format="%.3f")
        counter += 1
    
def dfPlot():
    plt.cla()
    fig = plt.figure(figsize=(16, 16))
    plt.plot(df['y'], label="CO2 Value")
    plt.plot(predict['yhat'], label = "prediction")
    # plt.plot(predict['yhat_lower'], label= "lower bound prediction")
    # plt.plot(predict['yhat_upper'], label= "upper bound prediction")
    plt.plot(mlpyhat['yhat'], label = "prediction mlp")
    # plt.plot(df['datetime'], df['temp(C)'], label="Temperature")
    
    plt.legend()
    
    # plt.show()
    return fig
def onlyProp():
    plt.cla()
    fig = plt.figure(figsize=(16, 16))
    plt.plot(df['y'], label="CO2 Value")
    plt.plot(predict['yhat'], label = "prediction")
    # plt.plot(predict['yhat_lower'], label= "lower bound prediction")
    # plt.plot(predict['yhat_upper'], label= "upper bound prediction")
    # plt.plot(df['datetime'], df['temp(C)'], label="Temperature")
    
    plt.legend()
    
    # plt.show()
    return fig

def terminate_program():
    global running
    running = False
    print("Program execution time exceeded. Stopping threads and exiting...")
    

running = True
timer_thread = threading.Thread(target=terminate_program, daemon=True)
timer_thread.start()

datathread = threading.Thread(target=datadf, args=())
prophetthread = threading.Thread(target=predictProphet, args=())
arimathread = threading.Thread(target=predictMLP, args=())
datathread.start()
prophetthread.start()
arimathread.start()
itter = 0

start_time = time.time()
while  running and time.time() - start_time < 3*3600:
    time.sleep(3630)
    if running:
        myplot=dfPlot()
        myplot.savefig(f'./plot_img/plotpred{itter}')
        propplot=onlyProp()
        propplot.savefig(f'./plot_img/onlyprop{itter}')
        # plt.show()
        itter += 1

datathread.join()
prophetthread.join()
arimathread.join()  