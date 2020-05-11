#Author : Dhanushkumar.M
#project : Capstone Project For BOLT IOT certification
import json,time,math,statistics,conf
from boltiot import Bolt,Sms,Email
def compute_bounds(history_data,frame_size,factor):
    if len(history_data)<frame_size :
        return None
    if len(history_data)>frame_size :
        del history_data[0:len(history_data)-frame_size]
    Mn=statistics.mean(history_data)
    Variance=0
    for data in history_data:
        Variance += math.pow((data-Mn),2)
    Zn=0
    Zn = factor*math.sqrt(history_data[frame_size-1])+Zn
    Low_bound = history_data[frame_size-1]-Zn
    High_bound = history_data[frame_size-1]+Zn
    return [High_bound,Low_bound]
mybolt = Bolt(conf.API_KEY, conf.DEVICE_ID)
sms = Sms(conf.SSID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER)
history_data=[]
while True:
    response = mybolt.analogRead('A0')
    data = json.loads(response)
    if data['success'] != 1:
        print("There was an error while retriving the data.")
        print("This is the error:"+data['value'])
        time.sleep(10)
        continue
    sensor_value= int(data['value'])
    sensor_valuec = sensor_value/10.24
    print("Current Freezer Temperature is "+str(sensor_valuec))
    sensor_value=0
    try:
        sensor_value = int(data['value'])
    except e:
        print("There was an error while parsing the response: ",e)
        continue
    bound = compute_bounds(history_data,conf.FRAME_SIZE,conf.MUL_FACTOR)
    if not bound:
        required_data_count=conf.FRAME_SIZE-len(history_data)
        print("Not enough data to computation. Need ",required_data_count," more data points")
        history_data.append(int(data['value']))
        time.sleep(10)
        continue
    try:
        if sensor_value > bound[0] :
            buzz=mybolt.digitalWrite('1',"HIGH")
            print(buzz)
            time.sleep(10)
            response = sms.send_sms("Temperature increased suddenly Current Temperature is: "+str(sensor_valuec))
            print("Response:",response)
            print("Anomaly of the temperature occured because of increase in temperature.")
            buzzoff=mybolt.digitalWrite('1',"LOW")
            print(buzzoff)
        elif sensor_value < bound[1]:
             buzz=mybolt.digitalWrite('1',"HIGH")
             print(buzz)
             time.sleep(10)
             print("Anomaly of the temperature occured because of decrease in temperature.")
             buzzoff=mybolt.digitalWrite('1',"LOW")
             print(buzzoff)
        history_data.append(sensor_value);
    except Exception as e:
        print ("Error",e)
    time.sleep(10)
