#Author : Dhanushkumar.M
#project : Capstone Project for BOLT IOT certification
import conf, json, time, math, statistics
from boltiot import Sms, Bolt
def send_telegram_message(message):
    url = "https://api.telegram.org/" + conf.telegram_bot_id + "/sendMessage"
    data = { "chat_id": conf.telegram_chat_id,
             "text": message
           }
    try:
        response = requests.request( "GET",
                                      url,
                                      params=data
                                   )
        print("This is the Telegram response")
        print(response.text)
        telegram_data = json.loads(response.text)
        return telegram_data["ok"]
    except Exception as e:
        print("An error occurred in sending the alert message via Telegram")
        print(e)
        return False
def compute_bounds(history_data,frame_size,factor):
   if len(history_data)<frame_size :
       return None
   if len(history_data)>frame_size :
       del history_data[0:len(history_data)-frame_size]
   Mn=statistics.mean(history_data)
   Variance=0
   for data in history_data :
       Variance += math.pow((data-Mn),2)
   Zn = factor * math.sqrt(Variance / frame_size)
   High_bound = history_data[frame_size-1]+Zn
   Low_Bound = history_data[frame_size-1]-Zn
   return [High_bound,Low_Bound]
mybolt = Bolt(conf.API_KEY, conf.DEVICE_ID)
sms = Sms(conf.SSID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER)
history_data=[]
while True:
   response = mybolt.analogRead('A0')
   data = json.loads(response)
   if data['success'] != 1:
       print("There was an error while retriving the data.")
       print("This is the error:"+data['value'])
       time.sleep(5)
       continue
   sensor_value1 = int(data['value'])
   Temperature = sensor_value1*0.0097
   print ("The current Temparature of Refrigarator is "+str(sensor_value1)+"  "+ str(Temperature)+" degree celsious ")
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
       time.sleep(5)
       continue
   try:
       if sensor_value > bound[0] :
           Temperature = sensor_value*0.097
           print ("bound[0] value is "+ str(bound[0]))
           print ("The Temparature level has been Incerased suddenly.Sending SMS")
           response = sms.send_sms("Someone Opened the fridge door. The Current temperature is " + str(Temperature)+ " degree celsious")
           message = "Alert! The Temparature level has been Increased suddenly.The Current temperature is " + str(Temperature)+ " degree celsious " 
           telegram_status = send_telegram_message(message)
           print("This is the response for SMS & Telegram ",response, telegram_status)
       elif sensor_value < bound[1] :
           Temperature= sensor_value*0.097
           print ("Anomaly is Occured due to sudden Change in Temperature")
           print("Sending Alert!")
           response = sms.send_sms("The temperature has decreased to : "+str(Temperature)+"degree celcius")
           message = "Alert! Sensor value has decreased The current value is " + str(Temperature)
           telegram_status = send_telegram_message(message)
           print("The Status of SMS and Telegram:",response, telegram_status)
       history_data.append(sensor_value);
   except Exception as e :
       print ("Error",e)
   time.sleep(5)

