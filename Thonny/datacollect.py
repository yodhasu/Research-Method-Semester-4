import machine
import utime
import math

temppin = 4
tempsen = machine.ADC(temppin)

conversion_factor = 3.3 / (65535)

ppm = 426.57
co2a = 110.7432567
co2b = -2.85935538
rload = 1000
mq2ao = machine.ADC(machine.Pin(27))
rtc = machine.RTC()

def get_temp(args):
    temp_val = tempsen.read_u16()
    vol_temp = conversion_factor * temp_val
    return (27 - (vol_temp - 0.706)/0.001721)

def get_time(idklol):
    timestamp = rtc.datetime()
    timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] +
                                                timestamp[4:7])
    return(timestring)
    
    
def get_ppm(skibidi):
    try:
        value = mq2ao.read_u16()
        converted_val = value * conversion_factor
        RS = ((1024 * rload) / value) - rload
        RO = RS * math.exp(math.log(co2a/ppm) / co2b)
        return (math.fabs(RO))
        #return(value * conversion_factor)
    except:
        return 1000
    #return(value * conversion_factor)
    

time = get_time(0)
data = get_ppm(0)

def print_data(idk):
    #print(data , " taken on " , time)
    return get_time(0), get_ppm(0), get_temp(0)
    
#timer = machine.Timer(-1)

#print_data(0)

#print_data(0)

# timer.init(period = 1000, mode= Timer.PERIODIC, callback=print_data)




#while True:
    #value = mq2ao.read_u16()   # Read and convert analog value to 16-bit integer
    # voltage = value * 5 / 4095
    #RS = ((1024 * rload) / value) - rload
    #RO = RS * math.exp(math.log(co2a/ppm) / co2b)
    # print("AO:", math.ceil(value/65.535))
    #data.append(value * conversion_factor)
    # print(timestamp, value * conversion_factor)
    # print("RO:", RO)
    # print("DO:", DigitIn.value())  # Print the analog value
    # print("Voltage:", voltage)
    # print("RS:", RS)
    # print("R0:", R0)
    #X =10 ^( math.log(Rs/Ro) - y1)/m +x1)
    #print("")
    #utime.sleep(1)  # Wait for 200 milliseconds before the next read
    # print("=============================================================")
    # print(time, data)
    #pass


    