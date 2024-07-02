import datacollect
import machine
import utime
import gc
import uos
import sys
#import numpy as np

interval = 2
datacol = machine.Timer(-1)
datasent = machine.Timer(-1)
df = []
timestamp = 0
ppm = 0
temp = 0
ppm_df = []

bmppower = machine.Pin(17, machine.Pin.OUT)
bmppower.toggle()

uart = machine.UART(0, baudrate = 115200)
uart.init(115200, bits = 8, parity=None, stop=1, tx=machine.Pin(0), rx=machine.Pin(1))

def free(full=False):
  F = gc.mem_free()
  A = gc.mem_alloc()
  T = F+A
  P = '{0:.2f}%'.format(100 - (F/T*100))
  if not full: return P
  else : return ('Total:{0} Free:{1} ({2})'.format(T,F,P))

def collect(args):
    timestamp, ppm, temp= datacollect.print_data(0)
    times = str(timestamp)
    pol = str(ppm)
    Celci = str(temp)
    sys.stdout.write(times + "\n")
    sys.stdout.write(pol+ "\n")
    sys.stdout.write(Celci+ "\n")
    #df.append([timestamp, ppm, temp])
    #ppm_df.append(ppm)
    #print(df)
    #df = []


def show(args):
    start = utime.time()
    datacol.init(period = 1 * 1000, mode= machine.Timer.PERIODIC, callback=collect)
    if utime.time() - start > 61:
        datacol.deinit()
    df.clear()
    ppm_df.clear()

datasent.init(period = 1 * 1000, mode= machine.Timer.PERIODIC, callback=collect)

#print(timestamp, ppm)
#print_data(0)

# Limitations:
# 1. MQ135 sensor sometimes "re-calibrate" it's sensor so it doesn't read, resulting ini null values
#	 Current value to replace the null is 1000 which is ppm in average indoor spaces
# 2. Most MQ sensors need to be "preheated" for at least 1 hour so the data for the first 1 hour is probably not accurate.
#	 Future changes will be made depends on project descision

