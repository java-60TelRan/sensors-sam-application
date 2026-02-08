from datetime import datetime
import os
from zoneinfo import ZoneInfo
from logger import logger
import json
def processMessage(messageDict: dict, tz_name: str):
    
    sensorId, value,  dt = messageDict["sensorId"],messageDict["value"]\
    , datetime.fromtimestamp(messageDict["timestamp"], tz=ZoneInfo(tz_name))
    print(f"sensorId = {sensorId}\navg value = {value}\ndate-time={dt}")
  
def processRecord(record, tz_name):
    message = record["Sns"]["Message"]
    logger.debug(f"message from SNS record is {message}")
    messageDict: dict = json.loads(message)
    processMessage(messageDict, tz_name)
    
def lambda_handler(event, context):
    try:
        tz_name = os.getenv('TZ', 'Asia/Jerusalem')
        for record in event["Records"]:
            processRecord(record, tz_name)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise e        
    

