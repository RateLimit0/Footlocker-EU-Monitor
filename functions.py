import time 
import datetime

def time_stmap():
      return str((round(time.time(), 3))).replace(".", "")

def webhook_time_stmap():
      return datetime.datetime.now().strftime("%H:%M:%S")      